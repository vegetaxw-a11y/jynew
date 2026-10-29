# -*- coding: utf-8 -*-
"""把郭靖/黄蓉的场景实例从 sit_on_chair 动画改回站立 idle。

现象：破庙里郭靖、黄蓉"坐在半空中"，之后每张图只要有他俩都在坐。
根因：prefab 实例的 m_Modifications 把 Animator.m_Controller 覆盖成了
      BuildSource/AnimationControllers/sit_on_chair.controller，
      而场景里并没有给他们摆椅子 —— 于是悬空盘坐。

用法: python tools/shendiao/_fix_sitting_npc.py [--apply]
"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
MAPS = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps')
APPLY = '--apply' in sys.argv

SIT_ON_CHAIR = '3c2253daa36057047816b5ab63f5950f'

# prefab guid -> 应使用的站立 controller
STAND = {
    'e258f6bf50035b54888fd864fd4996c5': ('郭靖', 'c1fb7eef08ade9f49869d15acfbbc888'),  # GuojingController
    '6c5e0db599ddbae4a9131a44e36f0342': ('黄蓉', 'afb4f35abeec2b0428bbbd377272bf07'),  # HuangrongController
}

report = []
for scene in sorted(os.listdir(MAPS)):
    if not scene.endswith('.unity'):
        continue
    fp = os.path.join(MAPS, scene)
    t = io.open(fp, encoding='utf-8').read()
    if SIT_ON_CHAIR not in t:
        continue
    orig = t
    for prefab_guid, (who, ctrl) in STAND.items():
        # 逐个 PrefabInstance 块处理
        pattern = re.compile(
            r'(^--- !u!1001 &-?\d+\nPrefabInstance:\n.*?m_SourcePrefab: \{fileID: 100100000, guid: '
            + prefab_guid + r', type: 3\})', re.S | re.M)
        pieces = []
        last = 0
        for m in pattern.finditer(t):
            pieces.append(t[last:m.start()])
            blk = m.group(1)
            if SIT_ON_CHAIR in blk:
                blk = blk.replace(
                    'objectReference: {fileID: 9100000, guid: ' + SIT_ON_CHAIR + ', type: 2}',
                    'objectReference: {fileID: 9100000, guid: ' + ctrl + ', type: 2}')
                report.append('%s: %s 改为站立 idle' % (scene, who))
            pieces.append(blk)
            last = m.end()
        pieces.append(t[last:])
        t = ''.join(pieces)
    if t != orig and APPLY:
        io.open(fp, 'w', encoding='utf-8', newline='\n').write(t)

out = ['%s: %d 处' % ('已写入' if APPLY else '预演', len(report))] + report
io.open(os.path.join(ROOT, 'Logs', '_sitting_fix.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
