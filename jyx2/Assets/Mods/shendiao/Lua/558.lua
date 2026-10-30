-- 【第一回 · 风月无情】佛堂供桌上的旧木箱（558）
-- 杨过身世的唯一实物线索：铁枪崩下来的残片 + 一块烧剩的焦纸。
-- flag「父亲遗物」被 1001（郭靖认亲）引用，不能改名。
if GetFlagInt("序章开始") == 0 then
    Talk(0, "（这里没什么可看的。）", EXPR.think)
    do return end
end
if GetFlagInt("父亲遗物") == 1 then
    Talk(0, "（旧木箱已经翻空了。）", EXPR.think)
    Talk(0, "（箱底的灰里，还能看出一个方方正正的印子。）", EXPR.think)
    do return end
end
Talk(0, "（供桌上落满香灰。香炉旁边搁着一只旧木箱，锁早锈死了。）", EXPR.think)
Talk(0, "（我掰开箱扣。里头压着三样东西。）", EXPR.think)
Talk(0, "（半截铁片——像是从枪杆上崩下来的，断口发黑。）", EXPR.think)
Talk(0, "（一片烧焦的纸，只剩一个半字。像是「康」，又像是「广」。）", EXPR.think)
Talk(0, "（还有一枚生锈的铁钉，钉头上缠着一小段红绳。）", EXPR.think)
Talk(0, "（娘说过，爹死在嘉兴的这座铁枪庙里。）", EXPR.think)
Talk(0, "（她说这话的时候，不敢看我。）", EXPR.think)
Talk(0, "（那年秋天，这庙里来过好些带刀的人，闹了一整夜。第二日，爹就没了。）", EXPR.think)
Talk(0, "（这些事，庙里只有一个人可能说得清。可是他不肯说。）", EXPR.think)
Talk(0, "（我把铁片和焦纸揣进怀里。铁钉太沉，留在箱底。）", EXPR.think)
SetFlagInt("父亲遗物", 1)
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2)
Talk(0, "（铁枪残片。去问<color=#FF0000>老庙祝</color>。）", EXPR.think)
do return end;
