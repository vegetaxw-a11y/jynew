if GetFlagInt("华山放行") == 0 then
    Talk(0, "（雪地上生着一堆火，火上架着泥团。）", EXPR.think)
    do return end;
end
if GetFlagInt("遇洪七公") == 1 then goto label9 end;
Talk(0, "（雪地里生着一堆火，火上架着两团泥。）", EXPR.think)
Talk(0, "（一个穿破衣的老头蹲在火边，正拿树枝拨火。）", EXPR.think)
Talk(31, "小娃娃，来得正好。")
Talk(0, "（他抬起头。满脸是灰，胡子烧掉了一截。）", EXPR.think)
Talk(0, "前辈……")
Talk(31, "别说话。再等一刻。")
Talk(0, "（我没说话，蹲在旁边看火。）", EXPR.think)
Talk(0, "（泥团裂开，香气冲出来。）", EXPR.think)
Talk(31, "叫花鸡。会吃的都是自己人。")
Talk(0, "（他撕了半只给我。）", EXPR.think)
Talk(0, "（我三口就吃完了。烫得舌头发麻。）", EXPR.think)
Talk(31, "吃完了，我给你看点东西。")
Talk(0, "（他从怀里摸出一根竹棒。）", EXPR.think)
Talk(31, "看好了。这一招叫「天下无狗」。")
Talk(0, "（竹棒在他手里转了一圈，雪地上扫出一条印子。就一下。）", EXPR.think)
Talk(0, "（我记了一辈子。）", EXPR.think)
LearnMagic2(0, 41, 0);
AddItem(49, 1);
SetFlagInt("遇洪七公", 1);
ShowMessage("学会了「打狗棒法」。")
Talk(31, "（他把竹棒往雪里一插。）", EXPR.think)
Talk(31, "对面那个披头散发的，是我几十年的对头。")
Talk(31, "他疯了。疯得连自己是谁都不认。")
Talk(31, "可他要跟我打，我就得打。")
do return end;
::label9::
Talk(31, "（老头还在拨火。）", EXPR.think)
Talk(31, "鸡肉要等。急不得。")
do return end;
