if GetFlagInt("击退李莫愁") == 0 then
    Talk(0, "（石棺侧面刻着密密麻麻的小字，须得凑近了才看得清。）")
    do return end;
end
if GetFlagInt("玉女心经") == 1 then goto label0 end;
    Talk(22, "这是玉女心经，古墓派的根本。")
    Talk(0, "你不是说烧了？")
    Talk(22, "骗她的。")
    Talk(0, "（原来她也会骗人。）")
    Talk(22, "心经须得两人同练，一阴一阳，互相印证。")
    Talk(0, "那……")
    Talk(22, "我教你。")
    LearnMagic2(0, 10, 0);
    LearnMagic2(0, 20, 0);
    SetFlagInt("玉女心经", 1);
    SetFlagInt("第一章完成", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("学会了「玉女剑法」「玉女素心剑」。")
    Talk(0, "（古墓之外，江湖上还在传着襄阳的战事。）")
    Talk(0, "（可我要先下山一趟。）")
    ShowMessage("第一章《活死人墓》完。接下来：终南山后的山洞。")
    do return end;
::label0::
    Talk(22, "剑要再快些。")
    do return end;
