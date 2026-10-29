"""列出场景里所有 NavMeshObstacle 的位置/尺寸/是否 carving，并关联到所属物体名与父节点坐标。"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
fp = os.path.join(ROOT, sys.argv[1])
t = io.open(fp, encoding='utf-8', errors='replace').read()
blocks = re.split(r'^--- ', t, flags=re.M)

# GameObject fileID -> name
goname = {}
for b in blocks:
    m = re.match(r'!u!1 &(-?\d+)', b)
    if m:
        nm = re.search(r'^  m_Name: (.*)$', b, re.M)
        goname[m.group(1)] = (nm.group(1) if nm else '?').strip('"')

# Transform fileID -> (go, father, pos)
tr = {}
for b in blocks:
    m = re.match(r'!u!4 &(-?\d+)', b)
    if not m:
        continue
    go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', b)
    fa = re.search(r'm_Father: \{fileID: (-?\d+)\}', b)
    pos = re.search(r'm_LocalPosition: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', b)
    tr[m.group(1)] = (go.group(1) if go else '0', fa.group(1) if fa else '0',
                      (float(pos.group(1)), float(pos.group(2)), float(pos.group(3))) if pos else (0, 0, 0))


def world(go):
    """沿 father 链累加位置（只加平移，忽略旋转/缩放）。"""
    tid = None
    for k, v in tr.items():
        if v[0] == go:
            tid = k
            break
    p = [0.0, 0.0, 0.0]
    hop = 0
    while tid and hop < 12:
        g, fa, pos = tr[tid]
        p = [p[0] + pos[0], p[1] + pos[1], p[2] + pos[2]]
        if fa == '0':
            break
        tid = fa
        hop += 1
    return p


out = ['=== %s NavMeshObstacle ===' % os.path.basename(fp)]
for b in blocks:
    if not b.startswith('!u!208 '):
        continue
    go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', b)
    name = goname.get(go.group(1), '?') if go else '?'
    shape = re.search(r'm_Shape: (\d)', b)
    center = re.search(r'm_Center: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', b)
    size = re.search(r'm_Size: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', b)
    carve = re.search(r'm_CarveOnlyStationary: (\d)', b)
    carving = re.search(r'm_Carving: (\d)', b)
    wp = world(go.group(1)) if go else (0, 0, 0)
    out.append('物体=%-18s 世界位置=(%.2f, %.2f, %.2f) shape=%s size=%s center=%s carving=%s' % (
        name[:18], wp[0], wp[1], wp[2],
        shape.group(1) if shape else '?',
        size.groups() if size else '-',
        center.groups() if center else '-',
        carving.group(1) if carving else '?'))

io.open(os.path.join(ROOT, 'Logs', '_obstacles.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
