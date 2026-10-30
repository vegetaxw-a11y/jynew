# JYX2 MOD 开发指南（含坑位清单）

> 面向：在 `jyx2/Assets/Mods/<id>/` 下写剧情 MOD 的人（和 AI）。
> 依据：`shendiao` 一个 MOD 从 0 到第一章可玩的全部实践 + 源码走读。
> 结论均在跑通的代码/工具里验证过；标注 `[推断]` 的是读代码得出、尚未实跑验证的。

---

## 0. 一页速览：MOD 到底是什么

一个 JYX2 MOD = **一个目录 + 一份 ModSetting + 两个 AssetBundle + 一堆 Excel 和 Lua**。

游戏本体（`wuxia_launch.exe`）不含任何剧情，它只做三件事：

1. 扫 `<游戏>/wuxia_launch_Data/mods/*/`，读每个 `<id>.xml` 认出有哪些 MOD；
2. `AssetBundle.LoadFromFile` 加载 `<id>_mod` / `<id>_maps`；
3. 用**通用解释器**跑你的 Excel 配置表和 Lua 剧本。

所以 MOD 的"游戏逻辑"全部由**数据**驱动，不需要（也不该）改 C#。
改 C# 只能进工程本体重编 player，那是另一条路。

### 心智模型：三层数据

| 层 | 文件 | 谁读 | 改完怎么生效 |
| --- | --- | --- | --- |
| **配置表** | `Configs/*.xlsx` → `Configs/Lua/*Config.lua` | `LuaToCsBridge.MapTable` 等 | 重跑 `configs` + **重打 AB** |
| **剧本** | `Lua/<事件id>.lua` | `LuaManager.LoadLua` | 重打 AB（Editor 内热重载秒生效） |
| **场景** | `Maps/GameMaps/*.unity` | Unity 场景加载 | 重打 `<id>_maps` |

三层里**任何一层改了都要重打 AB 并重装**，否则游戏里还是旧的。
这是最常见的"我明明改了却没反应"。

---

## 1. 加载链路（谁在什么时候读什么）

```
选 MOD
 └─ ResLoader.LaunchMod()               // 加载 <id>_mod / <id>_maps
    └─ RuntimeEnvSetup.Setup()
       ├─ CurrentModConfig = LoadAsset<MODRootConfig>("Assets/ModSetting.asset")
       ├─ ResLoader.Init()
       ├─ Jyx2ResourceHelper.Init()
       └─ LuaManager.LuaMod_Init()
          └─ PreloadLua()               // 跑 ModSetting.PreloadedLua 里列的脚本（如 hotfix）
进入场景
 └─ LevelMasterBooster.Awake()          // 实例化 LevelMaster
    └─ Start()
       ├─ MapChest.Init()  ×N
       ├─ RefreshSceneObjects()                 // 按存档重放 jyx2_ReplaceSceneObject
       ├─ foreach FixWithGameRuntime → Reload() // 按存档摆正场景物件
       └─ ShowMainUI()
玩家交互
 └─ GameEvent（挂在 Level/Triggers/<id>）
    └─ GameEventManager.OnTriggerEvent()
       └─ ExecuteJyx2Event(事件id)
          ├─ graph = LoadEventGraph(id)        // 蓝图事件（本文不涉及）
          ├─ path = string.Format(ModSetting.LuaFilePatten, id)
          ├─ LuaExecutor.Execute(path)
          └─ OnFinishEvent()                   // ← 必须走到，否则事件永久锁死
```

### 1.1 文件名是怎么从事件 id 算出来的

`ModSetting.asset` 的 `LuaFilePatten` 决定映射：

| MOD | LuaFilePatten | 事件 id 455 → 读的文件 |
| --- | --- | --- |
| `JYX2`（内置） | `ka{0}` | `ka455.lua` |
| `shendiao` | `{0}` | `455.lua` |

**坑**：照抄默认值 `ka{0}`，你写的 `455.lua` 永远不会被找到，日志里只有一句 `找不到文件 [ka455]`。
新建 MOD 后务必核对一眼 `ModSetting.asset` 的 `LuaFilePatten`。

### 1.2 场景触发器怎么和 Lua 对上

1. 场景里 `Level/Triggers/<名字>` 这个 GameObject 上挂 `GameEvent`；
2. `GameEvent.m_InteractiveEventId = "455"`（**字符串**，`-1` 表示没有交互事件）；
3. 这个 `<名字>` 同时是 `GameObject.Find("Level/Triggers/455")` 的查找键 —— **物体名与事件 id 必须一致**；
4. `LevelMaster` 运行时把 `Level/Triggers` 下所有子物体设成 `GameEvent`(Layer 28) 层。

三种事件字段：

| 字段 | 触发方式 | 优先级 |
| --- | --- | --- |
| `m_EnterEventId` | 玩家走进 Collider（**必须 isTrigger**） | Highest，直接执行 |
| `m_InteractiveEventId` | 靠近按交互键，弹交互面板 | Lowest |
| `m_UseItemEventId` | 同上，但点"使用物品"并选道具 | Lowest |

`-1` = 该槽位为空。三者都空时 `IsEmptyEvent` 为真，触发器不参与高亮/交互。

### 1.3 Lua 里哪些调用会"卡住事件"

`main.lua` 用 `util.async_to_sync(...)` 包了一层的是**阻塞式**：Lua 协程 yield，
直到 C# 回调才继续，**中间玩家可以一直不点**。

- 阻塞（等玩家/战斗）：`Talk` `ShowMessage` `ShowYesOrNoSelectPanel` `ShowSelectPanel`
  `ShowMessageSelectPanel` `TryBattle` `AskBattle` `AskJoin` `AskRest` `WeiShop`
  `LightScence` `DarkScence` `ShowEthics` `ShowRepute` `AskSoftStar`
  `jyx2_Wait` `jyx2_WalkFromTo` `TryBattleWithConfig`
- 非阻塞（立即返回）：其余全部，包括 `SetFlagInt` `AddItem` `PlayMusic` `jyx2_FixMapObject` `ShowToast`

**推论**：最后一个阻塞调用结束后事件才算完。玩家在对话中途退出/切场景，
`OnFinishEvent` 可能不执行 —— 这就是历史上"事件锁死"的来源（现已加三重兜底，见 §5.2）。

---

## 2. 目录与命名约定

```
<jyx2>/Assets/Mods/<id>/
├── ModSetting.asset          必填，MODRootConfig。ModId 必须与目录名一致（大小写不敏感）
├── README.md                 可选，工程内文档
├── Configs/
│   ├── *.xlsx                配置表（A1=LuaConfigGen，B1=表名）
│   └── Lua/*Config.lua       生成物，**不要手改**
├── Lua/
│   ├── <事件id>.lua          剧情脚本，文件名=事件 id
│   └── hotfix.lua            预加载脚本（ModSetting.PreloadedLua 列出）
├── Maps/GameMaps/*.unity     场景，标到 <id>_maps
├── Models/ Prefabs/ Skills/ ModelsResource/ Terrain/ Timeline/ Skybox/ Animations/
└── *.meta
```

### 2.1 只有两个 AssetBundle

游戏只认这两个名字（`Jyx2ModTool.GetModMainBundleName`）：

| 包名 | 放什么 |
| --- | --- |
| `<id>_mod` | 预制体、模型、贴图、`Configs`、`Lua` |
| `<id>_maps` | `Maps/` 下的场景 |

**`check` 会校验**：新加的资源如果没标 AB，它不会进包 → 运行时找不到（Unity 不报错，只是"东西不见了"）。

### 2.2 MOD 目录里不能放 `Scripts/`

会和工程本体同名类冲突，Unity 直接编译失败。
`SAMPLE` 里有 `Scripts/`（它是模板），从它复制出来的 MOD 要把 `Scripts/` 删掉。

### 2.3 命名不要用中文

`Lua/` 下用纯数字 id，`Maps/` 下用 `19_chongyanggong` 这种。中文只出现在 xlsx 数据和对话文本里。
（`Models/杨过.asset` 这类中文资源名在现有 MOD 里能用，但会增加打包和工具链的不确定性，非必要不用。）

---

## 3. 配置表（Excel → Lua）

### 3.1 表格必须遵守的 5 行结构

```
行1:  A1="LuaConfigGen"      B1=<表名>           ← 表名决定生成 <表名>Config.lua
行2:  字段中文注释（不参与生成）
行3:  类型：L_number / L_string / L_boolean / 复合(L_number,L_string) / 列表加 []
行4:  字段名（空列、# 开头的列会被忽略）
行5+: 数据（首列为空或 # 开头的行会被忽略）
```

生成命令（不需要 Unity，秒级）：

```powershell
python tools/moddev/jyx2mod.py configs shendiao
```

产物 `Configs/Lua/<表名>Config.lua`，含 `fieldIdx` 表 + `data` 二维数组，**手改无效**（下次生成即覆盖）。

### 3.2 shendiao 现有的 7 张表

| 文件 | B1 表名 | 生成物 | 关键字段 |
| --- | --- | --- | --- |
| 人物.xlsx | Character | `CharacterConfig.lua` | `Id` `Name` `Sexual` `Level` `MaxHp` `Attack` `Model`… |
| 场景.xlsx | Map | `MapConfig.lua` | `Id` `Name` `MapScene` `TransportToMap` `InMusic` `OutMusic` `EnterCondition` `Tags` |
| 战斗.xlsx | Battle | `BattleConfig.lua` | `Id` `Name` `Map` `Exp` `Money`… |
| 武功.xlsx | Skill | `SkillConfig.lua` | `Id` `Name` `Damage`… |
| 物品.xlsx | Item | `ItemConfig.lua` | `Id` `Name` `Buy` `Sell`… |
| 商店.xlsx | Shop | `ShopConfig.lua` | 商品列表 |
| 游戏设置.xlsx | Settings | `SettingsConfig.lua` | 全局数值 |

**人物 Id 0 = 主角**：`Talk(0, "...")` 就是主角头像说话（显示名由 `ModSetting.PlayerName` 决定）。

### 3.3 MapConfig 与大地图传送（最容易返工的一环）

一行长这样：

```lua
{1,[[重阳宫]],[[19_chongyanggong]],[[Leave:1000]],22,0,0,""},
   ↑Id     ↑Name      ↑MapScene       ↑TransportToMap  ↑In ↑Out ↑Cond ↑Tags
```

- `TransportToMap = "Leave:1000"` → 场景里 **`Level/Triggers/Leave`** 这个触发器，玩家碰到后传送去地图 1000（大地图）
- 回大地图时，**落点靠 `Map.Name` 匹配大地图里的触发器名**（`LevelMaster` 用 `para.triggerName = curMap.Name`）
  → 所以**改地图名必须同步改大地图 `1000_daditu` 里同名 GameObject**，否则玩家回大地图会被丢在原点
- `Tags`：`START:0` = 新游戏出生点；`WORLDMAP` = 这张图是大地图（`EnterCondition` 直接返回 0）；
  `POINTLIGHT` / `NONAVAGENT` 是场景表现开关
- `EnterCondition`：**目前是装饰字段**。`GameRuntimeData.GetSceneEntraceCondition()` 只有定义、
  全工程**零调用点**，`SceneEntraceCondition_<id>` 也没人读写。填 `1` 不会真的锁住任何东西，
  真正拦人的是大地图上那个触发器的目标场景。别拿它做章节门禁（想做门禁就在触发器上写 Lua 条件）

闭路校验（**改完地图一定要跑**）：

```powershell
python tools/shendiao/check_maplinks.py
```

它查四件事：MapScene 有没有对应 `.unity`、场景里有没有 `Leave` 触发器、
大地图有没有同名落点、大地图有没有"点了没反应"的死触发器。

### 3.4 Excel 的隐藏坑：必须用 xlsxwriter 重写

工程里打包的 `Excel.dll` 是**老版 ExcelDataReader，只认 sharedStrings**。
用 openpyxl 直接 `save()` 出来的文件，Unity 侧 `ExcelToLua.cs` 读会拿不到字符串。

- 走 `python tools/moddev/jyx2mod.py configs`（纯 Python 的 `excel2lua.py`）：**不受影响**（它自己用 openpyxl 读）
- 走 Unity 菜单「生成配置表」（`MODRootConfig.GenerateConfigs`）：**会中招**，
  所以 `apply_configs.py` 统一用 xlsxwriter 重写

**规矩**：改 xlsx 一律走 `tools/shendiao/apply_configs.py` 或手动用 xlsxwriter，别用 openpyxl 保存。

---

## 4. 写剧情脚本（Lua）

### 4.1 最小可用模板

```lua
-- Lua/<事件id>.lua，文件名 = 事件 id（LuaFilePatten={0} 时）
Talk(60, "站住！什么人？")            -- 人物 60 说话（数字=人物表 Id，0=主角）
Talk(0, "晚辈杨过。")
SetFlagInt("入全真", 1)                -- 存档变量，立即写入
if GetFlagInt("入全真") == 1 then
    -- ...
end
do return end;                         -- 惯例收尾
```

`do return end` 还有个特殊用途：**空脚本**必须是 `do return end;`，
`LuaExecutor.ExecuteLuaAsync` 会识别这个字符串直接跳过（否则会走一遍空协程）。

### 4.2 分文件复用：`文件.函数`

`LuaExecutor.Execute("xxx.funcName")` → 读 `xxx.lua`，在正文末尾追加 `\nfuncName()` 再执行。

注意它**不会** `require`，只是字符串拼接 —— 函数必须是全局函数，文件里不能在顶层 `return`。

### 4.3 存档变量：Flag 的三种写法

| API | 类型 | 何时用 |
| --- | --- | --- |
| `SetFlag/GetFlag(key)` | string | 一般不用，容易踩 `"1"` vs `"1.0"` |
| `SetFlagInt/GetFlagInt(key)` | int | **剧情分支首选**，最稳 |
| `scene_api.SetInt/GetInt(key)` | int，自动加 `SceneFlag:<地图id>@` 前缀 | 只在本场景有意义的状态 |

- Flag 存在存档 `KeyValues` 里，跨场景、跨存档保留
- 数值统一用 `SetFlagInt`，**不要**用 `SetFlag` 存数字
- 新增 Flag 在旧存档里读出来是 0 → 默认值按"没做过"设计，逻辑要对缺失 key 幂等

---

## 5. 事件机制：为什么会"锁死"

### 5.1 单槽状态机

`GameEventManager` 里只有一个 `curEvent` + 一个静态 `_currentEvt`（存 GameObject 名）：

```
ExecuteJyx2Event(id)
  ├─ if (GetCurrentGameEvent() != null) → LogError("在一个事件执行完毕以前不能执行新的事件") 并 return
  ├─ SetCurrentGameEvent(curEvent)      // _currentEvt = 触发器名
  ├─ ExecuteCurEvent().Forget()          // 异步跑 Lua
  └─ 正常路径结束时 OnFinishEvent() → _currentEvt = ""、curEvent = null
```

也就是说：**同一时刻只能有一个事件在跑**，第二个直接被丢弃（不是排队）。

### 5.2 三种"锁死"来源

| # | 成因 | 现象 | 现状 |
| --- | --- | --- | --- |
| 1 | `LuaManager.LoadLua` 返回 null（脚本缺失/文件名算错） | 该触发器不响应，之后**全场景事件都不响应** | `LuaExecutor.Execute` 已加 null 检查直接 return，让上层走完 `OnFinishEvent` |
| 2 | Lua 抛异常（语法错、`Talk` 传了不存在的人物 Id 导致 UI 空引用） | 同上 | `ExecuteLuaAsync` 的 catch 里手动 `LuaExecFinished`；`GameEventManager` 的 try/catch 之后仍执行 `OnFinishEvent` |
| 3 | Lua `await` 的调用永不回调（玩家在 `Talk` 里退出游戏/切场景） | 同上 | **无自动兜底**，只能靠 `LuaExecutor.Clear()`（切场景时调） |

历史上 `Talk(99, ...)` 传了人物表里没有的 Id，`ChatUIPanel` 空引用崩掉 → 事件永不结束 →
整张图再也点不动任何交互点。这就是 `tools/shendiao/check_story.py` 存在的原因 —— **导出前必跑**：

```powershell
python tools/shendiao/check_story.py
# 配置表：人物 61 / 物品 75 / 武功 29 / 战斗 27
# 检查 115 个剧情脚本：0 个错误，0 个提醒
```

它查：`Talk` 的 Id、`AddItem`/`UseItem` 的 Id、`TryBattle` 的 Id、`LearnMagic2` 的武功 Id、`goto`/`::label::` 配对。

**但它不查场景引用** —— 删掉某个 `<id>.lua` 时它不会报错（这正是误删 `0/3/4/10.lua`
却没被发现的原因）。删脚本前必须自己扫场景：

```powershell
Select-String -Path 'jyx2\Assets\Mods\<id>\Maps\GameMaps\*.unity' `
  -Pattern 'm_(InteractiveEventId|EnterEventId|UseItemEventId): 455$'
```

### 5.3 事件里不要做"同步重活"

`ShowToast` `PlayMusic` `SetFlagInt` 这类非阻塞调用立即返回；
但 `jyx2_Wait(3)` 是真等 3 秒（受 `jyx2_SetTimelineSpeed` 影响）。
一个事件里连续堆 20 个 `Talk` 没问题，但**不要在事件里等玩家做别的事**
（比如"等玩家走开再继续"），系统没有这种能力，只能写成"进入另一个触发器"。

### 5.4 交互点全哑了的排查顺序

1. `logs -f` 看有没有 `错误：在一个事件执行完毕以前不能执行新的事件`
2. 看有没有 `找不到文件 [xxx]`（→ 文件名 / `LuaFilePatten` 不对）
3. 看有没有 `lua执行错误：`（→ 语法或运行期异常；`check` 抓语法，`check_story` 抓 Id）
4. 实在不行切一次场景（`LuaExecutor.Clear()` 会清栈）

---

## 6. 存档状态机：让场景"记住"玩家干过什么

### 6.1 四个 API 的分工

| API | 存什么 | 生效时机 | 适用 |
| --- | --- | --- | --- |
| `SetFlagInt/GetFlagInt` | `KeyValues[flag]` | 立即 | 剧情分支 |
| `jyx2_ReplaceSceneObject(scene, path, replace)` | `SceneInfo[scene][path]` | **下次进场景** | 永久让某个 `Level/<path>` 显隐 |
| `jyx2_FixMapObject(key, value)` | `KeyValues[key]` | **立即** + 下次进场景 | 移动/摆放场景物件 |
| `scene_api.SetActive(path, bool)` | `SceneObj:<地图>@<path>` | 立即 | 纯场景内物体开关 |

### 6.2 `FixWithGameRuntime` 的正确用法

组件字段只有三个：`FixType`（目前只有 `Move`）、`Flag`、`MoveTo`（Transform 锚点）。

```csharp
// FixWithGameRuntime.cs 核心
if (runtime.KeyExist(Flag) && runtime.KeyValues[Flag] == "1")
    transform.position = MoveTo.position;   // ← 移动的是"挂载者自己"
else
    transform.position = storeP;            // ← 复位到首次 Reload 时的位置
```

调用时机只有两个：

1. 进场景时 `LevelMasterBooster.Start()` 遍历场上**所有** `FixWithGameRuntime` 调 `Reload()`
2. Lua 里 `jyx2_FixMapObject(key, value)` → 写 Flag，然后遍历所有组件、`Flag == key` 的调 `Reload()`

**装配清单（每一项都是坑）**：

- [ ] 组件挂在**要被移动的那个物体**上。挂在父节点/触发器上，移动的是父节点/触发器
- [ ] `MoveTo` 指向一个**专用空锚点**（自己建一个，别借用其他 NPC 的 Transform）
- [ ] `Flag` 全局唯一，`grep` 确认场上没有第二个同名组件的 Flag（两个同名会互相覆盖）
- [ ] Lua 里传**字符串** `"1"`：`jyx2_FixMapObject("xxx", 1)` 传 number 时，某些路径下会变成 `"1.0"`，`=="1"` 判定失败
- [ ] 给"已经做过这件事的老存档"补一次调用（幂等），否则老玩家永远看不到变化
- [ ] 锚点 `y` 用地面高度，别浮空也别埋地下

### 6.3 `jyx2_FixMapObject` 到底做了什么

```csharp
runtime.KeyValues[key] = value;
foreach (var obj in FindObjectsOfType<FixWithGameRuntime>())
    if (key == obj.Flag) obj.Reload();
FindObjectOfType<LevelMasterBooster>().RefreshSceneObjects().Forget();   // ← 注意这里
```

最后一句会按 `Level/<key>` 路径**重新 SetActive** 所有 `SceneInfo` 记录，顺带刷新场景显隐。
副作用：`LevelMasterBooster` 不存在时（比如战斗场景里调）这里会 NRE。

### 6.4 `scene_api`：不改场景也能加交互点

`Jyx2LuaBridge_SceneApi.cs` 提供的能力（**官方 JYX2 MOD 里基本没用过，半成品 API，用前先小范围验证**）：

| 函数 | 作用 |
| --- | --- |
| `scene_api.BindEvent(path, funcName, radius)` | 给 `Level/<path>` **运行时**加 `SphereCollider`(trigger) + `GameEvent` + `NavMeshObstacle`，并设成 GameEvent 层 |
| `scene_api.Register(path)` | 把物体登记进存档（首次记录激活状态，之后按 flag 恢复） |
| `scene_api.SetActive(path, bool)` | 开关该物体（写 `SceneObj:<地图>@<path>`） |
| `scene_api.SetInt/GetInt/SetString/GetString/SetBool/GetBool` | 带地图前缀的场景变量 |
| `scene_api.CallOnce(fn)` / `CallOnceWithFlag(fn, flag)` | 每场景只跑一次 / 按 flag 只跑一次 |

⚠️ **`BindEvent` 副作用**：它会 `GetOrAddComponent<NavMeshObstacle>()` 并设成 Capsule(radius 0.5, height 2)。
默认不 carving，所以不会挖 NavMesh；但如果那个位置本来就在窄通道上，**agent 绕不过去**。
把交互点绑在过道正中 = 自己造一堵墙。这一条与 §7.4 的"空气墙"同源。

---

## 7. 改场景（`.unity`）

### 7.1 场景骨架

```
Level
├── Player            ← 必须有，Jyx2Player；模型来自它引用的 prefab
├── NPC               ← 所有地图角色
├── Triggers          ← 事件触发器，运行时全部设成 GameEvent(Layer 28)
│   ├── 455           ← 名字 = 事件 id
│   ├── Leave         ← 传送点，与 TransportToMap 的 "Leave:1000" 对应
│   └── ...
├── Static            ← 建筑/地形/装饰
└── ...
```

### 7.2 NPC 摆放的三条硬约束

**约束一：NPC 的 x/z 必须等于对应触发器的 x/z。**

交互判定在 `Jyx2Player.CanSee`：

```csharp
var isInViewField = Vector3.Angle(transform.forward, target.transform.position - transform.position)
                    <= PLAYER_INTERACTIVE_ANGLE / 2;
var isInTrigger   = target.bounds.Contains(transform.position + targetDirection * _navMeshAgent.radius);
```

`target` 是 `Level/Triggers/<id>` 上的 BoxCollider。玩家的 NavMeshAgent 必须**真正站进这个盒子**。
把 NPC 摆到"看起来更好看"的地方 = 玩家永远点不到他。`set_npc.py` 的 `LAYOUT` 就是直接抄触发器坐标。

**约束二：触发器的 y 必须让盒子罩住玩家脚下。**
BoxCollider 1×1×1、中心在物体位置 → 范围 `[y-0.5, y+0.5]`。
地面 y=0 时触发器 y 用 0.5；写 y=5.61 而玩家在 5.0 → `Contains` 永远 false → 静默失效（真实发生过）。

**约束三：NPC 不要在 Layer 28（GameEvent）上。**
28 层留给 `Level/Triggers`。模型节点建议统一 Layer 16（相机可见层）。
`LevelMaster` 在 `Awake`/`Start` 里会把 `Level/Triggers` 的子物体全部改成 28 层。

### 7.3 触发器是"交互"还是"路过"

- `m_InteractiveEventId` 有值 + `m_EventTargets` 非空 → 靠近高亮，按交互键弹面板
- `m_EnterEventId` 有值 → `OnTriggerEnter` 直接执行，**Collider 必须 `m_IsTrigger: 1`**
  （`Leave` 传送点最常见。历史上 `19_chongyanggong` 的 `Leave` 是个 `isTrigger=0` 的 3×4.5m **实心墙**，
  玩家根本走不进去 → "走到地图边缘回不了大地图"）
- `m_UseItemEventId` → 需要对应道具

### 7.4 导航：本次踩得最惨的一类坑

| 现象 | 真凶 | 判据 |
| --- | --- | --- |
| 走不过去、"空气墙" | `NavMeshObstacle.m_Carve = 1` 在 Play 模式实时挖穿 NavMesh | Edit 模式探针看起来**完全连通**，Play 模式 `SetDestination` 无完整路径 |
| 站位"看得见但走不动" | 老存档 `WorldMapSaveData.areaMask = 0` | 必须用新存档验证 |
| 绕不过 NPC | `NavMeshObstacle` 默认带 avoidance | `scene_api.BindEvent` 会自动加一个 Capsule obstacle |

**`m_Carve` 的真实杀伤力**：BoxObstacle 的 `m_Extents` 是**局部尺寸**，世界尺寸要乘 Transform scale。
一个 `(1.5,1,0.5)` 的盒子在 scale=2 的节点下是 **6×2m**，足以把整个门洞挖掉；
挖掉后两侧剩不到 agent radius(0.5) 的宽度，寻路直接失败。

**诊断方法（两个都要做）**：

1. **静态**：`python tools/shendiao/list_colliders.py --scene <场景.unity> --near 32,11 --solid-only`
   把 local 尺寸乘 scale 折算成世界尺寸、按距离排序，一眼看出谁挡在通道上
2. **Play 模式探针**：`ShendiaoNavProbe.Probe` 只能看 Edit 模式的 NavMesh，
   **carving 在 Edit 模式不生效**，所以它同时打印 `NavMeshObstacle.carve` 值

**规矩**：
- 站在通道/门口的 NPC，`NavMeshObstacle` 一律 `m_Carve = 0`
- 真要挡人用物理 Collider（玩家有 CapsuleCollider），不要指望 obstacle 挖洞
- 新存档验证，不要用旧档

### 7.5 prefab 实例与 `m_Modifications`

场景里的角色是 `PrefabInstance` + 一串 `m_Modifications`（`target: {fileID: 内部id, guid: prefab guid}`）。

- **只改本场景的实例覆盖，不要改 prefab 源文件**：`QuanzhenDizi 1.prefab` 被 19/01 两张图共 133 个实例引用，
  改 prefab 会影响全部
- 换 prefab 必须重映射 `m_Modifications` 的 `target.fileID`，否则位置覆盖失效、角色掉到 `(0,0,0)`
  （`tools/shendiao/fix_player.py` 干的就是这件事）
- **不要把 override 指到 stripped（子 prefab 内部）对象**：一条 `m_IsActive: 0` 命中子 prefab 根会把整只模型关掉

### 7.6 手工编辑 `.unity` 的规矩

- **`m_Size` 是局部尺寸**，世界尺寸 = `m_Size × m_LocalScale`
- 新增对象要**手工分配 fileID**，且必须 `grep` 全文件确认不冲突（本工程用到的段位：`16xxxxxxx`、`21xxxxxxx`）
- 每个新增 GameObject 至少要有：`GameObject`(!u!1) + `Transform`(!u!4)，再按需挂 `MonoBehaviour`(!u!114)
- 新增组件要同时登记进父物体的 `m_Component` 列表，否则运行时不会实例化
- 中文文本用 `\uXXXX` 转义（YAML 里直接写 UTF-8 中文在部分工具链下会被破坏）
- 编辑完用 `git diff --stat` 确认没顺带改到别的文件

---

## 8. 坑位清单

### 8.1 已踩过的（有具体案例）

#### 资源与打包

| # | 坑 | 症状 | 根因 | 对策 |
| --- | --- | --- | --- | --- |
| 1 | 主角"是空气" | 能走能触发，但完全不可见，Unity 不报错 | prefab 依赖的 mesh 在 `ModelsResource/`，那里没标 AB → prefab 进包、mesh 没进 | 模型一律引 `Assets/BuildSource/ModelCharacters/**`（随 base_assets 发布）；`check_guids.py` / `check_refs.py` 体检 |
| 2 | 复制模板 MOD 后 NPC 隐形 | 同上 | `.meta` 换了新 GUID，资源文件里对旧 GUID 的引用没换 | `jyx2mod.py new` 已修；老 MOD 用 `fix_guids.py` |
| 3 | 新加的资源运行时找不到 | 编辑器里一切正常 | 没标 `shendiao_mod` / `shendiao_maps` | `jyx2mod.py check`；导出后 `grep` AB 内容确认 |
| 4 | 包体积莫名涨到 3 倍 | `<id>_maps` 从 114MB → 363MB | 增量导出跳过 `base_assets`，共享贴图/Shader 被复制进 MOD 包 | 分发前 `--with-base` 全量打一次 |
| 5 | 导出后 `git status` 多出一堆改动 | 3 个 water `.mat` + `DOTweenSettings.asset` + `EditorUserSettings.asset` | Unity batchmode 顺手重新序列化 | 导出后 `git checkout --` 这几个文件，**别提交** |
| 6 | **MOD 覆盖 base 资源（头像/贴图）不生效** | 图放进了 `Assets/Mods/<id>/`，游戏里还是原版那张 | ① 资源**没打 `assetBundleName`** → `Jyx2ModCli.CreateBundleBuild` 用 `GetAssetPathsFromAssetBundle` 收集，压根不进包；② 路径必须镜像 base 的 `assets/` 结构 | 放 `Assets/Mods/<id>/BuildSource/head/10.png`（`ResLoader.LaunchMod` 会把 `assets/mods/<id>/` 前缀剥掉、后登记的覆盖先登记的）；`.meta` 写 `assetBundleName: <id>_mod`；复制 `.meta` 时 `guid` 和 `spriteID` **都必须换新**，否则和原版撞 |

#### 战斗（缺失时不报错，只是"静默错乱"，最难查）

| # | 坑 | 症状 | 根因 | 对策 |
| --- | --- | --- | --- | --- |
| 28 | **进战斗一个人都没有**（连主角都不出现） | 场景切了、BGM 变了，但战场空白、无 HUD、无法操作；日志只有 `目标技能展现配置不存在, 技能名:[xxx]` + `NullReferenceException at BattleRole.SwitchSkillTo` | `SkillConfig.DisplayFileName`（留空则用技能名）找不到同名 `Skills/<名字>.asset` → `skill.GetDisplay()` 返回 null → `display.weaponCode` 抛 NRE；异常发生在 `BattleLoader.InitBattle` 协程里，协程当场中断，`roles.Add()` 和 `BattleManager.StartBattle()` 都没执行 | `python tools/shendiao/gen_skill_displays.py --mod <id> --apply`；`jyx2mod.py check` 已内置这项校验 |
| 29 | NPC/敌人**随机变成别人** | 没有任何显眼报错，只是"站在那的人不对" | 人物表 `ModelFileKey`（留空则用角色名）找不到同名 `Models/*.asset` → `ModelAsset.Get` 返回 null → 调用方退化成随机模型 | `python tools/shendiao/gen_model_assets.py --mod <id> --apply`；`jyx2mod.py check` 已内置这项校验 |

#### 场景与交互

| # | 坑 | 症状 | 根因 | 对策 |
| --- | --- | --- | --- | --- |
| 6 | 触发器高度写错 | "按交互没反应""走进去不触发"，全静默 | 触发器 y=5.61 而玩家 5.0，盒子 `[5.11,6.11]` 罩不住 | 触发器 y = 地面 + 0.5 |
| 7 | NPC 站在那但不能对话 | 连高亮都不出 | NPC 与触发器坐标不重合 → `bounds.Contains` false | `set_npc.py` 直接抄触发器 x/z |
| 8 | 走不到地图边缘回不了大地图 | 前方像有堵墙 | `Leave` 的 BoxCollider `m_IsTrigger: 0`（3×4.5m 实心墙） | 改 `m_IsTrigger: 1` |
| 9 | **空气墙** | 对话后走不进宫，像被无形墙顶住 | `NavMeshObstacle.m_Carve = 1` 在 Play 模式挖穿 NavMesh；Edit 模式探针看起来完全连通 | `m_Carve = 0`；用 `list_colliders.py --solid-only` 按世界尺寸查 |
| 10 | 人物"看得见但走不动" | NavMesh 明明烘好了 | 旧存档 `WorldMapSaveData.areaMask = 0` | 改场景/`Player.prefab` 后一律**新存档**验证 |
| 11 | 换 prefab 后角色掉到 (0,0,0) | — | `m_Modifications` 的 `target.fileID` 没重映射 | `fix_player.py`；或换回同结构 prefab |
| 12 | 改一个场景，另一张图也变了 | — | 改到了共享 prefab（`QuanzhenDizi 1.prefab` 有 133 个实例） | 只改场景内 prefab instance 的 override |
| 13 | **NPC"坐在半空中"** | 郭靖/黄蓉悬空盘坐，走到哪张图都这样，尤其出戏 | 场景实例的 `m_Modifications` 把 `Animator.m_Controller` 覆盖成了 `sit_on_chair.controller`，而场景里并没有给他俩摆椅子。注意 `LevelMaster` 只给 `controller == null` 的 `Level/NPC/*` 兜底赋值，兜底值是 `jyx2humanoidController`（默认态 `战斗待机`，半蹲，看着也像"坐"） | `_dump_instance.py <scene> <instanceID>` 看覆盖项；把 controller 换成角色自己的 `XxxController.controller`（默认态是 `站立` = `StandNormal@Idle`）。`_fix_sitting_npc.py` 可全场景批量修 |
| 14 | **门/路口"走不过去"** | 门就在眼前，点地面角色不动；`list_colliders.py --solid-only` 却一片干净 | `NavMeshObstacle.m_Carve: 1` 在运行时把门下的 NavMesh 挖掉（不是 Collider，所以 collider 工具查不到）。古墓 4 扇门全中 | `_nav_carve.py <scene> --carve-off --apply`；改的是场景里独立组件（`m_PrefabInstance: {fileID: 0}`）才有效 |
| 15 | **从子地图出来落在大地图原点/远处** | "桃花岛太远了""终南山也远" | `MapTeleportor.TransportTriggerName` 为空时，落点 = `curMap.Name` 去大地图 `Level/Triggers` 找同名节点，找不到就落默认点 | 给离场 `Leave` 的 `TransportTriggerName` 填目标节点名（`_set_transport.py`），出图即到门口 |

#### 剧情与事件

| # | 坑 | 症状 | 根因 | 对策 |
| --- | --- | --- | --- | --- |
| 13 | 剧本永远不执行 | 日志 `找不到文件 [ka455]` | `LuaFilePatten` 是 `ka{0}` 而文件叫 `455.lua` | 确认 `ModSetting.LuaFilePatten = {0}` |
| 14 | **全场景交互点哑掉** | 点谁都没反应，日志 `错误：在一个事件执行完毕以前不能执行新的事件` | 上一个事件没走到 `OnFinishEvent`（见 §5.2 三因） | 已加三处兜底；`check_story.py` 预检；切场景清栈 |
| 15 | `Talk` 用了不存在的人物 Id | 一对话就崩，之后全图哑 | `ChatUIPanel` 空引用 | `check_story.py` 必跑 |
| 16 | 对话说"让到一边"，人没动 | — | `FixWithGameRuntime` 挂在 `Triggers/1` 上，移动的是触发器 | 挂到 NPC 自己身上 |
| 17 | `jyx2_FixMapObject("x", 1)` 不生效 | Flag 写了但位置没变 | 传 number → 变 `"1.0"`，`=="1"` 判定 false | 传字符串 `"1"` |
| 18 | 两个组件同名 Flag | 落点随机（取决于执行顺序） | 场景里有重复 `FixWithGameRuntime` | `grep` 后去重 |
| 19 | 事件永久锁死（引用断裂） | 某场景事件全哑 | 删了 `0/3/4/10.lua` 但 `00_mochuanlinju`/`01_moqiaoshanzhuang` 还引用 | `check_story.py` **不查**这个，要自己扫场景引用 |
| 20 | 空脚本报错 | — | 空文件走空协程 | 空脚本写 `do return end;` |
| 21 | Editor 里跑剧本报异常、打包后不报 | 行为不一致 | `LuaManager.LoadLua` 在 Editor 下是 `File.ReadAllBytes(...)`（文件缺失直接抛异常），运行时走 `_luaMapper` 返回 null | 写脚本别依赖"文件存在"；Editor 里改完 Lua 确保文件真的落盘 |
| 28 | **孤儿脚本**：剧情写了但从不执行 | 玩家按提示去某处找 NPC，人根本不在（实例：`10.lua` 写"先与郭靖说话"，重阳宫场景里没有郭靖） | 文件名 = EventId，但场景里没有任何 `GameEvent` 指向这个 Id | 写剧情前先 `inspect_events.py` 列场景事件；`fill_missing_story.py` 反向核对"场景事件 ↔ Lua 文件"是否一一对应 |
| 29 | `gen_story.py` 把**手写剧情**清空重写 | 改好的剧本一夜回到解放前 | 它先 `clear_old_lua()` 删光 `Lua/*.lua`，再按 `STORY` 字典（早期草稿）重写 | 已改为默认跳过内容不同的已存在脚本，`--force` 才全量重建 |
| 30 | `add_scene_npc.py` 报"模板场景里找不到 guid" | 加不了 NPC | 它从**模板场景**里拷现成的 `PrefabInstance`，模板里没有该 prefab 的实例就无从下手 | 换一个有该实例的场景当模板；另注意 `Laotaitai.prefab` 这类实例没有 stripped `GameObject` 块，拿不到 fileID，**不能**作为 `m_EventTargets` 的目标 |
| 31 | **剧情说"习得×功"，武功列表里没有** | 学完打开技能面板是空的，战斗里也用不出来 | 只在 Lua 里写了 `SetFlagInt("蛤蟆功", 1)`——Flag 只控制剧情分支，**不会真的学武功** | 还要调 `LearnMagic2(roleId, skillId, noDisplay)`（`role.LearnMagic` 才进武功列表）；`skillId` 取 `SkillConfig` 的 Id，`noDisplay=1` 才弹"习得武学"提示。`check_story.py` 会校验技能 Id 存在 |
| 32 | 想在对话里**标红重点** | — | 聊天文本是 uGUI `Text`（支持富文本），但 `ChatUIPanel.ShowText` 在超过 `GameConst.MAX_CHAT_CHART_NUM = 156` 时会按标点**切段显示**，`<color>` 标签被切断就变成乱码 | 每句控制在 156 字符以内；写法 `<color=#FF0000>重点</color>`。`Talk` 的 roleId 同时决定头像图（`Assets/BuildSource/head/<roleId>.png`）和名字，不是表里的 `Pic` 字段 |
| 33 | **用弹框讲"下一步去哪"很出戏** | 对话正入戏，突然一个系统弹框："往桃花岛走" | `ShowMessage` 是纯提示框，没有角色语气 | 换成 `Talk(0, "（...）")` 内心独白，重点处加红色；只保留"得到物品""学会武功"这类纯反馈用 `ShowMessage` |

#### 配置表与工具链

| # | 坑 | 症状 | 根因 | 对策 |
| --- | --- | --- | --- | --- |
| 22 | 改完 xlsx，Unity 生成配置表全是空字符串 | 名字全空 | 老版 ExcelDataReader 只认 sharedStrings | 用 xlsxwriter 重写（`apply_configs.py` 已处理） |
| 23 | 两张表同名互相覆盖 | — | B1 表名重复 | `check` 会报 |
| 24 | 游戏里看不到 MOD | — | `ModId` 与目录名不一致 / 缺 `<id>.xml` | `list` + `check` |
| 25 | 改地图名后回大地图被丢到原点 | — | 大地图落点靠 `Map.Name` 匹配触发器名 | 同步改 `1000_daditu` 里的 GameObject 名；`check_maplinks.py` |
| 26 | MOD 目录有 `Scripts/` 就编译失败 | — | 与工程本体同名类冲突 | 删掉 |
| 27 | 中文 Windows 下 python 输出乱码 | `锟斤拷` / `����` | stdout 默认 cp936，PowerShell 解码必花 | `$env:PYTHONIOENCODING='utf-8'` + `Start-Process -RedirectStandardOutput` 落盘再读 |

### 8.2 未来很可能会踩的（按风险排序）

| 风险 | 说明 | 预防 |
| --- | --- | --- |
| **加新场景** | 要做四件事：`.unity` 标到 `<id>_maps`、MapConfig 加一行、大地图加同名落点触发器、场景内放 `Player`+`NavMesh`+`Leave` | `check_maplinks.py` + `check_refs.py` |
| **新旧存档兼容** | 任何"玩家走到这里应该看到 X"的改动，老存档里 flag 已经写过了 | 新 flag 按 0=未做；老 flag 分支补幂等调用（见 `455.lua` 第一分支） |
| **战斗场景** | `LevelMasterBooster.m_IsBattleMap = true` 时 `Start()` 直接 return，`FixWithGameRuntime` 不会跑 | 战斗场景别依赖场景状态机 |
| **`ModArchiveVersion`** | 改了存档结构（比如 Flag 语义翻转）要升版本 | 语义变更 = 换新 Flag 名 |
| **Timeline / 蓝图事件** | `ExecuteJyx2Event` 会先试 `LoadEventGraph`，蓝图存在就不跑 Lua | 想用 Lua 就别给同一 id 配蓝图 |
| **多语言** | UI 文本走 `i18n`（`"交互".GetContent(...)`）；对话文本目前直接写死中文 | 要上多语言得改成 key |
| **`PreloadedLua` 热更** | `hotfix.lua` 在 AB 里，改了还是要重打重装；它只能改 Lua 逻辑，改不了场景 | 当"补丁层"用：`hotfix.lua` 里覆盖全局函数 |
| **`scene_api.BindEvent`** | 半成品 API，会加 `NavMeshObstacle`(Capsule 0.5)，绑在过道上就是人造空气墙 | 只在开阔处用，或手工摆触发器 |
| **战斗必崩的三件套** | 技能 display 资源、角色模型资源、战斗表引用的角色 id —— 任一缺失都不是"报错退出"，而是"战场空白 / 人物变脸" | `jyx2mod.py check`（含技能/模型齐全性）+ `check_story.py` |
| **平台差异** | Android 扫 `/storage/emulated/0/jynew/mods/`，`install` 不管 | 手动拷整个 `<id>/` 目录 |

---

## 9. 标准工作流

### 9.1 完整一轮（改了剧情/配置/场景）

```powershell
# 0. 改东西（xlsx 走 apply_configs.py，Lua 直接写，场景在 Unity 里改或用 tools/shendiao/*.py）

# 1. 配置表 -> Lua（纯 Python，秒级）
python tools/moddev/jyx2mod.py configs shendiao

# 2. 体检（前两个是门禁，后两个是清单，见下）
python tools/shendiao/check_story.py         # 剧本引用 / goto 配对    ← 必须 0 错误
python tools/shendiao/check_maplinks.py      # 地图 <-> 大地图 传送闭路  ← 必须"全部闭合"
python tools/shendiao/check_guids.py         # GUID 引用分类          ← 只看新增资源那几条
python tools/shendiao/check_refs.py          # 资源引用分类           ← 同上
python tools/moddev/jyx2mod.py check shendiao

# 3. 导出 AB（增量；改了 MOD 约 2~4 分钟）
python tools/moddev/jyx2mod.py unity shendiao

# 4. 装进游戏（秒级，不要加 --force）
python tools/moddev/jyx2mod.py install shendiao --src Export

# 5. 启动 + 跟日志
python tools/moddev/jyx2mod.py run --follow
```

游戏日志：`%USERPROFILE%\AppData\LocalLow\jynew\群侠传启动\Player.log`

> **`check_refs.py` / `check_guids.py` 的 MISSING / error 不等于错误。** 它们对整个 MOD 目录跑，
> `Timeline/*.playable`、部分场景和 `Skills/*.asset` 引用的 guid 属于工程本体资源
> （随 `base_assets` 发布，MOD 内本来就没有对应 `.meta`），shendiao 现状稳定报
> `MISSING 462` / 几十条 `[error]`，`exit 1` 是常态。判断标准是：
> **里面有没有你自己新增的模型 / prefab / 贴图** —— 那才是会变成隐形的东西。
> 这两个脚本的定位是**清单**，不是门禁；门禁只有 `check_story`（0 错误）和 `check_maplinks`（全部闭合）。

### 9.2 改什么要做什么（省时间用）

| 改动 | 重打 `<id>_mod` | 重打 `<id>_maps` | 重编 player | 重装 |
| --- | --- | --- | --- | --- |
| `Lua/*.lua` | ✅ | | | ✅ |
| `Configs/*.xlsx` → `configs` | ✅ | | | ✅ |
| `ModSetting.asset` | ✅ | | | ✅ |
| `.unity` 场景 | ✅ | ✅ | | ✅ |
| `Models/` `Prefabs/` 打标后 | ✅ | | | ✅ |
| 工程本体 C# / `Assets/Prefabs` | | | ✅ | |

`unity` 命令会自动判断该打哪些，改了场景就会连 maps 一起重打。

### 9.3 重编 player（只有改 C# 才需要）

```powershell
$env:BUILD_PATH = 'C:\Games\jynew\Build\'      # 不给会弹 SaveFolderPanel，batchmode 下卡死
& "C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe" -batchmode -quit `
  -projectPath C:\Games\jynew\jyx2 `
  -executeMethod Jyx2Editor.BuildTool.Jyx2BuildTool.BuildForWindows `
  -logFile C:\Games\jynew\Logs\build_player.log
```

**不要动 Steam 安装目录**，产物留在 `Build/`。

---

## 10. 工具清单

### 10.1 `tools/moddev/`（通用，任何 MOD 都能用）

| 命令 | 作用 |
| --- | --- |
| `jyx2mod.py new <id>` | 从模板复制新 MOD，换 GUID / AB 名 / ModSetting |
| `jyx2mod.py configs <id>` | xlsx → `Configs/Lua/*Config.lua` |
| `jyx2mod.py check <id>` | 体检：ModSetting、AB 标记、配置表、Lua 语法 |
| `jyx2mod.py unity <id>` | batchmode 导出 AB + xml（`--force` 全量、`--with-base` 只重打 base） |
| `jyx2mod.py install <id> --src Export` | 装到 `<游戏>/wuxia_launch_Data/mods/<id>/` |
| `jyx2mod.py list` / `logs -f` / `run --follow` | 列 MOD / 看日志 / 启动 |
| `selftest.py` | 改 `excel2lua.py` 后必跑（要求 3 个内置 MOD 0 错误） |

### 10.2 `tools/shendiao/`（shendiao 专用，思路可复用）

| 脚本 | 用途 |
| --- | --- |
| `check_story.py` | 剧本引用校验（人物/物品/武功/战斗 Id、goto 配对） |
| `check_maplinks.py` | MapConfig ↔ 场景 `Leave` ↔ 大地图落点 闭路 |
| `check_refs.py` / `check_guids.py` | 引用分类清单（**不是"0 错误才算过"**）：输出里混着大量指向工程本体资源的正常引用，只看你**自己新增/改名**的那几个 |
| `check_scene_ab.py` | 场景资源是否都标了 AB |
| **`list_colliders.py`** | **按世界尺寸列 Collider**。`--scene <x.unity>` **必填**，另支持 `--near X,Z` 排序、`--solid-only` 只看实体 —— 查空气墙神器 |
| **`add_letway_npc.py`** | 给鹿清笃装配"让路"（锚点 + `FixWithGameRuntime` + 校验），幂等；`--dry-run` 预览。场景路径硬编码为 `19_chongyanggong` |
| `set_npc.py` / `add_scene_npc.py` | 按 LAYOUT 重建场景 NPC（坐标自动对齐触发器） |
| `add_model.py` / `fix_char_models.py` | 建 `Models/<名>.asset` 指向 BuildSource 官方预设 / 落表公式 |
| `fix_player.py` / `verify_player_refs.py` | 换 Player prefab 并重映射 `m_Modifications` |
| `apply_configs.py` / `gen_story.py` | 声明式改配置表 / 批量生成剧情脚本 |
| `inspect_*.py` | 场景树、节点、坐标、事件、大地图、世界地图 探针 |
| `move_prefab_instance.py` / `remove_scene_node.py` / `patch_scene_events.py` | 场景编辑小工具 |
| `daditu_*.py` / `leave_info.py` / `cmp_daditu.py` | 大地图节点与落点核对 |

### 10.3 `jyx2/Assets/Editor/ShendiaoNavProbe.cs`

```powershell
& "...\Unity.exe" -batchmode -quit -projectPath C:\Games\jynew\jyx2 `
  -executeMethod ShendiaoNavProbe.VerifyLetway -logFile C:\Games\jynew\Logs\verify.log
```

| 方法 | 输出 |
| --- | --- |
| `Probe` | NavMesh 三角化顶点数 / 关键点 `SamplePosition` / 双向 `CalculatePath` |
| `VerifyLetway` | NPC 组件、`NavMeshObstacle.carve`、`FixWithGameRuntime` 的 Flag 与实际落点 |

**重要**：这两个都在 **Edit 模式**跑，`carving` 不生效 —— 探针报"完全连通"**不代表 Play 模式能走**。
怀疑空气墙时，先看 `carve` 字段，再用 `list_colliders.py` 量世界尺寸。

### 10.4 出 player（验证 C# 改动 / 启用调试面板）

`jyx2mod.py` **没有**打包 player 的子命令，要直接调 Unity：

```powershell
$env:BUILD_PATH = 'C:\Games\jynew\Build\'      # 必须带尾部反斜杠
& "C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe" `
  -batchmode -quit -projectPath C:\Games\jynew\jyx2 `
  -executeMethod Jyx2Editor.BuildTool.Jyx2BuildTool.BuildForWindows `
  -logFile C:\Games\jynew\_build.log
```

实测（Mono 后端 + 全量 AB）：约 **15 分钟**，产物 2.4 GB 落在 `Build/`。

| 坑 | 表现 / 处理 |
| --- | --- |
| 类名写错 | `executeMethod class 'BuildTool' could not be found`。完整名是 **`Jyx2Editor.BuildTool.Jyx2BuildTool`**（`jyx2mod.py unity` 用的是 `...Jyx2ModCli.BuildMod`） |
| 没设 `BUILD_PATH` | `EditorUtility.SaveFolderPanel` 在 batchmode 下弹模态框 → 永久挂住 |
| 副作用① | 全量重打 AB 到 `Assets/StreamingAssets`（1.6 GB / 46 文件）。已加进 `jyx2/.gitignore`，别提交 |
| 副作用② | `bundleVersion` 被改成当天日期、`m_ShowUnitySplashScreen` 被打开 → 打完 `git checkout -- jyx2/ProjectSettings/ProjectSettings.asset` |
| 副作用③ | `Assets/XLua/Gen` 重新生成（已 ignore，无害）；顺带会**修掉重复 guid** 的 `.meta`（本次修好 `shendiao/Lua/10.lua.meta`） |
| 包缺 MOD 清单 | 运行时报 `GameModNative相关文件丢失 ... native_mods.txt` → 从 Steam 版 `wuxia_launch_Data/StreamingAssets/` 拷 `native_mods.txt` + `*.xml` 过来 |
| 装 MOD 到自建包 | `jyx2mod.py install` 只认 `wuxia_launch.exe`，自建包叫 `群侠传启动.exe` → 手动把 `Export/<mod>` 拷到 `<exe>_Data/mods/<mod>/` |
| TMP 材质 NRE | 进游戏后大量 `TMP_SubMeshUI.UpdateMaterial` NRE（TMP 材质没进 AB），MOD 选择界面阶段不出现 |

### 10.5 `tools/storyeditor/`（Web 剧情编辑器，2026-10 新增）

把 `Lua/*.lua` 解析成节点图，在浏览器里看/改对白，改完立刻做语法自检。
**只用 Python 标准库**，前端原生 JS + SVG，零 npm。

```powershell
python tools/storyeditor/serve.py            # http://127.0.0.1:8777
cd tools/storyeditor; docker compose up -d --build   # 或用 Docker（仓库挂到 /repo）
python tools/storyeditor/selftest_story.py   # 改了解析/回写逻辑必跑
```

- 解析器只覆盖剧本的既有写法（if/goto/label/Talk/动作调用）；出现 `while`/`for`/局部函数先跑
  `survey_lua.py` 看要不要补
- 回写是**行级替换**：保留缩进/分号/尾注释/CRLF；带乐观锁（原文对不上返回 409）、改前备份、
  改后 `lint_lua` 自检；人物 Id 不存在直接拒绝
- **每条剧情会标出「在哪张图、怎么触发」**：解析 `Maps/GameMaps/*.unity` 里挂
  `GameEvent`（guid `28456c42…`）的 `Level/Triggers/N` 对象，取
  `m_InteractiveEventId`（走近按交互）/ `m_EnterEventId`（踩点自动跑）/
  `m_UseItemEventId`（使用物品、宝箱），再加上 `CharacterConfig.LeaveStoryId`（侠客离队剧情）；
  场景名按 `MapConfig.MapScene` 翻成中文地图名
- 顺手能看出两类隐患：① 场景没在 `MapConfig` 登记（玩家根本进不去，shendiao 有 20/34 张这样）；
  ② 脚本没有任何入口（地图里没挂，也不是离队剧情）
- 它**只改源文件**，游戏里生效仍要 `jyx2mod.py unity` + `install`（Lua 在 `<id>_mod` 里）
- 详细说明与后续路线见 `tools/storyeditor/README.md`

---

## 11. 排查决策树

### "交互点点了没反应"

```
1. 日志有 "找不到文件 [...]"      → LuaFilePatten / 文件名
2. 日志有 "lua执行错误"           → check_story.py + Lua 语法
3. 日志有 "在一个事件执行完毕以前" → 前一个事件卡死了 → 切场景 / 查 §5.2
4. 什么都不打印                   → 触发器问题：
   a. NPC 是否站在触发器盒子里（x/z 一致？y 罩得住？）
   b. Collider 是 isTrigger 还是实体墙
   c. Level/Triggers/<名> 是否与 m_InteractiveEventId 一致
   d. m_EventTargets 是否非空（空的话不弹面板）
```

### "东西不见了 / 角色是空气"

```
1. check_refs.py / check_guids.py      → MISSING 里有没有你新增的资源（工程本体的引用属正常）
2. 模型是否指向 Assets/BuildSource/**  → 自建 ModelsResource 不进包
3. 资源有没有标 AB                      → check_scene_ab.py
4. 打开 Export/<id>/<id>_mod 搜网格名   → 搜不到就是没进包
```

### "走不过去 / 空气墙"

```
1. 换新存档复现（旧档 areaMask 可能为 0）
2. list_colliders.py --scene <场景.unity> --near X,Z --solid-only → 谁的世界尺寸盖住了通道
3. 看 NavMeshObstacle.m_Carve                 → 站在通道上的必须先改 0
4. 场景是否有烘焙好的 NavMesh（Maps/GameMaps/<scene>/NavMesh.asset）
```

### "改了没生效"

```
1. 是不是只改了 xlsx 没跑 configs？
2. 是不是没重打 AB / 没重装？（对比 Export/<id>/<id>_mod 的 mtime 与源文件）
3. 改的是 C# 吗？（那就得重编 player）
4. 旧存档的 flag 已经写死了？（加新 flag 或补幂等分支）
```

---

## 12. 一句话总结

> JYX2 MOD 的难点不在"写逻辑"，而在**三层数据的一致性与生效时机**：
> 配置表要重生成、剧本要进包、场景要重打 maps，
> 而玩家的存档会把这些棍子插在半路上。
> 每改一处，先问三个问题：
> **这个改动是"立刻生效"，还是"下次进场景生效"，还是"必须新存档才生效"？**
