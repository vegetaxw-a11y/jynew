# -*- coding: utf-8 -*-
"""查场景里指定名字对象的 Transform 局部旋转（四元数 + 欧拉角）。

用法: python /tmp/_rot.py <scene.unity> <name1> [name2 ...]
"""
import math
import re
import sys

BLOCK_RE = re.compile(r'^--- !u!(\d+) &(-?\d+)( stripped)?', re.M)


def unquote(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
        s = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), s)
    return s


def quat_to_euler(x, y, z, w):
    """Unity 的 ZXY 顺序 -> 度（近似，够判断用）。"""
    # pitch (x)
    sinp = 2.0 * (w * x + y * z)
    if abs(sinp) >= 1:
        rx = math.copysign(math.pi / 2, sinp)
    else:
        rx = math.asin(sinp)
    # yaw (y)
    ry = math.atan2(2.0 * (w * y - z * x), 1.0 - 2.0 * (x * x + y * y))
    # roll (z)
    rz = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (x * x + z * z))
    return tuple(round(math.degrees(v), 1) for v in (rx, ry, rz))


def main():
    path = sys.argv[1]
    names = sys.argv[2:]
    text = open(path, 'r', encoding='utf-8', errors='replace').read()

    blocks = list(BLOCK_RE.finditer(text))
    gos, rots = {}, {}
    for i, m in enumerate(blocks):
        if m.group(3):
            continue
        cls, fid = m.group(1), m.group(2)
        start, end = m.end(), (blocks[i + 1].start() if i + 1 < len(blocks) else len(text))
        body = text[start:end]
        if cls == '1':
            nm = re.search(r'^  m_Name: (.*)$', body, re.M)
            if nm:
                gos[fid] = unquote(nm.group(1))
        elif cls in ('4', '224'):
            go = re.search(r'^  m_GameObject: \{fileID: (\d+)\}', body, re.M)
            rot = re.search(
                r'^  m_LocalRotation: \{x: ([-\d.e]+), y: ([-\d.e]+), z: ([-\d.e]+), w: ([-\d.e]+)\}',
                body, re.M)
            pos = re.search(
                r'^  m_LocalPosition: \{x: ([-\d.e]+), y: ([-\d.e]+), z: ([-\d.e]+)\}', body, re.M)
            hint = re.search(
                r'^  m_LocalEulerAnglesHint: \{x: ([-\d.]+), y: ([-\d.]+), z: ([-\d.]+)\}',
                body, re.M)
            if go and rot:
                rots[go.group(1)] = {
                    'q': [float(rot.group(k)) for k in (1, 2, 3, 4)],
                    'p': [float(pos.group(k)) for k in (1, 2, 3)] if pos else None,
                    'hint': [float(hint.group(k)) for k in (1, 2, 3)] if hint else None,
                }

    print('场景: %s' % path)
    for go, name in gos.items():
        if names and name not in names:
            continue
        r = rots.get(go)
        if not r:
            print('  %-22s (无 Transform 或为 prefab 实例内部)' % name)
            continue
        q = r['q']
        e = quat_to_euler(*q)
        print('  %-22s  pos=%s  quat=[%.7f, %.7f, %.7f, %.7f]  euler≈%s  hint=%s'
              % (name, ['%.3f' % v for v in r['p']] if r['p'] else '?', *q, e, r['hint']))


if __name__ == '__main__':
    main()
