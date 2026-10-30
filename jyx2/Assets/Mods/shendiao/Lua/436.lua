if GetFlagInt("入绝情谷底") == 0 then
    Talk(0, "（竹屋的门虚掩着，屋前晒着草药。）", EXPR.think)
    do return end;
end
if GetFlagInt("重逢") == 1 then goto label9 end;
Talk(0, "（竹屋的门开着。门口的石头上晾着一层白色的东西。）", EXPR.think)
Talk(0, "（一个白衣人背对着我，正俯身翻动那些东西。）", EXPR.think)
Talk(22, "谁？")
Talk(0, "（我张了张嘴，发不出声音。）", EXPR.think)
Talk(0, "（她转过身。）", EXPR.think)
Talk(22, "……")
Talk(22, "过儿？")
Talk(0, "师父。")
Talk(0, "（她站在那儿，很久没有动。）", EXPR.think)
Talk(0, "（然后她走过来，抬起手，碰了碰我的脸。）", EXPR.think)
Talk(22, "你的头发白了。")
Talk(0, "（我笑了。笑着，眼泪就掉下来。）", EXPR.think)
Talk(22, "我在这里等了你十六年。")
Talk(0, "（她指了指竹屋的墙。）", EXPR.think)
Talk(0, "（墙上刻着一百多道短短的划痕。）", EXPR.think)
Talk(22, "一天一道。刻满了，就再刻这一面墙。")
Talk(0, "（墙上已经刻到第二面了。）", EXPR.think)
Talk(0, "我回来晚了。")
Talk(22, "（她摇摇头。）", EXPR.think)
Talk(22, "来了就好。")
Talk(0, "（谷底的风从竹林里穿过来，带着水汽和草味。）", EXPR.think)
Talk(0, "（十六年。她一个人在这里，养蜂、种菜、刻墙。）", EXPR.think)
Talk(0, "（我什么也没说。陪她站着，一直站到天黑。）", EXPR.think)
SetFlagInt("重逢", 1);
SetFlagInt("全篇完成", 1);
AddExp(0, 1000);
AddEthics(0, 5);
ShowMessage("第六章《十六年之约》完 —— 神雕主线第一版到此为止。")
do return end;
::label9::
Talk(22, "（她在菜畦边浇水，回头看了我一眼。）", EXPR.think)
Talk(22, "饭快好了。")
do return end;
