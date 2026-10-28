if GetFlagInt("上铁掌山") == 0 then
    Talk(0, "（山顶大殿，门开着，里面很暗。）")
    do return end;
end
if GetFlagInt("击退裘千仞") == 1 then goto label9 end;
Talk(0, "（大殿正中一个蒲团，蒲团上坐着一个人。）")
Talk(0, "（他没抬头，两只手掌摊在膝上，红得像刚出窑的铁。）")
Talk(39, "你就是那个断了臂的小子。")
Talk(0, "（裘千仞。）")
Talk(39, "我铁掌山的地界，也敢一路闯上来。")
Talk(0, "我要问一件事。绝情谷的公孙止，跟你是什么关系？")
Talk(39, "（他的手指动了一下。）")
Talk(39, "问死人做什么。")
Talk(0, "（他站起来了。整座大殿的光都暗了一暗。）")
if TryBattle(208) == true then
    Talk(0, "（他的掌风扫过我的耳侧，石柱上留下五个指印。）")
    Talk(0, "（可重剑比他的掌更沉。第三十七招，他退了半步。）")
    Talk(39, "……好剑。")
    Talk(39, "这世上能让我退半步的，不超过五个人。")
    AddExp(0, 500);
    AddItemWithoutHint(41, 1);
else
    Talk(0, "（一掌拍在胸口，我整个人飞出去撞在门上。）")
    Talk(0, "（重剑脱手，砸在地上，地砖裂了一道缝。）")
    Talk(39, "算你命大。滚。")
end
Talk(0, "（殿外的风灌进来，吹得蒲团上的灰满屋都是。）")
Talk(0, "（我扶着门框站起来。）")
Talk(0, "（下山的路上，我想着裘千仞那句话：问死人做什么。）")
SetFlagInt("击退裘千仞", 1);
SetFlagInt("第四章完成", 1);
ShowMessage("第四章《南国旧友》完。")
do return end;
::label9::
Talk(39, "（裘千仞还坐在蒲团上，一动不动。）")
Talk(39, "去吧。别再来。")
do return end;
