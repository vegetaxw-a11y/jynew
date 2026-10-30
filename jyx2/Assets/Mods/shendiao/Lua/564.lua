-- 【第一回 · 风月无情】用铁器拨开坟土（564 = 墓碑上的"用物品"事件）
-- 支线，不是主线必经：给出"掘墓人不要陪葬，只要人"的实证 + 一只玉镯。
-- 不给"坟地"flag，避免抢掉 563 第一次的三人坟前戏。
if GetFlagInt("第一回_玉镯") == 1 then
    Talk(0, "（土翻过两遍了。剩下的只有棺木的碎屑。）", EXPR.think)
    do return end
end
Talk(0, "（我用随身的铁器在棺底拨了几下。石灰底下还有一层棉垫。）", EXPR.think)
Talk(0, "（棉垫里滚出一只素白的玉镯，断成两截。内壁刻着两个字：沅君。）", EXPR.think)
Talk(0, "（旁边还有半个冷硬的馒头，硬得像石头。有人在这坟前守过。）", EXPR.think)
Talk(0, "（盗墓的不要陪葬，只要人。）", EXPR.think)
Talk(0, "（那只玉镯，我揣进了怀里。）", EXPR.think)
AddItem(70, 1)
SetFlagInt("第一回_玉镯", 1)
ShowMessage("得到「玉镯子」")
do return end;
