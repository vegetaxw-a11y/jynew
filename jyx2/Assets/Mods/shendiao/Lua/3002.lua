-- 神雕山洞·练级区（走过触发）：石缝里盘着毒蛇
if GetFlagInt("山洞_练级") == 0 then
    SetFlagInt("山洞_练级", 1)
    Talk(0, "（洞里潮气重，脚下一股腥味。）", EXPR.think)
    Talk(0, "（石缝里有东西在动，一动就是一条线。）", EXPR.think)
end
if TryBattle(180) == true then
    ShowMessage("毒蛇被打死了。手比进洞时快了些。")
    do return end
end
ShowMessage("蛇毒窜上手臂。赶紧退出洞去。")
