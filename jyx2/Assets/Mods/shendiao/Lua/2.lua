local mapId = GetCurrentGameMapid()
if mapId == 0 then
    Talk(0, "这口木箱的锁早就锈断了。")
    Talk(0, "箱底压着几块碎银，还有一件烂得看不出颜色的旧衣。")
    AddItem(174, 120);
elseif mapId == 1 then
    Talk(0, "箱中是一柄旧剑，剑鞘上刻着重阳宫的云纹。")
    AddItem(42, 1);
else
    Talk(0, "石箱里放着一卷帛书，纸都脆了。")
    AddItem(77, 1);
end
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
do return end;
