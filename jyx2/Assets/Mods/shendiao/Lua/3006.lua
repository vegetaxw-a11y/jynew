-- 古墓·练级区（走过触发）：墓道里的毒蛇
if GetFlagInt("古墓_练级") == 0 then
    SetFlagInt("古墓_练级", 1)
    Talk(0, "（墓道越往里越凉。石壁缝里渗着水。）", EXPR.think)
    Talk(0, "（水痕上有细细的爬迹，一路拖到脚下。）", EXPR.think)
end
if TryBattle(180) == true then
    ShowMessage("蛇身僵在石板上。墓道里这点动静，我听得比先前清楚。")
    do return end
end
ShowMessage("蛇毒发得快，腿一软。先退到亮处。")
