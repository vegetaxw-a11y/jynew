if GetFlagInt("见瑛姑") == 0 then
    Talk(0, "（泥沼边上有个窝，铺着干草。）", EXPR.think)
    do return end;
end
if GetFlagInt("灵狐") == 1 then
    Talk(0, "（窝空了。那只白狐搬走了。）", EXPR.think)
    do return end;
end
Talk(0, "（泥沼边的草丛里有个窝，窝里蜷着一只白狐。）", EXPR.think)
Talk(0, "（它尾巴断了一截，眼睛盯着我，不动。）", EXPR.think)
Talk(0, "（我蹲下去。它没跑。）", EXPR.think)
Talk(0, "（我撕了块干粮放在窝边，退开三步。）", EXPR.think)
Talk(0, "（它嗅了嗅，叼走了。）", EXPR.think)
Talk(0, "（第二天，窝边上多了两枚野果。）", EXPR.think)
AddExp(0, 100);
AddItemWithoutHint(37, 1);
SetFlagInt("灵狐", 1);
ShowMessage("得到【玉蜂浆】。")
do return end;
