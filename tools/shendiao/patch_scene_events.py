# -*- coding: utf-8 -*-
"""批量修场景里的 GameEvent：层级 / Trigger 开关 / 交互目标(EventTargets) / 触发器位置。

移植来的 JYX2 场景常见三种毛病，本工具一次修掉：

1. GameEvent 宿主物体落在 Default(0) 层，而 Jyx2Player 只用
   LayerMask.GetMask("GameEvent")（本项目 = 20）做 OverlapSphere，
   层级不对 → 交互面板永远不弹。
2. 触发器的 BoxCollider m_IsTrigger: 0 → 变成隐形实体方块，既挡路又不会触发
   OnTriggerEnter。
3. m_EventTargets 指向原版剧情的 NPC（被清理后变空 → HasEventTargets=false
   → GameEventManager.TryTrigger 直接 return，交互同样不弹）。

用法:
    python tools/shendiao/patch_scene_events.py --scene <scene.unity> \\
        --set-layer 20 --trigger \\
        --set-target 559=9141536188722368271 \\
        --clear-target 5,6 \\
        --move 559=-2.5,5.9,13.5 \\
        --collider 559=3.5,3.5,3.5 --apply
默认 dry-run。

--collider 给的是**世界尺寸**（会按 Transform 的 m_LocalScale 折算成 m_Size），
因为 Jyx2Player.CanSee() 用 target.bounds.Contains(player + dir*radius) 判定，
1x1x1 的小盒子玩家几乎踩不到，只有凑到某个角度才能交互。
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from list_prefab_instances import split_blocks  # noqa: E402

GO_RE = re.compile(r'm_GameObject: \{fileID: (-?\d+)\}')
# 空列表有两种写法：`m_EventTargets: []` 与 `m_EventTargets:` 换行接空列表，
# 只认后者会让「本来没有 target 的事件」永远绑不上目标（静默跳过，n=0）。
TARGETS_RE = re.compile(r'(^  m_EventTargets:)(?: \[\])?\n((?:  - \{fileID: -?\d+\}\n)*)', re.M)
POS_RE = re.compile(r'(^  m_LocalPosition: \{x: )([-0-9.e]+)(, y: )([-0-9.e]+)'
                    r'(, z: )([-0-9.e]+)(\})', re.M)
SIZE_RE = re.compile(r'(^  m_Size: \{x: )([-0-9.e]+)(, y: )([-0-9.e]+)'
                     r'(, z: )([-0-9.e]+)(\})', re.M)
SCALE_RE = re.compile(r'^  m_LocalScale: \{x: ([-0-9.e]+), y: ([-0-9.e]+), z: ([-0-9.e]+)\}',
                      re.M)


def parse_args(argv):
    opt = {'set-target': [], 'clear-target': [], 'move': [], 'collider': [], 'set-event': []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            k = a[2:]
            if k in ('apply', 'trigger'):
                opt[k] = True
                i += 1
            elif k in ('set-target', 'clear-target', 'move', 'collider', 'set-event'):
                opt[k].append(argv[i + 1])
                i += 2
            else:
                opt[k] = argv[i + 1]
                i += 2
        else:
            i += 1
    return opt


def find_events(blocks, by_fid):
    """返回 [{mono_fid, go_fid, go_name, ids{Interactive,UseItem,Enter}, body}]"""
    out = []
    for b in blocks:
        if b['cls'] != '114' or 'm_EventTargets' not in b['body']:
            continue
        m = GO_RE.search(b['body'])
        go = m.group(1) if m else None
        gob = by_fid.get(go)
        name = ''
        if gob:
            nm = re.search(r'^  m_Name: (.*)$', gob['body'], re.M)
            name = nm.group(1).strip() if nm else ''
        ids = {}
        for key in ('Interactive', 'UseItem', 'Enter'):
            v = re.search(r'm_%sEventId: (\S+)' % key, b['body'])
            ids[key] = v.group(1) if v else '-1'
        out.append({'mono': b, 'go': go, 'name': name, 'ids': ids})
    return out


def fmt(v):
    """浮点写成 Unity YAML 习惯的紧凑形式：1.75 / 3.5 / 2"""
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return s if s else '0'


def main_key(evt):
    """事件的主标识：优先返回第一个非 -1 的事件 ID，否则返回 GameObject 名"""
    for key in ('Interactive', 'UseItem', 'Enter'):
        if evt['ids'][key] not in ('-1', ''):
            return evt['ids'][key]
    return evt['name']


def resolve(events, token):
    hits = [e for e in events if main_key(e) == token]
    if not hits:
        hits = [e for e in events if e['name'] == token]
    if not hits:
        # 无名字的空事件物体（m_Name 为空）只能按 GameObject fileID 定位
        hits = [e for e in events if e['go'] == token]
    return hits



def main():
    opt = parse_args(sys.argv[1:])
    scene = opt['scene']
    apply = opt.get('apply', False)

    text = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)
    by_fid = {b['fid']: b for b in blocks}
    events = find_events(blocks, by_fid)
    print('%s' % scene)
    print('场景里有 %d 个 GameEvent' % len(events))
    print()

    edits = {}

    def set_body(b, nb):
        edits[b['fid']] = nb

    if opt.get('set-layer'):
        layer = int(opt['set-layer'])
        for e in events:
            gob = by_fid.get(e['go'])
            if not gob:
                continue
            nb, n = re.subn(r'^  m_Layer: \d+', '  m_Layer: %d' % layer,
                            edits.get(gob['fid'], gob['body']), count=1, flags=re.M)
            if n:
                set_body(gob, nb)
                print('  layer -> %-2d : %s' % (layer, e['name']))

    if opt.get('trigger'):
        for e in events:
            for b in blocks:
                if b['cls'] != '65':
                    continue
                m = GO_RE.search(b['body'])
                if not m or m.group(1) != e['go']:
                    continue
                body = edits.get(b['fid'], b['body'])
                nb = re.sub(r'^  m_IsTrigger: 0', '  m_IsTrigger: 1', body, count=1, flags=re.M)
                if nb != body:
                    set_body(b, nb)
                    print('  IsTrigger=1    : %s  (BoxCollider &%s)' % (e['name'], b['fid']))

    for spec in opt['set-target']:
        token, val = spec.split('=', 1)
        tgts = [t.strip() for t in val.split(',') if t.strip() and t.strip() != 'none']
        lst = ''.join('  - {fileID: %s}\n' % t for t in tgts)
        for e in resolve(events, token):
            body = edits.get(e['mono']['fid'], e['mono']['body'])
            nb, n = TARGETS_RE.subn(lambda m: m.group(1) + '\n' + lst, body, count=1)
            if n:
                set_body(e['mono'], nb)
                print('  targets=%-22s : %s' % (tgts, e['name']))

    for spec in opt['clear-target']:
        for token in spec.split(','):
            token = token.strip()
            if not token:
                continue
            for e in resolve(events, token):
                body = edits.get(e['mono']['fid'], e['mono']['body'])
                nb, n = TARGETS_RE.subn(lambda m: m.group(1) + '\n', body, count=1)
                if n:
                    set_body(e['mono'], nb)
                    print('  targets=[]                     : %s' % e['name'])

    for spec in opt['set-event']:
        token, val = spec.split('=', 1)
        for e in resolve(events, token):
            body = edits.get(e['mono']['fid'], e['mono']['body'])
            nb, n = re.subn(r'^  m_InteractiveEventId: \S+',
                            '  m_InteractiveEventId: %s' % val, body, count=1, flags=re.M)
            if n:
                set_body(e['mono'], nb)
                print('  event=%-24s : %s' % (val, e['name'] or e['go']))

    for spec in opt['move']:
        token, val = spec.split('=', 1)
        x, y, z = [v.strip() for v in val.split(',')]
        for e in resolve(events, token):
            tr = None
            for b in blocks:
                if b['cls'] in ('4', '224') and ('m_GameObject: {fileID: %s}' % e['go']) in b['body']:
                    tr = b
                    break
            if tr is None:
                print('  !! %s 找不到 Transform，跳过移动' % e['name'])
                continue
            body = edits.get(tr['fid'], tr['body'])
            nb = POS_RE.sub(lambda m: (m.group(1) + x + m.group(3) + y
                                       + m.group(5) + z + m.group(7)), body, count=1)
            set_body(tr, nb)
            print('  pos=(%s, %s, %s) : %s' % (x, y, z, e['name']))

    # Jyx2Player.CanSee() 用 target.bounds.Contains(player + dir*radius) 判定，
    # 盒子小到 1x1x1 时玩家几乎不可能命中，还会退化成 Raycast 分支 ——
    # 射线先打到 NPC 自己的碰撞体，判定直接失败。表现就是"对着人却没有光圈，
    # 只有某个角度、某个距离才能交互"。这里按**世界尺寸**给，内部自动除以
    # Transform 的 m_LocalScale。
    for spec in opt['collider']:
        token, val = spec.split('=', 1)
        wx, wy, wz = [float(v.strip()) for v in val.split(',')]
        for e in resolve(events, token):
            tr = None
            col = None
            for b in blocks:
                if ('m_GameObject: {fileID: %s}' % e['go']) not in b['body']:
                    continue
                if b['cls'] in ('4', '224') and tr is None:
                    tr = b
                if b['cls'] == '65' and col is None:
                    col = b
            if col is None:
                print('  !! %s 没有 BoxCollider，跳过' % e['name'])
                continue
            scale = (1.0, 1.0, 1.0)
            if tr is not None:
                m = SCALE_RE.search(edits.get(tr['fid'], tr['body']))
                if m:
                    scale = tuple(float(m.group(k)) for k in (1, 2, 3))
            size = tuple(a / (b if b else 1.0) for a, b in zip((wx, wy, wz), scale))
            body = edits.get(col['fid'], col['body'])
            nb = SIZE_RE.sub(lambda m: (m.group(1) + fmt(size[0]) + m.group(3)
                                        + fmt(size[1]) + m.group(5) + fmt(size[2])
                                        + m.group(7)), body, count=1)
            if nb != body:
                set_body(col, nb)
                print('  collider 世界=%-18s : %s  (BoxCollider &%s)'
                      % ('(%g, %g, %g)' % (wx, wy, wz), e['name'], col['fid']))

    spans = []
    for fid, nb in edits.items():
        b = by_fid[fid]
        hdr_len = (b['end'] - b['start']) - len(b['body'])
        spans.append((b['start'] + hdr_len, b['end'], nb))
    new_text = text
    for start, end, content in sorted(spans, key=lambda s: -s[0]):
        new_text = new_text[:start] + content + new_text[end:]

    print()
    print('改动 %d 个块；文件 %d -> %d 字节' % (len(edits), len(text), len(new_text)))
    if apply:
        io.open(scene, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(new_text)
        print('已写入 %s' % scene)
    else:
        print('（dry-run，未写盘；加 --apply 生效）')


if __name__ == '__main__':
    main()
