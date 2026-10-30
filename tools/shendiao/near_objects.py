# -*- coding: utf-8 -*-
"""列出 .unity 场景里某个平面位置附近的物体（含普通 GameObject，不只 prefab 实例）。

用途：往场景里摆 NPC 之前先看看目标点周围有什么（墓碑、树、石头、楼梯），
避免把人塞进石头里或者悬在半空。

只输出 Transform 的**局部坐标**（Level 下的子物体基本等于世界坐标；
如果父链上带缩放/偏移，先用 inspect_transform.py 核对）。

用法:
    python tools/shendiao/near_objects.py <scene.unity> --x 0 --z -14 --r 6
    python tools/shendiao/near_objects.py <scene.unity> --y 5 --r 8
"""
import io
import math
import re
import sys

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?\n', re.M)


def unescape(s):
    s = s.strip()
    while len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)


def parse(text):
    ms = list(BLOCK_RE.finditer(text))
    blocks = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        blocks.append((m.group(1), m.group(2), bool(m.group(3)), text[m.end():end]))

    name = {}
    tr_of_go = {}
    tr_info = {}
    for cls, fid, st, body in blocks:
        if st:
            continue
        if cls == '1':
            m = re.search(r'^  m_Name: (.*)$', body, re.M)
            if m:
                name[fid] = unescape(m.group(1))
        elif cls in ('4', '224'):
            g = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', body, re.M)
            fa = re.search(r'^  m_Father: \{fileID: (-?\d+)\}', body, re.M)
            anchor = ('m_AnchoredPosition' in body)
            if anchor:
                p = re.search(r'm_AnchoredPosition: \{x: (-?[\d.eE+-]+), y: (-?[\d.eE+-]+)\}',
                              body)
                pos = (float(p.group(1)), 0.0, float(p.group(2))) if p else (0, 0, 0)
            else:
                p = re.search(r'm_LocalPosition: \{x: (-?[\d.eE+-]+), y: (-?[\d.eE+-]+), '
                              r'z: (-?[\d.eE+-]+)\}', body)
                pos = tuple(float(x) for x in p.groups()) if p else None
            if g:
                tr_of_go[g.group(1)] = fid
            tr_info[fid] = (g.group(1) if g else None, fa.group(1) if fa else None, pos)
    return name, tr_of_go, tr_info


def main():
    argv = sys.argv[1:]
    scene = argv[0]
    def opt(k, d=None):
        return float(argv[argv.index('--' + k) + 1]) if '--' + k in argv else d
    cx = opt('x', 0.0)
    cz = opt('z', 0.0)
    radius = opt('r', 8.0)
    ymin = opt('y', 0.0)

    text = io.open(scene, encoding='utf-8', errors='replace').read()
    name, tr_of_go, tr_info = parse(text)

    rows = []
    for fid, (go, father, pos) in tr_info.items():
        if pos is None or go is None:
            continue
        d = math.hypot(pos[0] - cx, pos[2] - cz)
        if d > radius or pos[1] < ymin - 1.0:
            continue
        rows.append((d, name.get(go, '?'), pos))
    rows.sort()
    print('场景 %s  以 (%.1f, *, %.1f) 为中心、半径 %.1f 内的物体：%d 个'
          % (scene, cx, cz, radius, len(rows)))
    print('%-8s %-30s %s' % ('距离', '名称', '(x, y, z)'))
    print('-' * 70)
    for d, nm, pos in rows:
        print('%-8.1f %-30s (%.2f, %.2f, %.2f)' % (d, nm, pos[0], pos[1], pos[2]))


if __name__ == '__main__':
    main()
