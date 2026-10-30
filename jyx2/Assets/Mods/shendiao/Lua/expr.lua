--[[
 * 神雕侠侣 —— 对话表情系统（纯 Lua，不用重新编译游戏）
 *
 * 为什么能这么干：
 *   ChatUIPanel 取头像的路径是 Assets/BuildSource/head/<传给 Talk 的第一个参数>.png
 *   ——也就是"图片名 == 说话人 id"。所以换表情不必改 C#，只要传一个"表情虚拟 id"：
 *       虚拟 id = 9000000 + 角色id * 10 + 槽位号
 *   再用热更新把 ChatUIPanel.ChangePosition 的入参还原成真实角色 id，
 *   左右站位与姓名（含主角自定义名）就仍按真实角色算，看不出区别。
 *
 * 槽位号与 tools/shendiao/gen_sheets.py 的九宫格 SLOTS 一一对应：
 *   1 平静  2 怒  3 笑  4 沉思  5 全身正面  6 全身侧面  7 惊  8 悲恸·决绝  9 背身回望
 *   槽位 1（平静）直接用默认头像 <角色id>.png，不额外占图。
 *
 * 用法（剧本里给 Talk 加第三个参数）：
 *   Talk(22, "……那你要什么？", EXPR.think)
 *   Talk(0,  "我不要人可怜！",   EXPR.angry)
 *   Talk(0,  "（庙后的破窑，如今便是我的家。）")        -- 不写第三个参数 = 默认头像
 *
 * 注意：Lua 的标识符只认 ASCII，所以这里用英文键名，中文键要用 EXPR['怒']。
 * 图片由 tools/shendiao/gen_expr_heads.py 生成，并会把可用列表回填到下面的
 * HAVE_IDS 段；剧本里写了"没生成图"的表情会自动退回默认头像，不会变空白。
]]
local BASE = 9000000
local STEP = 10

-- 表情名 -> 九宫格槽位号（英文键给 Lua 用，中文键给 EXPR['怒'] 用）
EXPR = {
    calm     = 1, ['平静'] = 1,
    angry    = 2, ['怒']   = 2,
    smile    = 3, ['笑']   = 3,
    think    = 4, ['沉思'] = 4,
    body     = 5, ['全身'] = 5,
    bodyside = 6, ['全身侧'] = 6,
    shock    = 7, ['惊']   = 7,
    sad      = 8, ['悲']   = 8,
    lookback = 9, ['回望'] = 9,
}

-- >>> EXPR_HAVE 由 tools/shendiao/gen_expr_heads.py 自动生成，勿手改
local HAVE_IDS = {
    9000002, 9000003, 9000004, 9000008, 9000108, 9000202,
    9000212, 9000214, 9000218, 9000223, 9000224, 9000228,
    9000238, 9000264, 9000277, 9000284, 9000294, 9000313,
    9000314, 9000354, 9000362, 9000363, 9000364, 9000374,
    9000384, 9000392, 9000394, 9000404, 9000434, 9000602,
    9000604, 9000702, 9000708, 9000904,
}
-- <<< EXPR_HAVE

local HAVE = {}
for i = 1, #HAVE_IDS do
    HAVE[HAVE_IDS[i]] = true
end

local rawTalk = Talk

local warned = {}
local function warn_once(msg)
    if warned[msg] then return end
    warned[msg] = true
    print('[表情] ' .. msg)
end

local function slot_of(expr)
    if type(expr) == 'number' then return expr end
    return EXPR[expr]
end

--- 表情虚拟 id -> 真实角色 id（只认得上限 1000 个角色、9 个槽位）
local function ExprRealId(id)
    if id and id >= BASE and id < BASE + 1000 * STEP then
        return math.floor((id - BASE) / STEP)
    end
    return id
end

--- 给"角色 + 表情"算虚拟 id；表情非法时返回 nil
function ExprId(roleId, expr)
    local slot = slot_of(expr)
    if slot == nil or slot <= 1 then return nil end
    return BASE + roleId * STEP + slot
end

--- 是否已经为这个"角色 + 表情"生成了图
function ExprHas(roleId, expr)
    local vid = ExprId(roleId, expr)
    return vid ~= nil and HAVE[vid] == true
end

-- ChangePosition 热更新是否真的在跑（用于下面的一次性自检）
local hotfix_alive = false

--- 是否是一个表情参数（槽位号 1..9 或 EXPR 表里的名字）
local function is_expr(v)
    if v == nil then return false end
    if type(v) == 'number' then return v >= 1 and v <= 9 end
    return EXPR[v] ~= nil
end

-- ---------------------------------------------------------------------------
-- 1. 包一层 Talk：带表情就走虚拟 id，不带就原样转给 C#
--    注意要保住原来的参数个数：main.lua 的 Info() 就是 Talk(0, msg, "", 2) 四参用法，
--    参数被吞掉的话旁白会当成正常对话显示（多出头像和名字）。
-- ---------------------------------------------------------------------------
local talked = 0

if type(rawTalk) ~= 'function' then
    print('[表情] 错误：main.lua 里的 Talk 还没就绪，expr.lua 必须排在 PreloadedLua 里 hotfix 之后')
else
    function Talk(roleId, content, third, fourth)
        -- 热更新没生效时的自检：Talk 内部一定会调 ChangePosition，
        -- 上一句说话后还没看到补丁执行，就说明站位会错（玩家头像会跑到左边）。
        if talked > 0 and not hotfix_alive then
            warn_once('ChangePosition 热更新未生效：玩家表情头像会显示在左侧（姓名仍正确）')
        end
        talked = talked + 1

        if not is_expr(third) then
            -- 老用法：Talk(id, text) / Talk(id, text, talkName, type)
            if fourth ~= nil then
                rawTalk(roleId, content, third, fourth)
            elseif third ~= nil then
                rawTalk(roleId, content, third)
            else
                rawTalk(roleId, content)
            end
            return
        end

        local vid = ExprId(roleId, third)
        if vid == nil then
            rawTalk(roleId, content)
            return
        end
        if not HAVE[vid] then
            warn_once(string.format('缺少表情头像 %d（角色 %d / 槽位 %d），已退回默认头像',
                vid, roleId, vid % STEP))
            rawTalk(roleId, content)
            return
        end
        rawTalk(vid, content)
    end
end

-- ---------------------------------------------------------------------------
-- 2. 热更新 ChangePosition：虚拟 id 一律还原成真实角色 id
--    （站位靠 headId == 0 判定主角，姓名靠 CharacterTable 查，二者都必须拿到真实 id）
-- ---------------------------------------------------------------------------
local okHotfix = false
if util and util.hotfix_ex and CS and CS.ChatUIPanel then
    okHotfix = pcall(util.hotfix_ex, CS.ChatUIPanel, 'ChangePosition',
        function(self, headId, showName)
            hotfix_alive = true
            if showName == nil then showName = true end
            self:ChangePosition(ExprRealId(headId), showName)
        end)
end

if okHotfix then
    print(string.format('[表情] 已启用：%d 张表情头像（ChangePosition 热更新已挂，未注入时会自动告警）',
        #HAVE_IDS))
else
    print('[表情] 警告：ChangePosition 热更新挂载失败，玩家表情头像会显示在左侧')
end
