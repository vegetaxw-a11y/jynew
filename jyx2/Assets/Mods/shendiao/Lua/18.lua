if GetFlagInt("赵志敬收徒") == 0 then
    Talk(60, "新来的？这里可不是你闲逛的地方。")
    do return end;
end
if GetFlagInt("鹿清笃结怨") == 1 then goto label0 end;
    Talk(60, "喂，小子，把这担柴挑到灶房去。")
    Talk(0, "凭什么？", EXPR.angry)
    Talk(60, "凭我比你早入门三年。全真教的规矩，你当是什么？")
    if ShowYesOrNoSelectPanel("要动手吗？") == true then goto label1 end;
        Talk(0, "（人在屋檐下……）好，我挑。", EXPR.think)
        Talk(60, "算你识相。")
        SetFlagInt("鹿清笃结怨", 1);
        ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
        do return end;
::label1::
    Talk(0, "我不挑。")
    Talk(60, "好胆！")
    if TryBattle(60) == true then goto label2 end;
        DarkScence();
        Talk(0, "（……被打得浑身是伤。）", EXPR.think)
        LightScence();
        Talk(60, "哼，不自量力。柴还是得你挑。", EXPR.angry)
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
    Talk(60, "走开走开，别挡道。", EXPR.angry)
    do return end;
