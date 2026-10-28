if GetFlagInt("孙婆婆之死") == 0 then
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
