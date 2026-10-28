if GetFlagInt("拜入全真") == 0 then
    Talk(20, "你是何人，也配在重阳宫走动？")
    do return end;
end
if GetFlagInt("赵志敬收徒") == 1 then goto label1 end;
    Talk(20, "你就是郭靖送来的那个小子？")
    Talk(0, "弟子杨过，见过师父。")
    Talk(20, "哼。郭靖自己都不肯教，倒塞给我们全真教。")
    Talk(20, "拜师可以。本门戒律，你先背熟了，我再来问你。")
    Talk(0, "……是。")
    Talk(20, "还有，重阳宫不养闲人。今日起，你去后山砍柴、挑水。")
    Talk(0, "（这就是全真教的待客之道。）")
    SetFlagInt("赵志敬收徒", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("第一章·终南山：在后山做杂役，与师兄弟们打打交道。")
    do return end;
::label1::
    Talk(20, "柴劈完了没有？")
    Talk(0, "……还没有。")
    Talk(20, "那就去劈。少在这儿磨蹭。")
    do return end;
