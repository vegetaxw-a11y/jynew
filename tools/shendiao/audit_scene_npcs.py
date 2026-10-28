# -*- coding: utf-8 -*-
"""审计场景里的交互事件：谁挂着事件、有没有可见 NPC、NPC 离触发器多远。

要解决的问题（用户实测反馈）：
  "我去了桃花岛，郭芙没找到" —— 事件 922 让玩家去后院找郭芙，
  但 75_taohuadao.unity 里一个 prefab 实例都没有人物模型。

本工具对每个 GameEvent 输出：
  EventId / 触发器位置 / m_EventTargets 解析结果 / 附近的人形 prefab 实例 / 间距

判定：
  NO_TARGET   m_EventTargets 为空 → 靠近不显示高亮（事件永远点不到）
  DANGLING    targets 指向的 fileID 在场景里不存在
  FAR(x.xm)   target 距触发器 > 3m → 高亮框在别处，玩家以为没东西
  NO_NPC      有 target，但目标不是人形 prefab 且附近 3m 内没有人形实例
  OK          以上都不是

用法:
    python tools/shendiao/audit_scene_npcs.py <scene.unity> [--near 8]
    python tools/shendiao/audit_scene_npcs.py --all        （扫 shendiao 全部场景）
    python tools/shendiao/audit_scene_npcs.py --all --quiet （只打问题项）
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from list_prefab_instances import guid_index, split_blocks, unescape  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MAPS = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps')

GAME_EVENT_GUID = '28456c42ed689d9458276be4c9851804'
LUA_DIR = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua')
CHAR_CFG = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', 'shendiao',
                        'Configs', 'Lua', 'CharacterConfig.lua')
CHAR_RE = re.compile(r'^\{(\d+),[\d\-]+,[\d\-]+,\[\[(.+?)\]\]', re.M)


def char_names():
    """人物 id -> 中文名（从生成的 CharacterConfig.lua 读，保证与运行时一致）。"""
    if not os.path.exists(CHAR_CFG):
        return {}
    txt = io.open(CHAR_CFG, encoding='utf-8', errors='replace').read()
    return {int(i): n for i, n in CHAR_RE.findall(txt)}

MOD_RE = re.compile(r'propertyPath:\s*(\S+)\s*\n\s+value:\s*(.*?)\s*\n', re.M)
TARGETS_RE = re.compile(r'^  m_EventTargets:(.*?)(?=^  \w)', re.M | re.S)
POS_RE = re.compile(r'\{x: ([- \d.eE+]+), y: ([- \d.eE+]+), z: ([- \d.eE+]+)\}')


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


def pos_of(mods):
    """prefab 实例的局部位置；没 override 就是 None（真值在 prefab 内部，场景文件查不到）。"""
    if 'm_LocalPosition.x' not in mods:
        return None
    return (num(mods.get('m_LocalPosition.x')),
            num(mods.get('m_LocalPosition.y')),
            num(mods.get('m_LocalPosition.z')))


def load(path):
    text = io.open(path, encoding='utf-8', errors='surrogateescape').read()
    return text, split_blocks(text)


def build_index(blocks):
    """返回解析后的各种映射。"""
    go_name, tr_go, tr_pos, tr_father = {}, {}, {}, {}
    events, instances, stripped_owner = [], [], {}

    for b in blocks:
        cls, fid, st, body = b['cls'], b['fid'], b['stripped'], b['body']
        if cls == '1' and not st:
            m = re.search(r'^  m_Name: (.*)$', body, re.M)
            if m:
                go_name[fid] = unescape(m.group(1))
        elif cls in ('4', '224') and not st:
            g = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
            if g:
                tr_go[g.group(1)] = fid
            p = re.search(r'^  m_LocalPosition: ' + POS_RE.pattern, body, re.M)
            if p:
                tr_pos[fid] = tuple(num(p.group(k)) for k in (1, 2, 3))
            fa = re.search(r'^  m_Father: \{fileID: (-?\d+)\}', body, re.M)
            if fa:
                tr_father[fid] = fa.group(1)
        elif cls == '1001' and not st:
            src = re.search(r'm_SourcePrefab: \{fileID: -?\d+, guid: ([0-9a-f]{32})', body)
            mods = {k: v for k, v in MOD_RE.findall(body)}
            par = re.search(r'm_TransformParent: \{fileID: (-?\d+)\}', body)
            inst = {
                'fid': fid,
                'name': unescape(mods.get('m_Name', '')),
                'guid': src.group(1) if src else '',
                'pos': pos_of(mods),
                'parent_tr': par.group(1) if par else None,
                'root_tr': None,
            }
            instances.append(inst)
        elif cls == '114' and not st:
            sc = re.search(r'^  m_Script: \{fileID: 11500000, guid: (\w+)', body, re.M)
            if not sc or sc.group(1) != GAME_EVENT_GUID:
                continue
            g = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
            tm = TARGETS_RE.search(body)

            def fld(name):
                m = re.search(r'^  %s: (.*)$' % name, body, re.M)
                return unescape(m.group(1)) if m else None

            events.append({
                'go': g.group(1) if g else None,
                'inter': fld('m_InteractiveEventId'),
                'enter': fld('m_EnterEventId'),
                'useitem': fld('m_UseItemEventId'),
                'targets': re.findall(r'- \{fileID: (-?\d+)\}', tm.group(1)) if tm else [],
            })

    # stripped 子块归属（prefab 内部的 GameObject / Transform）
    for b in blocks:
        if not b['stripped']:
            continue
        m = re.search(r'^  m_PrefabInstance: \{fileID: (-?\d+)\}', b['body'], re.M)
        if not m:
            continue
        for inst in instances:
            if inst['fid'] == m.group(1):
                stripped_owner[b['fid']] = inst
                if b['cls'] in ('4', '224'):
                    inst['root_tr'] = b['fid']
                break
    return go_name, tr_go, tr_pos, tr_father, events, instances, stripped_owner


def make_world(tr_pos, tr_father, instances):
    inst_by_tr = {i['root_tr']: i for i in instances if i['root_tr']}

    def world(tr_fid, depth=0):
        if not tr_fid or depth > 32:
            return None
        if tr_fid in tr_pos:
            local, father = tr_pos[tr_fid], tr_father.get(tr_fid)
        elif tr_fid in inst_by_tr:
            inst = inst_by_tr[tr_fid]
            local, father = inst['pos'], inst['parent_tr']
        else:
            return None
        p = world(father, depth + 1) if father else None
        if local is None:
            return p
        if p is None:
            return local
        return (p[0] + local[0], p[1] + local[1], p[2] + local[2])

    return world


def is_char_prefab(path):
    if not path:
        return False
    p = path.replace('\\', '/').lower()
    return ('modelcharacters' in p) or ('/prefabs/' in p)


def dist(a, b):
    if not a or not b:
        return None
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def fmt(p):
    return '(%.1f, %.1f, %.1f)' % p if p else '?'


def audit(scene, idx, near=3.0, quiet=False, names=None):
    text, blocks = load(scene)
    go_name, tr_go, tr_pos, tr_father, events, instances, owner = build_index(blocks)
    world = make_world(tr_pos, tr_father, instances)

    chars = []
    known = {n for n in (names or {}).values() if n}
    for inst in instances:
        path = idx.get(inst['guid'], '')
        nm = inst['name'] or os.path.basename(path)
        if known:
            # 名字能对上人物表才算「剧情人物实体」（QZhenDiZi / Sark_1 这类不算）
            if not any(k in nm or nm in k for k in known):
                continue
        elif not is_char_prefab(path):
            continue
        w = world(inst['root_tr']) if inst['root_tr'] else inst['pos']
        chars.append({'name': nm, 'pos': w, 'path': path})

    rows, problems, lua_miss = [], 0, []
    for ev in events:
        name = go_name.get(ev['go'], ev['go'])
        tpos = world(tr_go.get(ev['go']))

        kind = 'inter'
        eid = ev['inter']
        if eid in (None, '-1'):
            eid, kind = ev['enter'], 'enter'
        if eid in (None, '-1'):
            eid, kind = ev['useitem'], 'item'

        tgt_desc, status, worst = [], 'OK', 0.0
        if kind == 'inter':
            if not ev['targets']:
                status = 'NO_TARGET'
            for tf in ev['targets']:
                if tf == '0':
                    status = 'DANGLING'
                    tgt_desc.append('<空引用>')
                    continue
                inst = owner.get(tf)
                if inst is None and tf in go_name:
                    tn, tp = go_name[tf], world(tr_go.get(tf))
                elif inst is not None:
                    tn = inst['name'] or os.path.basename(idx.get(inst['guid'], ''))
                    tp = world(inst['root_tr'])
                else:
                    tn, tp = '<不存在 &%s>' % tf, None
                    status = 'DANGLING'
                d = dist(tpos, tp)
                if d is not None and d > worst:
                    worst = d
                tgt_desc.append('%s%s' % (tn, '' if d is None else ' %.1fm' % d))
            if status == 'OK' and worst > near:
                status = 'FAR'

        # 剧情人物核对：Lua 里 Talk(id) 点名的人，场景里有实体吗
        if kind == 'inter' and eid and eid != '-1' and names:
            lp = os.path.join(LUA_DIR, '%s.lua' % eid)
            if os.path.exists(lp):
                src = io.open(lp, encoding='utf-8', errors='replace').read()
                want = sorted({int(x) for x in re.findall(r'\bTalk\(\s*(\d+)', src)} - {0})
                missing = []
                for cid in want:
                    cn = names.get(cid, '')
                    if not cn:
                        continue
                    if not any(cn in c['name'] or c['name'] in cn for c in chars):
                        missing.append('%s(%d)' % (cn, cid))
                if missing:
                    lua_miss.append('%s -> %s' % (eid, '、'.join(missing)))

        if status != 'OK':
            problems += 1

        rows.append({'name': name, 'eid': eid, 'kind': kind, 'pos': tpos, 'status': status,
                     'targets': ', '.join(tgt_desc) or '-',
                     'nearby': '、'.join(c['name'] for c in chars) or '-'})

    print('=' * 100)
    print('%s   事件 %d 个，问题 %d 个   在场人形 NPC：%s'
          % (os.path.basename(scene), len(events), problems,
             '、'.join(c['name'] for c in chars) or '【无】'))
    if lua_miss:
        print('  ! 剧情点名但场上没有：')
        for m in lua_miss:
            print('      %s' % m)
    if problems or not quiet:
        print('%-16s %-6s %-20s %-10s %-28s %s'
              % ('触发器', 'EventId', '位置', '判定', '目标(target)', '类型'))
        for r in rows:
            if quiet and r['status'] == 'OK':
                continue
            print('%-16s %-6s %-20s %-10s %-28s %s'
                  % (str(r['name'])[:16], r['eid'], fmt(r['pos']), r['status'],
                     r['targets'][:28], r['kind']))
    return problems


def main():
    argv = sys.argv[1:]
    idx = guid_index()
    names = char_names()
    near = 3.0
    if '--near' in argv:
        near = float(argv[argv.index('--near') + 1])
    quiet = '--quiet' in argv

    if '--all' in argv:
        total = 0
        for s in sorted(f for f in os.listdir(MAPS) if f.endswith('.unity')):
            total += audit(os.path.join(MAPS, s), idx, near, quiet, names)
        print()
        print('合计问题事件：%d' % total)
        return

    audit(argv[0], idx, near, quiet, names)


if __name__ == '__main__':
    main()

