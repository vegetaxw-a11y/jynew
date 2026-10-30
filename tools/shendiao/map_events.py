# -*- coding: utf-8 -*-
"""把「正式场景 -> 事件 -> 脚本首句」列出来，方便看章节骨架。

只统计 MapConfig 里真实存在的地图（其它是废弃场景，玩家进不去）。

用法:
    python tools/shendiao/map_events.py            # 全部正式场景
    python tools/shendiao/map_events.py 18_gumu    # 只看某个场景
"""
import io
import os
import re
import sys

GAME_EVENT_GUID = '28456c42ed689d9458276be4c9851804'
BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?', re.M)
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
MOD = 'shendiao'


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
        s = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)
    return s


def field(body, name):
    m = re.search(r'^  %s: (.*)$' % name, body, re.M)
    return unquote(m.group(1)) if m else None


def formal_maps():
    """从 MapConfig.lua 解析 id/名称/场景，只保留 id < 100 的正式地图。"""
    p = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', MOD, 'Configs', 'Lua', 'MapConfig.lua')
    txt = io.open(p, encoding='utf-8', errors='replace').read()
    out = {}
    for m in re.finditer(r'\{(\d+),\[\[(.*?)\]\],\[\[(\w+)\]\]', txt):
        mid, name, scene = int(m.group(1)), m.group(2), m.group(3)
        if mid < 100 and scene not in out:
            out[scene] = (mid, name)
    return out


def scan_scene(path):
    text = io.open(path, encoding='utf-8', errors='replace').read()
    blocks = []
    ms = list(BLOCK_RE.finditer(text))
    for i, m in enumerate(ms):
        if m.group(3):
            continue
        blocks.append((m.group(1), m.group(2), m.end(),
                       ms[i + 1].start() if i + 1 < len(ms) else len(text)))

    names, tr_pos = {}, {}
    for cls, fid, s, e in blocks:
        body = text[s:e]
        if cls == '1':
            n = field(body, 'm_Name')
            if n is not None:
                names[fid] = n
        elif cls in ('4', '224'):
            go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
            pos = re.search(r'^  m_LocalPosition: \{x: ([- \d.e]+), y: ([- \d.e]+), z: ([- \d.e]+)\}',
                            body, re.M)
            if go and pos:
                tr_pos[go.group(1)] = tuple(float(pos.group(k)) for k in (1, 2, 3))

    rows = []
    for cls, fid, s, e in blocks:
        if cls != '114':
            continue
        body = text[s:e]
        script = re.search(r'^  m_Script: \{fileID: 11500000, guid: (\w+)', body, re.M)
        if not script or script.group(1) != GAME_EVENT_GUID:
            continue
        ids = [field(body, 'm_InteractiveEventId'), field(body, 'm_UseItemEventId'),
               field(body, 'm_EnterEventId')]
        ids = [i for i in ids if i and i.lstrip('-').isdigit() and int(i) >= 0]
        if not ids:
            continue
        go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
        gid = go.group(1) if go else '?'
        pos = tr_pos.get(gid)
        for one in ids:
            rows.append((int(one), names.get(gid, gid), pos))
    return rows


def lua_first(path):
    if not os.path.exists(path):
        return '<无脚本>'
    for line in io.open(path, encoding='utf-8', errors='replace').read().split('\n'):
        s = line.strip()
        if not s or s.startswith('--'):
            continue
        return s[:70]
    return '<空>'


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    maps_dir = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', MOD, 'Maps', 'GameMaps')
    lua_dir = os.path.join(REPO, 'jyx2', 'Assets', 'Mods', MOD, 'Lua')
    formal = formal_maps()

    for scene, (mid, cname) in sorted(formal.items(), key=lambda kv: kv[1][0]):
        if only and only not in scene:
            continue
        path = os.path.join(maps_dir, scene + '.unity')
        if not os.path.exists(path):
            print('!! 场景缺失: %s' % scene)
            continue
        rows = sorted(scan_scene(path), key=lambda r: r[0])
        print('=== id=%-3d %-8s %-24s 事件 %d 个 ===' % (mid, cname, scene, len(rows)))
        for ev, obj, pos in rows:
            first = lua_first(os.path.join(lua_dir, '%d.lua' % ev))
            print('  ev=%-5d %-16s %-22s %s'
                  % (ev, obj[:16], ('(%.1f, %.1f)' % (pos[0], pos[2])) if pos else '?', first))
        print('')
    return 0


if __name__ == '__main__':
    sys.exit(main())
