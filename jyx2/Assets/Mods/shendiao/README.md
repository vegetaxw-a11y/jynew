# 神雕侠侣 MOD

基于《金庸群侠传3D重制版》的**同人剧情 MOD**：主角杨过，线性主线 + 开放大地图。
以 `SAMPLE`（渡城残魂传）为底，复用其场景、模型、音乐等美术资源，重写配置表与全部剧情脚本。

- ModId：`shendiao`
- 目录：`jyx2/Assets/Mods/shendiao`
- 主角：杨过（人物 Id 0）

## 章节进度

| 章节 | 内容 | 状态 |
| --- | --- | --- |
| 序章 | 嘉兴·铁枪庙：孤儿杨过、郭靖到访 | ✅ 已实现 |
| 第一章 | 终南山·重阳宫：拜师赵志敬、受欺、孙婆婆赠药 | ✅ 已实现 |
| 第一章 | 终南山·活死人墓：小龙女、李莫愁、孙婆婆之死、玉女心经 | ✅ 已实现 |
| 第二章 | 大胜关英雄会 | ⬜ 待开发 |
| 第三章 | 绝情谷（情花、公孙止） | ⬜ 待开发 |
| 第四章 | 襄阳·断臂与玄铁重剑 | ⬜ 待开发 |
| 第五章 | 重阳宫大战、十六年之约 | ⬜ 待开发 |
| 第六章 | 十六年后·神雕侠 | ⬜ 待开发 |

**当前可玩范围**：嘉兴·铁枪庙 → 终南山·重阳宫 → 终南山·活死人墓（第一章完）。

## 世界地图

大地图 `1000_daditu` 上的地名已改为神雕侠侣的地理，除下列三处外，其余地点进
入后会提示「此地尚未探明」，留给后续章节：

| Map Id | 场景文件 | 新地名 | 状态 |
| --- | --- | --- | --- |
| 0 | 00_mochuanlinju | 嘉兴·铁枪庙 | ✅ 序章 |
| 1 | 01_moqiaoshanzhuang | 终南山·重阳宫 | ✅ 第一章 |
| 2 | 02_wanzhushuyuan | 终南山·活死人墓 | ✅ 第一章 |
| 3 | 03_chaensi | 陆家庄 | ⬜ |
| 4 | 04_zhongmingge | 襄阳城 | ⬜ |
| 5 | 05_yilinlou | 临安·醉仙楼 | ⬜ |
| 6 | 06_jiangjunfu | 襄阳·安抚使府 | ⬜ |
| 7 | 07_yingsugu | 绝情谷 | ⬜ |
| 8 | 08_gezilou | 风陵渡 | ⬜ |
| 9 | 09_niutouling | 华山之巅 | ⬜ |
| 10 | 10_binhumaolu | 桃花岛 | ⬜ |
| 11 | 11_shuiguotan | 大胜关 | ⬜ |
| 12 | 12_suixiantang | 终南山·后山 | ⬜ |
| 13 | 13_yelanggu | 万兽山庄 | ⬜ |
| 14 | 14_yelangdong | 黑沼 | ⬜ |
| 15 | 15_gezilongtai | 断肠崖 | ⬜ |
| 16 | 16_heixionggu | 蒙古大营 | ⬜ |
| 17 | 17_luojibinghang | 牛家村 | ⬜ |
| 18 | 18_wumingku | 独孤剑冢 | ⬜ |
| 19 | 19_wujifang | 重阳宫·藏经阁 | ⬜ |

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
python tools/shendiao/gen_story.py         # 重排事件 Id、写剧情脚本、给未开发事件写占位

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
- `tools/shendiao/gen_story.py`：`STORY` 字典里按事件 Id 写剧情；没写的事件自动生成「尚未探明」占位。
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
8. 孙婆婆 → 小龙女（初见）→ 李莫愁（孙婆婆之死）→ 小龙女收留（学「全真剑法」）→ 寒玉床 → 李莫愁战斗（可胜可败）→ 玉女心经（学会「玉女剑法」「玉女素心剑」，**第一章完**）。

## 已知限制

- 场景地形、建筑、NPC 外观沿用模板资源，只有地名/人名/剧情是神雕的；头像亦未替换。
- 女性模型只有模板自带的三个，部分女角色共用同一模型。
- 2 号之后的地点是占位内容（提示「此地尚未探明」），留给后续章节填充。
- MOD 目录下不能放 `Scripts/`：会和工程里 `SAMPLE/Scripts` 的同名类冲突导致 Unity 编译失败。
