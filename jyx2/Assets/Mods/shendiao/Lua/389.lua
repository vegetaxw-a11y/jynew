if GetFlagInt("第一章完成") == 0 then
    Talk(0, "（山洞口子不大，风却是从里面往外灌的。）")
    Talk(0, "（先回活死人墓，把该学的学完再说。）")
    do return end;
end
if GetFlagInt("入神雕洞") == 1 then goto label2 end;
Talk(0, "（山下面的事，说来话长。）")
Talk(0, "（我在镇外撞见郭芙，一句话说得不对，她拔剑就砍。）")
Talk(0, "（右臂断了。血一路滴到山脚。）")
Talk(0, "（师父……我连去见她一面都不敢，怕她看见我这副样子。）")
Talk(0, "（天黑的时候，我爬进了这个洞。）")
Talk(0, "（洞里很黑。黑里有东西在呼吸，一声比一声沉。）")
SetFlagInt("入神雕洞", 1);
ShowMessage("第二章《神雕侠》开始。")
do return end;
::label2::
Talk(0, "（火堆还烧着。一只比人还高的大雕蹲在旁边，歪着头看我。）")
do return end;
