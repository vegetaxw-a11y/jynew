local mapId = GetCurrentGameMapid()
if mapId == 0 then
    Talk(0, "草丛里散落着几株晒干的草药。")
    AddItem(123, 2);
elseif mapId == 1 then
    Talk(0, "石缝里渗出一层蜂蜜似的黏浆。")
    AddItem(37, 1);
else
    Talk(0, "地上有些野果。")
    AddItem(110, 1);
end
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2);
do return end;
