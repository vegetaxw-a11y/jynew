-- 【第一回 · 风月无情】佛堂：白袍客人（1001 郭靖 / 11 黄蓉）
-- 一场戏一段话，每次交互都在 15 句内：
--   ①黄蓉解冰魄银针之毒（中毒线收口）
--   ②郭靖认亲（姓杨 → 杨康 → 郭靖）
--   ③邀他去桃花岛（选择：应允 / 拒辞）
-- 注意：「序章完成」不在这里置位——夜里那场戏（1002）才收束本回。
if GetFlagInt("序章完成") == 1 then goto label9 end;
-- 兜底：正常流程里 559 已经把这两位放出来了；旧存档 / 直接传送到这里时补一下
ShowSceneNpc("NPC/郭靖", true)
ShowSceneNpc("NPC/黄蓉", true)
if GetFlagInt("第一回_中毒") == 1 and GetFlagInt("第一回_解毒") == 0 then goto label1 end;
if GetFlagInt("第一回_认亲") == 0 then goto label2 end;
if GetFlagInt("第一回_应允") == 1 or GetFlagInt("第一回_拒辞") == 1 then goto label4 end;
goto label3;

::label1::
Talk(0, "（佛堂里点着两支残烛。一个白袍汉子站在铁枪前，看了很久。）", EXPR.think)
Talk(11, "把手伸出来。")
Talk(0, "（黄衫女子抓过我手腕，翻开掌心。）", EXPR.think)
Talk(11, "冰魄银针。赤练仙子的暗器。")
Talk(10, "蓉儿，你说什么？")
Talk(11, "先麻手，再麻臂，麻到心口，人就没了。你在哪儿碰的？")
Talk(0, "坟地里。捡的。")
Talk(0, "（她拿小刀在我腕上轻轻一划，挤出一串黑血，倒出两颗药丸。）", EXPR.think)
Talk(11, "嚼碎，吞下去。九花玉露丸。")
AddItem(30, 2)
Talk(0, "（一股清凉直透丹田。麻感退下去大半。）", EXPR.think)
Talk(10, "这针是谁的？")
Talk(0, "坟前站着个杏黄道袍的道姑。她说她姓李。")
Talk(10, "……赤练仙子李莫愁。")
Talk(11, "她还在嘉兴。今夜只怕还要来。你先坐下，这毒还没清透。")
SetFlagInt("第一回_解毒", 1)
SetFlagInt("第一回_见过郭靖", 1)
Talk(0, "（<color=#FF0000>左手</color>的黑气，退到了腕子上。）", EXPR.think)
do return end;

::label2::
if GetFlagInt("第一回_见过郭靖") == 1 then
    Talk(10, "毒清了？那好。小兄弟，你姓什么？")
else
    Talk(10, "小兄弟，你姓什么？")
end
Talk(0, "姓杨。")
Talk(10, "姓杨。……你爹，可是叫杨康？")
Talk(0, "你是什么人？")
Talk(10, "我姓郭，名靖。我与你父，是结义兄弟。")
Talk(0, "（娘说过，爹有个穿白袍的好兄弟。）", EXPR.think)
Talk(0, "娘死了。三年前。")
Talk(10, "……这些年，你一个人怎么过的？")
Talk(0, "讨饭，偷东西，睡破窑。")
Talk(11, "偷东西。")
Talk(10, "蓉儿！")
Talk(10, "过儿，你根骨不差。随我回桃花岛，我教你读书，教你做人。")
Talk(0, "（桃花岛。听着像个很远很远的地方。）", EXPR.think)
SetFlagInt("第一回_认亲", 1)
SetFlagInt("第一回_解毒", 1)
SetFlagInt("第一回_见过郭靖", 1)
do return end;

::label3::
Talk(10, "过儿，意下如何？")
Talk(0, "去了，还能回来么？")
Talk(10, "自然能回来。")
if GetFlagInt("父亲遗物") == 1 then
    Talk(0, "郭伯伯，你认得这个么？")
    Talk(10, "……这是你爹的东西。当年在这庙里，他手上就拿着一杆铁枪。")
end
if ShowYesOrNoSelectPanel("随郭靖前往桃花岛？") == true then goto label5 end;
Talk(0, "我不去。这破窑虽破，好歹是自己说了算。")
Talk(10, "……我在此等你三日。")
SetFlagInt("第一回_拒辞", 1)
goto label8;

::label5::
Talk(0, "……我跟你走。")
Talk(10, "好。好！")
SetFlagInt("第一回_应允", 1)
goto label8;

::label8::
Talk(10, "今夜就在庙里歇。外头的事，明日再说。")
Talk(11, "临睡前到我这儿来一趟。我有话问你。")
Talk(0, "（<color=#FF0000>黄蓉</color>在佛堂东首站着，眼睛却望着那杆铁枪。）", EXPR.think)
do return end;

::label4::
Talk(10, "过儿，今晚先在庙里歇。外头的事，明日再说。")
do return end;

::label9::
Talk(10, "过儿，可准备妥当了？")
Talk(0, "郭伯伯，我想再看看这庙。")
Talk(10, "……去罢。我在庙门口等你。")
do return end;
