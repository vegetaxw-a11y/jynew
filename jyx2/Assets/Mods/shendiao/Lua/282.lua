if GetFlagInt("华山遇西毒") == 0 then
    Talk(0, "（一条窄道通到崖后，风比山道上更硬。）", EXPR.think)
    do return end;
end
if GetFlagInt("入思过崖") == 1 then
    Talk(0, "（崖上的雪被人踩出一条路。）", EXPR.think)
    do return end;
end
Talk(0, "（一条窄道绕过山壁，尽头是一处平台。）", EXPR.think)
Talk(0, "（平台上没有雪。雪被人扫开了。）", EXPR.think)
Talk(0, "（豆腐块大的石头上摆着两只酒碗。）", EXPR.think)
Talk(0, "（我听见了掌风。）", EXPR.think)
SetFlagInt("入思过崖", 1);
do return end;
