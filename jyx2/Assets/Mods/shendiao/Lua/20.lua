if GetFlagInt("逃墓") == 0 then
    Talk(0, "（这里阴森森的，还是别进去了。）")
    do return end;
end
if GetFlagInt("入墓") == 1 then
    Talk(0, "（活死人墓。我如今也算半个活死人了。）")
    do return end;
end
Talk(0, "（后山这道石门，竟是虚掩着的。）")
Talk(0, "（身后有人在喊打喊杀……我一头钻了进来。）")
DarkScence();
Talk(0, "（里头黑得伸手不见五指。）")
LightScence();
SetFlagInt("入墓", 1);
ShowMessage("活死人墓：往里走，看看有没有人。")
do return end;
