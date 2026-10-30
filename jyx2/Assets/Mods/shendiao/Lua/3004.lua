-- 铁掌山·练级区（走过触发）：山道上一群野狼
if GetFlagInt("铁掌山_练级") == 0 then
    SetFlagInt("铁掌山_练级", 1)
    Talk(0, "（山道窄，两边是碎石坡。）", EXPR.think)
    Talk(0, "（坡上有绿点在动，一眨一眨的，是一双双眼睛。）", EXPR.think)
end
if TryBattle(140) == true then
    ShowMessage("狼群散了。山风一吹，身上的血都热了起来。")
    do return end
end
ShowMessage("被狼撵下山道。喘匀了气再上去。")
