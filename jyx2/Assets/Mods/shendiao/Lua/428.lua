if GetFlagInt("入思过崖") == 0 then
    Talk(0, "（崖顶石台上，两只酒碗还摆着。）", EXPR.think)
    do return end;
end
if GetFlagInt("第五章完成") == 1 then
    Talk(0, "（两个人还坐在那儿。雪落在他们肩上。）", EXPR.think)
    do return end;
end
Talk(0, "（不知过了多久，掌风停了。）", EXPR.think)
Talk(0, "（洪七公和欧阳锋面对面站着，两只手掌抵在一起。）", EXPR.think)
Talk(31, "老毒物，这一招，你破了三十年。")
Talk(40, "……破了。")
Talk(40, "我……我是谁？")
Talk(31, "你是欧阳锋。")
Talk(40, "欧阳锋。", EXPR.sad)
Talk(40, "我是欧阳锋。")
Talk(0, "（他念了两遍，像在确认一件丢了很久的东西。）", EXPR.think)
Talk(31, "那你笑什么？", EXPR.smile)
Talk(40, "（他笑了。这是我这几天第一次看见他笑。）", EXPR.think)
Talk(31, "（两个人的手都没松开。）", EXPR.think)
Talk(0, "（然后他们一起坐了下去，像两个累坏了的孩子。）", EXPR.think)
Talk(0, "（雪落在他们肩上，一层，又一层。）", EXPR.think)
Talk(0, "（我跪下去，给两位前辈磕了三个头。）", EXPR.think)
Talk(0, "（洪七公的手边，压着半只没吃完的叫花鸡。）", EXPR.think)
AddExp(0, 800);
AddEthics(0, 5);
SetFlagInt("第五章完成", 1);
ShowMessage("第五章《华山绝顶》完。")
do return end;
