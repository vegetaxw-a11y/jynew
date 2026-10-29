"""列出/关闭场景里 NavMeshObstacle 的 m_Carve（运行时挖掉 NavMesh = 空气墙）。

用法: python tools/shendiao/_nav_carve.py <scene.unity> [--carve-off] [--apply]
"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
rel = sys.argv[1]
CARVE_OFF = '--carve-off' in sys.argv
APPLY = '--apply' in sys.argv
fp = os.path.join(ROOT, rel)
t = io.open(fp, encoding='utf-8').read()

# GameObject fileID -> name
goname = {}
for m in re.finditer(r'^--- !u!1 &(-?\d+)\nGameObject:\n(.*?)(?=^--- |\Z)', t, re.S | re.M):
    nm = re.search(r'^  m_Name: (.*)$', m.group(2), re.M)
    goname[m.group(1)] = (nm.group(1) if nm else '?').strip('"')

out = []
changed = 0
for m in list(re.finditer(r'^--- !u!208 &(-?\d+)\nNavMeshObstacle:\n(.*?)(?=^--- |\Z)', t, re.S | re.M)):
    blk = m.group(0)
    carve = re.search(r'^  m_Carve: (\d)$', blk, re.M)
    if not carve:
        continue
    go = re.search(r'^  m_GameObject: \{fileID: (-?\d+)\}', blk, re.M)
    name = goname.get(go.group(1), '?') if go else '?'
    ext = re.search(r'^  m_Extents: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', blk, re.M)
    out.append('&%s %-20s carve=%s extents=%s' % (m.group(1), name[:20], carve.group(1),
                                                  ext.groups() if ext else '-'))
    if CARVE_OFF and carve.group(1) == '1':
        newblk = blk.replace('  m_Carve: 1', '  m_Carve: 0', 1)
        t = t.replace(blk, newblk, 1)
        changed += 1

if APPLY and changed:
    io.open(fp, 'w', encoding='utf-8', newline='\n').write(t)

res = ['=== %s ===' % os.path.basename(rel)] + out + ['', '改变 %d 个' % changed]
print('\n'.join(res))
io.open(os.path.join(ROOT, 'Logs', '_navcarve.txt'), 'w', encoding='utf-8').write('\n'.join(res))
