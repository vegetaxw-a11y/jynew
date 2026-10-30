if GetFlagInt("见一灯") == 0 then
    Talk(0, "（潭水是黑的，泥沼上浮着一层白雾。）", EXPR.think)
    Talk(0, "（这地方连鸟都不落。）", EXPR.think)
    do return end;
end
if GetFlagInt("见瑛姑") == 1 then goto label9 end;
Talk(0, "（泥沼当中有块石头，石头上坐着个白发妇人。）", EXPR.think)
Talk(37, "站住。再往前一步，陷进去我可不管。")
Talk(0, "（她手里绕着一条铁链，链子另一头进了泥里。）", EXPR.think)
Talk(37, "你身上有一股檀香味。")
Talk(37, "你见过一灯？")
Talk(0, "见过。")
Talk(37, "……他还活着。")
Talk(0, "（她笑了两声，笑到一半就没了声音。）", EXPR.think)
Talk(37, "我姓刘。三十年前，我抱着孩子去找他救命，他不肯。")
Talk(37, "孩子死在我怀里。")
Talk(0, "（泥沼里冒了一个泡，又瘪下去。）", EXPR.think)
Talk(37, "后来我在这儿住了三十年。一天一天地数他的罪。")
Talk(0, "（她抬起头。眼睛亮得吓人。）", EXPR.think)
Talk(37, "你替我带句话给他。就一句：姓刘的还没死。")
Talk(0, "（我答应了。她把手里的铁链松开，链子沉进泥里。）", EXPR.think)
Talk(37, "前面那片泥沼别碰。踩空一步，到死都爬不出来。")
SetFlagInt("见瑛姑", 1);
do return end;
::label9::
Talk(37, "（她还在转那条铁链。）", EXPR.think)
Talk(37, "话带到了？")
Talk(0, "（我点头。）", EXPR.think)
Talk(37, "……嗯。")
do return end;
