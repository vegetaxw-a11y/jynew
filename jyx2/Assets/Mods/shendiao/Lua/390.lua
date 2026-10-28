if GetFlagInt("入神雕洞") == 0 then
    Talk(0, "（洞壁上湿漉漉的，往下淌水。）")
    do return end;
end
if GetFlagInt("洞中爪印") == 1 then
    Talk(0, "（爪印还在。我没数错，一共七步。）")
    do return end;
end
Talk(0, "（石地上有一排爪印，比我的手掌还大三倍。）")
Talk(0, "（旁边拖着一道长长的划痕，像是有什么被拖过去。）")
Talk(0, "（爪印一路往洞底去了。）")
Talk(0, "（我顺着脚印走。走两步，忽然听见翅膀拍了一下。）")
SetFlagInt("洞中爪印", 1);
do return end;
