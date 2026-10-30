# -*- coding: utf-8 -*-
"""在整个 MOD 的场景里找「哪个物体绑了哪个事件 ID」。

用法:
    python tools/shendiao/find_event.py 4 557 558 559 1001
    python tools/shendiao/find_event.py --mod shendiao 559

输出: 每个命中事件的 (场景, 物体名, 局部坐标, 交互/用物品/经过)
用于排查「同一剧情被绑了两个不同事件」「旧版脚本还留在场景里」这类问题。
"""
import os
import re
import sys

GAME_EVENT_GUID = '28456c42ed689d9458276be4c9851804'
BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?', re.M)

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
        s = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)
    return s


def field(body, name):
    m = re.search(r'^  %s: (.*)$' % name, body, re.M)
    return unquote(m.group(1)) if m else None


def scan_scene(path, want):
    text = open(path, 'r', encoding='utf-8', errors='replace').read()
    # 快速跳过：三个字段一个都没出现
    if want is not None and not any(('EventId: %s' % w) in text for w in want):
        return []

    blocks = []
    ms = list(BLOCK_RE.finditer(text))
    for i, m in enumerate(ms):
        if m.group(3):
            continue
        blocks.append((m.group(1), m.group(2), m.end(),
                       ms[i + 1].start() if i + 1 < len(ms) else len(text)))

    names, tr_pos, parents = {}, {}, {}
    for cls, _fid, s, e in blocks:
        body = text[s:e]
        if cls == '1':
            n = field(body, 'm_Name')
            if n is not None:
                names[_fid] = n
        elif cls in ('4', '224'):
            go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
            pos = re.search(r'^  m_LocalPosition: \{x: ([- \d.e]+), y: ([- \d.e]+), z: ([- \d.e]+)\}',
                            body, re.M)
            par = re.search(r'^  m_Father: \{fileID: (-?\d+)\}', body, re.M)
            if go:
                if pos:
                    tr_pos[go.group(1)] = tuple(float(pos.group(k)) for k in (1, 2, 3))
                if par:
                    parents[go.group(1)] = par.group(1)
            elif pos:  # stripped prefab instance
                pass

    hits = []
    for cls, _fid, s, e in blocks:
        if cls != '114':
            continue
        body = text[s:e]
        script = re.search(r'^  m_Script: \{fileID: 11500000, guid: (\w+)', body, re.M)
        if not script or script.group(1) != GAME_EVENT_GUID:
            continue
        ids = (field(body, 'm_InteractiveEventId'),
               field(body, 'm_UseItemEventId'),
               field(body, 'm_EnterEventId'))
        found = [i for i in ids if (want is None and i and i.lstrip('-').isdigit()
                                    and int(i) >= 0) or (want is not None and i in want)]
        if not found:
            continue
        go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
        gid = go.group(1) if go else '?'
        pos = tr_pos.get(gid)
        # 同一个 GameEvent 可能同时挂交互/用物品/经过三种 id，逐个登记
        for one in found:
            hits.append((one, names.get(gid, gid),
                         '(%.1f, %.1f, %.1f)' % pos if pos else '?',
                         '%s / %s / %s' % ids,
                         names.get(parents.get(gid, ''), '')))
    return hits


def audit_all(mod):
    """双向比对：Lua 脚本 <-> 场景事件绑定。"""
    lua_dir = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', mod, 'Lua')
    lua_ids = {f[:-4] for f in os.listdir(lua_dir)
               if f.endswith('.lua') and f[:-4].isdigit()}

    maps = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', mod, 'Maps', 'GameMaps')
    scenes = sorted(f for f in os.listdir(maps) if f.endswith('.unity'))

    bound = {}   # event_id -> [(scene, obj, pos)]
    for sc in scenes:
        for ev, obj, pos, trio, _p in scan_scene(os.path.join(maps, sc), None):
            bound.setdefault(ev, []).append((sc, obj, pos))

    bound_ids = set(bound)
    dead = sorted(lua_ids - bound_ids, key=int)
    orphan = sorted(bound_ids - lua_ids, key=int)

    print('=== 事件/脚本双向审计（%s）===' % mod)
    print('  场景 %d 个 / 绑定事件 %d 个 / Lua 脚本 %d 个'
          % (len(scenes), len(bound_ids), len(lua_ids)))
    print('')
    print('一、写了脚本但没有任何场景绑定（玩家永远看不到）: %d' % len(dead))
    for i in dead:
        print('    %s.lua' % i)
    print('')
    print('二、场景绑了事件但没有对应脚本（点了没反应 / 报错）: %d' % len(orphan))
    for i in orphan:
        for sc, obj, pos in bound[i][:3]:
            print('    ev=%-6s %-30s %-8s %s' % (i, sc, obj, pos))
    print('')

    # 同一事件绑在多个场景的情况
    multi = {k: v for k, v in bound.items() if len({s for (s, _o, _p) in v}) > 1}
    print('三、同一事件绑在多个场景（可能是复用/也可能是残留）: %d' % len(multi))
    for k in sorted(multi, key=int):
        print('    ev=%-6s %s' % (k, ', '.join(sorted({s for (s, _o, _p) in multi[k]}))))
    return 0


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    mod = 'shendiao'
    if '--mod' in args:
        i = args.index('--mod')
        mod = args[i + 1]
        del args[i:i + 2]

    if '--all' in args:
        return audit_all(mod)

    want = set(args)

    maps = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', mod, 'Maps', 'GameMaps')
    scenes = sorted(f for f in os.listdir(maps) if f.endswith('.unity'))
    print('搜索事件 %s（%d 个场景）' % (', '.join(sorted(want)), len(scenes)))
    total = 0
    for sc in scenes:
        for ev, obj, pos, trio, parent in scan_scene(os.path.join(maps, sc), want):
            total += 1
            print('  ev=%-6s %-30s %-26s %-30s %s / %s'
                  % (ev, sc, obj, pos, trio, parent))
    print('命中 %d 处' % total)
    if total == 0:
        print('  （这些事件没有任何场景绑定 —— 对应 Lua 是死脚本，或者触发靠 Lua 内部调用）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
