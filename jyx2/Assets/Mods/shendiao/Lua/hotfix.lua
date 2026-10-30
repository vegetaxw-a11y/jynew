-- 这里是热修复C#逻辑代码的地方
local util = require 'xlua.util'

--这里是展示给大家如何通过lua的热更新进行函数逻辑重写
--[[
util.hotfix_ex(CS.Jyx2.RoleInstance, "InitData", function(self)
    print("lua hot fix called!") --打印调试信息
    self:InitData()  --先执行原函数++++

    --再补执行mod中的附加逻辑
    local function eszy()
        self.MaxHp = self.MaxHp + 100
    end

    local function normal()
        self.MaxHp = self.MaxHp + 200
    end

    local function hard()
        self.MaxHp = self.MaxHp + 300
    end

    local switch = {
        [0] = eszy,
        [1] = normal,
        [2] = hard,
    }

    local difficulty = CS.GameSettingManager.settings[CS.GameSettingManager.Catalog.Difficulty]

    print("Difficulty: ", difficulty)

    if (switch[difficulty]) then
        switch[difficulty]()
        print("switch difficulty called!")
    else
        print("case default")
    end

end)
]]


--修改Talk（例子已停用）
--  这个补丁原本每说一句话就往 Player.log 打一行 "lua hot fix 生效"，
--  1123 句台词就是 1123 行噪音，把真正要看的信息全刷掉了，所以关掉。
--  对话表情走的是 Lua/expr.lua 里对全局 Talk 的包装 + ChatUIPanel.ChangePosition 的补丁，
--  两者互不冲突；要调试时把下面三行的注释去掉即可。
--[[
util.hotfix_ex(CS.Jyx2.Jyx2LuaBridge, "Talk", function(a,b,c)
    print("lua hot fix 生效：CS.Jyx2.Jyx2LuaBridge.Talk called!")
    CS.Jyx2.Jyx2LuaBridge.Talk(a,b,c)  --先执行原函数
end)
]]

--修改UI的例子
util.hotfix_ex(CS.GameMainMenu, "OnCreate", function(self)
    print("lua hot fix 生效：CS.GameMainMenu.OnCreate called!")
    self:OnCreate()
end)


--通过热更新把版本号修改的例子
--[[
util.hotfix_ex(CS.GameInfoPanel, "OnShowPanel", function(self, paras)
    print("lua hot fix 生效：CS.GameInfoPanel.OnShowPanel")
    --self:OnShowPanel(paras)
    self.VersionText_Text.text = "hotfix test"
end)
]]


--[[TODO：
例子

 直接定义函数的例子
 修改UI的例子
 新建UI的例子
 修改战斗参数的例子
]]


-- 场景 NPC 的显隐（第一回坟前那几个人、破窑里的武三通都要反复开关）
--
-- 为什么要这个包装：C# 侧 LevelMasterBooster.RefreshSceneObjects 用的是
--     GameObject.Find("Level/" + path)
-- 而 GameObject.Find **只找激活中的对象** —— 一旦"藏"过一次，后面再想"放出来"
-- 就是 LogError + 不放。所以这里先用 Transform.Find 逐段下钻（它能找到 inactive
-- 的子节点）把人 SetActive(true)，再交给 jyx2_ReplaceSceneObject 记录状态进存档。
--
-- 用法：ShowSceneNpc("NPC/李莫愁", true) / ShowSceneNpc("NPC/李莫愁", false)
function ShowSceneNpc(path, on)
    if on == nil then on = true end
    if on == "0" or on == 0 or on == false then on = false else on = true end

    if on then
        local root = CS.UnityEngine.GameObject.Find("Level")
        local t = root and root.transform
        if t ~= nil then
            for seg in string.gmatch(path, "[^/]+") do
                if t == nil then break end
                t = t:Find(seg)
            end
            if t ~= nil then
                t.gameObject:SetActive(true)
            else
                print("[场景] 找不到对象 Level/" .. path)
            end
        end
    end

    jyx2_ReplaceSceneObject("", path, on and "1" or "0")
end
