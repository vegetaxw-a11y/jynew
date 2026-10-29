# -*- coding: utf-8 -*-
"""清掉 Skills/*.asset 里指向不存在资源的引用（悬空 guid -> {fileID: 0}）。

背景：进战斗时要实例化技能显示里的特效 prefab（blockPartilePrefab 等），
      引用的 guid 在工程里不存在 -> 运行时拿到 null -> 战斗静默错乱/崩。

用法: python tools/shendiao/_fix_skill_refs.py [--apply]
"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
ASSETS = os.path.join(ROOT, 'jyx2', 'Assets')
APPLY = '--apply' in sys.argv

# 1) 收集工程内所有 guid
known = set()
for dirpath, dirs, files in os.walk(ASSETS):
    for f in files:
        if not f.endswith('.meta'):
            continue
        try:
            head = io.open(os.path.join(dirpath, f), encoding='utf-8', errors='replace').read(400)
        except Exception:
            continue
        for line in head.splitlines():
            if line.startswith('guid:'):
                known.add(line.split(':', 1)[1].strip().lower())
                break

SKILLS = os.path.join(ASSETS, 'Mods', 'shendiao', 'Skills')
report = []
total = 0
for n in sorted(os.listdir(SKILLS)):
    if not n.endswith('.asset'):
        continue
    fp = os.path.join(SKILLS, n)
    t = io.open(fp, encoding='utf-8').read()
    orig = t
    fixed = []

    # 形如： xxx: {fileID: 123456, guid: <32hex>, type: 3}
    def sub(m):
        g = m.group(2).lower()
        if g in known:
            return m.group(0)
        fixed.append('%s(fileID %s)' % (g[:8], m.group(1)))
        return m.group(0).replace('fileID: ' + m.group(1), 'fileID: 0').replace(
            ', guid: ' + m.group(2), '')

    t = re.sub(r'fileID: (-?\d+), guid: ([0-9a-fA-F]{32})', sub, t)
    if t != orig:
        total += len(fixed)
        report.append('%s: 清掉 %d 处 -> %s' % (n, len(fixed), ', '.join(fixed)))
        if APPLY:
            io.open(fp, 'w', encoding='utf-8', newline='\n').write(t)

out = ['工程 guid %d 个' % len(known), '%s %d 处悬空引用' % ('已修' if APPLY else '待修', total), '']
out += report
io.open(os.path.join(ROOT, 'Logs', '_skillrefs.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[:2]))
