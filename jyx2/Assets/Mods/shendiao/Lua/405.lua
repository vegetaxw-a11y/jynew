if GetFlagInt("见瑛姑") == 0 then
    Talk(0, "（谷里开满了花，蜜蜂嗡嗡地飞。）", EXPR.think)
    Talk(0, "（花丛深处有人在哼小调。）", EXPR.think)
    do return end;
end
if GetFlagInt("遇周伯通") == 1 then goto label9 end;
Talk(0, "（一进谷，就有两只蜂追着我的耳朵转。）", EXPR.think)
Talk(36, "喂！新来的！")
Talk(0, "（一个白胡子老头倒挂在树上，两只手各抓一只蜂。）", EXPR.think)
Talk(36, "你会不会玩？")
Talk(0, "玩什么？")
Talk(36, "玩什么都行。打架也行。")
Talk(0, "（他翻身落地，人还在笑，一只手已经拍到我的肩膀。）", EXPR.think)
Talk(0, "（我抬手一格。他的另一只手从侧面又来了。）", EXPR.think)
Talk(0, "（这两只手……不是一个人的手法。）", EXPR.think)
Talk(36, "咦？你看出来了？")
Talk(36, "这叫左右互搏。左手右手各想各的，谁也管不着谁。")
Talk(0, "怎么练？")
Talk(36, "先学会不想。画圈，左手画方的，右手画圆的。")
Talk(0, "（我在花丛边蹲了半个时辰，画了一地的歪框。）", EXPR.think)
Talk(36, "哈哈哈！你比我当年笨！", EXPR.smile)
Talk(0, "（他笑得直拍大腿。可他把口诀全说了。）", EXPR.think)
AddAttack(0, 20);
AddSpeed(0, 10);
SetFlagInt("遇周伯通", 1);
ShowMessage("悟得「左右互搏」的道理：攻+20 轻功+10。")
Talk(36, "对了，你要去哪儿？")
Talk(0, "铁掌山。")
Talk(36, "铁掌山啊。那儿的帮主姓裘，手掌红得像火。")
Talk(36, "我这把老骨头不去了。你自个儿小心。")
do return end;
::label9::
Talk(36, "（老头正追着一只蜂满谷跑。）", EXPR.think)
Talk(36, "别挡道！它偷我的蜜！", EXPR.angry)
do return end;
