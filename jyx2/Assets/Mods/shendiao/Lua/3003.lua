-- 黑龙潭·练级区（走过触发）：潭边毒蛇
if GetFlagInt("黑龙潭_练级") == 0 then
    SetFlagInt("黑龙潭_练级", 1)
    Talk(0, "（潭水黑得像墨，岸上芦苇一动一动。）", EXPR.think)
    Talk(0, "（不是风。芦苇是往反方向倒的。）", EXPR.think)
end
if TryBattle(180) == true then
    ShowMessage("潭边安静下来了。这一架不算白打。")
    do return end
end
ShowMessage("被蛇逼回潭边小路。先退。")
