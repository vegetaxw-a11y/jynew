if GetFlagInt("孙婆婆收留") == 0 then
    Talk(0, "（石室里冷得厉害。）", EXPR.think)
    do return end;
end
if GetFlagInt("初见龙女") == 1 then goto label0 end;
    Talk(22, "婆婆，外人怎能进墓？")
    Talk(21, "龙姑娘，这孩子被全真教打得半死，我实在看不下去。")
    Talk(22, "本门规矩，外人入墓者死。")
    Talk(0, "……")
    Talk(22, "你笑什么？", EXPR.smile)
    Talk(0, "我笑你们古墓派，规矩比全真教还多。左右都是死，死在哪儿不是死。", EXPR.smile)
    Talk(22, "……")
    Talk(22, "婆婆，让他留下。明日送他出墓。")
    SetFlagInt("初见龙女", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    do return end;
::label0::
    Talk(22, "……")
    do return end;
