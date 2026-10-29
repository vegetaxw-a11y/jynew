if GetFlagInt("桃花岛学艺") == 0 then
    Talk(0, "（后院一片狼藉，几枝桃花被折断，扔在地上。）")
    do return end
end
if GetFlagInt("郭芙欺凌") == 1 then goto label5 end;
Talk(0, "（后院。石桌旁站着三个人。）")
Talk(41, "喂，你就是靖伯伯从外头捡回来的那个？")
Talk(0, "（一个穿红衫的女孩，眼睛长在头顶上。）")
Talk(0, "我叫杨过。")
Talk(41, "杨过？名字真难听。")
Talk(42, "芙妹，别理他。他爹是个坏人。")
Talk(0, "（我的指甲掐进掌心里。）")
Talk(41, "喂，把地上那些花捡起来。")
Talk(0, "为什么？")
Talk(41, "因为我说了。")
Talk(0, "（我没动。）")
Talk(41, "敦儒，教训他。")
Talk(0, "（两人一左一右围上来。）")
if TryBattle(202) == true then
    Talk(0, "（我拼死推开一个，另一个的拳头还是砸在我脸上。）")
    AddExp(0, 80)
else
    Talk(0, "（一记拳打在我脸上。我摔在地上，嘴里尝到铁锈味。）")
end
Talk(0, "（寡不敌众，我终究还是摔在地上。）")
if GetFlagInt("蛤蟆功") == 0 then
    Talk(0, "（我爬不起来。他们笑着走开了。）")
    Talk(0, "（总有一天……）")
    Talk(0, "（脸上火辣辣的。去<color=#FF0000>海边</color>走走。）")
    do return end
end
Talk(0, "（我趴在地上。喉咙里，忽然响起了那个声音。）")
Talk(42, "啊——！")
Talk(0, "（武敦儒倒飞出去，撞在石桌上。）")
Talk(41, "你、你这是什么邪门功夫！")
Talk(0, "（我看着自己的手。）")
Talk(0, "（我也不知道。）")
SetFlagInt("郭芙欺凌", 1)
Talk(0, "（我闯祸了。回<color=#FF0000>前院</color>找郭伯伯。）")
do return end;
::label5::
Talk(0, "（石桌旁空无一人。桌角还留着那天撞出的裂痕。）")
do return end;
