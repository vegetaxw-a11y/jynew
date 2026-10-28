if GetFlagInt("遇周伯通") == 0 then
    Talk(0, "（山道上横着拒马，几个穿黑衣的汉子守着。）")
    do return end;
end
if GetFlagInt("上铁掌山") == 1 then
    Talk(0, "（守山的汉子认得我了，摆了摆手。）")
    do return end;
end
Talk(0, "（山道上横着拒马，木头削得尖尖的。）")
Talk(0, "（一个铁掌帮弟子拦住去路，手掌又红又厚。）")
Talk(0, "站住。铁掌山，闲人免进。")
Talk(0, "我找你们帮主。")
Talk(0, "（他上下打量我，视线在我的空袖子上停了很久。）")
Talk(0, "找帮主？你这条命够硬么？")
Talk(0, "（他侧身让开半步。）")
Talk(0, "上去罢。山顶大殿。要是下不来，别怪我没拦。")
SetFlagInt("上铁掌山", 1);
do return end;
