"""打印场景里指定 GameObject 的世界坐标（沿 father 链累加平移）。用法: python _node_pos.py <scene> <名字> [...]"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
fp = os.path.join(ROOT, sys.argv[1])
targets = set(sys.argv[2:])
t = io.open(fp, encoding='utf-8', errors='replace').read()
blocks = re.split(r'^--- ', t, flags=re.M)

goname, goparent = {}, {}
tr = {}
for b in blocks:
    m1 = re.match(r'!u!1 &(-?\d+)', b)
    if m1:
        nm = re.search(r'^  m_Name: (.*)$', b, re.M)
        goname[m1.group(1)] = (nm.group(1) if nm else '?').strip('"')
    m2 = re.match(r'!u!4 &(-?\d+)', b)
    if m2:
        go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', b)
        fa = re.search(r'm_Father: \{fileID: (-?\d+)\}', b)
        pos = re.search(r'm_LocalPosition: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', b)
        tr[m2.group(1)] = (go.group(1) if go else '0', fa.group(1) if fa else '0',
                           (float(pos.group(1)), float(pos.group(2)), float(pos.group(3))) if pos else (0, 0, 0))
        if go:
            goparent[go.group(1)] = m2.group(1)

out = ['=== %s ===' % os.path.basename(fp)]
for go, name in gosorted if False else sorted(goname.items()):
    pass

for go, name in goname.items():
    if targets and name not in targets:
        continue
    tid = goparent.get(go)
    p = [0.0, 0.0, 0.0]
    chain = []
    hop = 0
    while tid and hop < 12:
        g, fa, pos = tr[tid]
        p = [p[0] + pos[0], p[1] + pos[1], p[2] + pos[2]]
        chain.append(goname.get(g, '?'))
        if fa == '0':
            break
        tid = fa
        hop += 1
    out.append('%-16s 世界(%7.2f,%7.2f,%7.2f)  链: %s' % (
        name[:16], p[0], p[1], p[2], ' <- '.join(chain)))

io.open(os.path.join(ROOT, 'Logs', '_nodepos.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
