if GetFlagInt("第五章完成") == 0 then
    Talk(0, "（一道裂缝通向地底，风从下面上来，带着水汽。）")
    Talk(0, "（这底下不知道有多深。）")
    do return end;
end
if GetFlagInt("入绝情谷底") == 1 then
    Talk(0, "（地缝里终年不见天日，石壁湿滑。）")
    do return end;
end
Talk(0, "（我从断肠崖上跳了下来。）")
Talk(0, "（原以为下面是石头，落下去才知道是水。）")
Talk(0, "（潭水冷得像刀。我顺着一道地缝往里有光的地方爬。）")
Talk(0, "（地缝越走越宽，最后竟成了一片山谷。）")
Talk(0, "（谷里有竹子，有菜畦，有晾着的白布。）")
Talk(0, "（有人住。）")
SetFlagInt("入绝情谷底", 1);
ShowMessage("第六章《十六年之约》开始。")
do return end;
