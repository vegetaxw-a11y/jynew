if GetFlagInt("得玄铁重剑") == 0 then
    Talk(0, "（一具枯骨，衣裳化成了灰。）", EXPR.think)
    do return end;
end
if GetFlagInt("第二章完成") == 1 then
    Talk(0, "（我已能一剑斩断碗口粗的石笋。）", EXPR.think)
    Talk(0, "（该下山了。师父还在等我。）", EXPR.think)
    do return end;
end
Talk(0, "（我在洞底住了下来。日里劈石，夜里练气。）", EXPR.think)
Talk(0, "（重剑无锋，大巧不工。八个字，我练了整整一个月。）", EXPR.think)
Talk(0, "（起初一剑下去，石头纹丝不动，虎口先裂了。）", EXPR.think)
Talk(0, "（后来石头裂了。再后来，我能一剑斩断碗口粗的石笋。）", EXPR.think)
Talk(0, "（大雕每日衔水来给我喝。它不会说话，可它懂。）", EXPR.think)
AddAttack(0, 30);
AddDefence(0, 25);
AddHp(0, 80);
AddMp(0, 40);
SetFlagInt("第二章完成", 1);
Talk(0, "（该去<color=#FF0000>绝情谷</color>了。）", EXPR.think)
Talk(0, "（临走的那个夜里，大雕把我送到洞口。）", EXPR.think)
Talk(0, "（它咧开喙，忽然叫了一声。山谷里全是回声。）", EXPR.think)
Talk(0, "（我回头看了一眼黑黢黢的洞口，往山下走。）", EXPR.think)
do return end;
