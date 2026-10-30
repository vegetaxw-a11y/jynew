-- 【第一章·古墓】玉女心经
-- 原著对应：第六回《玉女心经》+ 第七回《重阳遗篇》
-- 石棺侧面刻的是林朝英的《玉女心经》，前半篇写情，后半篇写剑；
-- 心经须两人同练，一阴一阳——这是全书师徒情的起点。
if GetFlagInt("击退李莫愁") == 0 then
    Talk(0, "（石棺侧面刻着密密麻麻的小字，须得凑近了才看得清。）", EXPR.think)
    do return end;
end
if GetFlagInt("玉女心经") == 1 then goto label0 end;
if GetFlagInt("断龙石") == 1 then
    Talk(0, "（断龙石落在墓道口。这墓里的光，从那一夜起就是全部的光了。）", EXPR.think)
    Talk(0, "（我在这墓里住了三年。）", EXPR.think)
    Talk(0, "（第一年学拳，第二年学剑，第三年把两样拆开，一样一样重练。）", EXPR.think)
end
Talk(0, "（石棺侧面刻着密密麻麻的小字。）", EXPR.think)
Talk(0, "（一笔一笔，刻得很深。像刻的人怕后人看不清楚。）", EXPR.think)
Talk(22, "这是玉女心经。")
Talk(0, "你不是说烧了？")
Talk(22, "骗她的。")
Talk(0, "（原来她也会骗人。）", EXPR.think)
Talk(0, "（石棺上刻的不只是剑法。前面半篇，写的全是情。）", EXPR.think)
Talk(0, "（写到纸上写不得的地方，就画一个小人，边上注两个字。）", EXPR.think)
Talk(22, "祖师一生没有嫁人。")
Talk(0, "那她写这些，写给谁看？")
Talk(22, "写给一个人。")
Talk(0, "那个人看见了么？")
Talk(22, "没有。")
Talk(0, "（她把话说得很平，像在说别人的事。）", EXPR.think)
Talk(0, "（可她说完，手指在石棺边上按了很久。）", EXPR.think)
Talk(22, "心经须得两人同练。一阴一阳，互相印证。")
Talk(0, "那……")
Talk(22, "我教你。")
LearnMagic2(0, 10, 0);
AddItem(12, 1);
LearnMagic2(0, 20, 0);
AddItem(20, 1);
SetFlagInt("玉女心经", 1);
SetFlagInt("第一章完成", 1);
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
ShowMessage("学会了「玉女剑法」「玉女素心剑」。")
Talk(0, "（练成了。两个人的剑，能当一个人的使。）", EXPR.think)
Talk(0, "（可这剑法要两个人都在，才算成。）", EXPR.think)
Talk(0, "（古墓之外，江湖上还在传着襄阳的战事。）", EXPR.think)
Talk(0, "（可我要先下山一趟。）", EXPR.think)
Talk(0, "（活死人墓的日子，到今夜为止。往<color=#FF0000>终南山后的山洞</color>去。）", EXPR.think)
do return end;
::label0::
Talk(22, "剑要再快些。")
do return end;
