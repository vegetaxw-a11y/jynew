# -*- coding: utf-8 -*-
"""把 sim_lua.py 跑出来的剧情流水，导出成便于通读的剧本文档。

用法:
    python tools/shendiao/sim_lua.py 557 559 563 563 563 559 1001 1001 1001 1002 1002 1002
    python tools/shendiao/export_story_doc.py

第一条命令把主线流水写到 Logs/_sim_out.txt，第二条加表头后落到
docs/第一回-风月无情-剧本.txt。表头里列了说话人 id 与记录符号的含义。
"""
import io
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(REPO, 'Logs', '_sim_out.txt')
DST = os.path.join(REPO, 'docs', u'第一回-风月无情-剧本.txt')

HEADER = u'''神雕侠侣 MOD · 第一回《风月无情》剧本（机器导出，勿手改）
=========================================================================
来源：tools/shendiao/sim_lua.py 离线跑出来的真实执行流水（lua 真跑，不是手抄）
导出命令：
    python tools/shendiao/sim_lua.py 557 559 563 563 563 559 1001 1001 1001 1002 1002 1002
    python tools/shendiao/export_story_doc.py

阅读约定
--------
* [0]      杨过（主角）自己的台词 / 内心独白
* [111]    老庙祝     * [70] 李莫愁   * [90] 程英   * [35] 陆无双   * [10] 郭靖   * [11] 黄蓉   * [30] 柯镇恶
* [【场景】] jyx2_ReplaceSceneObject 显隐 NPC     * [【镜头】] jyx2_CameraFollow 相机跟人
* [【战斗】] TryBattle(203) = 斗李莫愁（必败，输了脚本照样往下走）
* [【提示】] ShowMessage                          * [【系统】] luaBridge.RestTeam 战后回血
* （本场 N 句）  这一场戏里玩家要点的对话次数（设计上限 15 句）

场景布景（62_pomiao.unity / Level/NPC）
---------------------------------------
老庙祝 (-2.5, 5, 13.5)   郭靖 (0.8, 5, -6)   黄蓉 (2.2, 5, -7.2)
李莫愁 (-3.8, 5, -12.2)  程英 (-5.0, 5, -12.9)  陆无双 (-2.7, 5, -13.5)   ← 坟前三人，默认隐藏

=========================================================================

'''


def main():
    if not os.path.exists(SRC):
        raise SystemExit(u'找不到 %s，先跑 tools/shendiao/sim_lua.py' % SRC)
    body = io.open(SRC, encoding='utf-8').read()
    io.open(DST, 'w', encoding='utf-8', newline='').write(HEADER + body)
    print(u'已写出 %s (%d 字符)' % (DST, len(HEADER) + len(body)))


if __name__ == '__main__':
    main()
