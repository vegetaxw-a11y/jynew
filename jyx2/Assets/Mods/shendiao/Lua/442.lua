if GetFlagInt("孙婆婆相救") == 0 then
    Talk(0, "（一口石棺，棺盖半开。）", EXPR.think)
    Talk(0, "（里头空空的，铺着一层青白色的玉。）", EXPR.think)
    do return end
end
Talk(0, "（寒玉床。师父说，睡在上头练功，一日顶十日。）", EXPR.think)
Talk(0, "（可这上头冷得钻心。第一夜，我冻得直打哆嗦。）", EXPR.think)
Talk(0, "（第二夜，我睡着了。）", EXPR.think)
Talk(0, "（第三夜，师父站在门口看了一会儿，什么也没说。）", EXPR.think)
Talk(22, "……别翻身。")
Talk(0, "（石室里又只剩水声。）", EXPR.think)

do return end;
