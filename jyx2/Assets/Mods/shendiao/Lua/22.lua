if GetFlagInt("入墓") == 0 then
    Talk(21, "谁？")
    do return end;
end
if GetFlagInt("孙婆婆收留") == 1 then goto label0 end;
    Talk(21, "是你？你怎么进到墓里来了！")
    Talk(0, "老奶奶，后面有人在追我……")
    Talk(21, "罢了罢了。你先躲进石室里去。", EXPR.sad)
    Talk(0, "这里到底是什么地方？", EXPR.think)
    Talk(21, "活死人墓，古墓派的所在。本门弟子，生前不入世，死后不出墓。")
    Talk(0, "那你为什么救我？")
    Talk(21, "你这孩子被全真教那帮牛鼻子欺负成这样，我看着心疼。")
    AddItem(37, 1);
    SetFlagInt("孙婆婆收留", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    Talk(0, "（<color=#FF0000>石室深处</color>。古墓派的主人，就在那里。）", EXPR.think)
    do return end;
::label0::
    Talk(21, "孩子，墓里冷，多穿些。")
    do return end;
