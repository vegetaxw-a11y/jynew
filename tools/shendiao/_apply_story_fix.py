# -*- coding: utf-8 -*-
"""shendiao 剧情修复批次 1：
1) 923 学会蛤蟆功没真正学会 -> LearnMagic2(0, 31, 0)
2) 465 桃花岛"船靠了岸"旁白每次进出都复述 -> 只播一次
3) 28 处 ShowMessage 的"下一步去哪"改成角色内心独白 + 红色重点标注

用法: python tools/shendiao/_apply_story_fix.py [--apply]
"""
import io
import os
import sys

ROOT = r'c:\Games\jynew'
LUA = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'Lua')
APPLY = '--apply' in sys.argv

RED = '<color=#FF0000>%s</color>'

# ---- 1) ShowMessage -> 内心独白 -----
# key: (文件, 原文行)
REPL = [
    ('0', 'ShowMessage("序章·铁枪庙：在庙里四处走走，打听父亲的旧事。")',
     'Talk(0, "（' + RED % '庙里' + '还有几位香客。爹的旧事，或许有人记得。）")'),
    ('1001', 'ShowMessage("序章完成：出庙上大地图，往【桃花岛】走。")',
     'Talk(0, "（我把铁枪残片揣进怀里，跟着郭伯伯出了庙门。）")\n'
     'Talk(0, "（船就泊在' + RED % '庙外' + '的河口。）")'),
    ('113', 'ShowMessage("后山的活死人墓，夜里石门不关。")',
     'Talk(0, "（' + RED % '后山' + '有座活死人墓。听说石门夜里不关。）")'),
    ('20', 'ShowMessage("活死人墓：往里走，看看有没有人。")',
     'Talk(0, "（往里走。总得看看' + RED % '墓里' + '有没有人。）")'),
    ('210', 'ShowMessage("学会了「全真剑法」。去寒玉床上打坐。")',
     'Talk(0, "（全真剑法，我学会了。该去' + RED % '寒玉床' + '上打坐了。）")'),
    ('219', 'ShowMessage("第一章《活死人墓》完。接下来：终南山后的山洞。")',
     'Talk(0, "（活死人墓的日子，到今夜为止。往' + RED % '终南山后的山洞' + '去。）")'),
    ('22', 'ShowMessage("去石室深处，见一见古墓派的主人。")',
     'Talk(0, "（' + RED % '石室深处' + '。古墓派的主人，就在那里。）")'),
    ('28', 'ShowMessage("李莫愁还在墓中，小心行事。")',
     'Talk(0, "（' + RED % '李莫愁' + '还在墓里。走路要轻。）")'),
    ('394', 'ShowMessage("第二章《神雕侠》完。下一站：绝情谷。")',
     'Talk(0, "（该去' + RED % '绝情谷' + '了。）")'),
    ('4', 'ShowMessage("序章：出庙后往大地图右下方走，赶赴【重阳宫】寻访白袍客。")',
     'Talk(0, "（要寻那白袍客，得往' + RED % '重阳宫' + '去。）")'),
    ('455', 'ShowMessage("重阳宫：入内寻丘处机道长（顺着山门往宫里走）。")',
     'Talk(0, "（' + RED % '丘处机' + '道长在宫里。顺着山门往里走。）")'),
    ('456', 'ShowMessage("第一章·重阳宫：回大地图，往后山深处去。那里有座活死人墓。")',
     'Talk(0, "（重阳宫的日子到头了。往' + RED % '后山' + '去，那里有一座活死人墓。）")'),
    ('457', 'ShowMessage("第一章·重阳宫：去见你的师父赵志敬。")',
     'Talk(0, "（' + RED % '赵志敬' + '——我那位师父。该去见他了。）")'),
    ('465', 'ShowMessage("桃花岛：往里走，郭伯伯在等你。")',
     'Talk(0, "（' + RED % '往里走' + '。郭伯伯在等我。）")'),
    ('466', 'ShowMessage("桃花岛：随黄蓉读书。岛上还有别处可去。")',
     'Talk(0, "（跟着黄伯母读书。这岛上，还有别处可去。）")'),
    ('466', 'ShowMessage("桃花岛：回大地图，往【重阳宫】去。")',
     'Talk(10, "过儿，' + RED % '终南山，重阳宫' + '。")'),
    ('557', 'ShowMessage("序章·铁枪庙：庙里有位老庙祝，去问问他爹的旧事。")',
     'Talk(0, "（' + RED % '老庙祝' + '在庙里。爹的旧事，他也许知道。）")'),
    ('558', 'ShowMessage("得到【铁枪残片】。去问庙里的老庙祝。")',
     'Talk(0, "（铁枪残片。去问' + RED % '老庙祝' + '。）")'),
    ('559', 'ShowMessage("序章·铁枪庙：去庙内佛堂，见那位白袍客人。")',
     'Talk(0, "（' + RED % '佛堂' + '里那位白袍客人，还在等。）")'),
    ('837', 'ShowMessage("大雕似乎在叫你跟着它走。")',
     'Talk(0, "（大雕回头看了我一眼，像是叫我' + RED % '跟着它' + '。）")'),
    ('900', 'ShowMessage("郭靖下山去了。往后这重阳宫，只能靠自己。")',
     'Talk(0, "（郭伯伯下山了。这' + RED % '重阳宫' + '，往后只能靠自己。）")'),
    ('901', 'ShowMessage("第一章·重阳宫：在后山做杂役，与师兄弟们打打交道。")',
     'Talk(0, "（' + RED % '后山' + '的杂役。师兄弟们都在那儿。）")'),
    ('901', 'ShowMessage("赵志敬借故责罚。去问问后山的师兄弟们。")',
     'Talk(0, "（赵志敬又借故罚我。去问问' + RED % '后山的师兄弟' + '。）")'),
    ('902', 'ShowMessage("第一章·活死人墓：孙婆婆已死。往后，你便是古墓派的人。")',
     'Talk(0, "（' + RED % '孙婆婆' + '死了。往后，我便是古墓派的人。）")'),
    ('915', 'ShowMessage("洪七公与欧阳锋相约再比一场。去思过崖看看。")',
     'Talk(0, "（洪老前辈和欧阳锋约了再比一场。在' + RED % '思过崖' + '。）")'),
    ('922', 'ShowMessage("桃花岛·后院：被打了一顿。去海边走走。")',
     'Talk(0, "（脸上火辣辣的。去' + RED % '海边' + '走走。）")'),
    ('922', 'ShowMessage("桃花岛·后院：打伤了武敦儒。回前院找郭伯伯。")',
     'Talk(0, "（我闯祸了。回' + RED % '前院' + '找郭伯伯。）")'),
    ('923', 'ShowMessage("习得【蛤蟆功】。回后院去。")',
     'Talk(0, "（' + RED % '蛤蟆功' + '，我练成了。回后院去。）")'),
]

report = []
changed = 0

# ---- 逐文件处理 ----
for name, old, new in REPL:
    fp = os.path.join(LUA, name + '.lua')
    t = io.open(fp, encoding='utf-8').read()
    if old not in t:
        report.append('跳过(未找到) %s: %s' % (name, old[:40]))
        continue
    t = t.replace(old, new, 1)
    if APPLY:
        io.open(fp, 'w', encoding='utf-8', newline='\n').write(t)
    changed += 1
    report.append('替换 %s: %s' % (name, old[:36]))

# ---- 923 真学蛤蟆功 ----
fp = os.path.join(LUA, '923.lua')
t = io.open(fp, encoding='utf-8').read()
if 'LearnMagic2(0, 31' not in t:
    anchor = 'SetFlagInt("蛤蟆功", 1)'
    if anchor in t:
        t = t.replace(anchor, anchor + '\nLearnMagic2(0, 31, 0)', 1)
        if APPLY:
            io.open(fp, 'w', encoding='utf-8', newline='\n').write(t)
        report.append('923: 已加 LearnMagic2(0, 31, 0)（蛤蟆功）')
    else:
        report.append('923: **找不到 SetFlagInt("蛤蟆功", 1)**')
else:
    report.append('923: LearnMagic2 已存在')

# ---- 465 只播一次 ----
fp = os.path.join(LUA, '465.lua')
t = io.open(fp, encoding='utf-8').read()
if '初到桃花岛' not in t:
    head = 'if GetFlagInt("初到桃花岛") == 1 then do return end end\nSetFlagInt("初到桃花岛", 1)\n'
    t = head + t
    if APPLY:
        io.open(fp, 'w', encoding='utf-8', newline='\n').write(t)
    report.append('465: 已加"只播一次"守卫')
else:
    report.append('465: 守卫已存在')

io.open(os.path.join(ROOT, 'Logs', '_storyfix.txt'), 'w', encoding='utf-8').write('\n'.join(report))
print('%s  %d 处替换' % ('已写入' if APPLY else '预演(dry-run)', changed))
