if GetFlagInt("情花之毒") == 0 then
    Talk(28, "生面孔。谷里不收外人。")
    do return end;
end
if GetFlagInt("见谷主") == 1 then
    Talk(28, "（白须老者抱着臂，站在厅门边。）", EXPR.think)
    Talk(28, "谷主吩咐过，你可以在谷里走动。")
    do return end;
end
Talk(0, "（前厅里摆着一张长桌，桌上一柄刀，刀鞘上嵌着七颗石子。）", EXPR.think)
Talk(28, "站住。")
Talk(0, "（一个矮胖老者拦在门前，胡子拖到腰上。）", EXPR.think)
Talk(28, "谷里不留外人。你要住，得先答我一句。")
Talk(28, "你师父是谁？")
Talk(0, "（我说不出。古墓派的名字，江湖上没人认。）", EXPR.think)
Talk(0, "我没师父。")
Talk(28, "（他上下打量我，忽然哼了一声。）", EXPR.think)
Talk(28, "断了一条臂，还敢进绝情谷。胆子不小。")
Talk(28, "老朽樊一翁，谷中执事。你既来了，就守谷里的规矩。")
Talk(28, "第一，不许碰情花。第二，不许往后山石窟去。")
Talk(0, "为什么？")
Talk(28, "（他没答，转身走了。）", EXPR.think)
SetFlagInt("见谷主", 1);
do return end;
