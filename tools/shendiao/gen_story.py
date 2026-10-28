"""神雕侠侣 MOD 的剧情脚本生成器。

事件脚本 = `Mods/<mod>/Lua/<eventId>.lua`，脚本里的 Talk(roleId, ...) 会以
人物表里对应 Id 的头像/名字显示对话。

本文件做三件事：
1. 把场景里需要独占逻辑的触发器改成新的事件 Id（EVENT_REMAP）；
2. 为 STORY 里的事件写剧情脚本；
3. 为场景里引用到、但还没写剧情的其余事件，写一个「尚未开放」的占位脚本。

用法：python tools/shendiao/gen_story.py
"""
from __future__ import annotations

import os
import re
import sys
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOD_ID = "shendiao"
MOD_DIR = os.path.join(ROOT, "jyx2", "Assets", "Mods", MOD_ID)
LUA_DIR = os.path.join(MOD_DIR, "Lua")
MAPS_DIR = os.path.join(MOD_DIR, "Maps", "GameMaps")

sys.path.insert(0, os.path.join(ROOT, "tools", "moddev"))
import _scene_scan as scan_tool  # noqa: E402

# ---------------------------------------------------------------------------
# 事件 Id 重排：同一场景里多个触发器指向同一个 Lua 时，给其中一个换新 Id，
# 这样每处剧情都能独立编写。
# 格式：{场景名: {触发器节点名: {字段: 新Id}}}
# ---------------------------------------------------------------------------
EVENT_REMAP = {
    "00_mochuanlinju": {
        "6": {"m_InteractiveEventId": 1001},   # 郭靖黄蓉到访
    },
}

# ---------------------------------------------------------------------------
# 第一章《铁枪庙》
# ---------------------------------------------------------------------------

MAP0 = 0   # 嘉兴·铁枪庙
MAP1 = 1   # 终南山·重阳宫
MAP2 = 2   # 终南山·活死人墓

STORY: dict[int, str] = {}

# 开场（进入事件）
STORY[0] = """ScreenVignette(true)
Talk(0, "（娘临走时说，爹死在嘉兴的这座铁枪庙里。）")
Talk(0, "（庙里的那杆铁枪还在，人却早没了。）")
Talk(0, "（我叫杨过，字改之。娘说，盼我一辈子改过向善。）")
Talk(0, "（可我连爹娘的模样都记不清，又改谁的过？）")
Talk(0, "（庙后的破窑，如今便是我的家。）")
ScreenVignette(false)
SetFlagInt("序章开始", 1)
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
ShowMessage("序章·铁枪庙：在庙里四处走走，打听父亲的旧事。")
do return end;
"""

# 木箱（三个场景各有一口）
STORY[2] = """local mapId = GetCurrentGameMapid()
if mapId == 0 then
    Talk(0, "这口木箱的锁早就锈断了。")
    Talk(0, "箱底压着几块碎银，还有一件烂得看不出颜色的旧衣。")
    AddItem(174, 120);
elseif mapId == 1 then
    Talk(0, "箱中是一柄旧剑，剑鞘上刻着重阳宫的云纹。")
    AddItem(42, 1);
else
    Talk(0, "石箱里放着一卷帛书，纸都脆了。")
    AddItem(77, 1);
end
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
do return end;
"""

# 箱子用物事件（箱子在交互里开掉了，这里兜个底）
STORY[3] = """Talk(0, "箱子已经空了。")
do return end;
"""
STORY[114] = """Talk(0, "箱子已经空了。")
do return end;
"""
STORY[216] = """Talk(0, "箱子已经空了。")
do return end;
"""

# 庙祝
STORY[4] = """if GetFlagInt("父亲遗物") == 1 then goto label0 end;
    Talk(111, "小娃娃，又来庙里躲雨？")
    Talk(0, "老庙祝，我爹当年是不是就死在这庙里？")
    Talk(111, "你爹？……那年秋天的事，我记不真了。只记得庙里来过好些带刀的人，闹了一整夜。")
    Talk(0, "都是些什么人？")
    Talk(111, "我一个烧香的，哪里敢细看。倒是后来听说，你娘抱着你，连夜就走了。")
    Talk(0, "……")
    Talk(111, "去罢去罢，别在这儿碍着我扫地。")
    do return end;
::label0::
    Talk(111, "你手里那块铁片……倒像是当年那位杨爷的东西。")
    Talk(0, "你认得？")
    Talk(111, "我不过是个庙祝，认得什么。只记得那位杨爷有个总穿白袍的兄弟，隔三差五来看他。")
    Talk(0, "白袍的兄弟……郭伯伯？")
    Talk(111, "他若还在江湖上走动，你去江南打听打听，兴许能寻着。")
    SetFlagInt("庙祝指路", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("序章：往大地图东行，去江南寻访白袍客。")
do return end;
"""

# 郭靖黄蓉到访（重排后的事件）
STORY[1001] = """if GetFlagInt("庙祝指路") == 0 then
    Talk(0, "（我这副穷酸样子，还是别惊动旁人了。）")
    do return end;
end
if GetFlagInt("郭靖到访") == 1 then goto label0 end;
    SetFlagInt("郭靖到访", 1);
    Talk(10, "庙里可有人？")
    Talk(0, "你是什么人？")
    Talk(10, "在下郭靖，路过此地，想给一位故人上炷香。")
    Talk(0, "郭靖？江南七怪的徒弟，北侠郭靖？")
    Talk(10, "虚名罢了。小兄弟，你姓什么？")
    Talk(0, "姓杨。")
    Talk(10, "……姓杨。你爹，可是叫杨康？")
    Talk(0, "你怎么知道？")
    Talk(10, "我与他，是结义兄弟。")
    Talk(11, "靖哥哥，你就是心软。这孩子的眉眼，跟他爹真是一模一样。")
    Talk(10, "蓉儿，他到底是康弟的骨肉。")
    Talk(11, "骨肉归骨肉，性子归性子。庙里养大的孩子，规矩怕是不大好。")
    Talk(0, "我又没求你们养我。")
    Talk(11, "哟，还挺横。")
    Talk(10, "孩子，你叫什么名字？")
    Talk(0, "杨过。")
    Talk(10, "杨过……改之。好，好名字。你娘呢？")
    Talk(0, "死了。")
    Talk(10, "……")
    Talk(11, "……靖哥哥。")
    Talk(10, "过儿，你根骨不差，可流落在这荒庙里，终究不是出路。")
    Talk(10, "我送你去终南山全真教学艺，你意下如何？")
    if ShowYesOrNoSelectPanel("随郭靖前往终南山全真教？") == true then goto label1 end;
        Talk(0, "我不去。一个人过得挺好。")
        Talk(11, "瞧瞧，这就是你说的好孩子。")
        Talk(10, "过儿，江湖险恶，总要学些本事。我在此等你三日。")
        do return end;
::label1::
    Talk(0, "……好。我跟你走。")
    Talk(10, "这才对。蓉儿，我们明日启程。")
    Talk(11, "唉，又多一个。")
    SetFlagInt("序章完成", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("请前往大地图，赶赴「终南山·重阳宫」。")
    do return end;
::label0::
    Talk(10, "过儿，可准备妥当了？")
    if ShowYesOrNoSelectPanel("启程前往终南山？") == true then goto label2 end;
        Talk(10, "不急，我再等等你。")
        do return end;
::label2::
    Talk(0, "走吧。")
    do return end;
"""

# 采集点（多个场景共用）
STORY[726] = """local mapId = GetCurrentGameMapid()
if mapId == 0 then
    Talk(0, "草丛里散落着几株晒干的草药。")
    AddItem(123, 2);
elseif mapId == 1 then
    Talk(0, "石缝里渗出一层蜂蜜似的黏浆。")
    AddItem(37, 1);
else
    Talk(0, "地上有些野果。")
    AddItem(110, 1);
end
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
do return end;
"""


# ---------------------------------------------------------------------------
# 终南山·重阳宫
# ---------------------------------------------------------------------------

STORY[10] = """if GetFlagInt("序章完成") == 0 then
    Talk(0, "重阳宫的香火倒是旺，可我上来做什么？")
    do return end;
end
if GetFlagInt("拜入全真") == 1 then
    Talk(0, "（重阳宫。这里的规矩，比铁枪庙的雨还冷。）")
    do return end;
end
Talk(0, "（好大的山门。郭伯伯说，这里是天下武学正宗。）")
Talk(0, "（可我心里，怎么一点也欢喜不起来。）")
ShowMessage("终南山·重阳宫：先与郭靖说话。")
do return end;
"""

STORY[11] = """if GetFlagInt("序章完成") == 0 then
    Talk(10, "小兄弟，此处是重阳宫，闲人免进。")
    do return end;
end
if GetFlagInt("拜入全真") == 1 then goto label0 end;
    Talk(10, "过儿，重阳宫到了。")
    Talk(10, "我与你爹是结义兄弟，本想着亲自教你。只是我常年守在襄阳，实在分身乏术。")
    Talk(0, "郭伯伯，你和我爹，当年是怎样的交情？")
    Talk(10, "……那是很久以前的事了。你爹他聪明绝顶，只可惜走错了路。")
    Talk(0, "走错路的人，就该死么？")
    Talk(10, "过儿。")
    Talk(10, "我今日把你托付给全真教，你须得听师父的话，好好学艺，不许使性儿。")
    Talk(0, "……知道了。")
    SetFlagInt("拜入全真", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("去重阳宫正殿，拜见师父赵志敬。")
    do return end;
::label0::
    Talk(10, "过儿，我这就要去襄阳了。你在此好好学艺，三年后我来看你。")
    AddItem(174, 200);
    Talk(0, "郭伯伯……")
    Talk(10, "男儿有泪不轻弹。去吧。")
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    do return end;
"""

STORY[13] = """if GetFlagInt("拜入全真") == 0 then
    Talk(20, "你是何人，也配在重阳宫走动？")
    do return end;
end
if GetFlagInt("赵志敬收徒") == 1 then goto label1 end;
    Talk(20, "你就是郭靖送来的那个小子？")
    Talk(0, "弟子杨过，见过师父。")
    Talk(20, "哼。郭靖自己都不肯教，倒塞给我们全真教。")
    Talk(20, "拜师可以。本门戒律，你先背熟了，我再来问你。")
    Talk(0, "……是。")
    Talk(20, "还有，重阳宫不养闲人。今日起，你去后山砍柴、挑水。")
    Talk(0, "（这就是全真教的待客之道。）")
    SetFlagInt("赵志敬收徒", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("第一章·终南山：在后山做杂役，与师兄弟们打打交道。")
    do return end;
::label1::
    Talk(20, "柴劈完了没有？")
    Talk(0, "……还没有。")
    Talk(20, "那就去劈。少在这儿磨蹭。")
    do return end;
"""

STORY[18] = """if GetFlagInt("赵志敬收徒") == 0 then
    Talk(60, "新来的？这里可不是你闲逛的地方。")
    do return end;
end
if GetFlagInt("鹿清笃结怨") == 1 then goto label0 end;
    Talk(60, "喂，小子，把这担柴挑到灶房去。")
    Talk(0, "凭什么？")
    Talk(60, "凭我比你早入门三年。全真教的规矩，你当是什么？")
    if ShowYesOrNoSelectPanel("要动手吗？") == true then goto label1 end;
        Talk(0, "（人在屋檐下……）好，我挑。")
        Talk(60, "算你识相。")
        SetFlagInt("鹿清笃结怨", 1);
        ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
        do return end;
::label1::
    Talk(0, "我不挑。")
    Talk(60, "好胆！")
    if TryBattle(60) == true then goto label2 end;
        DarkScence();
        Talk(0, "（……被打得浑身是伤。）")
        LightScence();
        Talk(60, "哼，不自量力。柴还是得你挑。")
        SetFlagInt("鹿清笃结怨", 1);
        ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
        do return end;
::label2::
    Talk(60, "你……你竟敢打我？！")
    Talk(0, "我不喜欢有人指使我。")
    AddExp(0, 60);
    SetFlagInt("鹿清笃结怨", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    do return end;
::label0::
    Talk(60, "走开走开，别挡道。")
    do return end;
"""

STORY[113] = """if GetFlagInt("赵志敬收徒") == 0 then
    Talk(21, "小娃娃，你也是来上香的？")
    do return end;
end
if GetFlagInt("孙婆婆赠药") == 1 then goto label0 end;
    Talk(21, "小娃娃，你身上这伤，是清笃打的？")
    Talk(0, "……老奶奶，你是？")
    Talk(21, "我姓孙，在后山活死人墓里伺候人的。")
    Talk(0, "活死人墓？")
    Talk(21, "全真教的地界，你少打听。")
    Talk(21, "喏，这瓶药你拿着，伤好得快些。")
    AddItem(38, 2);
    SetFlagInt("孙婆婆赠药", 1);
    Talk(0, "多谢老奶奶。")
    Talk(21, "……你这孩子的眼神，倒像我们墓里的人。")
    Talk(21, "若在这儿待不下去，就到后山来寻我。石门夜里不关。")
    SetFlagInt("逃墓", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("后山的活死人墓，夜里石门不关。")
    do return end;
::label0::
    Talk(21, "又挨打了？忍着吧。全真教的规矩，比铁还硬。")
    do return end;
"""

# ---------------------------------------------------------------------------
# 终南山·活死人墓
# ---------------------------------------------------------------------------

STORY[20] = """if GetFlagInt("逃墓") == 0 then
    Talk(0, "（这里阴森森的，还是别进去了。）")
    do return end;
end
if GetFlagInt("入墓") == 1 then
    Talk(0, "（活死人墓。我如今也算半个活死人了。）")
    do return end;
end
Talk(0, "（后山这道石门，竟是虚掩着的。）")
Talk(0, "（身后有人在喊打喊杀……我一头钻了进来。）")
DarkScence();
Talk(0, "（里头黑得伸手不见五指。）")
LightScence();
SetFlagInt("入墓", 1);
ShowMessage("活死人墓：往里走，看看有没有人。")
do return end;
"""

STORY[22] = """if GetFlagInt("入墓") == 0 then
    Talk(21, "谁？")
    do return end;
end
if GetFlagInt("孙婆婆收留") == 1 then goto label0 end;
    Talk(21, "是你？你怎么进到墓里来了！")
    Talk(0, "老奶奶，后面有人在追我……")
    Talk(21, "罢了罢了。你先躲进石室里去。")
    Talk(0, "这里到底是什么地方？")
    Talk(21, "活死人墓，古墓派的所在。本门弟子，生前不入世，死后不出墓。")
    Talk(0, "那你为什么救我？")
    Talk(21, "你这孩子被全真教那帮牛鼻子欺负成这样，我看着心疼。")
    AddItem(37, 1);
    SetFlagInt("孙婆婆收留", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("去石室深处，见一见古墓派的主人。")
    do return end;
::label0::
    Talk(21, "孩子，墓里冷，多穿些。")
    do return end;
"""

STORY[24] = """if GetFlagInt("孙婆婆收留") == 0 then
    Talk(0, "（石室里冷得厉害。）")
    do return end;
end
if GetFlagInt("初见龙女") == 1 then goto label0 end;
    Talk(22, "婆婆，外人怎能进墓？")
    Talk(21, "龙姑娘，这孩子被全真教打得半死，我实在看不下去。")
    Talk(22, "本门规矩，外人入墓者死。")
    Talk(0, "……")
    Talk(22, "你笑什么？")
    Talk(0, "我笑你们古墓派，规矩比全真教还多。左右都是死，死在哪儿不是死。")
    Talk(22, "……")
    Talk(22, "婆婆，让他留下。明日送他出墓。")
    SetFlagInt("初见龙女", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    do return end;
::label0::
    Talk(22, "……")
    do return end;
"""

STORY[28] = """if GetFlagInt("初见龙女") == 0 then
    Talk(0, "（墓道深处似乎有打斗声。）")
    do return end;
end
if GetFlagInt("孙婆婆之死") == 1 then goto label0 end;
    Talk(70, "师妹，师姐来看你了，怎么闭门不见？")
    Talk(22, "李莫愁，你早已不是古墓派的人。")
    Talk(70, "玉女心经是师父传给我的，凭什么不给我？")
    Talk(21, "李姑娘，你叛出师门在先，还有脸来讨心经？")
    Talk(70, "老东西，滚开！")
    jyx2_Wait(1.0);
    DarkScence();
    Talk(0, "孙婆婆！")
    LightScence();
    Talk(21, "孩子……我这条命，本来就是早该埋了的……")
    Talk(21, "龙姑娘，这孩子……你替我照看……")
    Talk(22, "婆婆！")
    SetFlagInt("孙婆婆之死", 1);
    Talk(0, "（她死了。为了我这个素不相识的人。）")
    Talk(22, "……")
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("李莫愁还在墓中，小心行事。")
    do return end;
::label0::
    Talk(0, "（孙婆婆的尸身，静静躺在石台上。）")
    do return end;
"""

STORY[210] = """if GetFlagInt("孙婆婆之死") == 0 then
    Talk(0, "（石室里空荡荡的。）")
    do return end;
end
if GetFlagInt("拜师龙女") == 1 then goto label0 end;
    Talk(22, "婆婆死了。这墓里只剩下我。")
    Talk(0, "……对不起。")
    Talk(22, "不必对不起。她救你，是她的意思。")
    Talk(22, "从今日起，你拜我为师，入古墓派。")
    Talk(0, "我不拜。")
    Talk(22, "为何？")
    Talk(0, "我这一辈子，被人推来推去。郭伯伯把我推给全真教，全真教把我推给后山。")
    Talk(0, "我不要人可怜，也不要人推。")
    Talk(22, "……那你要什么？")
    Talk(0, "我要自己选一次。我选留下。")
    Talk(22, "好。那你不必拜师，只当我古墓派的客人。")
    Talk(22, "但你要学武，我教你。")
    SetFlagInt("拜师龙女", 1);
    LearnMagic2(0, 1, 0);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("学会了「全真剑法」。去寒玉床上打坐。")
    do return end;
::label0::
    Talk(22, "寒玉床在里间，去练功。")
    do return end;
"""

STORY[1210] = """if GetFlagInt("拜师龙女") == 0 then
    Talk(0, "（一张玉石床，寒气逼人。）")
    do return end;
end
if GetFlagInt("寒玉床") == 1 then goto label0 end;
    Talk(0, "（躺上去，冻得我直打哆嗦。）")
    Talk(22, "睡不着，是因为心里有事。")
    Talk(0, "……")
    Talk(22, "把心静下来。寒气入体，内力自生。")
    jyx2_Wait(1.0);
    AddMp(0, 40);
    AddExp(0, 200);
    Talk(0, "（竟真的暖了起来。）")
    SetFlagInt("寒玉床", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    do return end;
::label0::
    Talk(0, "（在寒玉床上又躺了一会儿。）")
    AddMp(0, 10);
    do return end;
"""

STORY[217] = """if GetFlagInt("孙婆婆之死") == 0 then
    Talk(0, "（墓中一片死寂。）")
    do return end;
end
if GetFlagInt("击退李莫愁") == 1 then goto label0 end;
    Talk(70, "小娃娃，你就是那个姓杨的？")
    Talk(0, "你杀了孙婆婆。")
    Talk(70, "杀了又如何？本门的事，轮不到你插嘴。")
    if TryBattle(70) == true then goto label1 end;
        DarkScence();
        Talk(0, "（我连她一掌都接不住。）")
        LightScence();
        Talk(70, "凭你也想拦我？今日看在我师妹面上，饶你一命。")
        Talk(22, "李莫愁，你要的心经，我烧了。")
        Talk(70, "你！……好，咱们走着瞧。")
        SetFlagInt("击退李莫愁", 1);
        ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
        do return end;
::label1::
    Talk(70, "……好小子，有点门道。")
    Talk(22, "师姐，够了。")
    Talk(70, "哼，师妹，你护着他？")
    Talk(70, "罢了。今日之事，我记下了。")
    AddExp(0, 300);
    AddItem(71, 2);
    SetFlagInt("击退李莫愁", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    do return end;
::label0::
    Talk(0, "（墓门紧闭，李莫愁已经走了。）")
    do return end;
"""

STORY[219] = """if GetFlagInt("击退李莫愁") == 0 then
    Talk(0, "（石壁上刻着密密麻麻的小字。）")
    do return end;
end
if GetFlagInt("玉女心经") == 1 then goto label0 end;
    Talk(22, "这是玉女心经，古墓派的根本。")
    Talk(0, "你不是说烧了？")
    Talk(22, "骗她的。")
    Talk(0, "（原来她也会骗人。）")
    Talk(22, "心经须得两人同练，一阴一阳，互相印证。")
    Talk(0, "那……")
    Talk(22, "我教你。")
    LearnMagic2(0, 10, 0);
    LearnMagic2(0, 20, 0);
    SetFlagInt("玉女心经", 1);
    SetFlagInt("第一章完成", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("学会了「玉女剑法」「玉女素心剑」。")
    Talk(0, "（古墓之外，江湖上还在传着襄阳的战事。）")
    Talk(0, "（总有一天，我要去看看外面的天下。）")
    ShowMessage("第一章《活死人墓》完。第二章《大胜关英雄会》敬请期待。")
    do return end;
::label0::
    Talk(22, "剑要再快些。")
    do return end;
"""

# ---------------------------------------------------------------------------
# 生成逻辑
# ---------------------------------------------------------------------------

DOC_RE = re.compile(r"^--- !u!(\d+) &(-?\d+).*?\n(.*?)(?=^--- |\Z)", re.M | re.S)

PLACEHOLDER = """Talk(0, "此地尚未探明，容后再说。")
do return end;
"""


def load_docs(text):
    docs = []
    for m in DOC_RE.finditer(text):
        docs.append({
            "type": m.group(1),
            "id": m.group(2),
            "body": m.group(3),
            "body_start": m.start(3),
        })
    return docs


def remap_scene(scene: str, mapping: dict) -> int:
    """把场景里指定触发器的事件 Id 换成新 Id"""
    path = os.path.join(MAPS_DIR, scene + ".unity")
    text = open(path, encoding="utf-8").read()
    docs = load_docs(text)

    go_name, tf_go, tf_father, go_tf = {}, {}, {}, {}
    for d in docs:
        if d["type"] == "1":
            m = re.search(r"^  m_Name: (.*)$", d["body"], re.M)
            if m:
                go_name[d["id"]] = scan_tool.decode_name(m.group(1))
        elif d["type"] == "4":
            m = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", d["body"])
            if m:
                tf_go[d["id"]] = m.group(1)
                go_tf[m.group(1)] = d["id"]
            m = re.search(r"m_Father: \{fileID: (-?\d+)\}", d["body"])
            tf_father[d["id"]] = m.group(1) if m else "0"

    def path_of(go_id):
        tf = go_tf.get(go_id)
        parts = []
        while tf and tf != "0":
            gid = tf_go.get(tf)
            if gid:
                parts.append(go_name.get(gid, "?"))
            tf = tf_father.get(tf, "0")
        return "/".join(reversed(parts))

    edits = []
    for d in docs:
        if d["type"] != "114":
            continue
        m = re.search(r"m_GameObject: \{fileID: (-?\d+)\}", d["body"])
        if not m:
            continue
        node_path = path_of(m.group(1))
        for trigger, fields in mapping.items():
            if node_path != "Level/Triggers/" + trigger:
                continue
            for field, value in fields.items():
                fm = re.search(r"^  %s: .*$" % field, d["body"], re.M)
                if not fm:
                    print(f"  [warn] {scene}/{trigger} 没有字段 {field}")
                    continue
                start = d["body_start"] + fm.start()
                end = d["body_start"] + fm.end()
                edits.append((start, end, "  %s: %s" % (field, value)))

    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]

    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return len(edits)


def clear_old_lua() -> int:
    removed = 0
    for name in os.listdir(LUA_DIR):
        if not name.endswith(".lua") or name == "hotfix.lua":
            continue
        os.remove(os.path.join(LUA_DIR, name))
        meta = os.path.join(LUA_DIR, name + ".meta")
        if os.path.exists(meta):
            os.remove(meta)
        removed += 1
    return removed


def write_lua(event_id: int, code: str) -> None:
    path = os.path.join(LUA_DIR, "%d.lua" % event_id)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(code.strip("\n") + "\n")
    meta = path + ".meta"
    if not os.path.exists(meta):
        content = (
            "fileFormatVersion: 2\n"
            "guid: %s\n"
            "ScriptedImporter:\n"
            "  internalIDToNameTable: []\n"
            "  externalObjects: {}\n"
            "  serializedVersion: 2\n"
            "  userData:\n"
            "  assetBundleName:\n"
            "  assetBundleVariant:\n"
            "  script: {instanceID: 0}\n" % uuid.uuid4().hex
        )
        with open(meta, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)


def collect_event_ids() -> set:
    guids = scan_tool.script_guids()
    ids = set()
    for name in sorted(os.listdir(MAPS_DIR)):
        if not name.endswith(".unity"):
            continue
        events, _npcs = scan_tool.scan(os.path.join(MAPS_DIR, name), guids)
        for _p, interactive, enter, use_item in events:
            for value in (interactive, enter, use_item):
                if value and value.isdigit():
                    ids.add(int(value))
    return ids


def main() -> int:
    if not os.path.isdir(LUA_DIR):
        print(f"找不到 Lua 目录：{LUA_DIR}")
        return 1

    for scene, mapping in EVENT_REMAP.items():
        count = remap_scene(scene, mapping)
        print(f"事件重排 {scene}: {count} 处")

    used = collect_event_ids()
    print(f"场景里被引用的事件共 {len(used)} 个")

    removed = clear_old_lua()
    print(f"清理模板旧剧情脚本 {removed} 个")

    for event_id, code in sorted(STORY.items()):
        write_lua(event_id, code)
        if event_id not in used:
            print(f"  [warn] 事件 {event_id} 没有被任何场景引用")

    placeholders = 0
    for event_id in sorted(used - set(STORY)):
        write_lua(event_id, PLACEHOLDER)
        placeholders += 1

    print(f"写入剧情 {len(STORY)} 个，占位 {placeholders} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
