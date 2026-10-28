# -*- coding: utf-8 -*-
"""列出场景里所有 GameEvent 的配置（所属物体、位置、三种事件 ID）。

用法: python tools/shendiao/inspect_events.py <scene.unity>
"""
import re
import sys

GAME_EVENT_GUID = '28456c42ed689d9458276be4c9851804'

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?', re.M)


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
        s = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)
    return s


def field(body, name):
    m = re.search(r'^  %s: (.*)$' % name, body, re.M)
    return unquote(m.group(1)) if m else None


def main():
    path = sys.argv[1]
    text = open(path, 'r', encoding='utf-8', errors='replace').read()

    blocks = []
    ms = list(BLOCK_RE.finditer(text))
    for i, m in enumerate(ms):
        if m.group(3):
            continue
        blocks.append((m.group(1), m.group(2), m.end(),
                       ms[i + 1].start() if i + 1 < len(ms) else len(text)))

    names, tr_pos, parents = {}, {}, {}
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
            par = re.search(r'^  m_Father: \{fileID: (-?\d+)\}', body, re.M)
            if go:
                if pos:
                    tr_pos[go.group(1)] = tuple(float(pos.group(k)) for k in (1, 2, 3))
                if par:
                    parents[go.group(1)] = par.group(1)

    print('场景: %s' % path)
    print('%-8s %-28s %-28s %-10s %s' % ('物体', '位置(x, y, z)', '交互/用物品/经过', '父物体', '组件'))
    for cls, fid, s, e in blocks:
        if cls != '114':
            continue
        body = text[s:e]
        script = re.search(r'^  m_Script: \{fileID: 11500000, guid: (\w+)', body, re.M)
        if not script or script.group(1) != GAME_EVENT_GUID:
            continue
        go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
        gid = go.group(1) if go else '?'
        pos = tr_pos.get(gid)
        print('%-8s %-28s %-28s %-10s %s'
              % (names.get(gid, gid),
                 ('(%.1f, %.1f, %.1f)' % pos) if pos else '?',
                 '%s / %s / %s' % (field(body, 'm_InteractiveEventId'),
                                   field(body, 'm_UseItemEventId'),
                                   field(body, 'm_EnterEventId')),
                 names.get(parents.get(gid, ''), '?'),
                 (re.search(r'^  m_EventTargets:\n(.*?)(?=^  \w)', body, re.M | re.S) or
                  [None]) and 'targets?' or ''))


if __name__ == '__main__':
    main()
