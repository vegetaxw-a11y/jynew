if GetFlagInt("第三章完成") == 0 then
    Talk(0, "（一间小院，晒着草药，檐下挂着两串干辣椒。）", EXPR.think)
    Talk(0, "（屋里没人应声。）", EXPR.think)
    do return end;
end
if GetFlagInt("程英相救") == 1 then goto label9 end;
Talk(0, "（我倒在院门口，血把门槛染了一片。）", EXPR.think)
Talk(0, "（醒来的时候，臂上的伤口已经包扎好了。）", EXPR.think)
Talk(90, "醒了？别动。")
Talk(0, "（一个青衫女子端着药碗，站在床边。）", EXPR.think)
Talk(0, "是你救的我？")
Talk(90, "你倒在门口。我总不能看着你死。")
Talk(90, "断了一条臂，还敢跟人动手。这命是自己不要的。")
Talk(0, "（她说得冷淡，可递药碗的手很稳。）", EXPR.think)
Talk(90, "我叫程英。这里是我表妹家的旧宅。")
Talk(0, "（药苦得舌头都麻了。）", EXPR.think)
Talk(90, "这伤要养半个月，急不得。")
Talk(90, "我看你按剑的手法，是学过剑的。")
Talk(0, "学过一点。")
Talk(90, "（她取出一支玉箫，在指间转了半圈。）", EXPR.think)
Talk(90, "箫也能当剑使。可惜我没空教你。")
Talk(0, "（她还是教了。教了一下午，一句多余的话都没有。）", EXPR.think)
LearnMagic2(0, 71, 0);
AddItem(76, 1);
SetFlagInt("程英相救", 1);
ShowMessage("学会了「玉箫剑法」。")
do return end;
::label9::
Talk(90, "药在灶上温着。自己盛。")
do return end;
