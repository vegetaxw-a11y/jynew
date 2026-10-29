if GetFlagInt("赵志敬收徒") == 0 then
    Talk(21, "小娃娃，你也是来上香的？")
    do return end;
end
if GetFlagInt("孙婆婆赠药") == 1 then goto label0 end;
    Talk(21, "小娃娃，你身上这伤，是清笃打的？")
    Talk(0, "……老奶奶，你是？")
    Talk(21, "我姓孙，在后山活死人墓里伺候人的。")
    Talk(0, "活死人墓？")
    Talk(21, "全真教的地界，你少打听。")
    Talk(21, "喏，这瓶药你拿着，伤好得快些。")
    AddItem(38, 2);
    SetFlagInt("孙婆婆赠药", 1);
    Talk(0, "多谢老奶奶。")
    Talk(21, "……你这孩子的眼神，倒像我们墓里的人。")
    Talk(21, "若在这儿待不下去，就到后山来寻我。石门夜里不关。")
    SetFlagInt("逃墓", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    Talk(0, "（<color=#FF0000>后山</color>有座活死人墓。听说石门夜里不关。）")
    do return end;
::label0::
    Talk(21, "又挨打了？忍着吧。全真教的规矩，比铁还硬。")
    do return end;
