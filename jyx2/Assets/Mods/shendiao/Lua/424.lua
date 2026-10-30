if GetFlagInt("遇陆无双") == 0 then
    Talk(0, "（庵堂里点着一盏灯，灯芯爆了一下。）", EXPR.think)
    Talk(0, "（没人在。）", EXPR.think)
    do return end;
end
if GetFlagInt("见一灯") == 1 then goto label9 end;
Talk(0, "（庵堂里只有一个老僧在扫地，扫得很慢。）", EXPR.think)
Talk(38, "施主身上的杀气，比伤还重。")
Talk(0, "大师怎么知道我有伤？")
Talk(38, "你的右肩是空的。")
Talk(0, "（我下意识摸了摸袖子。）", EXPR.think)
Talk(0, "大师，我来求一件事。有人中了情花之毒。")
Talk(38, "情花。")
Talk(38, "（他放下扫帚，在蒲团上坐下。）", EXPR.think)
Talk(38, "那毒我解不了。能解的，只有下毒的那个人，和他自己的心。")
Talk(0, "这话我听不懂。")
Talk(38, "杀心一起，毒就入骨。你越想杀人，自己烂得越快。")
Talk(38, "你身上已经有味道了。")
Talk(0, "（我低头看自己的手。指甲底下一线暗红。）", EXPR.think)
Talk(38, "老衲这里有一部九阴疗伤篇。学不学，在你。")
Talk(0, "学。")
Talk(38, "（他把手掌按在我头顶。气息一路沉到丹田。）", EXPR.think)
LearnMagic2(0, 32, 0);
AddItem(31, 1);
AddHp(0, 120);
SetFlagInt("见一灯", 1);
ShowMessage("学会了「九阴疗伤篇」。")
Talk(38, "去黑龙潭罢。有人在那儿等了很多年。")
do return end;
::label9::
Talk(38, "（老僧还在扫地。这次扫得慢一些。）", EXPR.think)
Talk(38, "黑龙潭的水，不要太靠近。")
do return end;
