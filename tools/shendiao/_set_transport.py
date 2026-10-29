# -*- coding: utf-8 -*-
"""把子地图 Leave 传送点的落点改成指定的大地图触发器，实现"剧情结束后直接到门口"。

原理（MapTeleportor.DoTransport）:
    没配 TransportTriggerName 时 -> para.triggerName = curMap.Name（即落回同名节点）
    配了                          -> para.triggerName = TransportTriggerName

用法: python tools/shendiao/_set_transport.py [--apply]
"""
import io
import os
import re
import sys

ROOT = r'c:\Games\jynew'
MAPS = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Maps', 'GameMaps')
APPLY = '--apply' in sys.argv
GUID = '77ff8b67996ae6c419a86e052dfcd6e2'  # MapTeleportor.cs

# 场景 -> 落点（大地图 Level/Triggers 下的节点名）
PLAN = {
    '62_pomiao.unity': '桃花岛',    # 序章结束后出庙，直接落到桃花岛渡口
    '75_taohuadao.unity': '重阳宫',  # 离岛赴终南
}


def escaped(s):
    return '"' + ''.join(c if ord(c) < 128 else '\\u%04X' % ord(c) for c in s) + '"'


report = []
for scene, target in PLAN.items():
    fp = os.path.join(MAPS, scene)
    t = io.open(fp, encoding='utf-8').read()
    # 找到挂 MapTeleportor 且物体名为 Leave 的那个块
    blocks = re.split(r'(?m)^(--- )', t)
    done = False
    out = []
    i = 0
    while i < len(blocks):
        seg = blocks[i]
        if GUID in seg and 'TransportTriggerName' in seg:
            old = re.search(r'(?m)^  TransportTriggerName: .*$', seg)
            if old:
                newline = '  TransportTriggerName: ' + escaped(target)
                seg = seg[:old.start()] + newline + seg[old.end():]
                done = True
                report.append('%s: TransportTriggerName -> %s' % (scene, target))
        out.append(seg)
        i += 1
    t2 = ''.join(out)
    if not done:
        report.append('%s: **没找到 MapTeleportor/TransportTriggerName**' % scene)
        continue
    if APPLY:
        io.open(fp, 'w', encoding='utf-8', newline='\n').write(t2)

io.open(os.path.join(ROOT, 'Logs', '_transport_fix.txt'), 'w', encoding='utf-8').write('\n'.join(report))
print(('%s' % ('已写入' if APPLY else '预演')) + '\n' + '\n'.join(report))
