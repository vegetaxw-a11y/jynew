if GetFlagInt("入思过崖") == 0 then
    Talk(0, "（崖壁上刻着三个字：思过崖。）", EXPR.think)
    do return end;
end
if GetFlagInt("第五章完成") == 1 then
    Talk(0, "（崖顶的风一直没停。）", EXPR.think)
    do return end;
end
Talk(0, "（崖顶的风把雪吹成一条一条的白线。）", EXPR.think)
Talk(0, "（两个人影在雪里转，快得看不清脸。）", EXPR.think)
Talk(0, "（一个穿破衣，一个披头散发。）", EXPR.think)
Talk(0, "（掌对掌，棒对棒。已经不知道是第几天了。）", EXPR.think)
Talk(0, "（我不敢出声。这种时候，谁都不能打断。）", EXPR.think)
do return end;
