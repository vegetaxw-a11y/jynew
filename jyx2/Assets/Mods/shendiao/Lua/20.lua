if GetFlagInt("逃墓") == 0 then
    Talk(0, "（这里阴森森的，还是别进去了。）", EXPR.think)
    do return end;
end
if GetFlagInt("入墓") == 1 then
    Talk(0, "（活死人墓。我如今也算半个活死人了。）", EXPR.think)
    do return end;
end
Talk(0, "（后山这道石门，竟是虚掩着的。）", EXPR.think)
Talk(0, "（身后有人在喊打喊杀……我一头钻了进来。）", EXPR.think)
DarkScence();
Talk(0, "（里头黑得伸手不见五指。）", EXPR.think)
LightScence();
SetFlagInt("入墓", 1);
Talk(0, "（往里走。总得看看<color=#FF0000>墓里</color>有没有人。）", EXPR.think)
do return end;
