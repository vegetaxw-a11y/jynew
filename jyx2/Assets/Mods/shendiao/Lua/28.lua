if GetFlagInt("初见龙女") == 0 then
    Talk(0, "（墓道深处似乎有打斗声。）")
    do return end;
end
if GetFlagInt("孙婆婆之死") == 1 then goto label0 end;
    Talk(70, "师妹，师姐来看你了，怎么闭门不见？")
    Talk(22, "李莫愁，你早已不是古墓派的人。")
    Talk(70, "玉女心经是师父传给我的，凭什么不给我？")
    Talk(21, "李姑娘，你叛出师门在先，还有脸来讨心经？")
    Talk(70, "老东西，滚开！")
    jyx2_Wait(1.0);
    DarkScence();
    Talk(0, "孙婆婆！")
    LightScence();
    Talk(21, "孩子……我这条命，本来就是早该埋了的……")
    Talk(21, "龙姑娘，这孩子……你替我照看……")
    Talk(22, "婆婆！")
    SetFlagInt("孙婆婆之死", 1);
    Talk(0, "（她死了。为了我这个素不相识的人。）")
    Talk(22, "……")
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    Talk(0, "（<color=#FF0000>李莫愁</color>还在墓里。走路要轻。）")
    do return end;
::label0::
    Talk(0, "（孙婆婆的尸身，静静躺在石台上。）")
    do return end;
