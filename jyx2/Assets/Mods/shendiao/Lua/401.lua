if GetFlagInt("得情花") == 0 then
    Talk(0, "（后山的石窟黑得看不见底。）", EXPR.think)
    Talk(0, "（谷里人说，谁都不许进去。）", EXPR.think)
    do return end;
end
if GetFlagInt("击退公孙止") == 1 then goto label9 end;
Talk(0, "（石窟深处有一口枯井，井底传来说话声。）", EXPR.think)
Talk(29, "下来。")
Talk(0, "（井底坐着个老妇，浑身是泥，手脚都软软垂着。）", EXPR.think)
Talk(29, "你身上的情花香，隔着三丈我都闻得到。")
Talk(29, "我是裘千尺。公孙止的结发妻子。")
Talk(0, "（她的声音像铁片刮石头。）", EXPR.think)
Talk(29, "他挑断我的手筋脚筋，把我扔在这井里十几年。")
Talk(0, "为什么？")
Talk(29, "因为我知道他的底细。他拿情花练功，练得人不人鬼不鬼。")
Talk(29, "他要娶你师妹，是不是？他要的是她身上的血。")
Talk(0, "（我浑身的血一下凉了。）", EXPR.think)
Talk(29, "想活着出谷，就得先过他那一关。")
Talk(29, "他的刀法只有十二路。第十二路使完，他要换一口气。")
Talk(29, "就在那一瞬。你只有一瞬。")
Talk(0, "（她费力地抬起头，吐出三枚枣核，咄咄咄钉在石壁上。）", EXPR.think)
Talk(0, "（井上传来脚步。）", EXPR.think)
Talk(26, "小兄弟，前厅说话。")
Talk(0, "（我爬出井口。公孙止站在石窟门口，手里那柄刀已经出了鞘。）", EXPR.think)
if TryBattle(207) == true then
    Talk(0, "（我数着。第十一路，十二路——就是现在。）", EXPR.think)
    Talk(0, "（重剑砸在他换气的空当上。）", EXPR.think)
    Talk(26, "……好，好得很。")
    AddExp(0, 400);
    AddItemWithoutHint(41, 1);
else
    Talk(0, "（他的刀像一阵风。我连人影都看不清。）", EXPR.think)
    Talk(26, "念你年幼，留你一命。")
    Talk(26, "把那柄剑留下，滚。")
    Talk(0, "（我摔在石壁上，重剑脱手。）", EXPR.think)
    Talk(0, "（井底忽然传出三声轻响。）", EXPR.think)
    Talk(0, "（三枚枣核，咄咄咄，钉在他脚前的石板上。）", EXPR.think)
    Talk(26, "……裘千尺！", EXPR.angry)
    Talk(29, "公孙止，你连一个断了手的娃儿都容不下？")
    Talk(26, "你不许再出手！")
    Talk(29, "我不出手。我只数你的刀。")
    Talk(29, "十二路，我一路一路数给你听。")
    Talk(0, "（他退了一步，又退一步，转身出了石窟。）", EXPR.think)
end
Talk(29, "（井底传来一阵笑声，笑得直不起腰。）", EXPR.think)
Talk(29, "公孙止，你也有今日！")
Talk(0, "（她笑完了，声音忽然低下去。）", EXPR.think)
Talk(29, "孩子，走罢。别回头。")
Talk(0, "（我扶着石壁站起来。谷里亮得反常。）", EXPR.think)
Talk(0, "（情花丛烧起来了。）", EXPR.think)
Talk(0, "（火是从花丛中间起的。烧得很慢，一朵一朵地爆开。）", EXPR.think)
Talk(0, "（那个女人站在火里。）", EXPR.think)
Talk(70, "问世间，情是何物，直教生死相许……")
Talk(0, "（她的杏黄道袍被火卷起来，像一面旗。）", EXPR.think)
Talk(0, "（她不挣扎。只是站着，一句一句地唱。）", EXPR.think)
Talk(70, "天南地北双飞客，老翅几回寒暑。")
Talk(70, "欢乐趣，离别苦，就中更有痴儿女。")
Talk(0, "（她认不出我了。也许她谁都不认了。）", EXPR.think)
Talk(70, "君应有语：渺万里层云，千山暮雪，只影向谁去？")
Talk(0, "（唱到这里，火已经吞到她的肩。）", EXPR.think)
Talk(0, "（她朝我这边看了一眼。）", EXPR.think)
Talk(70, "……小兄弟。")
Talk(70, "那张网，你终究没替我解。")
Talk(0, "（她笑了一下。这是我在她脸上见过的第一个笑。）", EXPR.think)
Talk(70, "也好。")
Talk(0, "（火塌下去了。花丛还在噼啪地响。）", EXPR.think)
Talk(0, "（谷里安静下来。）", EXPR.think)
Talk(0, "（我在那儿站到火熄。焦土上什么也没剩下。）", EXPR.think)
Talk(0, "（只有一股甜味，很久都散不掉。）", EXPR.think)
SetFlagInt("击退公孙止", 1);
SetFlagInt("第三章完成", 1);
ShowMessage("第三章《绝情谷》完。")

do return end;
::label9::
Talk(29, "（井底只剩一点呼吸声。）", EXPR.think)
Talk(29, "……走罢。")
do return end;
