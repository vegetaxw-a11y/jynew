# -*- coding: utf-8 -*-
"""列出场景里所有 Collider，并把 local 尺寸折算成**世界尺寸**（乘 Transform 的 m_LocalScale）。

用途：排查"空气墙" / "走不过去" —— 找出挡在路上的实体碰撞体（m_IsTrigger: 0）。
注意：Unity 里 BoxCollider.m_Size 是 local 的，实际占据空间还要乘 lossyScale。

用法:
    python tools/shendiao/list_colliders.py --scene <scene.unity> [--near 32,11] [--solid-only] [--all]

    --near X,Z      按到该平面点的距离升序输出（默认取全场景前 20 条）
    --solid-only    只看实体碰撞体（m_IsTrigger: 0），排查空气墙时用这个
    --all           输出全部
"""
import io
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from list_prefab_instances import split_blocks  # noqa: E402

POS = re.compile(r"m_LocalPosition: \{x: ([-0-9.e]+), y: ([-0-9.e]+), z: ([-0-9.e]+)\}")
SIZ = re.compile(r"m_Size: \{x: ([-0-9.e]+), y: ([-0-9.e]+), z: ([-0-9.e]+)\}")
SCL = re.compile(r"m_LocalScale: \{x: ([-0-9.e]+), y: ([-0-9.e]+), z: ([-0-9.e]+)\}")
RAD = re.compile(r"m_Radius: ([-0-9.e]+)")
HGT = re.compile(r"m_Height: ([-0-9.e]+)")
TRIG = re.compile(r"m_IsTrigger: ([-0-9.e]+)")

# Unity YAML class id -> 名称
COLL = {
    "64": "Mesh",
    "65": "Box",
    "135": "Sphere",
    "136": "Capsule",
    "143": "CharCtrl",
}


def dec(s):
    """把 YAML 里 \\uXXXX 转义的中文还原。"""
    try:
        return s.encode("ascii", "ignore").decode("unicode_escape")
    except Exception:
        return s


def parse_args(argv):
    opt = {}
    i = 0
    while i < len(argv):
        if argv[i].startswith('--'):
            k = argv[i][2:]
            if k in ('all', 'solid-only'):
                opt[k] = True
                i += 1
            else:
                opt[k] = argv[i + 1]
                i += 2
        else:
            i += 1
    return opt


def world_size(body, trans):
    """返回 (世界尺寸 or None, 半径 or None, 高度 or None)"""
    sc = SCL.search(trans)
    scale = [float(sc.group(k)) for k in (1, 2, 3)] if sc else [1.0, 1.0, 1.0]

    sz = SIZ.search(body)
    size = None
    if sz:
        # 注意 group 是 1..3，不是 0..2
        size = tuple(float(sz.group(k + 1)) * scale[k] for k in range(3))

    rad = RAD.search(body)
    radius = float(rad.group(1)) * max(abs(scale[0]), abs(scale[2])) if rad else None

    hgt = HGT.search(body)
    height = float(hgt.group(1)) * abs(scale[1]) if hgt else None

    return size, radius, height


def main():
    opt = parse_args(sys.argv[1:])
    scene = opt['scene']
    near = None
    if opt.get('near'):
        a, b = opt['near'].split(',')
        near = (float(a), float(b))

    text = io.open(scene, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)
    by = {b['fid']: b for b in blocks}

    rows = []
    for b in blocks:
        kind = COLL.get(b['cls'])
        if kind is None:
            continue
        m = re.search(r"m_GameObject: \{fileID: (\d+)\}", b['body'])
        if not m:
            continue
        go = by.get(m.group(1))
        if not go:
            continue

        nm = re.search(r'm_Name: "?([^"\n]*)', go['body'])
        name = dec(nm.group(1)) if nm else '?'

        # GameObject 的第一个 component 一定是 Transform
        comp = re.search(r"- component: \{fileID: (\d+)\}", go['body'])
        trans = by.get(comp.group(1)) if comp else None
        if not trans:
            continue

        p = POS.search(trans['body'])
        if not p:
            continue
        x, y, z = (float(p.group(k)) for k in (1, 2, 3))

        tr = TRIG.search(b['body'])
        trig = int(tr.group(1)) if tr else 0

        size, radius, height = world_size(b['body'], trans['body'])
        rows.append({
            'name': name, 'kind': kind, 'pos': (x, y, z),
            'size': size, 'radius': radius, 'height': height,
            'trigger': trig, 'enabled': 'm_Enabled: 0' not in b['body'],
        })

    solid = [r for r in rows if r['trigger'] == 0 and r['enabled']]
    print('场景: %s' % scene)
    print('Collider 共 %d 个，其中实体(trigger=0, enabled) %d 个' % (len(rows), len(solid)))

    show = solid if opt.get('solid-only') else rows
    if opt.get('solid-only'):
        show = solid

    if near:
        show = sorted(show, key=lambda r: math.hypot(r['pos'][0] - near[0], r['pos'][2] - near[1]))
    if not opt.get('all'):
        show = show[:20]

    print()
    for r in show:
        x, y, z = r['pos']
        desc = []
        if r['size']:
            sx, sy, sz = r['size']
            desc.append('世界尺寸=(%.1f, %.1f, %.1f)' % (sx, sy, sz))
            desc.append('x[%.1f,%.1f]' % (x - sx / 2, x + sx / 2))
            desc.append('z[%.1f,%.1f]' % (z - sz / 2, z + sz / 2))
        if r['radius'] is not None:
            desc.append('半径=%.2f' % r['radius'])
        if r['height'] is not None:
            desc.append('高=%.1f' % r['height'])
        d = (' d=%.1fm' % math.hypot(x - near[0], z - near[1])) if near else ''
        flag = 'TRIGGER' if r['trigger'] else '**实体**'
        print('  %-9s %-14s pos=(%7.2f,%6.2f,%7.2f)%s  %s  %s' % (
            r['kind'], r['name'], x, y, z, d, flag, ' '.join(desc)))


if __name__ == '__main__':
    main()
