"""打印指定 instanceID 的 PrefabInstance 原始 YAML 块。用法: python _dump_instance.py <scene> <instanceID>"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
fp = os.path.join(ROOT, sys.argv[1])
target = sys.argv[2]
t = io.open(fp, encoding='utf-8', errors='replace').read()
for m in re.finditer(r'^--- !u!1001 &(-?\d+)\nPrefabInstance:\n(.*?)(?=^--- |\Z)', t, re.S | re.M):
    if m.group(1) != target:
        continue
    io.open(os.path.join(ROOT, 'Logs', '_inst_dump.txt'), 'w', encoding='utf-8').write(
        '--- !u!1001 &%s\nPrefabInstance:\n%s' % (m.group(1), m.group(2)))
    print('found %d chars' % len(m.group(2)))
    break
else:
    print('not found')
