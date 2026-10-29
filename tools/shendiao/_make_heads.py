# -*- coding: utf-8 -*-
"""用 JYX2 原版头像图覆盖 shendiao 的角色头像。

背景（ResLoader.LaunchMod）:
    MOD 包里的 assets/mods/<id>/xxx 会被登记成 assets/xxx，
    后登记覆盖先登记 —— 所以 Assets/Mods/shendiao/BuildSource/head/10.png
    会顶掉 base_assets 里的 Assets/BuildSource/head/10.png。

用法: python tools/shendiao/_make_heads.py [--apply]
"""
import io
import os
import re
import shutil
import sys
import uuid

ROOT = r'c:\Games\jynew'
SRC = os.path.join(ROOT, 'jyx2', 'Assets', 'BuildSource', 'head')
DST = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'BuildSource', 'head')
APPLY = '--apply' in sys.argv

# shendiao 角色 id -> 原版头像 id（原版人物表：55 郭靖 56 黄蓉 57 黄药师 58 杨过 59 小龙女
# 60 欧阳锋 62 金轮法王 63 程英 64 周伯通 65 一灯 66 瑛姑 67 裘千仞 68 丘处机 69 洪七公）
MAP = {
    0: 58,    # 杨过
    10: 55,   # 郭靖
    11: 56,   # 黄蓉
    20: 19,   # 赵志敬（道士，伪君子）-> 岳不群
    21: 15,   # 孙婆婆（老婆婆）-> 金花婆婆
    22: 59,   # 小龙女
    23: 68,   # 丘处机
    24: 5,    # 神雕（白雕，借白发老者示意）
    26: 33,   # 公孙止（中年文士）-> 黑白子
    27: 2,    # 公孙绿萼（清秀少女）-> 程灵素
    28: 12,   # 樊一翁（白眉老汉）-> 殷天正
    29: 6,    # 裘千尺（枯槁老妇）-> 灭绝
    30: 13,   # 柯镇恶（瞎眼老汉）-> 谢逊
    31: 69,   # 洪七公
    35: 47,   # 陆无双（刁蛮少女）-> 阿紫
    36: 64,   # 周伯通
    37: 66,   # 瑛姑
    38: 65,   # 一灯
    39: 67,   # 裘千仞
    40: 60,   # 欧阳锋
    41: 25,   # 郭芙（娇纵小姐）-> 蓝凤凰
    42: 36,   # 武敦儒（少年弟子）-> 林平之
    43: 43,   # 华山派弟子 -> 白万剑
    60: 4,    # 鹿清笃（无赖弟子）-> 阎基
    70: 17,   # 李莫愁（美貌女魔头，用毒）-> 王难姑
    80: 29,   # 童四二 -> 田伯光
    90: 63,   # 程英
    91: 44,   # 牛不三 -> 岳老三
    111: 16,  # 庙祝（瘦老者）-> 胡青牛
    123: 21,  # 孙不二（道姑）-> 定闲
    190: 49,  # 路人乙 -> 虚竹
}

report = []
missing = []
if APPLY:
    os.makedirs(DST, exist_ok=True)

for sid, oid in sorted(MAP.items()):
    sp = os.path.join(SRC, '%d.png' % oid)
    smeta = sp + '.meta'
    if not os.path.isfile(sp) or not os.path.isfile(smeta):
        missing.append('原版 %d.png 不存在（给 shendiao %d）' % (oid, sid))
        continue
    dp = os.path.join(DST, '%d.png' % sid)
    dmeta = dp + '.meta'
    if APPLY:
        shutil.copyfile(sp, dp)
        # 复制导入设置，但换一个新 guid，避免和原版资源撞 guid
        m = io.open(smeta, encoding='utf-8').read()
        newguid = uuid.uuid4().hex
        m = re.sub(r'(?m)^guid: [0-9a-f]{32}$', 'guid: ' + newguid, m, count=1)
        io.open(dmeta, 'w', encoding='utf-8', newline='\n').write(m)
    report.append('%2d <- 原版 %2d.png' % (sid, oid))

out = ['%s 共 %d 条映射' % ('已写入' if APPLY else '预演', len(MAP)), '']
out += report
if missing:
    out += ['', '缺失:'] + missing
io.open(os.path.join(ROOT, 'Logs', '_heads.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[:2]))
