if GetFlagInt("第四章完成") == 0 then
    Talk(0, "（山道很陡，风里夹着雪粒。）")
    Talk(0, "（华山上下一片白。）")
    do return end;
end
if GetFlagInt("上华山") == 1 then
    Talk(0, "（华山的山道上，雪还没化。）")
    do return end;
end
Talk(0, "（华山的山道一级一级往上，雪没到脚踝。）")
Talk(0, "（路上没有人。只有一些新踩的脚印，很浅。）")
Talk(0, "（这么大的雪，谁会往山上走？）")
Talk(0, "（我顺着脚印往上。）")
SetFlagInt("上华山", 1);
do return end;
