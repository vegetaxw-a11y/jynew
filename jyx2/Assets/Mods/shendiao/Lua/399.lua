if GetFlagInt("第二章完成") == 0 then
    Talk(0, "（谷里飘着一股甜腻腻的香，闻久了头晕。）", EXPR.think)
    Talk(0, "（这地方不对劲。还是先走。）", EXPR.think)
    do return end;
end
if GetFlagInt("入绝情谷") == 1 then goto label9 end;
Talk(0, "（谷口的石壁上刻着三个字：绝情谷。）", EXPR.think)
Talk(0, "（谷里开满了红花，一丛一丛，红得像血。）", EXPR.think)
Talk(26, "这位小兄弟，从哪儿来？")
Talk(0, "（一个青衣汉子站在花丛后头，手里提着拂尘。）", EXPR.think)
Talk(0, "终南山。")
Talk(26, "终南山……好地方。")
Talk(26, "在下公孙止，这绝情谷的主人。")
Talk(26, "谷中清静，最宜养伤。小兄弟这臂上的伤，怕是还没好罢？")
Talk(0, "（他怎么知道？我袖子遮得严严的。）", EXPR.think)
Talk(26, "请。谷里有客舍，有热汤。")
Talk(0, "（他笑得极和气。可他眼睛一直没离开我的右肩。）", EXPR.think)
Talk(0, "（路只有一条。往回走是荒山，往前走是这个谷。）", EXPR.think)
Talk(0, "（我进了谷。）", EXPR.think)
Talk(0, "（花丛深处有响动。有人在扯什么东西。）", EXPR.think)
Talk(0, "（一个穿杏黄道袍的女人，被一张细麻渔网罩在花丛里。）", EXPR.think)
Talk(0, "（她不喊。一根一根地扯网绳，扯断一根，又缠上两根。）", EXPR.think)
Talk(70, "小兄弟。")
Talk(0, "（是李莫愁。）", EXPR.think)
Talk(70, "过来，把这网给我解开。")
Talk(70, "我记你一个人情。")
Talk(0, "（她身后还站着一个杏黄短打的年轻女子，脸白得像纸。）", EXPR.think)
Talk(70, "别看她。她胆小。")
Talk(0, "（我没有过去。）", EXPR.think)
Talk(70, "……")
Talk(70, "好。好得很。", EXPR.angry)
Talk(0, "（她低下头继续扯网，头发从肩上滑下来，遮住了脸。）", EXPR.think)
Talk(0, "（这一谷的花，红得刺眼。）", EXPR.think)
SetFlagInt("入绝情谷", 1);
ShowMessage("第三章《绝情谷》开始。")
do return end;
::label9::
Talk(26, "（公孙止立在花丛边，含笑不语。）", EXPR.think)
do return end;
