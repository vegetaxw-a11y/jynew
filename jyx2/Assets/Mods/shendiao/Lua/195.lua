if GetFlagInt("第四章完成") == 0 then
    Talk(0, "（一道石牌坊，写着「华山」两个字，漆掉了大半。）", EXPR.think)
    do return end;
end
if GetFlagInt("华山放行") == 1 then
    Talk(43, "（山门的弟子拱了拱手，让开了。）", EXPR.think)
    do return end;
end
Talk(0, "（山门口立着几个佩剑的汉子，衣襟上绣着一柄小剑。）", EXPR.think)
Talk(43, "站住。华山封山了。")
Talk(0, "封山？")
Talk(43, "山上有人比武。掌门吩咐，谁也不许上去。")
Talk(0, "比武？谁跟谁？")
Talk(43, "（他犹豫了一下。）", EXPR.think)
Talk(43, "两个老头。一个穿破衣，一个披头散发。")
Talk(43, "已经打了三天三夜了。")
Talk(0, "（我心里一动。）", EXPR.think)
Talk(0, "（穿破衣的那个，说不定是他。）", EXPR.think)
Talk(0, "我要上去。")
Talk(43, "你——")
Talk(0, "（我把袖子撩起来，露出那条空荡荡的臂。）", EXPR.think)
Talk(0, "我上去找人。找完就下来。")
Talk(43, "（他看了很久，最后叹了口气。）", EXPR.think)
Talk(43, "上头的人若问起，别说是我放你上去的。")
SetFlagInt("华山放行", 1);
do return end;
