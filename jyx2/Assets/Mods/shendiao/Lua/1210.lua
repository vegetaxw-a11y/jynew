if GetFlagInt("拜师龙女") == 0 then
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
