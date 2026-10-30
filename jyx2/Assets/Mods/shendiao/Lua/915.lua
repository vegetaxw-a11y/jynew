if GetFlagInt("遇洪七公") == 0 then
    Talk(0, "（雪地上一串杂乱脚印，一直通到崖边。）", EXPR.think)
    do return end;
end
if GetFlagInt("华山遇西毒") == 1 then goto label9 end;
Talk(0, "（崖边的雪被压平了一大片，中间站着一个人。）", EXPR.think)
Talk(0, "（他披头散发，衣服破得像渔网，手里抓着一条活蛇。）", EXPR.think)
Talk(40, "……蛇。蛇会咬人。")
Talk(40, "你见过我的儿子么？")
Talk(0, "（他转过脸。眼睛是空的，瞳孔缩成一点。）", EXPR.think)
Talk(0, "前辈，你的儿子……")
Talk(40, "（他忽然笑起来，笑得整座山都在响。）", EXPR.think)
Talk(40, "我儿子听话！我儿子不听话！")
Talk(0, "（蛇从他手里脱开，钻进雪里。）", EXPR.think)
Talk(40, "打架罢。")
Talk(0, "（他抬手，掌风把雪扫成一片白雾。）", EXPR.think)
if TryBattle(204) == true then
    Talk(0, "（他的掌法乱得没有章法，可每一掌都落在实处。）", EXPR.think)
    Talk(0, "（我撑到第八十招，他的呼吸终于乱了。一个破口。）", EXPR.think)
    Talk(40, "……咦？")
    Talk(40, "（他停下来，歪着头看我，像在认一张旧画。）", EXPR.think)
    AddExp(0, 600);
else
    Talk(0, "（一掌拍在胸口，我在雪地上滑出两丈。）", EXPR.think)
    Talk(0, "（他没再追，只是站在原地，喃喃地念着什么。）", EXPR.think)
end
Talk(31, "（破衣老头不知什么时候站在了崖边。）", EXPR.think)
Talk(31, "老毒物。够了。")
Talk(40, "……你？")
Talk(31, "是我。你是欧阳锋，我是洪七公。")
Talk(40, "（他愣了很久，忽然一屁股坐在雪地里。）", EXPR.think)
Talk(40, "洪七公……洪七公是好人。")
Talk(31, "（老头笑了。）", EXPR.think)
Talk(31, "三十年了。你还记得这句。")
SetFlagInt("华山遇西毒", 1);
Talk(0, "（洪老前辈和欧阳锋约了再比一场。在<color=#FF0000>思过崖</color>。）", EXPR.think)
do return end;
::label9::
Talk(40, "（欧阳锋坐在雪里，抓着雪往嘴里塞。）", EXPR.think)
do return end;
