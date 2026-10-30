if GetFlagInt("见谷主") == 0 then
    Talk(0, "（一只木箱，箱盖上有薄薄一层灰。）", EXPR.think)
    Talk(0, "（谷里的人说，这屋子不许进。）", EXPR.think)
    do return end;
end
if GetFlagInt("得情花") == 1 then
    Talk(0, "（箱子空了一半。信还压在箱底。）", EXPR.think)
    do return end;
end
Talk(0, "（丹房里一排木箱，靠墙摆着，箱盖上都有灰。）", EXPR.think)
Talk(0, "（最上面那只没锁。）", EXPR.think)
Talk(0, "（箱里是几包晒干的红花，还有一封没写完的信。）", EXPR.think)
Talk(0, "「萼儿：情花之毒无解，唯有……」")
Talk(0, "（后面的字被墨涂了，涂得很用力，纸都破了。）", EXPR.think)
Talk(0, "（我拿了一朵干花揣进怀里。这花的名字，我在古墓的旧书上见过。）", EXPR.think)
AddItem(122, 1);
AddExp(0, 120);
SetFlagInt("得情花", 1);
ShowMessage("得到【情花】，并发现半封信。")
do return end;
