-- 【第一回 · 风月无情】老庙祝（111）——本回的说书人
-- 一场景 15 句内说完，只讲三件事：①墙上的九个血手印 ②十年前那桩婚事的十年之期
--                                ③后山坟被人刨了，去看可以，土里的东西别用手碰。
-- 讲完把坟前那三个人放出来（李莫愁 / 程英 / 陆无双），玩家走过去就是"本来就站在那儿"。
if GetFlagInt("第一回_旧事") == 0 then goto label1 end;
if GetFlagInt("第一回_中毒") == 1 and GetFlagInt("第一回_求医") == 0 then goto label2 end;
if GetFlagInt("序章完成") == 0 then goto label3 end;
goto label4;

::label1::
Talk(111, "小娃娃，天一黑就关门。城里这两日不太平。")
Talk(0, "陆家庄的事，真的？")
Talk(111, "真的。白墙上九个血手印，一个不多，一个不少。")
Talk(0, "九个手印，九条命？")
Talk(111, "庄里连阿根和两个丫头，一共七口。多出来那两个，是给死人留的。")
Talk(111, "陆大爷夫妇的坟。人都死了三年，她照样算在数里。")
Talk(0, "她是谁？")
Talk(111, "赤练仙子李莫愁。十年前陆大爷在大理娶了何沅君，她带着一拂尘闯了喜宴。")
Talk(111, "那回天龙寺的高僧出手，镇住她，逼她立誓：十年之内不许动陆家。")
Talk(0, "今年是第十年。")
Talk(111, "今年是第十年。偏生陆大爷三年前就病死了。")
Talk(0, "欠债的人死了，债不会死。")
Talk(111, "后山那两座坟，昨夜被人刨开。棺盖掀在一旁，尸首不见了。")
Talk(111, "你要真想知道，去看看。记住一句：土里的东西，别用手碰。")
Talk(0, "（后山坟头上，好像站着个人。）", EXPR.think)
SetFlagInt("第一回_旧事", 1)
SetFlagInt("庙祝指路", 1)
-- 放出坟前的三人（位置见 62_pomiao.unity 的 Level/NPC）
ShowSceneNpc("NPC/李莫愁", true)
ShowSceneNpc("NPC/程英", true)
ShowSceneNpc("NPC/陆无双", true)
do return end;

::label2::
Talk(0, "（他看见我的手，扫帚啪的一声掉在地上。）", EXPR.think)
Talk(111, "你的手怎么了！")
Talk(0, "坟地里捡了一枚针，捏了一下。")
Talk(111, "冰魄银针！赤练仙子的成名暗器，见血封喉。")
Talk(111, "中这针的人，先麻手，再麻臂，麻到胸口，人就没了。")
Talk(0, "那怎么办？")
Talk(111, "庙里还有两位客人。白袍的汉子像个种田的，黄衫的女客眼睛厉害，好像懂医。")
Talk(111, "在佛堂。快去，别在这儿耽搁。")
SetFlagInt("第一回_求医", 1)
-- 佛堂那两位这时候才登场
ShowSceneNpc("NPC/郭靖", true)
ShowSceneNpc("NPC/黄蓉", true)
Talk(0, "（<color=#FF0000>佛堂</color>里那两位客人。得快些。）", EXPR.think)
do return end;

::label3::
-- 走到这里说明玩家听过旧事，但还没中毒 / 已经去了佛堂但本回没收束。
-- 郭靖、黄蓉 只在「已经被指去佛堂求医」之后才补显 —— 否则玩家拿了铁枪残片
-- （558 让他"去问老庙祝"）、回头再问庙祝，就会在坟地那桩事之前先撞见两位客人。
if GetFlagInt("第一回_求医") == 1 then
    ShowSceneNpc("NPC/郭靖", true)
    ShowSceneNpc("NPC/黄蓉", true)
    if GetFlagInt("第一回_解毒") == 1 then
        Talk(111, "佛堂里那两位客人还没走。你要问什么，趁现在。")
    else
        Talk(111, "毒还没清透罢？佛堂里那两位客人还等着，快去。")
    end
    do return end;
end
Talk(111, "后山那两座坟，你还没去看罢。")
Talk(111, "去看可以。土里的东西，别用手碰。")
do return end;

::label4::
Talk(0, "（他在扫地，扫到庙门口，又扫回来。）", EXPR.think)
if GetFlagInt("第一回_完") == 0 then
    Talk(111, "佛堂那两位还在。你要问什么，趁现在。")
    do return end;
end
Talk(111, "昨夜那位，来过了？")
Talk(0, "来了。")
Talk(111, "你要走了罢。这庙里就我一个，倒也清静。")
Talk(111, "小娃娃——外头的人，比庙里的鬼难缠。你自己留神。")
do return end;
