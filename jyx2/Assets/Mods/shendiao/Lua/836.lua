if GetFlagInt("神雕试剑") == 0 then
    Talk(0, "（石壁上凿着字，年深日久，笔画都被水汽磨圆了。）", EXPR.think)
    do return end;
end
if GetFlagInt("得玄铁重剑") == 1 then
    Talk(0, "（三块石头还压在那儿。第三块下面空了。）", EXPR.think)
    do return end;
end
Talk(0, "（洞底一块大石壁上凿着两行字，字有拳头大。）", EXPR.think)
Talk(0, "「剑魔独孤求败，既无敌于天下，乃埋剑于斯。」")
Talk(0, "「呜呼！群雄束手，长剑空利，不亦悲夫。」", EXPR.sad)
Talk(0, "（石壁下压着四块石头，每块底下藏着一柄剑。）", EXPR.think)
Talk(0, "（第一柄青光闪闪，锋锐得能照出人脸。）", EXPR.think)
Talk(0, "（剑边石上刻着一行小字：「凌厉刚猛，无坚不摧，弱冠前以之与河朔群雄争锋。」）", EXPR.think)
Talk(0, "（第二柄是软的，像一条腰带，剑身上刻着「紫薇」。）", EXPR.think)
Talk(0, "（旁边没有说明，只有一行更小的字：「误伤义士，不祥，弃之深谷。」）", EXPR.think)
Talk(0, "（第三柄黑黝黝的，又厚又钝，抱起来压得我手臂发麻。）", EXPR.think)
Talk(0, "（剑身上刻着：「重剑无锋，大巧不工，四十岁前恃之横行天下。」）", EXPR.think)
Talk(0, "（第四块石头底下没有剑。只有一截木头。）", EXPR.think)
Talk(0, "（木头被削成剑的样子，早烂了半边。）", EXPR.think)
Talk(0, "（压着的石头上刻着：「四十岁后，不滞于物，草木竹石均可为剑。」）", EXPR.think)
Talk(0, "（后面还有一行，笔画很浅。像是刻的人也拿不准——）", EXPR.think)
Talk(0, "（「自此精修，渐进于无剑胜有剑之境。」）", EXPR.think)
Talk(0, "（无剑。）", EXPR.think)
Talk(0, "（我低头看手里这柄又厚又钝的东西，忽然觉得它重得很。）", EXPR.think)
AddItem(41, 1);
LearnMagic2(0, 40, 0);
AddItem(142, 1);
SetFlagInt("得玄铁重剑", 1);
ShowMessage("得到【玄铁重剑】，学会了「玄铁剑法」。")
Talk(0, "（大雕在旁边站着，翅膀轻轻扇了一下，像是在点头。）", EXPR.think)
do return end;
