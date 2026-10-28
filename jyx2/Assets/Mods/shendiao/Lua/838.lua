if GetFlagInt("神雕试剑") == 0 then
    Talk(0, "（一具白骨靠着石壁坐着，衣袍早烂成灰。）")
    Talk(0, "（骨头旁边散着几枚锈钉，像是兵器上的。）")
    do return end;
end
if GetFlagInt("白骨遗刻") == 1 then
    Talk(0, "（白骨还在那儿。我给它磕了个头。）")
    do return end;
end
Talk(0, "（洞底一具白骨，盘腿坐着，骨头都泛黄了。）")
Talk(0, "（它身前的石地上，有人用小刀刻了一行字：）")
Talk(0, "「余仰慕剑魔遗风，来此三年，终不得其门。」")
Talk(0, "（刻字的人早死了。他的手边落着一柄断剑。）")
Talk(0, "（我把断剑收起来，替他合上骨节。）")
AddExp(0, 150);
AddItemWithoutHint(71, 2);
SetFlagInt("白骨遗刻", 1);
ShowMessage("得到【冰魄银针】x2。")
do return end;
