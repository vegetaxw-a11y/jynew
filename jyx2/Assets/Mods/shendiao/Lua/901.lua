if GetFlagInt("拜入全真") == 0 then
    Talk(20, "你是何人？重阳宫不许乱走。")
    Talk(0, "弟子杨过。")
    Talk(20, "杨过？没听说过。")
    do return end
end
if GetFlagInt("赵志敬收徒") == 0 then
    Talk(20, "你就是郭靖送来的那个小子？")
    Talk(0, "弟子杨过，见过师父。")
    Talk(20, "哼。")
    Talk(20, "郭靖自己一身武功，倒把人塞给我们全真教。")
    Talk(0, "（他上下打量我，眼神像在看一件碍事的东西。）", EXPR.think)
    Talk(20, "拜师可以。本门戒律，你先背熟了。")
    Talk(20, "《重阳立教十五论》，三日之内，一字不许错。")
    Talk(0, "是。")
    Talk(20, "还有。重阳宫不养闲人。")
    Talk(20, "今日起，挑水、劈柴、扫地，都是你的活。")
    Talk(0, "（这就是全真教的待客之道。）", EXPR.think)
    Talk(0, "（也是我爹的待客之道么？）", EXPR.think)
    SetFlagInt("赵志敬收徒", 1)
    Talk(0, "（<color=#FF0000>后山</color>的杂役。师兄弟们都在那儿。）", EXPR.think)
    do return end
end
if GetFlagInt("赵志敬为难") == 0 then
    Talk(20, "叫你背的书，背熟了么？")
    Talk(0, "背熟了。")
    Talk(20, "背来我听。")
    Talk(0, "「凡出家者，先须投庵。庵者，舍也……」")
    Talk(20, "错了。")
    Talk(0, "……哪里错了？")
    Talk(20, "第三句。")
    Talk(0, "（第三句我背了三日，一个字都不会错。）", EXPR.think)
    Talk(20, "伸出手来。")
    Talk(0, "（戒尺打在掌心上，火辣辣地疼。）", EXPR.think)
    Talk(0, "（这一下，比打柴挨的冻还疼。我不服。）", EXPR.think)
    Talk(20, "怎么？还想还手？")
    if TryBattle(201) == true then
        Talk(0, "（我一掌拍在他手肘上，戒尺飞了出去。）", EXPR.think)
        Talk(20, "……好，好小贼！", EXPR.angry)
        Talk(0, "（他的手在抖。可这一仗，我打得太早了。）", EXPR.think)
        AddExp(0, 100)
    else
        Talk(0, "（我抬手挡了一下，被他反手抽在脸上。）", EXPR.think)
        Talk(20, "还敢挡？")
    end
    Talk(20, "本门武功，讲的是根基。你这个根基，还差得远。")
    Talk(20, "去，把后山那三百斤柴劈完。劈不完，今日不必吃饭。")
    Talk(0, "……是。")
    SetFlagInt("赵志敬为难", 1)
    Talk(0, "（赵志敬又借故罚我。去问问<color=#FF0000>后山的师兄弟</color>。）", EXPR.think)
    do return end
end
if GetFlagInt("决意出走") == 0 then
    Talk(20, "柴劈完了么？")
    Talk(0, "……还没有。")
    Talk(20, "那就去劈。少在这儿磨蹭。")
    do return end
end
Talk(20, "你还敢回来？")
Talk(0, "（他眼里没有半分师父的样子。）", EXPR.think)
do return end;
