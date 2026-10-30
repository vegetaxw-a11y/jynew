-- 【第一回 · 风月无情】后山陆家老坟（563 交互）
-- 第一次：三个人在坟前的戏（李莫愁 / 程英 / 陆无双 三个模型都在场，镜头锁在李莫愁身上）
--         棺被刨开、尸首不见，都由李莫愁自己说出来——不用旁白。
-- 第二次：杨过 ↔ 李莫愁 → 必败之战 → 中毒 → 得暗器「冰魄银针」
-- 第三次：只剩坟和针（解毒之后）——一句收尾
if GetFlagInt("第一回_坟地") == 0 then goto label1 end;
if GetFlagInt("第一回_李莫愁") == 0 then goto label2 end;
if GetFlagInt("第一回_中毒") == 0 then goto label3 end;
goto label4;

::label1::
-- 三个人此刻都站在坟前（559 已经放出来了，这里再确认一次，防止旧存档里被藏过）
ShowSceneNpc("NPC/李莫愁", true)
ShowSceneNpc("NPC/程英", true)
ShowSceneNpc("NPC/陆无双", true)
-- 镜头对准坟前的三个人（Cinemachine 的 Follow 改到李莫愁身上，路径相对场景根）
jyx2_CameraFollow("Level/NPC/李莫愁")
Talk(0, "（后山一片乱坟。坟前站着三个人。）", EXPR.think)
Talk(0, "（一个杏黄道袍的道姑背对着我，她身后跪着两个小丫头。）", EXPR.think)
Talk(70, "陆门何夫人。三年了，这碑还是新的。")
Talk(35, "……那是我娘。")
Talk(70, "你是陆立鼎的女儿。叫什么？")
Talk(35, "陆无双。")
Talk(70, "无双。好名字。", EXPR.smile)
Talk(70, "你颈子上挂的是什么？")
Talk(35, "我娘留给我的。")
Talk(90, "别碰她！")
Talk(70, "我不碰她。", EXPR.sad)
Talk(70, "你们两个走罢。往北，出嘉兴，别回头。")
Talk(0, "（一个提剑的小道姑把两个丫头领走了。她站着没动。）", EXPR.think)
Talk(70, "……谁在碑后头？", EXPR.angry)
jyx2_CameraFollowPlayer()
ShowSceneNpc("NPC/程英", false)
ShowSceneNpc("NPC/陆无双", false)
SetFlagInt("第一回_坟地", 1)
Talk(0, "（她转过身来了。走近些再与她说话。）", EXPR.think)
do return end;

::label2::
ShowSceneNpc("NPC/李莫愁", true)
Talk(0, "（我从碑后走出来。）", EXPR.think)
Talk(70, "庙后破窑里那个孩子。姓杨。")
Talk(0, "你怎么知道？")
Talk(70, "嘉兴城里的人，我一个个都认得。", EXPR.smile)
Talk(0, "坟里少了两具尸首。")
Talk(70, "我搬的。我总得给他换个干净地方。")
Talk(0, "庄里那七个人，你认得几个？")
Talk(70, "一个都不认得。")
Talk(0, "那你为什么杀他们？")
Talk(70, "因为他们姓陆。", EXPR.angry)
Talk(0, "（我抄起坟边半截断槐，挡在碑前。）", EXPR.think)
-- 必败之战：这一场是 3 打 1（李莫愁 + 两个曼陀谷弟子，见 战斗.xlsx 203），
-- 现在的杨过打不过。输了不会 GameOver——引擎弹一句「战斗失败」就回到地图，
-- 脚本继续往下走；赢了也是同一条路，所以不必强留玩家送死。
if TryBattle(203) == false then
    Talk(0, "（断槐脱手。膝盖一软，我跪在坟前。）", EXPR.think)
else
    Talk(0, "（她退了半步，拂尘一收。）", EXPR.think)
end
-- 战后主角往往只剩一口气：全队回满，免得玩家拖着 0 血走剧情
luaBridge.RestTeam()
Talk(70, "骨头倒硬。起来，我还有话跟你说。")
SetFlagInt("第一回_李莫愁", 1)
do return end;

::label3::
Talk(0, "（左手心忽然一麻。三点寒星，两根钉进碑上，一根钉进我的掌心。）", EXPR.think)
Talk(70, "冰魄银针。见血封喉。", EXPR.sad)
Talk(0, "（黑气顺着手腕往上爬。）", EXPR.think)
Talk(0, "解药。")
Talk(70, "我身上有。可我为什么要给你？")
Talk(0, "（我把掌上那根拔下来，连碑上两根一并攥在手里。针身雕着花纹，冰凉。）", EXPR.think)
Talk(70, "告诉庙里那个疯汉——我在这里等他。")
Talk(0, "（她转身走了。杏黄的袍角在坟头上一晃，就不见了。）", EXPR.think)
SetFlagInt("第一回_中毒", 1)
AddItem(71, 3)
ShowMessage("得到「冰魄银针」×3")
-- 她走了，坟前没人了
ShowSceneNpc("NPC/李莫愁", false)
if GetFlagInt("第一回_求医") == 1 then
    Talk(0, "（手麻到臂弯了。<color=#FF0000>佛堂</color>里有客人，庙祝说那位女客懂医。）", EXPR.think)
else
    Talk(0, "（手麻到臂弯了。先去庙里问<color=#FF0000>庙祝</color>。）", EXPR.think)
end
do return end;

::label4::

if GetFlagInt("第一回_中毒") == 1 and GetFlagInt("第一回_解毒") == 0 then
    Talk(0, "（坟前没人了。左手已经麻到肩膀。）", EXPR.think)
    if GetFlagInt("第一回_求医") == 1 then
        Talk(0, "（去<color=#FF0000>佛堂</color>。）", EXPR.think)
    else
        Talk(0, "（先去庙里问<color=#FF0000>庙祝</color>。）", EXPR.think)
    end
    do return end;
end
Talk(0, "（棺盖斜插在土里，棺是空的。人死了三年，坟也被人刨了两回。）", EXPR.think)
do return end;
