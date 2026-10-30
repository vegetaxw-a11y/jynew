if GetFlagInt("孙婆婆之死") == 0 then
    Talk(0, "（石室里空荡荡的。）", EXPR.think)
    do return end;
end
if GetFlagInt("拜师龙女") == 1 then goto label0 end;
    Talk(22, "婆婆死了。这墓里只剩下我。")
    Talk(0, "……对不起。", EXPR.sad)
    Talk(22, "不必对不起。她救你，是她的意思。", EXPR.sad)
    Talk(22, "从今日起，你拜我为师，入古墓派。")
    Talk(0, "我不拜。")
    Talk(22, "为何？")
    Talk(0, "我这一辈子，被人推来推去。郭伯伯把我推给全真教，全真教把我推给后山。")
    Talk(0, "我不要人可怜，也不要人推。", EXPR.sad)
    Talk(22, "……那你要什么？")
    Talk(0, "我要自己选一次。我选留下。")
    Talk(22, "好。那你不必拜师，只当我古墓派的客人。")
    Talk(22, "但你要学武，我教你。")
    SetFlagInt("拜师龙女", 1);
    LearnMagic2(0, 1, 0);
    AddItem(1, 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    Talk(0, "（全真剑法，我学会了。该去<color=#FF0000>寒玉床</color>上打坐了。）", EXPR.think)
    do return end;
::label0::
    Talk(22, "寒玉床在里间，去练功。")
    do return end;
