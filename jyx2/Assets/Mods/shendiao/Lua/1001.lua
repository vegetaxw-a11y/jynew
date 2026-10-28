if GetFlagInt("庙祝指路") == 0 then
    Talk(0, "（我这副穷酸样子，还是别惊动旁人了。）")
    do return end;
end
if GetFlagInt("郭靖到访") == 1 then goto label0 end;
    SetFlagInt("郭靖到访", 1);
    Talk(10, "庙里可有人？")
    Talk(0, "你是什么人？")
    Talk(10, "在下郭靖，路过此地，想给一位故人上炷香。")
    Talk(0, "郭靖？江南七怪的徒弟，北侠郭靖？")
    Talk(10, "虚名罢了。小兄弟，你姓什么？")
    Talk(0, "姓杨。")
    Talk(10, "……姓杨。你爹，可是叫杨康？")
    Talk(0, "你怎么知道？")
    Talk(10, "我与他，是结义兄弟。")
    Talk(11, "靖哥哥，你就是心软。这孩子的眉眼，跟他爹真是一模一样。")
    Talk(10, "蓉儿，他到底是康弟的骨肉。")
    Talk(11, "骨肉归骨肉，性子归性子。庙里养大的孩子，规矩怕是不大好。")
    Talk(0, "我又没求你们养我。")
    Talk(11, "哟，还挺横。")
    Talk(10, "孩子，你叫什么名字？")
    Talk(0, "杨过。")
    Talk(10, "杨过……改之。好，好名字。你娘呢？")
    Talk(0, "死了。")
    Talk(10, "……")
    Talk(11, "……靖哥哥。")
    Talk(10, "过儿，你根骨不差，可流落在这荒庙里，终究不是出路。")
    Talk(10, "我送你去终南山全真教学艺，你意下如何？")
    if ShowYesOrNoSelectPanel("随郭靖前往终南山全真教？") == true then goto label1 end;
        Talk(0, "我不去。一个人过得挺好。")
        Talk(11, "瞧瞧，这就是你说的好孩子。")
        Talk(10, "过儿，江湖险恶，总要学些本事。我在此等你三日。")
        do return end;
::label1::
    Talk(0, "……好。我跟你走。")
    Talk(10, "这才对。蓉儿，我们明日启程。")
    Talk(11, "唉，又多一个。")
    SetFlagInt("序章完成", 1);
    ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
    ShowMessage("请前往大地图，往右下方赶赴【重阳宫】。")
    do return end;
::label0::
    Talk(10, "过儿，可准备妥当了？")
    if ShowYesOrNoSelectPanel("启程前往终南山？") == true then goto label2 end;
        Talk(10, "不急，我再等等你。")
        do return end;
::label2::
    Talk(0, "走吧。")
    do return end;
