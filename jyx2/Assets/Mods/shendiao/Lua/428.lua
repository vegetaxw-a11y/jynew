if GetFlagInt("入思过崖") == 0 then
    Talk(0, "（崖顶石台上，两只酒碗还摆着。）")
    do return end;
end
if GetFlagInt("第五章完成") == 1 then
    Talk(0, "（两个人还坐在那儿。雪落在他们肩上。）")
    do return end;
end
Talk(0, "（不知过了多久，掌风停了。）")
Talk(0, "（洪七公和欧阳锋面对面站着，两只手掌抵在一起。）")
Talk(31, "老毒物，这一招，你破了三十年。")
Talk(40, "……破了。")
Talk(31, "那你笑什么？")
Talk(40, "（他笑了。这是我这几天第一次看见他笑。）")
Talk(31, "（两个人的手都没松开。）")
Talk(0, "（然后他们一起坐了下去，像两个累坏了的孩子。）")
Talk(0, "（雪落在他们肩上，一层，又一层。）")
Talk(0, "（我跪下去，给两位前辈磕了三个头。）")
Talk(0, "（洪七公的手边，压着半只没吃完的叫花鸡。）")
AddExp(0, 800);
AddEthics(0, 5);
SetFlagInt("第五章完成", 1);
ShowMessage("第五章《华山绝顶》完。")
do return end;
