if GetFlagInt("序章开始") == 0 then
    Talk(0, "（这里没什么可看的。）")
    do return end
end
if GetFlagInt("父亲遗物") == 1 then
    Talk(0, "（旧木箱已经翻空了。）")
    do return end
end
Talk(0, "（供桌上落满香灰，只有一只旧木箱。）")
Talk(0, "（箱底压着半截铁片——像是铁枪上崩下来的。）")
Talk(0, "（我把铁片揣进怀里。）")
SetFlagInt("父亲遗物", 1)
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2)
ShowMessage("得到【铁枪残片】。去问庙里的老庙祝。")
do return end
