if GetFlagInt("见瑛姑") == 0 then
    Talk(0, "（一脚踩下去，泥就没过了脚踝。）")
    Talk(0, "（再往前，怕是要沉。）")
    do return end;
end
if GetFlagInt("黑龙潭淤泥") == 1 then
    Talk(0, "（泥沼上只冒出几串气泡。）")
    do return end;
end
Talk(0, "（泥沼表面结了一层绿皮，看着像地，其实不是。）")
Talk(0, "（我掰了一根树枝戳下去，半截就没了。）")
Talk(0, "（泥底下咕的一声，像是有什么翻了个身。）")
Talk(0, "（瑛姑说过，踩空一步，到死都爬不出来。）")
SetFlagInt("黑龙潭淤泥", 1);
do return end;
