-- 百花谷·练级区（走过触发）：草丛里一群野狼
if GetFlagInt("百花谷_练级") == 0 then
    SetFlagInt("百花谷_练级", 1)
    Talk(0, "（谷里花气冲鼻。草叶倒了一片，不是风压的。）", EXPR.think)
    Talk(0, "（是新踩出来的印子，还很深。）", EXPR.think)
end
if TryBattle(140) == true then
    ShowMessage("狼群退了。这一趟拳脚熟了不少。")
    do return end
end
ShowMessage("被狼群撵了出来。伤得不轻，先歇会儿再来。")
