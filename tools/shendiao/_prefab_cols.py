"""列出 prefab 里所有 Collider（类型 / 中心 / 尺寸 / 是否 trigger / 所属物体名）。"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
rel = sys.argv[1]
t = io.open(os.path.join(ROOT, rel), encoding='utf-8', errors='replace').read()

# GameObject fileID -> name
goname = {}
for m in re.finditer(r'^--- !u!1 &(-?\d+)\nGameObject:\n(.*?)(?=^--- |\Z)', t, re.S | re.M):
    nm = re.search(r'^  m_Name: (.*)$', m.group(2), re.M)
    goname[m.group(1)] = (nm.group(1) if nm else '?').strip('"')

out = ['=== %s ===' % rel]
cnt = {}
for m in re.finditer(r'^--- !u!(\d+) &(-?\d+)\n(\w+):\n(.*?)(?=^--- |\Z)', t, re.S | re.M):
    kind, fid, cls, body = m.group(1), m.group(2), m.group(3), m.group(4)
    if cls not in ('BoxCollider', 'MeshCollider', 'SphereCollider', 'CapsuleCollider'):
        continue
    go = re.search(r'm_GameObject: \{fileID: (-?\d+)\}', body)
    name = goname.get(go.group(1), '?') if go else '?'
    center = re.search(r'm_Center: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', body)
    size = re.search(r'm_Size: \{x: ([-eE\d.]+), y: ([-eE\d.]+), z: ([-eE\d.]+)\}', body)
    trig = re.search(r'm_IsTrigger: (\d)', body)
    en = re.search(r'm_Enabled: (\d)', body)
    out.append('%-14s %-22s trigger=%s enabled=%s center=%s size=%s' % (
        cls, name[:22],
        trig.group(1) if trig else '?', en.group(1) if en else '?',
        center.groups() if center else '-', size.groups() if size else '-'))
    cnt[cls] = cnt.get(cls, 0) + 1

out.insert(1, '合计: %s' % cnt)
io.open(os.path.join(ROOT, 'Logs', '_prefab_cols.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('ok %s' % cnt)
