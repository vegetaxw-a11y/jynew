# 神雕侠侣 MOD

基于《金庸群侠传3D重制版》的**同人剧情 MOD**：主角杨过，线性主线 + 开放大地图。
以 `SAMPLE`（渡城残魂传）为底，复用其场景、模型、音乐等美术资源，重写配置表与全部剧情脚本。

- ModId：`shendiao`
- 目录：`jyx2/Assets/Mods/shendiao`
- 主角：杨过（人物 Id 0）

## 章节进度

| 章节 | 内容 | 状态 |
| --- | --- | --- |
| 序章 | 嘉兴·铁枪庙：孤儿杨过、老庙祝、郭靖黄蓉上香认亲 | ✅ 已实现 |
| 第一章 | 桃花岛：黄蓉只教读书、郭芙与武氏兄弟欺凌、欧阳锋传蛤蟆功、柯镇恶逐客 | ✅ 已实现 |
| 第一章 | 终南山·重阳宫：鹿清笃守门、郭靖托付丘处机、赵志敬收徒、全真门下受欺 | ✅ 已实现 |
| 第一章 | 活死人墓：孙婆婆护杨过而死、小龙女收徒、寒玉床、斗李莫愁、玉女心经 | ✅ 已实现 |
| 第二章 | 神雕山洞：断臂入洞、神雕试剑、剑冢三剑、玄铁重剑 | ✅ 已实现 |
| 第三章 | 绝情谷：情花、公孙止、樊一翁、裘千尺 | ⬜ 待开发 |
| 第四章 | 南国旧友：程英居、铁掌山、黑龙潭、一灯居、百花谷 | ⬜ 待开发 |
| 第五章 | 华山绝顶：洪七公与欧阳锋、思过崖 | ⬜ 待开发 |
| 第六章 | 绝情谷底：十六年之约、谷底重逢 | ⬜ 待开发 |

> MOD 可进入的地图只有 14 张（见「世界地图」），**没有「大胜关」「襄阳」**，
> 原著这两段（英雄会、断臂于襄阳城外）用旁白带过；章节顺序按现有地图重排。

**当前可玩范围（原著第二~四回）**：
破庙（嘉兴·铁枪庙）→ 桃花岛 → 重阳宫 → 古墓（活死人墓）（第一章完）。

### 第一章剧情锚点（Lua → 场景 → 原著）

| 场景 | EventId | 剧情 | 原著 |
| --- | --- | --- | --- |
| `62_pomiao` | 557 | 进庙独白（铁枪庙、破窑） | 第二回·故人之子 |
| `62_pomiao` | 559 | 老庙祝讲杨康旧事，指往佛堂 | 第二回（原创衔接） |
| `62_pomiao` | 558 | 供桌取【铁枪残片】 | 第二回（原创道具） |
| `62_pomiao` | 1001 | 郭靖认亲：「你爹可是叫杨康？」 | 第二回 |
| `62_pomiao` | 1002 | 黄蓉试探：「我怕你学得太快」 | 第二回 |
| `75_taohuadao` | 465 | 登岛 | 第二回末 |
| `75_taohuadao` | 466 | 黄蓉只教读书；事后郭靖言明送终南山的缘由 | 第二回末 / 第三回首 |
| `75_taohuadao` | 923 | 欧阳锋收义子、传蛤蟆功 | 第二回 |
| `75_taohuadao` | 922 | 郭芙与武敦儒欺凌，杨过以蛤蟆功反击 | 第二回 |
| `19_chongyanggong` | 900 | 山门外郭靖交代；事毕辞别「别学你爹」 | 第三回·求师终南 |
| `19_chongyanggong` | 455 | 鹿清笃拦门，郭靖出面，弟子让路 | 第三回 |
| `19_chongyanggong` | 457 | 丘处机认出郭靖，郭靖托孤 | 第三回 |
| `19_chongyanggong` | 901 | 赵志敬收徒，只教口诀不教招式，借故责罚 | 第四回·全真门下 |
| `19_chongyanggong` | 456 | 师兄弟讥讽「你爹是个认贼作父的」 | 第四回 |
| `18_gumu` | 902 | 孙婆婆护杨过、被全真掌力所伤、小龙女收徒 | 第四回 |
| `18_gumu` | 442 | 寒玉床 | 第五回·玉女心经 |
| `18_gumu` | 217 | 李莫愁闯墓，孙婆婆之死的余波（斗李莫愁） | 第五回 |
| `18_gumu` | 219 | 石棺侧壁刻玉女心经，学会「玉女剑法」「玉女素心剑」，**第一章完** | 第五回 |
| `07_shandong` | 389 | 断臂后逃入山洞（进入触发） | 第二十五回·内伤 |
| `07_shandong` | 390 | 洞中爪印（原创衔接，指向洞底） | 原创 |
| `07_shandong` | 837 | 神雕衔木剑逼杨过拆招（斗神雕） | 第二十五回 |
| `07_shandong` | 838 | 洞底白骨遗刻「仰慕剑魔遗风」 | 原创 |
| `07_shandong` | 836 | 剑冢石壁「剑魔独孤求败…埋剑于斯」，得【玄铁重剑】、学「玄铁剑法」 | 第二十六回·神雕重剑 |
| `07_shandong` | 394 | 练重剑有成，**第二章完** | 第二十六回 |

> 战斗：`922` → 战斗 **202**（斗武氏兄弟）、`901` → **201**（斗赵志敬）、
> `902` → **200**（斗鹿清笃，孙婆婆当队友）、`217` → **203**（斗李莫愁）、
> `837` → **206**（斗神雕）。另有 204 斗欧阳锋 / 205 斗全真群道 备用。
> 全部是「赢了多加经验、输了照常推进」—— 原著这几仗本来就是挨打。
>
> 剧情 flag 链：`序章完成 → 桃花岛学艺 → 蛤蟆功 → 郭芙欺凌 → 离岛赴终南 →
> 入全真 → 拜入全真 → 赵志敬收徒 → 赵志敬为难 → 决意出走 → 孙婆婆相救 →
> 击退李莫愁 → 玉女心经 → 第一章完成 → 入神雕洞 → 洞中爪印 → 神雕试剑 →
> 白骨遗刻 → 得玄铁重剑 → 第二章完成`。
> 每个脚本都用 `GetFlagInt` 自查前置条件，跳场景也不会卡死。


## 世界地图

大地图 `1000_daditu` 上的地名已改为神雕侠侣的地理。**以 `Configs/Lua/MapConfig.lua` 为准**，
当前实际生效的是下列 14 个地点：

| Map Id | 场景文件 | 地名 | 备注 |
| --- | --- | --- | --- |
| 0 | `62_pomiao` | 破庙 | 序章，`Tags=START:0` 出生点 |
| 1 | `19_chongyanggong` | 重阳宫 | 第一章 |
| 2 | `18_gumu` | 古墓 | 第一章，`Tags=POINTLIGHT` |
| 3 | `07_shandong` | 神雕山洞 | `Tags=POINTLIGHT` |
| 4 | `22_jueqinggu` | 绝情谷 | |
| 5 | `80_jueqinggudi` | 绝情谷底 | |
| 6 | `20_baihuagu` | 百花谷 | |
| 7 | `57_huashanpai` | 华山派 | |
| 8 | `81_siguoya` | 思过崖 | |
| 9 | `48_tiezhangshan` | 铁掌山 | |
| 10 | `21_heilongtan` | 黑龙潭 | `Tags=NONAVAGENT`，大地图不出导航 |
| 11 | `47_yidengju` | 一灯居 | |
| 12 | `45_chengyingju` | 程英居 | |
| 13 | `75_taohuadao` | 桃花岛 | |
| 1000 | `1000_daditu` | 大地图 | `Tags=WORLDMAP`，`TransportToMap=-1` |

> `100–164` 是**占位行**：`MapScene` 一律指向 `62_pomiao`，`Name` 带「〔未开放〕」后缀，
> `EnterCondition=1`。注意 **`EnterCondition` 目前在引擎里没有任何读取点**
> （`GameRuntimeData.GetSceneEntraceCondition` 只有定义、无调用），`1` 纯属人工标记，
> 真正让它"进不去"的是大地图上对应触发器的目标场景。

## 目录结构

```
Configs/            配置表（Excel，改这里） + Lua/（生成物，勿手改）
Lua/<eventId>.lua   剧情脚本，事件 Id 与场景 Level/Triggers 下的触发器一一对应
Maps/GameMaps/      场景（.unity），大地图入口靠 GameObject 名字匹配 Map.Name
Models/             角色模型资源（Models/<角色名>.asset，m_View 指向官方人物预设）
Prefabs/            地图角色 prefab（模板遗留，场景里已改用 BuildSource 官方预设）
Skills/             武功资源
Terrain/ Timeline/ Skybox/ ...  美术资源（沿用模板）
```

## 开发流程

```bash
# 1. 改配置表 / 剧情（推荐走脚本，见下）
python tools/shendiao/apply_configs.py     # 地图/人物/武功/物品改名 + 大地图 GameObject 同步改名
python tools/shendiao/gen_story.py         # 重排事件 Id + 补缺失占位（默认**不覆盖**已有脚本，--force 才按 STORY 重建）
python tools/shendiao/fill_missing_story.py --apply   # 只补「场景挂了事件、Lua 目录没脚本」的空洞

# 1.5 角色模型（角色名 -> BuildSource 里的官方人物预设，一人一个，不共用）
python tools/shendiao/add_model.py 杨过 BattleNpc/Yangguo        # 生成 Models/杨过.asset
python tools/shendiao/fix_char_models.py                          # 把人物表的 =D{row} 公式落成模型名 + 校验模型存在
python tools/shendiao/set_npc.py --dry                            # 查看地图 NPC 布置（角色/模型/坐标/朝向）
python tools/shendiao/set_npc.py --apply                          # 重建场景里的 NPC 实例

# 2. 导出 Excel -> Lua 并体检
python tools/moddev/jyx2mod.py configs shendiao
python tools/shendiao/check_story.py       # 剧情脚本引用校验（人物/物品/武功/战斗 Id、goto 配对）
python tools/shendiao/check_guids.py       # 资源引用校验（模型/NPC 隐形就是这里断了）
python tools/moddev/jyx2mod.py check shendiao

# 3. 导出 AssetBundle（首次/工程本体资源变动时才需要 base，慢约 10 分钟）
python tools/moddev/jyx2mod.py unity shendiao --output Export --no-base

# 4. 安装到游戏
python tools/moddev/jyx2mod.py install shendiao --src Export

# 5. 直接启动游戏测试（可选）
python tools/moddev/jyx2mod.py run --follow
```

- `tools/shendiao/apply_configs.py`：声明式表，改地图名/角色名/武功名/物品名只改字典即可。
- `tools/shendiao/add_model.py`：给角色建 `Models/<角色名>.asset`，模型直接引用
  `Assets/BuildSource/ModelCharacters/{BattleNpc,StoryNpc}/<预设>.prefab`（随游戏本体发布，
  JYX2 官方 MOD 也是这样引用的）。模板自带的 `Prefabs/*.prefab` 都是路人外形，不要拿来演主角。
- `tools/shendiao/set_npc.py`：`LAYOUT` 里按「场景 -> [(角色名, 模型, 坐标, 朝向)]」重建地图 NPC。
  重建时会清掉场景里旧的 `PrefabInstance` + stripped Transform，并把新实例的所有 GameObject
  统一到一个可见层（Layer 16），再重建 `Level/NPC` 的 `m_Children`。
  **坐标必须等于地面高度，且必须与 `Level/Triggers` 里对应触发器的 x/z 重合**（见下）。
- `tools/shendiao/fix_player.py`：把 MOD 的 `Prefabs/Player.prefab` 换成官方
  `Assets/Prefabs/Player.prefab`（内嵌 `BuildSource/ModelCharacters/Player/Zhujue.prefab`），
  同时把三张场景里 Player 实例 `m_Modifications` 的 target fileID 重映射到新 prefab。
- `tools/shendiao/check_refs.py`：体检 MOD 内所有资源引用，区分
  SELF / BUILD / GLOBAL / **OTHERMOD** / **MISSING**，导出前跑一次。
- `tools/shendiao/gen_story.py`：`STORY` 字典里按事件 Id 写剧情；没写的自动生成占位。
  **默认不覆盖已存在的脚本**（第一章起剧情是手写的，STORY 里留的是旧草稿），
  确实要按 STORY 重建时加 `--force`。
- `tools/shendiao/fill_missing_story.py`：扫场景里所有 GameEvent 的三种事件 Id，
  凡是 Lua 目录里没有对应脚本的，生成「此处暂无可叙之事」占位。缺脚本不会锁死事件系统，
  但那一个滑块点下去毫无反应，玩家会以为游戏坏了。
- `tools/shendiao/patch_scene_events.py`：批量修 GameEvent 的 layer / IsTrigger /
  EventTargets / 触发器位置 / 碰撞盒尺寸，`--set-event <物体>=<新Id>` 可直接改事件 Id。
- `tools/shendiao/audit_scene_npcs.py`：**NPC 在场性审计**。逐个场景列出 GameEvent 的
  target 判定（`OK` / `FAR` / 空），并交叉比对「Lua 里 `Talk(60,…)` 点到的人，场上到底有没有」。
  `--all --quiet` 只看有问题的场景。位置以触发器为圆心、`--near`（默认 3m）为半径算距离。
- `tools/shendiao/add_prefab.py`：**往场景里插任意 prefab 实例**，不需要模板场景里已有同款实例
  （`add_scene_npc.py` 的硬限制）。直接读 prefab 的根 GameObject/Transform fileID，手写
  `PrefabInstance` + stripped Transform + stripped GameObject 三块并挂进父节点 `m_Children`，
  末尾打印 **stripped GameObject fileID** —— 那就是 `m_EventTargets` 该填的值。默认 dry-run。
- `tools/shendiao/edit_instance.py`：改场景里 prefab 实例的显示名 / 局部坐标 / 朝向
  （写进 `m_Modifications` 覆盖）。`--list` 列出所有实例的 instanceID、名字、坐标。
- `tools/shendiao/lint_lua.py`：**剧情脚本语法体检**（工程里没有 lua/luac，`jyx2mod check`
  只查 `Configs/Lua` 的 7 个生成文件）。查块关键字配平、字符串/注释闭合、括号配平、
  代码里的全角标点、`Talk` 的人物 Id 与 `TryBattle` 的战斗 Id 是否在表里。`--battle` 开后者。
- `tools/shendiao/check_scene_fileids.py`：**场景内部 fileID 完整性**。上面几个工具都是直接改
  YAML 文本，写错一个 fileID 要等 Unity 打开才发现；这里查 `m_TransformParent` / `m_Father` /
  `m_Children` / stripped 的 `m_PrefabInstance` 是否都能解析、有没有重复 `!u!x &id`。
- `tools/moddev/_scene_scan.py`：扫描场景里的交互点/NPC/传送点，编排剧情时用来查事件 Id。

> Excel 注意：工程里的 `Excel.dll` 是老版 ExcelDataReader，只认 sharedStrings，
> 所以 xlsx 必须用 xlsxwriter 重写（`apply_configs.py` 已处理），不能直接用 openpyxl 保存。

> GUID 注意：从模板复制 MOD 时，`.meta` 换新 GUID 的同时**必须**把资源文件里对这些
> GUID 的引用一起换掉，否则模型变空气、NPC 隐形、贴图丢失，且 Unity 不报任何错。
> `jyx2mod.py new` 已修复此问题；老 MOD 用 `tools/shendiao/fix_guids.py` 补，
> 用 `tools/shendiao/check_guids.py` 体检。

## 踩过的坑（改动前务必读）

### 1. 主角"是空气"——模型资源必须在 base_assets 里

`RoleHelper.FindPlayer()` 找的是 `Level/Player`，玩家可见的模型来自
**`Level/Player` 实例所引用 prefab 内嵌的那个角色 prefab**，不是 `ModelFileKey`。

导出 AssetBundle 时，只有「显式分配了 bundle 的资源」才会进包（`manifest` 的 Assets 列表里能看到）。
`Prefabs/Taoliuyi.prefab` 依赖 `ModelsResource/陶六一/TaoLiuYi.fbx|.mat`，
而 `ModelsResource/` 没有分配任何 bundle —— 于是 prefab 进包了、mesh 没进，
`SkinnedMeshRenderer` 无网格，主角能走能触发剧情但**完全不可见**，且 Unity 不报错。

正确做法：主角 prefab 内嵌模型一律指向 `Assets/BuildSource/ModelCharacters/**`
（这些随 `base_assets` 发布，官方 JYX2 MOD 的 `08_dalunsi` 就是这么用的）。
自建 `ModelsResource/` 只在编辑器里能看，导出后必丢。
验证：`Export/shendiao/shendiao_mod` 里能搜到 `M2_P00_body`（Zhujue 的网格名）才说明 mesh 进包了。

### 2. NPC"站在那但不能对话"——位置和触发器必须重合

交互判定在 `Jyx2Player.CanSee()`：

```csharp
var isInTrigger = target.bounds.Contains(transform.position + targetDirection * _navMeshAgent.radius);
```

- `target` 是 `Level/Triggers/<事件Id>` 上的 BoxCollider（1×1×1，中心就是该物体的位置）
- 玩家的 `NavMeshAgent` 必须真正站进这个盒子，且视线 120° 内、无遮挡

所以：**把 NPC 摆到离触发器几米外的"好看位置"就等于没法对话**。
`set_npc.py` 的 `LAYOUT` 坐标应当直接抄对应触发器的 x/z。

另外 `LevelMaster.Start()` 会在运行时把 `Level/Triggers/*` 全部设为 `GameEvent` 层（Layer 28），
**不要把 NPC 自己放到 28 层** —— 也不需要给 NPC 挂 `GameEvent`，事件都挂在 `Triggers` 上。

### 3. 触发器高度写错会让所有交互静默失效

00_mochuanlinju 的触发器曾被写成 `y=5.61`，而地面/玩家在 `y=5.0`：
碰撞盒范围是 `[5.11, 6.11]`，`Contains(玩家位置)` 永远为 false，
于是"按交互没反应""走进触发区不触发剧情"，全部静默失败。

`01`/`02` 的触发器在 `y=0.5`、玩家 `y≈0.1`，盒 `[0,1]` 能覆盖玩家，所以那两张图正常。
`set_npc.py` 的 `TRIGGER_Y` 就是用来把触发器 y 拉回地面的。

### 4. 换 prefab 必须同步重映射场景的 `m_Modifications`

场景里的 `PrefabInstance` 用 `target: {fileID: 内部对象id, guid: prefab guid}` 记录位置/名字覆盖。
换成另一份 prefab 后内部 fileID 全变了，不重映射的话位置覆盖失效、主角被丢到 `(0,0,0)`。
`fix_player.py` 按文档出现顺序自动配对生成映射表。

还要注意：**不要把 override 指到 stripped（子 prefab 内部）对象上** ——
一条 `m_IsActive: 0` 命中子 prefab 的根就会把整只模型关掉，`clean_stripped_mods()` 专门清理这种情况。



1. 启动游戏 → MOD 选择界面选「神雕侠侣」→ 开局应在**嘉兴·铁枪庙**，主角名「杨过」。
2. 原地触发开场独白（序章）。
3. 与**庙祝**对话，打听到「白袍的兄弟」。
4. 打开木箱拿到银两，再与庙祝对话 → 触发**郭靖、黄蓉到访**，答应去终南山。
5. 走到地图边缘 `Leave` 点回大地图 → 前往「终南山·重阳宫」。
6. 与郭靖对话 → 与赵志敬对话（拜师）→ 与鹿清笃对话（可选择动手/忍让，有必败战）→ 与孙婆婆对话（得到提示「后山石门夜里不关」）。
7. 回大地图 → 前往「终南山·活死人墓」。
8. 孙婆婆 → 小龙女（初见）→ 李莫愁（孙婆婆之死）→ 小龙女收留（学「全真剑法」）→ 寒玉床 → 李莫愁闯墓（斗李莫愁，可胜可败）→ 石棺侧壁的玉女心经（学会「玉女剑法」「玉女素心剑」，**第一章完**）。
9. 回大地图 → 前往「终南山·神雕山洞」。
10. 进洞独白（断臂）→ 洞中爪印 → 大雕（斗神雕）→ 洞底白骨 → 剑冢石壁（得【玄铁重剑】、学「玄铁剑法」）→ 独孤求败遗蜕前练剑（**第二章完**）。

## 已知限制

- 场景地形、建筑、NPC 外观沿用模板资源，只有地名/人名/剧情是神雕的；头像亦未替换。
- 女性模型只有模板自带的三个，部分女角色共用同一模型。
- 第三章之后的地点是占位内容（提示「此地尚未探明」），留给后续章节填充。
- `03 神雕山洞` 起的新章节只用旁白 + 触发器目标（大雕、石棺、白骨）交互，没有可对话的活人 NPC。
- 旧存档里 `WorldMapSaveData.areaMask = 0` 会让 NavMesh 失效（人物看得见却走不动），改动场景后请用新存档验证。
- MOD 目录下不能放 `Scripts/`：会和工程里 `SAMPLE/Scripts` 的同名类冲突导致 Unity 编译失败。
