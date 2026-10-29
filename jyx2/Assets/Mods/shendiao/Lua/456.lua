if GetFlagInt("入全真") == 0 then
    Talk(60, "山门尚未准入，不得擅入。")
    do return end
end
if GetFlagInt("赵志敬收徒") == 0 then
    Talk(60, "师弟莫要乱走。全真教的规矩，比别处多。")
    do return end
end
if GetFlagInt("赵志敬为难") == 0 then
    Talk(60, "喂，新来的。")
    Talk(0, "……师兄。")
    Talk(60, "听说你爹是个认贼作父的？")
    Talk(0, "（我握紧了拳。）")
    Talk(60, "看什么看？我说得不对么。")
    Talk(0, "（在重阳宫，我连还嘴的资格都没有。）")
    Talk(0, "（这地方的水，比铁枪庙的雨还冷。）")
    do return end
end
if GetFlagInt("决意出走") == 0 then
    Talk(60, "柴劈完了？师父说了，劈不完不给饭吃。")
    Talk(0, "（他们笑着走开了。）")
    Talk(0, "（这地方，一天也待不下去了。）")
    SetFlagInt("决意出走", 1)
    Talk(0, "（重阳宫的日子到头了。往<color=#FF0000>后山</color>去，那里有一座活死人墓。）")
    do return end
end
Talk(60, "听说后山那位……又不吃饭了。")
Talk(0, "（后山。活死人墓。）")
do return end;

