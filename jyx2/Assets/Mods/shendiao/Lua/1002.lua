-- 【第一回 · 风月无情】夜闯破窑（1002 交互 · 本回收束）
-- 原著对照：第一回结尾破窑之战 + 第二回开头（李莫愁掳走陆无双、青袍客救走程英）
-- 分三次交互，每次都在 15 句左右：
--   ①入窑：程英、陆无双、武三通（窑门口的疯汉）
--   ②李莫愁到：洪凌波堵门 + 抱人那一下 + 三点寒星被打落
--   ③收束：青袍客救程英、郭靖认亲后的去处 + 转场去桃花岛
-- 「序章完成」在本脚本末尾置位：夜里这场戏才是第一回的收束。
if GetFlagInt("序章完成") == 1 then goto label9 end;
-- 兜底：正常流程里 559 已经把这两位放出来了
ShowSceneNpc("NPC/郭靖", true)
ShowSceneNpc("NPC/黄蓉", true)
if GetFlagInt("第一回_解毒") == 0 then goto label0 end;
if GetFlagInt("第一回_夜") == 0 then goto label1 end;
if GetFlagInt("第一回_夜变") == 0 then goto label2 end;
goto label3;

::label0::
Talk(0, "（黄蓉抬眼看了看我。）", EXPR.think)
Talk(11, "先去找靖哥哥。你那只手，拖不得。")
do return end;

::label1::
DarkScene()
LightScene()
-- 窑里三个人都在：程英、陆无双早就躲在草堆上，武三通蹲在窑门口等"何沅君"。
ShowSceneNpc("NPC/武三通", true)
Talk(0, "（入夜。我没睡佛堂，回了庙后那孔破窑。）", EXPR.think)
Talk(0, "（草堆上缩着两个女孩子，窑门口蹲着个蓬头大汉。）", EXPR.think)
Talk(44, "何沅君呢？何沅君到哪儿去了！")
Talk(0, "我不认得。")
Talk(90, "老伯伯，他不是坏人。")
Talk(35, "你又是谁？")
Talk(0, "这话该我问。这是我的家。")
Talk(35, "……那我们占了你的家。我叫陆无双，她是我表姐程英。")
Talk(90, "庄里起火的时候，是这位老伯伯把我们挟出来的。")
Talk(35, "喂，你叫什么？")
Talk(0, "杨过。")
Talk(35, "杨过。……记住了，我欠你一间破窑。")
if GetFlagInt("第一回_玉镯") == 1 then
    Talk(0, "（老伯伯捧着那只断玉镯，忽然不出声了，攥得指节发白。）", EXPR.think)
end
Talk(0, "「问世间，情是何物，直教生死相许？」", "", 2)
SetFlagInt("第一回_夜", 1)
do return end;

::label2::
-- 李莫愁带着弟子洪凌波到窑门口；柯镇恶随后赶到。
ShowSceneNpc("NPC/洪凌波", true)
Talk(73, "师父，窑口窄，我堵着门。", EXPR.calm)
Talk(70, "两个女娃娃在这里，是不是？不论死活，都给我抛出来。")
Talk(70, "庙后破窑里那个孩子，你也在。")
Talk(0, "（我没答话。她记得我。）", EXPR.think)
Talk(70, "程姑娘，你倒护着她。")
Talk(90, "你要杀就杀我。")
Talk(70, "我不杀你。你颈子上那半块帕子，是我绣的。", EXPR.sad)
Talk(70, "他宁可给一个女娃娃，也不肯自己来求我。")
Talk(0, "（那大汉抱着一截断树干冲出去，被拂尘一扫就撞在窑壁上。）", EXPR.think)
ShowSceneNpc("NPC/柯镇恶", true)
Talk(30, "李莫愁！你杀陆家满门，老夫今日跟你拼了！")
Talk(70, "柯瞎子，你也来了。")
Talk(0, "（拂尘一扬，三点寒星。一枚银针钉进窑门的木框。）", EXPR.think)
Talk(0, "（她背对着我。我扑上去，从后面抱住了她。）", EXPR.think)
Talk(0, "大美人儿！你到我家里来捉人，也不跟主人打个招呼？")
Talk(70, "你可知我十几年没让男人碰过一根指头。", EXPR.angry)
Talk(0, "（黑暗里嗤嗤两声。两枚银针落在地上——十几丈外有人弹了石子。）", EXPR.think)
SetFlagInt("第一回_夜变", 1)
do return end;

::label3::
Talk(0, "（她手腕一翻，把我甩开。我撞在窑壁上，眼前一黑。）", EXPR.think)
Talk(0, "（等我再睁眼，她已经挟着陆无双退到十步之外。）", EXPR.think)
Talk(35, "放开我！表姐！")
Talk(0, "（拂尘朝程英当头拂下去。斜刺里伸出一只手，抓住拂尘尾丝，把程英往腋下一夹。）", EXPR.think)
Talk(70, "好。好。")
Talk(0, "（她挟着陆无双，几个起落，没入桑林。那只青袖的手也早已不见。）", EXPR.think)
-- 布景收束：李莫愁带走陆无双、青袍客带走程英、武三通被打飞后自己跑了，
-- 这四个人都不该再杵在坟前（柯镇恶留下，随郭靖一道）。
ShowSceneNpc("NPC/李莫愁", false)
ShowSceneNpc("NPC/洪凌波", false)
ShowSceneNpc("NPC/陆无双", false)
ShowSceneNpc("NPC/程英", false)
ShowSceneNpc("NPC/武三通", false)
Talk(10, "过儿！")
Talk(11, "赤练仙子。果然是她。一个被掳走了，另一个，被人救走了。")
Talk(10, "这地方不能住了。明日一早，随我回桃花岛。")
SetFlagInt("第一回_完", 1)
SetFlagInt("序章完成", 1)
ShowMessage("第一回 · 风月无情 —— 完")
-- 过场：嘉兴 → 桃花岛（大跨度换场景，用"转暗—转亮"卡一段旁白）
Talk(0, "（第二日清早，郭伯伯把我的破窑收拾了一遍，只留一只碗给我。）", EXPR.think)
DarkScene()
LightScene()
-- 一张图代替 CG：桃花岛远眺（BuildSource/cg/taohuadao.png，见 tools/shendiao/gen_scene_pic.py）
ShowSceneNpc("去桃花岛", true)
Talk(0, "（船出南湖，荷叶枯尽。嘉兴城在背后缩成一线白墙。）", EXPR.think)
Talk(0, "（出太湖，过东海。桃花岛还在三天水路之外。）", EXPR.think)
ShowSceneNpc("去桃花岛", false)
do return end;

::label9::
Talk(11, "外头有规矩：不许偷，不许抢，不许对人无礼。")
Talk(0, "那要是别人先无礼呢？")
Talk(11, "……你这孩子。答不上来，就先记住前三条。")
do return end;
