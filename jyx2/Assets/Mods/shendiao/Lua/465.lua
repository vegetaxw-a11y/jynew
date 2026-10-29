if GetFlagInt("初到桃花岛") == 1 then do return end end
SetFlagInt("初到桃花岛", 1)
ScreenVignette(true)
Talk(0, "（船靠了岸。）")
Talk(0, "（海上起了雾。一岛的桃花，却开得像火。）")
Talk(0, "（这就是桃花岛。）")
Talk(0, "（郭伯伯说，这里住着他师父的故人。）")
ScreenVignette(false)
Talk(0, "（<color=#FF0000>往里走</color>。郭伯伯在等我。）")
do return end;
