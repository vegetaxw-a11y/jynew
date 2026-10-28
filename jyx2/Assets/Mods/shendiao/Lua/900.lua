if GetFlagInt("入全真") == 0 then
    Talk(10, "过儿，到了。")
    Talk(0, "（石阶一路铺上去，望不见头。）")
    Talk(0, "（这就是天下武学正宗？）")
    Talk(10, "终南山，重阳宫。全真教的重地。")
    Talk(0, "郭伯伯，你当年也在这里学过艺？")
    Talk(10, "……没有。教我武功的，是江南七怪，还有洪七公老前辈。")
    Talk(10, "全真教的道长们，于我亦有恩。")
    Talk(0, "那你自己教我，不好么？")
    Talk(0, "（他沉默了很久。）")
    Talk(10, "过儿，有些本事，我教不了你。")
    Talk(0, "（这话听着怪。）")
    Talk(10, "去叫门罢。我在后头看着。")
    do return end
end
if GetFlagInt("拜入全真") == 1 then
    if GetFlagInt("郭靖辞别") == 1 then
        Talk(10, "过儿，好好学。")
        do return end
    end
    Talk(10, "过儿，我要走了。")
    Talk(0, "郭伯伯……")
    Talk(10, "男子汉大丈夫，别哭哭啼啼。")
    Talk(10, "记住一句话：侠之大者，为国为民。")
    Talk(0, "……")
    Talk(10, "还有。别学你爹。")
    Talk(0, "（他转身就走，一步也没有回头。）")
    SetFlagInt("郭靖辞别", 1)
    ShowMessage("郭靖下山去了。往后这重阳宫，只能靠自己。")
    do return end
end
Talk(10, "去罢。丘道长在殿里等你。")
do return end;
