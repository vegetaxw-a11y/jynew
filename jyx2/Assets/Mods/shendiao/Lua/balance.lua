--[[
 * 神雕侠侣 —— 战斗数值平衡层（纯 Lua，不重新编译游戏）
 *
 * 解决三件事：
 *  1) 「等级很高，血量/真气却还是 1 级的」
 *     → RoleInstance.LevelUp() 每级只给 (HpInc+rand(0,3))*3 ≈ 9~27 点血，
 *       而剧本里大量用 AddExp()（只加经验，不升级）；一旦 Level 被别的途径
 *       直接改写（AddLevelreturnUper / 读档），MaxHp 就永远停在旧值。
 *       这里按「等级」给出一个**只补不降**的血量地板：
 *         floorHp = 40 + (等级-1) * 6
 *       斜率 6 取得很小（LevelUp 真实增量是每级 9~27），所以地板只负责把
 *       「完全停在 1 级数值」的角色拉回来：杨过 Lv13 配表 300 血、地板 112，
 *       不动；真掉到 40 血才会被补到 112。补的方式是 MaxHp 与 Hp 同步加同一个
 *       增量，所以在战斗中途调用也不会「凭空回血」。
 *
 *  2) 「郭芙一掌把杨过秒了」
 *     引擎公式（Assets/LuaScripts/Jyx2Battle/DamageCaculator.lua:171-220）：
 *         v = (总攻击 - 总防御*3)*2/3 + RND20 - RND20
 *     防御被乘了 3 倍，谁防御低谁被秒，谁攻击不够谁打不动 —— 天生不平滑。
 *     这里不改引擎文件，而是在 Jyx2.Battle.DamageCaculator.GetSkillResult
 *     外面包一层：拿到原结果后，把「伤害」重新锚定到「目标最大生命的某个比例」，
 *     比例由双方综合实力（Power）之比决定。
 *
 *  3) 「一场仗要磨十几二十回合，太拖沓」
 *     锚定后势均力敌约 6 回合、碾压 3 回合、苦战 10 回合；并且目标越残血
 *     挨打越狠（残血加速 50%），收尾不会拖。
 *
 * 原公式的结果没有被丢掉：它作为「±25% 的倾向修正」参与计算，
 * 所以武功等级、距离修正、体力、武学常识这些差异仍然能体现出来。
 ]]
local M = {}

----------------------------------------------------------------------
-- 一、血量 / 真气地板
----------------------------------------------------------------------
local HP_BASE = 40   -- 1 级基准生命
local MP_BASE = 20   -- 1 级基准真气
-- 每级「最低」成长。LevelUp() 实际给 9~27 点血、12~32 点真气，这里故意取更小的值：
-- 地板只负责把「完全停在 1 级数值」的角色拉回来，绝不主动上调配表已经合理的角色。
local HP_PER_LEVEL = 6
local MP_PER_LEVEL = 3

--- 只补不降：把角色属性拉到「按等级应有的下限」
function M.FixStats(r)
    if r == nil then return end
    local ok, ret = pcall(function()
        local lv = r.Level or 1
        if lv < 2 then return end

        local floorHp = HP_BASE + (lv - 1) * HP_PER_LEVEL
        local floorMp = MP_BASE + (lv - 1) * MP_PER_LEVEL

        local maxHp = r.MaxHp or 0
        if maxHp < floorHp then
            local d = floorHp - maxHp
            r.MaxHp = floorHp
            r.Hp = (r.Hp or 0) + d      -- 同步补，等于「凭空多出来的上限直接回满」
            print(string.format("[balance] %s Lv%d 生命 %d -> %d", tostring(r.Name), lv, maxHp, floorHp))
        end

        local maxMp = r.MaxMp or 0
        if maxMp < floorMp then
            local d = floorMp - maxMp
            r.MaxMp = floorMp
            r.Mp = (r.Mp or 0) + d
            print(string.format("[balance] %s Lv%d 真气 %d -> %d", tostring(r.Name), lv, maxMp, floorMp))
        end
    end)
    return ok and ret or nil
end


----------------------------------------------------------------------
-- 二、伤害重锚定
----------------------------------------------------------------------
local BASE_RATIO = 0.16   -- 势均力敌时，一击打掉目标最大生命的比例
local RATIO_MIN, RATIO_MAX = 0.10, 0.40
local K_EXP = 1.15        -- 实力比 -> 伤害比的曲线指数
local TILT = 1.2          -- 原公式结果对最终伤害的影响强度
local TILT_CAP = 0.25     -- 影响上限 ±25%
local LOW_HP_BOOST = 0.5  -- 目标残血时，额外最多 +50% 伤害（防止磨血）

--- 综合实力（越强越大），只用于比值，不需要和别的模组对齐
function M.Power(r)
    if r == nil then return 1 end
    local atk = r.Attack or 0
    local def = r.Defence or 0
    local lv = r.Level or 1
    local hp = r.MaxHp or 0
    return atk * 1.0 + def * 0.9 + lv * 5.0 + hp * 0.08
end

--- 把原公式算出来的 dmg 重新锚定到目标血量的合理比例上
function M.AdjustDamage(r1, r2, dmg)
    if dmg == nil or dmg <= 0 then return dmg end
    if r2 == nil then return dmg end
    local hp2 = r2.MaxHp or 0
    if hp2 <= 0 then return dmg end

    local p1, p2 = M.Power(r1), M.Power(r2)
    local k = 1.0
    if p2 > 0 then k = p1 / p2 end
    if k < 0.25 then k = 0.25 elseif k > 4 then k = 4 end

    local ratio = BASE_RATIO * (k ^ K_EXP)
    if ratio < RATIO_MIN then ratio = RATIO_MIN elseif ratio > RATIO_MAX then ratio = RATIO_MAX end

    -- 残血加速：被打得越惨，每一击越狠，战斗不会拖成「磨血」
    local cur = r2.Hp or hp2
    if cur > 0 and cur < hp2 then
        ratio = ratio * (1 + LOW_HP_BOOST * (1 - cur / hp2))
    end

    local target = hp2 * ratio

    -- 原公式结果只做倾向修正，保留武功等级 / 距离 / 体力的手感差异
    local dev = (dmg / hp2 - ratio) * TILT
    if dev > TILT_CAP then dev = TILT_CAP elseif dev < -TILT_CAP then dev = -TILT_CAP end

    local out = math.floor(target * (1 + dev))
    if out < 1 then out = 1 end
    return out
end


----------------------------------------------------------------------
-- 三、接管引擎的伤害函数
----------------------------------------------------------------------
local PATCH_FLAG = "__shendiao_balance_patched"
local patched = false

--- 延迟绑定：Jyx2.Battle 可能比 mod 的 PreloadedLua 更晚才建好，多试几次
function M.TryPatchDamage()
    if patched then return true end
    local jyx2 = rawget(_G, "Jyx2")
    if jyx2 == nil or jyx2.Battle == nil then return false end
    local dc = jyx2.Battle.DamageCaculator
    if dc == nil or type(dc.GetSkillResult) ~= "function" then return false end
    if rawget(dc, PATCH_FLAG) then patched = true; return true end

    local orig = dc.GetSkillResult

    dc.GetSkillResult = function(caster, target, skill, blockVector)
        local rst = orig(caster, target, skill, blockVector)

        -- 顺手修血：战斗中也不会有副作用（只加上限 + 等量当前值）
        M.FixStats(caster)
        M.FixStats(target)

        if rst ~= nil and rst.damage ~= nil and rst.damage > 0 and skill ~= nil then
            local ok, magic = pcall(function() return skill.Data:GetSkill() end)
            -- 只重锚定「普通伤害」(DamageType 0)；吸内/用毒/解毒/治疗/暗器保持原样
            if ok and magic ~= nil and magic.DamageType == 0 then
                local out = M.AdjustDamage(caster, target, rst.damage)
                rst.hurt = math.floor(out / 10)
                rst.damage = out
            end
        end
        return rst
    end

    rawset(dc, PATCH_FLAG, true)
    patched = true
    print("[balance] 伤害公式已接管（锚定最大生命的 10%~40%）")
    return true
end

----------------------------------------------------------------------
-- 四、挂在角色生命周期上
----------------------------------------------------------------------
M.TryPatchDamage()

local okHot, errHot = pcall(function()
    local util = require 'xlua.util'

    -- 读档 / 创建角色后校正
    util.hotfix_ex(CS.Jyx2.RoleInstance, "InitData", function(self)
        self:InitData()
        M.FixStats(self)
        M.TryPatchDamage()   -- InitData 一定发生在引擎 Lua 初始化之后，是可靠的重试点
    end)

    -- 升级后校正（LevelUp 本身会加，但「直接改 Level」的情况它管不到）
    util.hotfix_ex(CS.Jyx2.RoleInstance, "LevelUp", function(self)
        self:LevelUp()
        M.FixStats(self)
    end)
end)
if not okHot then
    print("[balance] 挂生命周期钩子失败：" .. tostring(errHot))
end

SHENDIAO_BALANCE = M
