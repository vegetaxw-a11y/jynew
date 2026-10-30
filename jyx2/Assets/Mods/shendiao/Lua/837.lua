if GetFlagInt("入神雕洞") == 0 then
    Talk(0, "（一只大雕，羽毛黑得像铁，蹲在石台上。）", EXPR.think)
    Talk(0, "（它看了我一眼，又低下头去。）", EXPR.think)
    do return end;
end
if GetFlagInt("神雕试剑") == 1 then goto label9 end;
Talk(0, "（大雕忽然站起来，翅膀一展，洞里的火都晃了。）", EXPR.think)
Talk(0, "（它衔起一柄木剑，甩在我脚边。）", EXPR.think)
Talk(0, "（我懂了：它要我陪它练。）", EXPR.think)
if TryBattle(206) == true then
    Talk(0, "（我出了一身血，竟没被它啄倒。）", EXPR.think)
    Talk(0, "（大雕盯着我看了很久，忽然低头，用喙碰了碰我的肩。）", EXPR.think)
    AddExp(0, 200);
else
    Talk(0, "（三个回合，木剑就被它打飞。）", EXPR.think)
    Talk(0, "（可它把剑捡回来，又甩给我。）", EXPR.think)
    Talk(0, "（一次，两次，十七次。到最后我连抬手的力气都没了。）", EXPR.think)
end
Talk(0, "（它转身往洞底走。走两步，回头看我一眼。）", EXPR.think)
SetFlagInt("神雕试剑", 1);
Talk(0, "（大雕回头看了我一眼，像是叫我<color=#FF0000>跟着它</color>。）", EXPR.think)
do return end;
::label9::
Talk(0, "（大雕趴在火边打盹。听见脚步，抬了抬翅膀。）", EXPR.think)
do return end;
