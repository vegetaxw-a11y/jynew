if GetFlagInt("序章完成") == 0 then
    Talk(0, "重阳宫的香火倒是旺，可我上来做什么？")
    do return end;
end
if GetFlagInt("拜入全真") == 1 then
    Talk(0, "（重阳宫。这里的规矩，比铁枪庙的雨还冷。）")
    do return end;
end
Talk(0, "（好大的山门。郭伯伯说，这里是天下武学正宗。）")
Talk(0, "（可我心里，怎么一点也欢喜不起来。）")
ShowMessage("终南山·重阳宫：先与郭靖说话。")
do return end;
