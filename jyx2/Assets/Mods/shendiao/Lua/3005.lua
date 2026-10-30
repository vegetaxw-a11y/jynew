-- 一灯居·练级区（走过触发）：后山野狼
if GetFlagInt("一灯居_练级") == 0 then
    SetFlagInt("一灯居_练级", 1)
    Talk(0, "（转过竹林，路越走越窄。）", EXPR.think)
    Talk(0, "（前面有新刨的土，还有几根啃剩的骨头。）", EXPR.think)
end
if TryBattle(140) == true then
    ShowMessage("林子里静了。手脚比来时快。")
    do return end
end
ShowMessage("被狼群逼回竹林。先歇一歇。")
