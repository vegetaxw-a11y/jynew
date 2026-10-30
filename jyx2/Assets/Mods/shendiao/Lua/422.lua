if GetFlagInt("见瑛姑") == 0 then
    Talk(0, "（一脚踩下去，泥就没过了脚踝。）", EXPR.think)
    Talk(0, "（再往前，怕是要沉。）", EXPR.think)
    do return end;
end
if GetFlagInt("黑龙潭淤泥") == 1 then
    Talk(0, "（泥沼上只冒出几串气泡。）", EXPR.think)
    do return end;
end
Talk(0, "（泥沼表面结了一层绿皮，看着像地，其实不是。）", EXPR.think)
Talk(0, "（我掰了一根树枝戳下去，半截就没了。）", EXPR.think)
Talk(0, "（泥底下咕的一声，像是有什么翻了个身。）", EXPR.think)
Talk(0, "（瑛姑说过，踩空一步，到死都爬不出来。）", EXPR.think)
SetFlagInt("黑龙潭淤泥", 1);
do return end;
