if GetFlagInt("遇洪七公") == 0 then
    Talk(0, "（火堆边的泥团已经凉了。）", EXPR.think)
    do return end;
end
Talk(0, "（我把怀里的玉蜂浆递过去。）", EXPR.think)
Talk(31, "（老头眯起眼睛看了看，一把抓过去。）", EXPR.think)
Talk(31, "好小子。你倒是懂行。")
Talk(0, "（他揭开封泥，喝了一大口。）", EXPR.think)
Talk(31, "嗯。甜。华山上的雪水兑这个，正好。")
Talk(0, "（他把剩下的半罐塞回我手里。）", EXPR.think)
Talk(31, "好东西不能一个人喝完。")
AddItemWithoutHint(37, 1);
AddExp(0, 120);
AddHpWithoutHint(0, 60);
do return end;
