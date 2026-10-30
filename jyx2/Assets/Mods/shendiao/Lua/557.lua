-- 【第一回 · 风月无情】楔子：破庙（进庙自动播放一次）
-- 这一场只做一件事：把玩家放进嘉兴铁枪庙，指到庙祝身上。
-- 原著那段"采莲 / 九个血手印 / 掘坟"的旁白搬到 563 的坟前，由
-- 李莫愁、程英、陆无双 三个人自己演——这里只留四句内心独白。
if GetFlagInt("第一回_楔子") == 1 then
    do return end
end

-- 布景：坟前那三个人还没到，先藏起来（由 559 庙祝指路时放出来）。
-- 佛堂里那两位客人（郭靖 / 黄蓉）也先藏起来 —— 按剧情他们要到"去佛堂求医"才登场，
-- 免得玩家一进庙就看见两个跟眼前这桩事无关的人杵在那儿。
-- 参数格式见 Jyx2LuaBridge.jyx2_ReplaceSceneObject："" = 当前场景，路径相对 Level/。
ShowSceneNpc("NPC/李莫愁", false)
ShowSceneNpc("NPC/程英", false)
ShowSceneNpc("NPC/陆无双", false)
ShowSceneNpc("NPC/郭靖", false)
ShowSceneNpc("NPC/黄蓉", false)
-- 夜里的两位也是：武三通（窑门口的疯汉）与柯镇恶（江南七怪之首，随郭靖寻来）要等 1002 才登场。
ShowSceneNpc("NPC/武三通", false)
ShowSceneNpc("NPC/柯镇恶", false)
-- 洪凌波是李莫愁的弟子，跟着师父一起到坟前，也是 1002 才现身。
ShowSceneNpc("NPC/洪凌波", false)
-- 结局那张"桃花岛远眺"的图（Level/去桃花岛，Canvas+Image），到 1002 末尾才放出来。
ShowSceneNpc("去桃花岛", false)

Talk(0, "（嘉兴，铁枪庙。风把庙门吹得吱呀响。）", EXPR.think)
Talk(0, "（殿上供着一杆铁枪。人早没了。）", EXPR.think)
Talk(0, "（我叫杨过。娘死后，我就住在庙后那孔破窑里。）", EXPR.think)
Talk(0, "（<color=#FF0000>庙祝</color>在殿前扫地。这座城里的事，他比我清楚。）", EXPR.think)

SetFlagInt("第一回_楔子", 1)
SetFlagInt("序章开始", 1)
ModifyEvent(-2, -2, -2, -2, -1, -1, -1, -2, -2, -2, -2, -2, -2)
do return end
