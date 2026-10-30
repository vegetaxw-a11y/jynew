# 神雕 MOD —— 历史会话上下文归档

> 来源：Cline 会话 `1792746945933_ab9ml`（c:\Games\jynew）
> 归档时间：2026-10-28 14:32
> 说明：该会话因上游网关连续返回兜底文案而作废，此处保留其自动压缩摘要，供新会话接手。

---

Context summary:

## Goal
Fix `shendiao` MOD so leaving 铁枪庙 (map `00`) lands the player correctly on world map `1000_daditu` with movement and camera follow — this session = user request "大地图我看下": static inspection of the world map scene and the full teleport chain.

## State
- **Done**
  - Built inspection tooling under `tools/shendiao/`:
    - `_inspect_worldmap.py` — splits `.unity` into `--- !u!` docs; reports roots, `Level` children, Player PrefabInstance overrides, camera `m_Follow`, all `Level/Triggers` children + attached scripts (guid→`.cs.meta` name map), key nodes (`CameraGroup`, `CM vcam1`, `BattleboxRoot`, `Dynamic`, `LevelMaster`, `NavMeshSurface`).
    - `_wm_inst.py` — dumps all `m_Modifications` of one PrefabInstance.
    - `_wm_prefab_root.py` — prints root Transform (pos/scale/rot) and NavMeshAgent params (`radius/height/speed/accel/baseOffset/areaMask`).
    - `_wm_trigger_fields.py` — dumps all components on a named trigger.
    - `check_maplinks.py` — parses `MapConfig.lua` rows; verifies every map's `.unity` exists, has `Level/Triggers`, each `TransportToMap` target trigger exists, and every daditu trigger maps back to a real map name (dead-trigger check). Both directions reported.
  - Fixed parser bugs: `fileID: 0` → `None`; PrefabInstance names decoded via `json` (`unquote`) for YAML `\uXXXX`; stripped Transform names resolved through `m_PrefabInstance`; emoji ❌/✔ replaced with `[X]`/`[OK]`; `sys.stdout.reconfigure(errors='replace')`.
  - **World map is structurally sound**: `Level` present, Player PrefabInstance overrides = `m_LocalPosition (124.15, 14.9, 155.13)` / `m_LocalScale (2,2,2)`, camera `m_Follow` resolves to Player, 18 triggers under `Level/Triggers`.
  - **Provenance finding**: shendiao `1000_daditu/NavMesh.asset` is **byte-identical to SAMPLE** (1.67 MB) and differs from official JYX2 (4.27 MB / ~79 locations); terrain, bounds, NavMesh, Player prefab all match SAMPLE — shendiao daditu is the SAMPLE template with only trigger renames. So every trigger point is on the baked NavMesh.
  - Transport semantics confirmed (`LevelMaster.Transport(Vector3)` = `NavMeshAgent.Warp(pos)` **plus** forced `transform.position`) → an off-NavMesh landing yields "visible but immobile".
  - Trigger naming chain confirmed: `para.triggerName = curMap.Name`; map `00` Name in `MapConfig.lua` = **嘉兴·铁枪庙**, and that exact trigger exists in daditu → spawn at `(39.46, 15, 144.09)`, not the scene default position.
  - `MapTeleportor` both sides consistent: `00_mochuanlinju/Leave` leaves target empty (falls back to map name); daditu trigger has `TransportTriggerName: Leave`.
- **In Progress**
  - Final post-change verification just launched: `verify_player_refs.py` → `_wm_verify.txt`, `git status --short` → `_wm_git.txt`. **Outputs not yet read** (last command only printed file length / first lines).
- **Blocked / Open**
  - No in-game retest of the fixed build yet (`Player.log` last write still 12:59, pre-fix).
  - ~`_wm_*.txt` scratch files still in repo root (earlier `_st.txt` was deleted; scratch count printed but not acted on).

## Highlights
- `WorldMapSaveData.areaMask` default `0` would disable NavMesh if loaded from an old save → must retest with a **new game**.
- `Jyx2_PlayerMovement.UpdateMovement` uses `NavMeshAgent.speed` as the Lerp factor; `PLAYER_MOVE_SPEED_WORLD_MAP = 10` is fine, so immobility is purely positional/reference breakage.
- `Player.prefab` guids: SAMPLE `bcb2170b…` (Player.prefab had **zero** modifications there), official `3865cb9c…`; root Transform fileID `4006807282602162` is the valid override target.
- Scratch-output convention: `python … 2>&1 | Out-String -Width 200 | Set-Content -Encoding utf8 _*.txt`, then `read_files` (console mangles CJK/UTF-8).

## Next
1. Read `_wm_verify.txt` — confirm 4 scenes / 0 invalid refs.
2. Read `_wm_git.txt` — confirm only the 4 `.unity` + `fix_player.py`/`verify_player_refs.py` are modified; the `tools/shendiao` probes are new/untracked.
3. Clean up: `Remove-Item _wm_*.txt`; decide whether to keep only `fix_player.py`, `verify_player_refs.py`, `check_maplinks.py` and drop the `_*.py` probes (`Remove-Item tools\shendiao\_*.py`).
4. Retest in game: **new game** → 铁枪庙 → walk out → confirm `1000_daditu` loads, spawn at trigger `(39.46,15,144.09)`, camera follows, player moves.
5. If still broken: fresh `Player.log` (`%USERPROFILE%\AppData\LocalLow\jynew\群侠传启动\Player.log`, check LastWriteTime changed), grep `NullReference|Exception|StartAtTrigger|NavMesh|Transport|调用了未定义的游戏设置|Failed to create agent`.
6. Optional commit for `check_maplinks.py` / inspection tooling; commit messages previously written to `_msg.txt` (UTF-8) and verified with `cmd /c git log > _mraw.txt`.

## Files
Read: `c:\Games\jynew\_st.txt`, `_wm_sd.txt`, `_wm_sample.txt`, `_wm_jyx2.txt`, `_wm_root.txt`, `_wm_inst_sample.txt`, `_wm_inst_sd.txt`, `_wm_leave.txt`, `_wm_trig.txt`, `_wm_links.txt`, `_wm_verify.txt` (partial), `_wm_git.txt` (unread); `jyx2\Assets\Mods\shendiao\Configs\Lua\MapConfig.lua`; `jyx2\Assets\Scripts\GameMaps\LevelMaster.cs`, `MapTeleportor.cs`, `Jyx2Player.cs`; `tools\shendiao\_inspect_worldmap.py`.
Edited/Created: `tools\shendiao\_inspect_worldmap.py`, `_wm_inst.py`, `_wm_prefab_root.py`, `_wm_trigger_fields.py`, `check_maplinks.py`.
Previously modified & committed (unchanged this session): `jyx2\Assets\Mods\shendiao\Maps\GameMaps\{00_mochuanlinju, 01_moqiaoshanzhuang, 02_wanzhushuyuan, 1000_daditu}.unity`, `tools\shendiao\fix_player.py`, `tools\shendiao\verify_player_refs.py` (commit `f677c7879`).

再确认一个会直接影响"重测新游戏"的点：新游戏从 map 0 起步时用哪个落点触发器：

地图 00 有 3 个 `m_Follow: {fileID: 0}`（空跟随）—— 要看清楚是哪些相机，对比大地图：

**决定性证据**：`UpdateCameraParams()` 开头就是 `if (WORLDMAP) return;` —— 大地图根本不走运行时设置 Follow 的分支，**只能依赖场景里序列化的 `m_Follow`**。所以 daditu 那个 null 才是"镜头不跟随"的真正原因，也说明修复方向正确。再确认另一个会设 Follow 的 `GameViewPortManager` 是否覆盖大地图：

<user_input mode="act">不是，我只是想看看地图长啥样，能不能生成图片我看下每个地点位置</user_input>

明白了 —— 你要的是"地图长什么样 + 每个地点在哪"的可视化。我来从场景里把地形高程数据抽出来，渲染成一张俯视图，再把 18 个地点、主角落点标上去。先看环境有没有图像库，并定位地形数据：

PIL 可用（无 numpy），地形是 Unity Terrain（TerrainData guid `d4c1a58a…`）。定位它并看数据结构：

地形数据是 Unity 二进制序列化（`2020.3.32f1`），文本解析不了。看看有没有现成的大地图贴图（游戏内"大地图"UI 用的那张图）：

---

## Next 执行回执（2026-10-28 新会话）

按上文 `## Next` 逐条推进的结果：

| # | 事项 | 结果 |
| --- | --- | --- |
| 1 | 读 `_wm_verify.txt` | ✅ **4 场景 / 0 失效引用**。`Player.prefab` guid = `3865cb9c075a411d920aee4d5c7d0149`，与工程 `Player.prefab.meta` 一致；`m_Modifications` 12/12/12/15 条、`m_CorrespondingSourceObject` 2/1/1/1 条，全部有效 |
| 2 | 读 `_wm_git.txt` | ✅ 工作区干净。4 个 `.unity` + `fix_player.py` + `verify_player_refs.py` 均已在 commit `f677c7879`（HEAD）中，故不出现于 status。另发现 3 个噪音改动已丢弃 |
| 3 | 清理 | ✅ 删除 14 个 `_wm_*.txt` / `_terr_head.txt`；`git checkout` 掉 3 个无意义改动（2 个 `.mat` 浮点末位漂移 + `DOTweenSettings.asset` 仅 LF/CRLF 差异）。`tools/shendiao/_*.py` 20 个探针**保留**（未跟踪，可复用） |
| 4 | 游戏内重测 | ⚠️ **日志已证明传送链路跑通，但手感项未验证** —— 见下 |
| 5 | 若仍坏则抓新日志 | ⏭ 跳过（未发现 NavMesh / NullReference 异常） |
| 6 | 提交探针工具 | ⏸ 待决定（`check_maplinks.py` 等仍是未跟踪状态） |

### 关键证据：`Player.log`（2026-10-28 14:02:45，700 行，场景改于 13:46:44）

场景切换序列完整覆盖了大地图往返，且**跑了两轮**：

```
175: Scene 00_mochuanlinju is loaded      ← 铁枪庙
309: Scene 1000_daditu is loaded          ← 出图 → 大地图   [第 1 次]
318: Scene 01_moqiaoshanzhuang is loaded  ← 从大地图进入
483: Scene 1000_daditu is loaded          ← 返回大地图
494: Scene 08_gezilou is loaded
519: Scene 00_mochuanlinju is loaded      ← 重新开始
643: Scene 1000_daditu is loaded          ← 出图 → 大地图   [第 2 次]
652: Scene 10_binhumaolu is loaded
674: Exception 版本:20230510, 触发时间:2026/10/28 14:02:43   ← 退出时 LuaEnv dispose（无害）
```

- ✅ 无 `NavMesh` 相关错误、无 `NullReferenceException`、无 `Failed to create agent`
- ✅ `00_mochuanlinju → 1000_daditu` 反复进出均正常
- ❌ 日志无法反映的三项：**落点是否 `(39.46, 15, 144.09)`**、**相机是否跟随**、**主角能否移动**
- ⚠️ 无法确认那次是否使用**新存档**（旧存档 `WorldMapSaveData.areaMask = 0` 会导致人物可见但走不动）

**下一步只剩这一件事**：开新游戏 → 铁枪庙 → 走出地图 → 目视确认主角能走、镜头跟随、落点在铁枪庙触发器上。

---

## 2026-10-28 下午：弃用渡城地图，改用 JYX2 官方地图（线性路线版）

提交 `8d5ab801d`。上一轮修的"传送链路"本身没问题，但**地图选错了**，本轮是换底。

### 三层诊断（按证据）

1. **地图是假的**：shendiao 的 20 张图是 SAMPLE「渡城」的复制品。`场景.xlsx` 的
   `Id / MapScene / TransportToMap / 音乐 / 标签` 与 SAMPLE 逐行相同，**只有 `Name` 列被改成神雕地名**
   （莫穿林居→嘉兴·铁枪庙、茶恩寺→陆家庄、钟鸣阁→襄阳城、野狼谷→万兽山庄、黑熊谷→蒙古大营…）。
2. **大地图太小且方位全错**：shendiao 172×172 单位 / 18 个点；JYX2 是 440×440 / 79 个点。
   shendiao 的落点照抄渡城城内布局：嘉兴在 x=39（最西）、襄阳在 x=211（最东）。
3. **文案与坐标脱节**：`Lua/4.lua:18` 写 `"序章：往大地图东行，去江南寻访白袍客。"`，
   而江南（嘉兴 x=39 / 临安 x=124）在西半张图 —— 按指引往东找，必然找不到。

### 坐标系结论（重要，别再猜）

Unity 世界轴与地理方位（由 15+ 个 JYX2 地点交叉验证：光明顶/昆仑派 x≈400+ 在西、侠客岛/万鳄岛 z≈440+ 在南、桃花岛 x=137/z=341 在东南）：

```
+X = 西      -X = 东
+Z = 南      -Z = 北
```

**且** `CM vcam1` 原本是 `euler(45, 225, 0)`，45° 斜视角让屏幕方向再偏 45°：

| | 原相机 225° | 改后 180° |
| --- | --- | --- |
| 屏幕上方 | 东北 | **北** |
| 屏幕右方 | 东南 | **东** |

这就是"东南西北搞错"的机制根源，本轮已把相机转正。

### 搬运可行性（关键数据）

JYX2 场景的资源引用几乎全是 `GLOBAL`（随游戏本体 `base_assets` 走），每个场景只有 **1 个**私有资源（自己的 `NavMesh.asset`），大地图额外多 1 个 `SampleSettings.lighting`：

| 场景 | GLOBAL 引用 | 私有 |
| --- | --- | --- |
| `1000_daditu` | 10445 / 175 个 | 2 |
| `19_chongyanggong` | 7844 / 63 个 | 1 |
| `22_jueqinggu` | 15745 / 59 个 | 1 |
| `75_taohuadao` | 22430 / 56 个 | 1 |

所以复制 `.unity` + 自己的 `NavMesh.asset` 即可，不用搬模型贴图。`tools/shendiao/import_jyx2_maps.py` 负责这件事（重写 GUID + 同步引用 + AB 重标 `shendiao_maps`）。

### 传送机制（改配置前必看）

```csharp
// MapTeleportor.cs:127-131  —— 大地图上点触发器
var nextMap = LuaToCsBridge.MapTable[0];              // ← 默认值就是地图 Id 0！
if (curMap.Tags.Contains("WORLDMAP"))
    nextMap = nextMap.GetMapByName(this.gameObject.name);

// MapTeleportor.cs:155-161  —— 离开场景
else if (curMap.Tags.Contains("WORLDMAP"))  para.triggerName = "Leave";
else if (nextMap.Tags.Contains("WORLDMAP")) para.triggerName = curMap.Name;
```

**双向都靠 `Name` 与大地图触发器名逐字匹配。** 匹配不上的后果不是报错，而是**默默传送到 Id 0**。
所以大地图 79 个地名必须全部配齐 —— 这是本轮给 65 个地点配"未开放"占位的原因。

`EnterCondition = 1` 时 `CheckCanEnterMap()` 返回 false（`GameRuntimeData.cs:699`），
`ShowEnterButton()` 直接 return —— 不显示进入按钮，玩家踩上去无反应也不会误传送。

### 线性路线（剧情 + 地理最近邻）

| 序 | Id | 名称 | 坐标 (x,z) | 上一站距离 |
| --- | --- | --- | --- | --- |
| 1 | 0 | 破庙 | 181, 19 | — |
| 2 | 1 | 重阳宫 | 217, 145 | 131 |
| 3 | 2 | 古墓 | 219, 144 | 2 |
| 4 | 3 | 神雕山洞 | 170, 68 | 90 |
| 5 | 4 | 绝情谷 | 259, 134 | 110 |
| 6 | 5 | 绝情谷底 | 254, 131 | 6 |
| 7 | 6 | 百花谷 | 271, 158 | 32 |
| 8 | 7 | 华山派 | 302, 193 | 46 |
| 9 | 8 | 思过崖 | 301, 188 | 5 |
| 10 | 9 | 铁掌山 | 343, 302 | 122 |
| 11 | 10 | 黑龙潭 | 351, 309 | 11 |
| 12 | 11 | 一灯居 | 370, 314 | 19 |
| 13 | 12 | 程英居 | 422, 295 | 56 |
| 14 | 13 | 桃花岛 | 138, 341 | 288（终章远行） |

第 2 站必须是重阳宫：`Lua/1001.lua` 序章正剧是"郭靖送杨过上终南山"，
第 40 行原写 `赶赴「终南山·重阳宫」`，已改为 `往西南方赶赴【重阳宫】`。

其余 65 个地点 `EnterCondition=1`、`Name` 加 `〔未开放〕` 后缀，
大地图触发器的 GameObject 名字也已同步改名（`m_Name` 在 `.unity` 里是 `"\uXXXX"` 转义，
必须按转义形式改，否则匹配 0 次）。

### 校验

- `python tools/shendiao/check_maplinks.py` → **14 开放 + 65 未开放，结论：全部闭合**
- `python tools/moddev/jyx2mod.py check shendiao` → **一切正常**
- `python tools/moddev/jyx2mod.py unity shendiao` → `shendiao_maps` 135.8 MB + `shendiao_mod` 35.1 MB（未带 base_assets，共享资源被复制进包，故偏大）
- `python tools/moddev/jyx2mod.py install shendiao --src Export` → 已装入游戏

### 待办

1. **游戏内验证**（需人工）：新存档 → 破庙 → 出图 → 醒目视确认「屏幕上方=北、右方=东」、主角能动、镜头跟随
2. 导入场景内的 `GameEvent` 仍指向 JYX2 的 story id(0~16)，会与 shendiao 现有 Lua 串戏
   （如 `62_pomiao` 有 id 0/3/4/5/6/10，其中 4 恰好是庙祝对话，其余不匹配）→ 剧情阶段统一重绑
3. 原 20 张渡城场景仍在包内占体积，确认无用后删除
4. 桃花岛距第 13 站 288 单位，若嫌远可换成 `23_hongqigongju`（210,168，紧邻古墓一带）

### 在 Unity 编辑器里看地图（操作手册）

工程已装 Unity **2020.3.32f1c1（中国版，带 c1 后缀）**，路径 `C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe`；
Hub 里选错成 `2020.3.32f1` 会报版本不匹配。

1. Hub → Add → `c:\Games\jynew\jyx2` → 打开
2. Project 窗口 `Assets → Mods → shendiao → Maps → GameMaps → 双击 1000_daditu`
3. 选中 `CameraGroup/CM vcam1` → 菜单 **`GameObject → Align View to Selected`**
   → Scene 视图变成游戏视角（45° 俯角，上北右东）

快捷键（2020.3 默认值，官方 `SceneViewNavigation` 页核对）：

| 功能 | 键 |
| --- | --- |
| 飞（Flythrough） | 按住右键 + `WASD` + `QE`（升/降）+ `Shift` 加速 |
| 环绕 / 缩放 | `Alt`+左键拖 / 滚轮（或 `Alt`+右键拖） |
| 飞到选中物体 | 鼠标悬停在 Scene 视图上按 `F`（`Edit > Frame Selected`） |
| 锁定跟随选中 | `Shift+F` |
| 顶视图 | 点 Scene Gizmo 的 Y 轴锥形臂 |

**易错点（已踩过）**：

- `Ctrl+P` 是 **Play 模式**，不是搜索 —— 看地图时按了会把场景交给游戏脚本，直接传送
- `Ctrl+Shift+F` 是 `Align with View`（**物体 → 视图**），方向与想要的反了，会把 `CM vcam1` 挪位；
  `Align View to Selected` **没有默认快捷键**，只能点菜单
- `F` 生效要求鼠标在 Scene 视图内，在 Hierarchy 上按无效
- **Unity 顶视图是反的**：Z 轴朝上而 `+Z=南`、`+X=西`，画面整体旋转 180°（上南下北、右西左东）；
  只有对齐 `CM vcam1` 后才是上北右东
- 看场景不要 `Ctrl+S`（会改写 `.unity` 产生浮点/GUID 漂移）；开编辑器时不要同时跑 `jyx2mod.py unity`（抢工程锁）

不开编辑器查层级：`python tools/shendiao/inspect_scene_tree.py <scene.unity> --depth 3 [--filter 未开放]`

大地图实测层级（332 个 GameObject / 79 个地名触发器）：

```
Main Camera  ·  Level(PlayerBoat/Bake/Dynamic/FX/Triggers)  ·  CameraGroup/CM vcam1
LevelMasterBooster  ·  [Decal Root]  ·  cankao(参考图)  ·  BigMapNameDrawer
```

`62_pomiao` 的 `Level/Triggers` 下可直观看到残留的 JYX2 story id `0/3/4/5/6/10`
与 `Timeline/[Timeline]ka564_小虾米破庙挖坟` 过场 —— 即"串戏"待办的具体位置。

---

## 更正：大地图相机参数（此前结论有误，以本节为准）

前文写的「`CM vcam1` 原为 `euler(45,225,0)`、转正为 `(45,180,0)`」是**错的**，已回滚。实测数据：

| | `m_LocalRotation`（真值） | 换算欧拉角 | `m_LocalEulerAnglesHint` |
| --- | --- | --- | --- |
| JYX2 原版 = 当前还原值 | `{0.13088542, -0.8681629, 0.31598538, 0.3596048}` | **俯角 27°、偏航 -127.5°** | `(45, 225, 0)` ← **过期缓存，不可信** |

**教训（花了两次打包才确认）**：

- `m_LocalEulerAnglesHint` 只是编辑器面板显示的缓存值，**可能与 `m_LocalRotation` 完全不一致**。
- 改 `.unity` 里的旋转**必须改 `m_LocalRotation` 四元数**；按 hint 反推四元数会连俯角一起改掉
  （本次 27°→45°），透视压缩明显变化，用户观感即"画面变形"。
- 回滚方式：`python tools/shendiao/set_camera_rotation.py <场景> --name "CM vcam1" --copy-from <JYX2原场景> --apply`

### 原视角下的屏幕方位映射（实测换算）

相机 `yaw=-127.5°`（`pitch=27°` 不影响水平朝向）。世界轴 `+X=西 / +Z=南`：

| 屏幕方向 | 地理方位 | 方位角（北=0°顺时针） |
| --- | --- | --- |
| 上 | 东北偏东 | 52.5° |
| 右 | 东南偏南 | 142.5° |
| 下 | 西南偏西 | 232.5° |
| 左 | 西北偏北 | 322.5° |

**JYX2 原版大地图本身就是"斜 45°"视角设计**，屏幕上≠北，这不是 bug。

### 最终决策（2026-10-28 二次修正，用户确认）

- **相机保持 JYX2 原版原样**，不做任何旋转（转正会变形，已否决）
- **地图点位与建筑也不移动**：大地图引用 100+ 个独立 Prefab，点位本身与地形严丝合缝；
  且 `NavMesh.asset` 是提前烘培的二进制数据，移建筑后不会重烘 → 玩家会撞空气墙 / 看得见走不动
- **方位指引改用"屏幕方向"**：

| 文件 | 改后文案 |
| --- | --- |
| `Lua/4.lua:18` | `序章：出庙后往大地图右下方走，赶赴【重阳宫】寻访白袍客。` |
| `Lua/1001.lua:40` | `请前往大地图，往右下方赶赴【重阳宫】。` |

推导：破庙 `(181,19)` → 重阳宫 `(217,145)`，`ΔX=+36`（西）、`ΔZ=+126`（南）；
在屏幕坐标系里投影为 **下方 105.3 / 右方 78.0** → 右下方（从正下向右偏约 37°）。

### 查/改旋转的两个工具

```powershell
# 查任意对象的四元数、换算欧拉角、hint
python tools/shendiao/inspect_transform.py <scene.unity> "CM vcam1"

# 从参考场景原样复制 / 指定欧拉角（默认 dry-run，加 --apply 生效）
python tools/shendiao/set_camera_rotation.py <scene.unity> --name "CM vcam1" --copy-from <ref.unity>
python tools/shendiao/set_camera_rotation.py <scene.unity> --name "CM vcam1" --euler 27,180,0
```




---

## 剧情系统：Lua 必须按 EventId 命名（2026-10-28 三次修正）

### 症状

进破庙后既没有 NPC 也没有剧情。`Player.log` 里是：

```
Scene 62_pomiao is loaded
找不到文件 [557]
ArgumentNullException: Array cannot be null.   (Jyx2.LuaExecutor.Execute)
GameEvent:OnTriggerEnter(Collider)
```

### 根因一：Lua 文件名 = GameEvent 的 EventId，不是 GameObject 名

- `MODRootConfig.LuaFilePatten` 默认 `ka{0}`（JYX2 用），shendiao 的 `ModSetting.asset` 设为 `{0}`
- EventId 是 `GameEvent` 组件上的**字符串**字段：`m_InteractiveEventId` / `m_UseItemEventId` / `m_EnterEventId`
- 和 `Level/Triggers/<物体名>` 的物体名**完全无关**（物体名只是编辑器里的标签）

> 上一轮的 `0.lua` / `3.lua` / `4.lua` / `10.lua` 全是按物体名起的，一个都不会被加载。

### 根因二：场景 NPC 埋在土里

- `Level` / `Triggers` / `NPC` 三个节点都在 (0, 0, 0)
- 原有 7 个 JYX2 NPC（`azi` / `youtanzhi` / `星宿弟子5~9`）局部 y ≈ 0，而地面与触发器在 **y = 5.5**
- → **NPC 全部埋在地面下 5.5 米**，玩家看不见（prefab 本身加载正常，日志无相关报错）

### 破庙 62_pomiao 事件表（实测）

| 物体名 | 局部坐标 | 交互 | 用物品 | 经过 | 对应 Lua |
| --- | --- | --- | --- | --- | --- |
| 0 | (-0.4, 5.5, 22.0) | −1 | −1 | **557** | 557 进庙独白 |
| 3 | (0.1, 5.5, 12.8) | **558** | −1 | −1 | 558 供桌木箱 |
| 4 | (-0.6, 5.0, 12.6) | **559** | −1 | −1 | 559 庙祝对话 |
| 5 / 6 | — | −1 | −1 | −1 | 空事件，不用管 |
| 10 | (1.9, 5.5, −13.3) | **563** | **564** | −1 | 563 / 564 断碑 |
| Leave | (-0.62, 5.5, 28.75) | — | — | — | 出生 / 离场点 |

### `ModifyEvent` 签名（禁用一次性事件用）

```csharp
ModifyEvent(scene, eventId, canPass, changeToEventId,
            interactiveEventId, useItemEventId, enterEventId, p7..p12)
// scene=-2 当前场景；eventId=-2 当前事件（注意用的是 GameObject 名，int.Parse(evt.name)）
// 三个 EventId 传 -1 = 禁用
```

### 本轮实现（破庙序章）

| 文件 | 作用 |
| --- | --- |
| `Lua/557.lua` | 进庙自动独白；末尾 `ModifyEvent(-2,-2,-2,-2,-1,-1,-1,...)` 关闭自己，只播一次 |
| `Lua/558.lua` | 供桌旧木箱 → `SetFlagInt("父亲遗物", 1)` |
| `Lua/559.lua` | 庙祝（111 号，人物表已有"庙祝"）对话 → `SetFlagInt("庙祝指路", 1)`、`SetFlagInt("序章完成", 1)`，提示「大地图右下方 → 重阳宫」 |
| `Lua/563.lua` / `564.lua` | 断碑 / 挖土提示 |
| `Lua/457.lua` | 原 `10.lua` 的重阳宫文案，改挂重阳宫物体 0 的交互 EventId = 457 |

- 删除 `0.lua` / `3.lua` / `4.lua`（永不加载）
- 场景新增 `Level/NPC/老庙祝`：prefab `StoryNpc/Suanmingxiansheng.prefab`，位置 **(-2.5, 5.5, 13.5)**，朝 +Z

### 新增工具

```powershell
# 列出场景里所有 GameEvent 的 EventId（交互/用物品/经过）
python tools/shendiao/inspect_events.py <scene.unity>

# 精确查看某节点，含 prefab 实例内部的 stripped 块
python tools/shendiao/inspect_node.py <scene.unity> NPC --depth 3

# 检查场景引用的 prefab / 资源落在哪个 AssetBundle
python tools/shendiao/check_scene_ab.py <scene.unity> --prefabs-only

# 往场景里塞一个 prefab 实例（NPC / 摆件），默认 dry-run
python tools/shendiao/add_scene_npc.py --scene <scene> --template-scene <src scene> \
  --prefab-guid <guid> --parent NPC --name 老庙祝 --pos -2.5,5.0,13.5 --rot-y 180 --apply
```

### 其它开放场景的 EventId（待逐个对齐 Lua）

| 场景 | 有用 EventId |
| --- | --- |
| `19_chongyanggong` | 455, 456, 457, 850, 851, 852 |
| `18_gumu` | 442 |
| `07_shandong` | 389, 390, 394, 836, 837, 838 |
| `22_jueqinggu` | 399, 400, 401, 856, 857 |
| `80_jueqinggudi` | 435, 436 |
| `81_siguoya` | 282, 283 |
| `48_tiezhangshan` | 448, 449, 450, 453, 454, 907 |
| `21_heilongtan` | 416 |
| `45_chengyingju` | 402, 906 |
| `75_taohuadao` | 465, 466, 922, 923 |
| `57_huashanpai` | 192, 913, 914 |

> 只要 `Lua/<EventId>.lua` 存在就会被加载，所以**下一步只需按这张表补/改脚本**，不用改场景。


---

## 2026-10-28｜破庙"什么都点不到 / 地图里有闲人"的根因（重要）

用户反馈两条：①地图里有不相关的人；②"供桌"根本找不到。查下来不是 Lua 问题，
而是**导入场景的 GameEvent 三个字段全错**，外加原版剧情 NPC 没清。

### 一、GameEvent 交互的三要素（缺一个就永远点不到）

`Jyx2Player.Update()` → `DetectInteractiveGameEvent()`：

```csharp
const float PLAYER_INTERACTIVE_RANGE = 2f;
_gameEventLayerMask = LayerMask.GetMask("GameEvent");          // 本项目 = layer 20
Physics.OverlapSphereNonAlloc(player.pos, 2f, targets, _gameEventLayerMask);
// CanSee(): 视野角度内 && target.bounds.Contains(player + forward*radius)
```

`GameEventManager.TryTrigger()`：

```csharp
if (!evt.IsInteractiveOrUseItemEvent) return false;
if (!evt.HasEventTargets) return false;       // ← targets 为空直接 return，面板不弹
ShowInteractUIPanel(evt);
UnityTools.HighLightObjects(evt.m_EventTargets, Color.red);   // 目标物会变红高亮
```

| # | 字段 | 移植后常见值 | 正确值 | 错了会怎样 |
| - | --- | --- | --- | --- |
| 1 | 宿主 GameObject 的 `m_Layer` | `0` (Default) | `20` (GameEvent) | OverlapSphere 扫不到 → 交互面板永不出现 |
| 2 | `BoxCollider.m_IsTrigger` | `0` | `1` | 隐形实体方块：挡路，且 `OnTriggerEnter`（Enter 事件）不触发 |
| 3 | `m_EventTargets` | 指向原版剧情 NPC | 指向**玩家看得见的实物** | 目标被清理后为空 → `TryTrigger` 直接 return；指向地下尸体则高亮看不见 |

> 层索引见 `jyx2/ProjectSettings/TagManager.asset`：`Player=12, NPC=16, GameEvent=20`。
> `m_EventTargets` 不是"事件目标列表"这么抽象 —— 它决定**冒红光的那个东西**，
> 也是玩家唯一能察觉"这里能交互"的视觉提示，所以必须挂可见模型。

### 二、"供桌找不到"的具体原因

`62_pomiao` 里 558（取铁枪残片）的 `m_EventTargets` 指向 `azi`，而 azi 是原版
天龙八部剧情的 NPC，埋在 `y≈0`（地面在 `y≈5.0`）。也就是说：**要走到地下一具
看不见的尸体上**才会弹交互，玩家站在空地上什么都不会出现。

真正的家具全在**庙的深处**（z 为负）：

| 物件 | prefab | 位置 |
| --- | --- | --- |
| 供桌 | `Table_17.FBX` | (-1.6, 5.1, -8.8) |
| 佛像 | `Statue_1.prefab` | (-1.7, 6.3, -8.7) |
| 香炉×2 | `Censer_1/2` | (2.9, 6.4, -9.5) / (3.6, 6.3, -9.4) |
| 烛台×2 | `Zhutai_1.prefab` | (1.4, 5.1, -8.7) / (-5.2, 5.1, -8.7) |
| 香案×2 | `Sark_7.prefab` | (-3.5, 5.1, -0.5) / (-0.1, 5.1, -0.5) |
| 椅子×2 | `Chair_9.prefab` | (-0.8, 5.1, -5.4) / (-2.4, 5.1, -5.4) |
| 墓碑 | `mubei.FBX` | (-1.9, 6.0, -13.2) |

而 558 的触发器原来摆在 `z=+12.8` 的**空地**上 —— 那儿一件家具都没有。

### 三、清理移植场景的遗留物

prefab 实例在场景里只有 `stripped` 块，**名字和坐标都在 `PrefabInstance(!u!1001)`
的 `m_Modifications` 里**，看层级树永远是一堆 `<prefab内部/stripped>`。

```powershell
# 1) 先列清谁是谁（这是唯一能看见 prefab 实例名字/坐标的办法）
python tools/shendiao/list_prefab_instances.py <scene.unity> --parent NPC
python tools/shendiao/list_prefab_instances.py <scene.unity> --grep 桌

# 2) 删掉原版剧情 NPC（连带 stripped 块 + 挂在被删 GameObject 上的组件块 + 父 m_Children 摘链）
python tools/shendiao/remove_scene_node.py --scene <scene> \
  --name "azi,youtanzhi,星宿弟子5,星宿弟子6,星宿弟子7,星宿弟子8,星宿弟子9" \
  --parent NPC --apply
```

`remove_scene_node.py` 会做 **m_GameObject 传递闭包**：prefab 实例的 GameObject 是
stripped，但它上面的 `NavMeshAgent`/`NavMeshObstacle`/`GameEvent` 等组件块是**普通块**，
反向 `m_GameObject` 指向被删的 GameObject —— 不一起删就留下"无主组件"。
工具还会报警"外部仍有引用"，若报警不为空说明还有 `m_EventTargets` 指过来，得先改。

### 四、魔改后的 62_pomiao 布局

| 剧情 | EventId | 触发器位置 | EventTargets → |
| --- | --- | --- | --- |
| 进庙独白 | 557 (Enter) | (0, 5.5, 22.0) | 空（Enter 不需要） |
| 老庙祝对话 | 559 | (-0.575, 5.0, 12.62) | `老庙祝` GameObject（(-2.5, 5.0, 13.5)） |
| 供桌取残片 | 558 | (-1.6, 5.5, -7.2) | `供桌木箱`（`Box_1.prefab`, (-1.6, 5.15, -7.2)） |
| 断碑 | 563/564 | (-1.9, 5.5, -11.6) | `mubei` GameObject（(-1.9, 6.0, -13.2)） |

- 删除了 7 个 JYX2 天龙剧情 NPC：`azi` / `youtanzhi` / `星宿弟子5~9`
- 地面高度 = **y 5.0**（Player、Chair_9、Sark_7、Table_17 全部在 5.0~5.1），NPC 原点在脚底 → 站立高度写 5.0
- 从 `JYX2/70_xiaoxiamiju.unity` 借 `Box_1.prefab` 实例当"旧木箱"，父节点 `Dynamic`

### 五、本次新增工具

```powershell
# prefab 实例清单（名字/坐标/父节点/源 prefab），支持 --parent / --grep / --detail
python tools/shendiao/list_prefab_instances.py <scene.unity>

# 批量修 GameEvent：层级 / IsTrigger / EventTargets / 触发器位置
python tools/shendiao/patch_scene_events.py --scene <scene> \
  --set-layer 20 --trigger \
  --set-target 559=<gameObjectFileID> --clear-target 5,6 \
  --move 558=-1.6,5.5,-7.2 --apply

# 改 prefab 实例的坐标/朝向（改 m_Modifications，不是 Transform）
python tools/shendiao/move_prefab_instance.py --scene <scene> --name 老庙祝 --pos -2.5,5.0,13.5 --apply

# 删 prefab 实例（含组件块闭包 + 父节点摘链）
python tools/shendiao/remove_scene_node.py --scene <scene> --name "azi,youtanzhi" --parent NPC --apply
```

> **移植别人场景的标准流程**：`list_prefab_instances.py` 全量列一遍 →
> 删掉不属于本 MOD 的 NPC/摆件 → `patch_scene_events.py` 修 layer/IsTrigger/targets →
> 缺哪个实物就用 `add_scene_npc.py` 从别的场景借一个实例。


---

## 2026-10-28 二次｜"对着人点不到" 与 "事件永久锁死"

### 一、交互必须"人站在碰撞盒里"，否则凑角度才能点

`Jyx2Player.CanSee()`（`Scripts/GameMaps/Jyx2Player.cs:290`）是两级判定：

```csharp
bool CanSee(Collider target)   // target 是**触发器自身的 Collider**，不是 NPC
{
    // ① 视野角度：玩家 forward 与 target.transform.position（=触发器中心）夹角 ≤ 60°
    if (Vector3.Angle(transform.forward, target.transform.position - transform.position)
        > PLAYER_INTERACTIVE_ANGLE / 2) return false;

    // ② 玩家“身体前缘”是否落在触发器包围盒内
    var dir = (target.transform.position - transform.position).normalized;
    if (target.bounds.Contains(transform.position + dir * _navMeshAgent.radius)) return true;

    // ③ 兜底：射线第一个命中的必须就是这个触发器本身
    if (Physics.Raycast(..., Physics.AllLayers, QueryTriggerInteraction.Ignore)
        && hit.transform != target.transform) return false;   // ← NPC 自己把射线挡住了
    return true;
}
```

**这就是"面对人物没有光圈、只有某个距离+角度能交互"的完整解释**：
触发器是个小盒子，NPC 站在盒子外/边缘 → ② 不成立 → 走 ③ 射线兜底 →
射线先打到 **NPC 自己的 CapsuleCollider** → `hit != target` → 判 false。

修法：**触发器必须包住 NPC，且盒子要够大**。本项目统一 **世界尺寸 3.5×3.5×3.5**，
中心抬到 NPC 位置上方 ~0.9 m。这样玩家站在 NPC 周围 1.7 m 内任意角度都能交互，
且 `IsTrigger=1` 不会挡路。

```powershell
# --collider 给的是世界尺寸，工具会自动除以 Transform 的 m_LocalScale 折算成 m_Size
python tools/shendiao/patch_scene_events.py --scene <scene> \
  --move 559=-2.5,5.9,13.5 --collider 559=3.5,3.5,3.5 \
  --collider 558=3.5,3.5,3.5 \
  --move 563=-1.9,6.9,-13.2 --collider 563=3.5,3.5,3.5 --apply
```

> 破庙修正后的实测值：
> | 事件 | Transform | m_LocalScale | m_Size | 世界尺寸 |
> | --- | --- | --- | --- | --- |
> | 559 老庙祝 | (-2.5, 5.9, 13.5) | (2,2,2) | (1.75,1.75,1.75) | 3.5³ |
> | 558 供桌木箱 | (-1.6, 5.5, -7.2) | (1,1,2) | (3.5,3.5,1.75) | 3.5³ |
> | 563 断碑 | (-1.9, 6.9, -13.2) | (3,1,3) | (1.1667,3.5,1.1667) | 3.5³ |

老庙祝朝向：`--rot-y 180` 是**背对大门**（朝庙里），玩家从 z≈29 进来只见后脑勺 →
prefab `Suanmingxiansheng` 正面是 +Z，**要写 `--rot-y 0`**。

### 二、"在一个事件执行完毕以前不能执行新的事件" = 缺失 Lua 把全局锁焊死了

`Player.log` 的真实因果链：

```
Error: 找不到文件 [455]                                   ← LuaManager.LoadLua 返回 null
ArgumentNullException: Array cannot be null. Parameter name: bytes
  at System.Text.Encoding.GetString(Byte[] bytes)          ← LuaExecutor.Execute 直接 GetString(null)
  at Jyx2.LuaExecutor.Execute
  at GameEventManager.ExecuteCurEvent
UniTaskExtensions.Forget                                    ← 异常被 Forget() 吞掉，没人收
错误：在一个事件执行完毕以前不能执行新的事件。            ← GetCurrentGameEvent() 永远非空
```

三个环节缺一不可：

1. `LuaManager.LoadLua(path)` 对缺失文件只 `Debug.LogError("找不到文件 [...]")` + `return null`；
2. `LuaExecutor.Execute()` 拿到 null 后**没有任何检查**，直接 `Encoding.UTF8.GetString(chunk)` → 抛异常；
3. `GameEventManager.ExecuteJyx2Event()` 用 `ExecuteCurEvent().Forget()` 发起，
   异常不会回流，`OnFinishEvent()`（负责 `SetCurrentGameEvent(null)`）**永远不执行** →
   `curEvent` 一直挂着 → **此后整个场景任何事件全部被拒**。

表现：点一次缺失脚本的 NPC → 之后谁都不能对话、进任何场景都弹这句话。

**双保险修复**（`Scripts/`，属于引擎改动，需重编游戏本体才生效）：

```csharp
// LuaCore/LuaExecutor.cs —— 两个分支都加 null 检查
var chunk = LuaManager.LoadLua(file);
if (chunk == null) return;          // 当做空事件，让上层释放锁


## 2026-10-28 晚：重阳宫"空气墙"真凶 + 让路机制

### 一、空气墙 = `NavMeshObstacle.m_Carve = 1`（不是 Collider，也不是 NavMesh 缺失）

现象：对完话走不进宫，像被无形墙顶住。

**最容易误判的地方**：在 Unity 编辑器（Edit 模式）里跑 NavMesh 探针，结果「完全连通」——
`CalculateTriangulation()` 有 2569 顶点，7 个关键点 `SamplePosition` 全部命中，
双向 `CalculatePath` 全部 `PathComplete`。

原因是 `NavMeshObstacle.carving` **只在 Play 模式才真正挖洞**，Edit 模式的探针看不见洞。

真凶：`QuanzhenDizi 1.prefab` 实例（鹿清笃）覆盖了 `m_Carve: 1`：

| 字段 | 值 |
|---|---|
| `m_Carve` | **1** → 运行时挖穿 NavMesh |
| `m_Shape` | 1 (Box) |
| `m_Extents` | (1.5, 1, 0.5) → 世界 3×2×1 |
| `m_Center.y` | 1 |
| 站位 | (32.3, 0, 11.4) |

footprint **x[30.8, 33.8] × z[10.9, 11.9]**，正压在山门墙缺口（`x=31.63`，缺口 `z[9.7,13.6]`）正中。
挖洞后两侧只剩 1.2m / 1.7m，再被 agent radius(0.5) 侵蚀 → 实际可走 0.2m / 0.7m，
`SetDestination` 算不出完整路径 → 玩家原地不动。

**修复**：`m_Carve: 1 → 0`（弟子仍靠 avoidance 挡人，但玩家 `NoObstacleAvoidance`，可穿过）。

### 二、让路：`FixWithGameRuntime` 必须挂在 NPC 自己身上

`FixWithGameRuntime.Reload()` 做的是 `transform.position = MoveTo.position` ——
**移动的是挂载者自己**。历史上把它挂在 `Level/Triggers/1` 上，于是每次只把触发器搬走，
鹿清笃从来没动过（台词却在说"侧身让到门边"）。


### 三、回归：`Lua/0.lua`、`3.lua`、`4.lua`、`10.lua` 曾被误删

`git status` 显示工作区删了这 4 个脚本，但场景仍在引用：

| 脚本 | 引用场景 | 字段 |
|---|---|---|
| `0.lua` / `3.lua` / `4.lua` | `00_mochuanlinju` | `m_InteractiveEventId` |
| `10.lua` | `01_moqiaoshanzhuang` | `m_InteractiveEventId` |

`LuaExecutor` 拿不到 chunk 时事件链不会 `OnFinishEvent` → **该场景事件永久锁死**。
已 `git checkout HEAD --` 恢复，`check_story` 从 111 个脚本回到 **115 个 / 0 错误**。

**教训**：`check_story` 只查 Lua 语法，**不查"场景引用的事件 id 是否已有对应脚本"**。
删脚本前必须扫一遍场景引用；`git status` 里的 ` D ` 项要逐条确认是不是有意为之。

### 四、新增诊断工具

| 文件 | 用途 |
|---|---|
| `tools/shendiao/list_colliders.py` | 列场景内所有 Collider，把 local 尺寸乘 scale 折算成**世界尺寸**；`--near x,z` 按距离排序，`--solid-only` 只看实体墙（查空气墙用） |
| `tools/shendiao/add_letway_npc.py` | 给 NPC 实例装配"让路"（锚点 + `FixWithGameRuntime` + `m_AddedComponents`），带幂等保护与 dry-run |
| `jyx2/Assets/Editor/ShendiaoNavProbe.cs` | `Probe`：NavMesh 三角化 / 采样 / 双向连通性；`VerifyLetway`：打印 NPC 组件、`carving`、让路 `Flag`/`MoveTo` |

```powershell
& "C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe" -batchmode -quit `
  -projectPath C:\Games\jynew\jyx2 `
  -executeMethod ShendiaoNavProbe.VerifyLetway -logFile C:\Games\jynew\Logs\verify.log
# 输出 C:\Games\jynew\_letway.txt
```

**API 坑**：`NavMesh.GetAreaName` 是 Unity 2021+ 才有的，2020.3 只能用 `GetAreaFromName` 反查。

### 五、本轮验证清单（均已通过）

| 项 | 结果 |
|---|---|
| 鹿清笃站位 | `(32.3, 0.0, 11.4)` 门口 |
| `NavMeshObstacle.carving` | `False` |
| 弟子上 `FixWithGameRuntime` | 唯一一个，`MoveTo = 弟子让路点 @ (32,0,12.9)` |
| `Level/NPC/弟子让路点` | `(32.0, 0.0, 12.9)` |
| `Level/Triggers/1` | `GameEvent interactive=455, enter=-1, targets=1` |
| `check_story` | 115 剧本 / 0 错误 |
| `jyx2mod check` | `[ok] 一切正常` |
| 导出 + 安装 | maps 363MB / mod 78MB，装到 Steam `mods/shendiao`（20:01）|

**测法**：进游戏读档（旧档也行，455 第一分支会补设 flag）→ 走到山门 → 与鹿清笃对话
→ 他应当**当场移动到门边**（`(32,0,12.9)`）→ 然后沿山门往宫里走，不再被挡。

正确装配：
1. 空锚点 `Level/NPC/弟子让路点` @ `(32, 0, 12.9)` —— 缺口北侧，真的让开通道且 `y=0` 不浮空
2. `FixWithGameRuntime` 挂在**弟子实例**上，`Flag = "重阳宫大门弟子让路"`，`MoveTo = 弟子让路点`
3. 对话里 `jyx2_FixMapObject("重阳宫大门弟子让路", "1")` → 立刻 `Reload()`，无需重进场景

坑：
- **值必须传字符串 `"1"`**：`FixWithGameRuntime` 按 `KeyValues[Flag] == "1"` 比较，
  Lua 传 number 在某些路径下会变成 `"1.0"`，判定失败。
- 同一 Flag 挂两个组件会互相覆盖（落点取决于执行顺序）——装配前先 grep 一遍。
- `jyx2_WalkFromTo` **只驱动玩家**，不能用来移动 NPC。
- 旧存档兼容：已对话过（`入全真 == 1`）的玩家走 455 第一分支，那里也要补一次
  `jyx2_FixMapObject`，否则永远看不到让路。
- **只改场景/Lua 不需要重编 player**（AB 即生效）；改 C# 才需要。

// GameMaps/GameEventManager.cs —— 保证 OnFinishEvent 一定被调用
try {
    var graph = await Jyx2ResourceHelper.LoadEventGraph(eventName);
    if (graph != null) { graph.Run(OnFinishEvent); return; }   // 蓝图自己回调，不能重复解锁
    await Jyx2.LuaExecutor.Execute(eventLuaPath);
} catch (Exception e) {
    Debug.LogError($"[GameEvent] 事件 {eventName} 执行失败：{e}");
}
OnFinishEvent();
```

> **在 C# 修复生效之前，唯一的规避办法就是：场景里出现的每个 EventId 都必须有对应 Lua。**
> 一个都不能少 —— 缺一个就锁死全场景。

### 三、重阳宫补齐的 5 个脚本

`19_chongyanggong` 有 9 个 GameEvent，用到 `455 / 456 / 457 / 850 / 851 / 852`，
其中**只有 457 存在**，其余全缺 → 进门第一个弟子就锁死。

EventId 与场景物体一一对应（触发器坐标 = NPC 坐标，所以能正常触发，纯属脚本缺失）：

| EventId | 触发器 | 对应物体 | 脚本 |
| --- | --- | --- | --- |
| 455 | (32.2, 0.5, 11.4) | `QZhenDiZi` (32.3, 0, 11.4) 山门弟子 | 鹿清笃盘问 → `SetFlagInt("入全真", 1)` |
| 456 | ×5 处 | `QZhenDiZi (1)~(5)` 宫内巡逻 | 已放行才让过，否则拦下 |
| 457 | (6.3, 0.5, 25.1) | `qiuchuji` (6.3, 0.2, 25.1) | 重阳宫独白（提示找丘处机） |
| 850/851/852 | (21.6/23.2/24.6, 0.5, -5.3) | `Box_3` / `Sark_1` ×2 | 陈设独白 |

**人物表里没有"全真弟子""丘处机"**（`Configs/人物.xlsx` 只有 61 人）。
可用替代：**60 鹿清笃**（全真弟子，原著里带头欺负杨过的就是他）、20 赵志敬、123 孙不二、190 路人乙。
本次 455/456 都用 60。

### 四、破庙与重阳宫的地面高度不一样

| 场景 | 地面 y | 触发器 y 习惯 |
| --- | --- | --- |
| `62_pomiao` | **5.0**（Player/桌椅/供桌全在 5.0~5.15） | 交互盒中心抬到 +0.9 |
| `19_chongyanggong` | **0.0~0.2**（NPC 脚底 y=0，触发器 y=0.5） | 原值可用 |

> 写坐标前一定先用 `list_prefab_instances.py --parent NPC` 看一眼 NPC 的 y。


---

## 2026-10-28 三次｜一键传送（DebugPanel）与弟子挡路

### 一、JYX2 本来就有一键传送，不用新写

`Assets/Scripts/UI/DebugPanel.cs`，挂在 `Assets/Prefabs/LevelMaster.prefab` 上
（LevelMaster 是全局单例，每个场景都实例化 → 任何场景都能用）。

两个下拉框：

| 控件 | 数据源 | 行为 |
| --- | --- | --- |
| `m_ChangeScene` | `LuaToCsBridge.MapTable` 全部非 `BATTLE` 地图 | `LevelLoader.LoadGameMap()` → **跨场景跳转** |
| `m_TransportDropdown` | **当前场景 `Level/Triggers` 的全部子物体名** | `LevelMaster.Instance.Transport(name)` → **场景内瞬移** |

> **核心结论：数据源就是 `Level/Triggers` 的子节点。**
> 在 Triggers 下加一个空 GameObject，传送下拉里立刻多一项，**不用改任何 C#**。

`LevelMaster.Transport(name)` 的实现（`LevelMaster.cs:469`）：

```csharp
public void Transport(string transportName)
{
    _playerNavAgent.enabled = false;
    TransportToTransform("Level/Triggers", transportName, "");   // 找不到会回落到 Level/Dynamic
    _playerNavAgent.enabled = true;
}
// TransportToTransform 内部：Warp 到该点，并复制该点的 rotation 作为朝向
// （rotation 为 identity 时不改朝向；想要朝向 0 度就把节点转成 360）
```

### 二、按 ` 键没反应？两个坑叠在一起

**坑 1 —— 难度封锁**

`ModSetting.asset`：

```yaml
IsConsoleEnable: 1
ConsoleDisableDifficulty: 0100000002000000   # = List<Jyx2_GameDifficulty>{1, 2}
```

`DebugPanel.RefreshValidity()`（`DebugPanel.cs:162`）发现当前难度命中列表就直接
`gameObject.SetActive(false)` —— 面板整个被关掉。

修：清空列表。

```yaml
ConsoleDisableDifficulty: []
```

（`MODRootConfig.cs:43` 的 `List<Jyx2_GameDifficulty>` 字段没有初始化，
写 `[]` 反序列化成空表而非 null，`foreach` 安全。）

**坑 2 —— 按键自锁（真 bug）**

```csharp
public bool CanUpdate => _isDebugPanelOn;                 // 面板关着 → false
public void OnUpdate() {
    if (Input.GetKeyUp(KeyCode.BackQuote)) DebugPanelSwitch();
}
```

`InputContextManager.Update()`（`InputContextManager.cs:131`）：

```csharp
if (CurrentContext != null && CurrentContext.CanUpdate)
    CurrentContext.OnUpdate();
```

面板没打开 → `CanUpdate == false` → `OnUpdate` 根本不被调用 → 按 ` 收不到 →
永远打不开。**自锁死循环**。

修（`DebugPanel.cs`）：把按键监听从 `OnUpdate` 挪到组件自己的 `Update()`，
和 `ScreenLoggerHotkeyManager`（F12 截图日志）用的模式一致：

```csharp
public void OnUpdate() { /* 面板开关不在这里处理，见 Update() */ }

private void Update()
{
    // 常驻监听 `（BackQuote）键，面板关闭时也能唤醒
    if (Input.GetKeyUp(KeyCode.BackQuote))
        DebugPanelSwitch();
}
```

> ⚠️ **不要**改成在 `Start()` 里 `AddInputContext(this)`。
> `AddInputContext` 会把面板插到 `m_Contexts` 末尾并顶成 `CurrentContext`，
> 且 `prevContext is Jyx2_PlayerInput` → `FirePlayerInputChangeEvent(false)`
> → **玩家立刻走不了路**。

### 三、传送点对照表

`Level/Triggers` 下的子物体名字是数字，别改名 —— **Lua 里 `jyx2_MovePlayer("0")` 靠名字索引**。

**19_chongyanggong**

| 节点 | 位置 | 对应 |
| --- | --- | --- |
| `Leave` | (36.63, 0.5, 11.55) | 出场景口 |
| `1-让路` | (31.02, 0.5, 10.33) | 山门内侧空地（原设计给弟子让路用） |
| `1` | (32.17, 0.5, 11.39) | **山门鹿清笃**（455） |
| `0` | (6.35, 0.5, 25.11) | **丘处机**（457） |
| `2`~`6` | 29.1/26.9/14.9/19.5/22.2 | 巡逻弟子 ×5（456） |
| `7` / `8` / `9` | 21.6 / 23.2 / 24.6, z=-5.2 | 香烛箱 / 经卷 / 砚台（850/851/852） |

**62_pomiao**

| 节点 | 位置 | 对应 |
| --- | --- | --- |
| `Leave` | (-0.62, 5.5, 28.75) | 出场景口 |
| `0` | (-0.41, 5.5, 21.96) | 进门独白（557） |
| `4` | (-2.5, 5.9, 13.5) | **老庙祝**（559） |
| `5` / `6` | 0.0 / 2.09, z≈15 | 香炉 / 水缸 |
| `3` | (-1.6, 5.5, -7.2) | 供桌木箱（558） |
| `10` | (-1.9, 6.9, -13.2) | 断碑（563） |

> 传送是 `NavMeshAgent.Warp`，**不会**被 NPC 碰撞体挡住，可以直接落在 NPC 身上。

### 四、弟子挡路 —— 是 `NavMeshObstacle`，不是 Collider

`QuanzhenDizi 1.prefab` 里：

- **没有任何 Collider**（`BoxCollider` 为 0 个）
- 但有 **`NavMeshObstacle`（class `!u!208`）**：

```yaml
m_Enabled: 1
m_Shape: 0                       # Box
m_Extents: {x: 0.5, y: 1, z: 0.5}   # 世界 1×2×1 m
m_Carve: 0                       # 不挖 NavMesh
m_Center: {x: 0, y: 1.2, z: 0}
```

所以「挡路」是寻路层面的 1 米方形障碍，不是物理碰撞。

> 玩家自己 `obstacleAvoidanceType = NoObstacleAvoidance`（`LevelMaster.cs:408`，
> 无条件设置），**玩家不会绕开 obstacle**，理论上能直接穿过；
> 但 NPC 之间会互相绕，且视觉上弟子杵在门正中确实像堵路。

处理：把山门弟子从 `1`(32.32, 11.4) 挪到原设计预留的 `1-让路`(31.02, 10.33)，
并让 455 的台词交代「侧身让到门边」。

```powershell
python tools/shendiao/move_prefab_instance.py `
  --scene jyx2/Assets/Mods/shendiao/Maps/GameMaps/19_chongyanggong.unity `
  --name QZhenDiZi --pos 31.02,0.5,10.33 --apply
```

挪位后与 455 触发器（32.2, 0.5, 11.4，世界 3.5³）距离 1.65 m，
仍在盒内 → 交互不受影响。

> **NPC 无法用 Lua 移动**：`jyx2_WalkFromTo(from, to, cb)` 只驱动
> `Level/Player` 的 `Jyx2_PlayerAutoWalk`，目标点还必须放在 `Level/NavigateObjs/` 下。
> 场景里没有 `NavigateObjs` 节点，NPC 走位只能靠改场景坐标。

### 五、C# 改动生效范围

| 改动 | Editor Play | Steam 已装版 |
| --- | --- | --- |
| `ModSetting.asset` / Lua / `.unity` | ✅ | ✅（进 MOD AB 包） |
| `DebugPanel.cs` / `LuaExecutor.cs` / `GameEventManager.cs` | ✅ 立即 | ❌ 需重编 player |

重编本体（`InternalBuildPkg` 在没设 `BUILD_PATH` 时会弹 `SaveFolderPanel`，
batchmode 下会卡死，必须先给环境变量）：

```powershell
$env:BUILD_PATH = 'C:\Games\jynew\Build\'
& "C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe" -batchmode -quit `
  -projectPath C:\Games\jynew\jyx2 `
  -executeMethod Jyx2Editor.BuildTool.Jyx2BuildTool.BuildForWindows `
  -logFile C:\Games\jynew\Logs\build_player.log
```


---

## 2026-10-28 四次｜第一章按原著重写 + 修「找不到郭靖」断链

### 一、用户报的 bug 与真实根因

> 「杨过为啥出来就去重阳宫找郭靖？我根本没找到郭靖，是不是编写错了」

**确实错了，而且是三处连锁**：

| # | 位置 | 问题 |
| - | --- | --- |
| 1 | `Lua/559.lua`（老庙祝） | 台词写「你去终南山重阳宫打听打听」，还顺手 `SetFlagInt("序章完成", 1)` |
| 2 | `Lua/1001.lua`（郭靖认亲） | **孤儿脚本** —— 破庙只挂了 557/558/559/563/564，1001 没有任何 GameEvent 指向它，永远不执行 |
| 3 | `19_chongyanggong.unity` | 场景 NPC 只有 6×`QZhenDiZi` + `qiuchuji`，**没有郭靖**；`10.lua`/`11.lua`/`13.lua` 同样是孤儿 |

也就是说：玩家被指去重阳宫找一个「只在未挂载脚本里存在」的人。

### 二、顺带查出的系统性问题

用 `fill_missing_story.py` 扫全 MOD：**11 个场景、31 个事件挂了 GameEvent 却没有 Lua**。

```
07_shandong   389,390,394,836,837,838      22_jueqinggu  399,400,401,856,857
18_gumu       442                          45_chengyingju 402,906
20_baihuagu   404,405                      48_tiezhangshan 448,449,450,453,454,907
21_heilongtan 416                          57_huashanpai 192,913,914,915
75_taohuadao  465,466,922,923              80_jueqinggudi 435,436   81_siguoya 282,283
```

> 缺 Lua **不会**锁死事件系统（`LuaExecutor.Execute` 已加 null 检查），
> 但那一个滑块点下去毫无反应。本轮已全部补齐（第一章 6 个手写，其余 25 个占位）。

### 三、场景改动（全部用脚本，未手改 YAML）

| 场景 | 新增 NPC | 事件改动 |
| --- | --- | --- |
| `62_pomiao` | 郭靖 `Guojing.prefab`(0.8,5,-6.0)、黄蓉 `Huangrong.prefab`(2.2,5,-7.2) | 空物体 `5`→事件 **1001**、`6`→**1002**，targets 指向郭靖/黄蓉 |
| `19_chongyanggong` | 郭靖(34.5,0,13.0)、赵志敬 `QuanzhenDizi 1`(10.5,0,22.5) | 原杂物事件 `850`→**900**(郭靖)、`851`→**901**(赵志敬)，`852` 保留 |
| `18_gumu` | 孙婆婆 `Laotaitai.prefab`(-12.5,0,-9.5) | 空物体 `0`→**902**，targets=小龙女 `33130135` |
| `75_taohuadao` | 无（郭靖黄蓉本就在） | `923` 挪到 (30,-5.5) 避免与 `922` 重叠；4 个缺 Lua 全部补齐 |

要点：
- `add_scene_npc.py` 复制 prefab 实例时，**要求模板场景里有同 guid 的实例**。
  `Laotaitai.prefab` 只有 `02_wanzhushuyuan.unity` 有实例，且该实例**没有 stripped GameObject 块**，
  所以孙婆婆的 GameObject fileID 无法被 `m_EventTargets` 引用 —— 她的戏并进小龙女事件（902），
  场景里只作为可见 NPC 站着。
- `patch_scene_events.py` 新增 `--set-event <物体>=<新Id>`，可直接把空事件物体改成任意 EventId。
  空名字物体的 token 用它的 GameObject fileID（如破庙的 `5`/`6`）。

### 四、配置表改动

`人物.xlsx` 新增 **id=23 丘处机**（原有角色表里没有他，`Talk(23, ...)` 会没有名字/头像）。
加完必须 `python tools/moddev/jyx2mod.py configs shendiao` 重新生成 ——
`Configs/Lua/*.lua` 是生成物，手改会被下次生成覆盖。

### 五、工具链保护（重要）

`gen_story.py` 原本会 **清空整个 `Lua/` 目录再按 `STORY` 重写**，而 `STORY` 里还是旧草稿 ——
跑一次就把手写的第一章打回原形。已改成：

- 默认 **不覆盖**已存在的脚本（内容不同则跳过并汇总报告）
- 只有 `--force` 才 `clear_old_lua()` + 全量重建

`set_npc.py` 的 `LAYOUT` 还停留在换地图之前的场景名（`00_mochuanlinju` 等），
对当前 `62_pomiao`/`19_chongyanggong`/`18_gumu` 不生效，暂时无害；将来要用它必须先重写 LAYOUT。

### 六、验证

```powershell
python tools/shendiao/fill_missing_story.py     # 无输出 = 所有场景事件都有 Lua
python tools/shendiao/check_story.py           # 154 个脚本，0 错误 0 提醒
python tools/shendiao/check_guids.py           # 23 条 error，与改动前完全一致（全是既有场景引用）
python tools/moddev/jyx2mod.py configs shendiao
```

### 七、第一章剧情锚点（原著第二~四回）

`破庙(嘉兴·铁枪庙) → 桃花岛 → 重阳宫 → 古墓`

flag 链：
`序章完成 → 桃花岛学艺 → 蛤蟆功 → 郭芙欺凌 → 离岛赴终南 → 入全真 → 拜入全真 → 赵志敬收徒 → 赵志敬为难 → 决意出走 → 孙婆婆相救`

事件对照见 `jyx2/Assets/Mods/shendiao/README.md` 的「第一章剧情锚点」表。

---

# 2026-10-28 晚：故事 NPC「点名却不在场」+ 手写 prefab 实例 + 战斗接入

## 一、症状

玩家按提示跑到桃花岛后院，Lua（`922.lua`）里郭芙、武敦儒一句接一句地说话，
**场上却只有郭靖黄蓉**；跑到重阳宫找鹿清笃、古墓找孙婆婆，同样找不到对应的人。
换句话说：剧情脚本里 `Talk(41, …)` 的 41（郭芙）**从来没有在场景里存在过**。

## 二、根因（两条，都很隐蔽）

1. **事件只绑了「触发点」，没绑「人」**。`GameEvent.m_EventTargets` 决定高亮谁；
   `922`/`923` 原本指向场景里的一些杂物，`902` 的 target 曾被 `patch_scene_events.py --set-target`
   **整体覆盖**过 —— 原本指向小龙女（`33130135`）的条目被冲掉，只剩孙婆婆。
   > `--set-target` 是**覆盖**而非追加：改之前必须把要保留的旧 id 一起列出来。
2. **审计口径太窄**。老的 `audit_scene_npcs.py` 靠 prefab 路径判定「是不是人形 NPC」，
   而古墓的小龙女是 FBX 直接引用的 prefab（`xiaolongnv`），于是被判成「没有人」。

## 三、审计口径整改

`tools/shendiao/audit_scene_npcs.py` 现在：

- 从 `Configs/Lua/CharacterConfig.lua` 取 **人物表中文名集合**，场景里 PrefabInstance 的
  显示名（`m_Name` 覆盖）能对上人物表的，就算「在场 NPC」；
- 新增一栏 **「剧情点名但场上没有」**：读该事件对应的 `Lua/<EventId>.lua`，抽出所有
  `Talk(id, …)` 的 id，减去「该事件 targets 指向的人」和「场上已有的人」，剩下的就是
  玩家永远找不到的人；
- `--all --quiet` 只打印有问题的场景，方便每次改完跑一遍。

跑完全库后的结论：14 个开放场景里 `lua_miss` 全部为 0；仍有占位（`FAR`/`Sark_` 之类）
的只剩 6 个**未被 `MapConfig` 启用**的场景（`00_mochuanlinju`、`01_moqiaoshanzhuang`、
`02_wanzhushuyuan`、`03_chaensi`、`06_jiangjunfu`、`07_yingsugu`），暂不处理。

## 四、本次补上的人

| 场景 | 新增 | PrefabInstance fileID | stripped GameObject（事件要填的值） | 坐标 |
| --- | --- | --- | --- | --- |
| `75_taohuadao` | 郭芙 | `2150000000` | `2150000002` | `36.3, 0, -4` |
| `75_taohuadao` | 武敦儒 | `2150000003` | `2150000005` | `34.4, 0, -5.2` |
| `75_taohuadao` | 欧阳锋 | `2150000006` | `2150000008` | `30, 0, -4`（海边大石） |
| `18_gumu` | 鹿清笃 | `2150000000` | `2150000002` | `-13.7, 0, -12.7` |

改名（实例早就在，只是沿用模板名，人和审计都认不出）：

| 场景 | 实例 | 旧名 → 新名 | 对应事件 |
| --- | --- | --- | --- |
| `19_chongyanggong` | `1242392862` | `qiuchuji` → 丘处机 | `457` |
| `19_chongyanggong` | `1070426209` | `QZhenDiZi` → 鹿清笃 | `455` |

> `19_chongyanggong` 场景里还有 5 个 `QZhenDiZi (1..5)` 顶着模板名（分别绑 `456`/`456`…），
> 不影响交互，将来做「全真群道」事件时直接用它们。

**922/923 有没有丢原有 target？** 没有。`git diff` 显示它们原来指向 `173052893` / `491599802`，
查下去这两个 fileID 是**事件物体自己**（!u!1 上只挂了一个 MonoBehaviour，就是 GameEvent 本体），
即「target 指向自身」的占位。换成指向郭芙/武敦儒/欧阳锋是净增益。
真正被覆盖丢掉的是 `902` 的小龙女（`33130135`），已恢复并保留。

事件绑定：

| 事件 | 场景 | 新 targets |
| --- | --- | --- |
| `922`（郭芙欺凌） | `75_taohuadao` | `2150000002,2150000005`（郭芙 + 武敦儒） |
| `923`（欧阳锋传功） | `75_taohuadao` | `2150000008`（欧阳锋） |
| `902`（孙婆婆相救） | `18_gumu` | `33130135,2150000002`（小龙女 + 鹿清笃） |

要点：

- **fileID 用固定基址 `2150000000`，不用 `max+1`**。这些场景里有 `1772915332072161268` 这种
  天文数字的 fileID（Unity 的 64 位引用），继续往上加会超出某些工具的浮点精度，
  于是改成「在 21.5 亿段内手工编号」。同一场景内三个新实例按 0/3/6 递增，
  stripped Transform/GameObject 顺延 1/2。
- 鹿清笃要摆在**离 902 触发器 ~3m 内**：交互判定是 `Jyx2Player.CanSee()` ——
  玩家的 `NavMeshAgent` 必须站进触发器的 `BoxCollider`，NPC 离远了就等于没有。
- 孙婆婆（`7136715299767151795`）**没有 stripped GameObject 块**，所以无法被
  `m_EventTargets` 引用，她的戏继续并进 902；场景里只作为可见 NPC 站着。

## 五、第一次给 shendiao 接战斗

改之前全 MOD 的 154 个剧情脚本里 `TryBattle` 出现 **0 次** —— 所有「我一掌拍在他手肘上」
都是纯文本。`战斗.xlsx` 新增 6 场（生成后 `Configs/Lua/BattleConfig.lua` 第 49 行起）：

| Id | 名字 | 战场 | 经验 | 队友 | 敌人 |
| --- | --- | --- | --- | --- | --- |
| 200 | 斗鹿清笃 | `02_Battle` | 1200 | 杨过 + 孙婆婆（`0,21`） | 鹿清笃（`60`） |
| 201 | 斗赵志敬 | `02_Battle` | 2000 | 杨过（`0`） | 赵志敬（`20`） |
| 202 | 斗武氏兄弟 | `00_Battle` | 800 | 杨过（`0`） | 郭芙、武敦儒（`41,42`） |
| 203 | 斗李莫愁 | `05_Battle` | 3000 | 杨过（`0`） | 李莫愁 + 2 弟子（`70,71,72`） |
| 204 | 斗欧阳锋 | `06_Battle` | 4000 | 杨过（`0`） | 欧阳锋（`40`） |
| 205 | 斗全真群道 | `02_Battle` | 1500 | 杨过（`0`） | 鹿清笃（`60`） |

已接进剧情的三处（都是「赢了多加经验，输了照样往下走」——原著这几仗本来就是挨打）：

| 脚本 | 位置 | 调用 |
| --- | --- | --- |
| `902.lua` | 古墓墓门，孙婆婆被围攻 | `if TryBattle(200) == true then … AddExp(0,60)` |
| `901.lua` | 重阳宫，赵志敬用戒尺 | `if TryBattle(201) == true then … AddExp(0,100)` |
| `922.lua` | 桃花岛后院，郭芙命武敦儒动手 | `if TryBattle(202) == true then … AddExp(0,80)` |

`203`/`204`/`205` 先备着（李莫愁尚未在古墓场景生成实例，欧阳锋的 923 是「传功」不该打，
全真群道留给「逃出重阳宫」那段）。**接 204 前必须确认 `GetFlagInt("蛤蟆功") == 1`**，
否则刚磕头认了义父就把义父打了。

> `TryBattle` 的返回值：`true` = 胜利（`Jyx2LuaBridge.TryBattleWithConfig` 里
> `isWin = (ret == BattleResult.Win)`）。工程惯例是 `if TryBattle(N) == true then goto label`
> 或 `== false`，与 `JYX2/Lua/ka*.lua` 写法一致。

## 六、新工具（4 个，都在 `tools/shendiao/`）

| 工具 | 解决什么 |
| --- | --- |
| `audit_scene_npcs.py`（重写） | NPC 在场性 + 「剧情点名但场上没有」 |
| `add_prefab.py`（新） | 往场景插**任意** prefab 实例，不要求别的场景摆过（`add_scene_npc.py` 的硬限制） |
| `edit_instance.py`（新） | 改实例的显示名 / 局部坐标 / 朝向（`rename_instance.py` 已并入并删除） |
| `lint_lua.py`（新） | 剧情脚本语法体检 —— 工程里**没有 lua/luac**，`jyx2mod check` 只查生成物 |
| `check_scene_fileids.py`（新） | 场景 YAML 内部 fileID 自引用完整性，不依赖 Unity 就能发现断链 |

`add_prefab.py` 的实现要点（手改 YAML 时照着抄）：读 prefab 文件找根 GameObject /
根 Transform 的 fileID → 写 `!u!1001 PrefabInstance`（`m_Modifications` 里给
`m_Name`/`m_LocalPosition.*`/`m_LocalRotation.*`/`m_LocalEulerAnglesHint.y`）→
写 `stripped !u!4 Transform` + `stripped !u!1 GameObject`（两者的
`m_CorrespondingSourceObject` 指向 prefab 根，`m_PrefabInstance` 指向新 1001）
→ 把 stripped Transform 加进父节点的 `m_Children`。
**stripped GameObject 的 fileID 才是 `m_EventTargets` 该填的值**（不是 1001 的）。

`lint_lua.py` 与 `check_scene_fileids.py` 都用「故意做坏一份临时副本」验证过能报错
（`_zz_test*.lua`、`_tmp_test.unity`，验证完已删）。

## 七、验证（全部已跑过，结果贴在这里）

```powershell
python tools/moddev/jyx2mod.py configs shendiao            # 战斗表 -> BattleConfig.lua
python tools/shendiao/lint_lua.py --battle                 # 检查 154 个脚本，有问题 0 个
python tools/shendiao/check_scene_fileids.py               # 检查 37 个场景，问题 0 条
python tools/shendiao/audit_scene_npcs.py --all --quiet    # 见下
python tools/moddev/jyx2mod.py check shendiao              # [ok] 一切正常
python tools/shendiao/check_story.py                       # 154 个脚本：0 错误 0 提醒
python tools/moddev/jyx2mod.py unity shendiao              # Unity 真解析一遍场景
```

### 1. Unity 导出（最硬的验证）

`JyX2ModCli` 跑完输出 `[ok] 导出完成 C:\Games\jynew\Export\shendiao`
（`shendiao_maps` 363MB + `shendiao_mod` 78MB），说明**手写的 PrefabInstance /
stripped 块被 Unity 正常反序列化**。再看 `Logs/unity_build_shendiao.log` 的
`Broken text PPtr`（fileID 指向不存在的对象时 Unity 才会打这条）：

```
x172  02_wanzhushuyuan.unity
x 16  01_moqiaoshanzhuang.unity
x 10  00_mochuanlinju.unity
```

**只出现在 3 个未启用场景**（模板自带的历史垃圾）。
改过的 `18_gumu` / `75_taohuadao` / `19_chongyanggong` / `62_pomiao` **一条都没有**。

另外日志里的 `Script attached to 'Prefab_3 (1)' … missing`（`19_chongyanggong` 2 条）、
`'Cube (x)' … missing`（`80_jueqinggudi` 17 条、`47_yidengju` 70 条）都是**既有**问题：
模板场景里还挂着已删掉/未导入的脚本，与本次改动无关。

### 2. NPC 审计结果

- 已启用场景（`MapConfig` 里有 15 个）：**问题事件 0**。
- 全部 17 个问题事件都落在 6 个**未在 `MapConfig` 注册**的老场景上：
  `00_mochuanlinju`(2)、`01_moqiaoshanzhuang`(3，另缺孙婆婆一个)、`02_wanzhushuyuan`(7)、
  `03_chaensi`(1)、`06_jiangjunfu`(3)、`07_yingsugu`(1)。玩家到不了，暂不管。

### 3. Unity 路径（踩坑记录）

Unity 装的是**自定义路径** `C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe`，
不在 `find_unity()` 的探测目录（它只找 `Unity\Hub\Editor\<ver>`）里，必须：

```powershell
$env:JYX2_UNITY='C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe'
python tools/moddev/jyx2mod.py unity shendiao
```

`--unity "带空格的路径"` 经 `Start-Process -ArgumentList` 会被拆成两个参数
（报 `unrecognized arguments: Files\Unity ...`），**用环境变量**。
首次导出会全量重导 shader，约 4 分钟；之后快很多。

## 八、遗留

- 场景结构已被 Unity 验证，但**运行时手感没人验证过**：新 NPC 的朝向是否背对玩家、
  `y=0` 的贴地高度在本场景是否正确、923 的欧阳锋是否挡路、战斗 200-205 的敌人能不能正常加载。
  这些只能进游戏看（`python tools/moddev/jyx2mod.py install shendiao --src Export` 后跑）。
- 新存档验证：旧存档的 `WorldMapSaveData.areaMask` 可能是 0，会导致 NavMesh 失效、
  「看得见但走不动」，与本次改动无关但会让人误判。
- `62_pomiao` 这轮的 `git diff` 有 3.7 万行（批量改 `m_Layer 0→20`、触发器尺寸等），
  是上一个会话用脚本刷的**真实改动**，不是行尾噪声，提交时别被吓到。






---

# 2026-10-28 深夜：第一章「打不通」的根因 + 第二章《神雕侠》

## 一、症状

第一章做到「寒玉床」（`442`）就断了：`玉女心经`（`219`）、`击退李莫愁`（`217`）怎么都触发不了，
`第一章完成` 永远为 0，后面所有章节的前置条件全部卡死。

## 二、根因：103 / 153 个 Lua 脚本是「孤儿」

Lua 剧情脚本是**按事件 Id 全局查找**的（`LuaExecutor` 从 `Mods/<mod>/Lua/<id>.lua` 加载），
但事件 Id 必须出现在**已注册地图**的场景里才会被 `GameEvent` 触发。

`MapConfig.lua` 只注册 14 张图；而 `219`（玉女心经）、`217`（斗李莫愁）、`20/22/24/28/210/113/1210`
（入墓、初见龙女、孙婆婆之死、拜师、寒玉床旧版）全都挂在 **`02_wanzhushuyuan`** 上 ——
那张图在 shendiao 里**没有注册**，玩家永远进不去。

统计口径（启用场景的事件 Id 集合 × Lua 文件名集合）：

```
启用场景事件 id 数: 50    Lua 脚本数: 153
孤儿脚本(不可达) 103: 0,2,3,4,10,11,13,18,20,22,24,28,30,...217,219,1210,1911
场景有事件但无 Lua: 0
```

103 个孤儿里大多（约 60 个）是「此地尚未探明」占位，真正有剧情的是：
`0/2/3/4`（序章庙祝/木箱）、`18`（鹿清笃结怨）、`20/22/24/28/113/210/1210`（古墓线前半）、
`217/219`（李莫愁 + 玉女心经）、`726/850/851`（杂项）。

其中古墓线前半（20/22/24/210/1210）的内容**已被启用场景里的 `902`、`442` 覆盖**，
所以真正需要迁移的只有 **`217`、`219`** 两个。

## 三、修复：把 217 / 219 迁到 `18_gumu` 的空闲事件上

`18_gumu` 有 4 个 GameEvent、其中 2 个空闲（`m_InteractiveEventId: -1`，物体名就叫 `1` 和 `4`）：

| 事件物体 | 原位置 | 改成 | target |
| --- | --- | --- | --- |
| `1` | (-15.0, 0.5, -10.2) | inter **217**（斗李莫愁） | 新加的「李莫愁」（`EmeiDizi.prefab`，strippedGO `2150000005`） |
| `4` | (19.5, 0.5, -12.2) | inter **219**（玉女心经） | 场景原有的 `Shiguan` 石棺（`480963069`） |

配套改动：

- 删掉场景里那个多余的 **「杨过」实例**（`1743472808`）—— 主角自己就叫杨过，
  场上再站一个同名 NPC 只会让玩家困惑；它原本正是 217 的 target。
- `217.lua` 前置从 `孙婆婆之死`（没人设置，孤儿脚本 28 才设）改成 `孙婆婆相救`（`902` 设置）；
  `TryBattle(70)` → **`TryBattle(203)`** —— 70 是**人物 Id**，不是战斗 Id，这是老脚本的硬错。
  两个分支都补上 `SetFlagInt("孙婆婆之死", 1)` 保持向后兼容。
- `219.lua` 首句改成「石棺侧面刻着密密麻麻的小字」（target 是石棺），
  结尾提示改成「接下来：终南山后的山洞」。

## 四、第二章《神雕侠》（`07_shandong`）

原著顺序是「大胜关英雄会 → 断臂 → 神雕」，但 shendiao 只有 14 张图、**没有大胜关/襄阳**，
所以第二章直接落在「神雕山洞」，断臂用 `389` 的旁白交代（一行提示，不占场景）。

| 事件 | 类型 | 位置 | target | 内容 |
| --- | --- | --- | --- | --- |
| `389` | enter | (16.1, 0.5, -11.2) | - | 断臂独白，设 `入神雕洞` |
| `390` | enter | (9.2, 0.5, -10.7) | - | 洞中爪印，设 `洞中爪印` |
| `837` | inter | (5.9, 0.5, -10.5) | 大雕 `1951046537` | 神雕衔木剑逼招，**TryBattle(206)**，设 `神雕试剑` |
| `838` | inter | (0.0, 0.5, -21.5) | 白骨 `1380787743` | 白骨遗刻「仰慕剑魔遗风」，设 `白骨遗刻` |
| `836` | inter | (-21.1, 0.5, 9.5) | 白骨 `1291385134` | 剑冢石壁三剑，得【玄铁重剑】41、学「玄铁剑法」40，设 `得玄铁重剑` |
| `394` | inter | (-15.1, 0.5, -23.6) | 独孤求败 `2150000002` | 练重剑，加攻/防/血/内，设 `第二章完成` |

场景侧改动：

- `837`/`838` 两个触发器**挪位置**去贴已有物体（`--move`）：837 从 (8.1,5.5) 挪到雕旁
  1.3m，838 从 (1.5,-22.9) 挪到白骨 1.8m。其余沿用 `--collider 3.5` + `--set-layer 20 --trigger`。
- 新增 **「独孤求败」**（`Fengqingyang.prefab`，`add_prefab`），删掉模板里的 **「杨过」实例**（`1602630064`）
  —— 同 18_gumu 的理由，且 `394` 的台词本来就是对着「剑魔遗蜕」说的。

## 五、新人物 / 新战斗 / 新 ModelAsset

神雕要参战，就必须有**人物条目 + ModelAsset**（`RoleInstance` 用 `ModelAsset.Get(ModelFileKey)`
按 ScriptableObject 的 **m_Name** 查，查不到会 `LogError` 后**随机挑一个模型**）：

- `人物.xlsx` 第 67 行：`24 神雕`，等级 32、血 4000、攻 160、技能 `{40,600}`（玄铁剑法），
  `ModelFileKey = 神雕`
- 新建 `jyx2/Assets/Mods/shendiao/Models/神雕.asset` + `.meta`（新 GUID `dfe114cb…`），
  `m_View` 指向 `BattleNpc/Diao.prefab`（guid `7cb2047e6a2a8cf46bb6b808b4950214`，
  根 GameObject `1455276952132468255`），结构照抄 `Models/丘处机.asset`（685 字节，只有 `m_View` 关键）
- `战斗.xlsx` 第 38 行：`206 斗神雕 / 02_Battle / 3500 / 23 / 队友 -1 / 自动队友 0 / 敌人 24`

改完必须重跑 `python tools/moddev/jyx2mod.py configs shendiao`，否则 Lua 配置还是旧表。

## 六、新工具：`resolve_target.py`

`m_EventTargets` 要填的是 **stripped GameObject 的 fileID**，不是 `PrefabInstance` 的 instanceID
（上一轮踩过的坑）。`add_prefab.py` 只打印**自己新建**实例的 id；场景里原有的物体
（石棺、白骨、大雕）没法查，只能翻 YAML 里 `m_PrefabInstance: {fileID: <instanceID>}` 的块。

```powershell
python tools/shendiao/resolve_target.py --scene <scene.unity>              # 全列
python tools/shendiao/resolve_target.py --scene <scene.unity> --name 大雕   # 按名字
```

实现：先扫全部 `!u!1001` 取 instanceID/名字/源 prefab，再扫 stripped `!u!1`/`!u!4` 块的
`m_PrefabInstance` 反查，输出 `instanceID / 名字 / strippedGO / strippedTr`。

## 七、验证（已跑，结果贴在这里）

```
python tools/shendiao/lint_lua.py --battle        -> 检查 154 个脚本，有问题 0 个
python tools/shendiao/check_story.py              -> 人物 63 / 物品 75 / 武功 29 / 战斗 34；154 脚本 0 错 0 提醒
python tools/shendiao/check_scene_fileids.py      -> 检查 37 个场景，问题 0 条
python tools/moddev/jyx2mod.py check shendiao     -> [ok] 一切正常
python tools/shendiao/audit_scene_npcs.py <scene> -> 18_gumu 4 事件 0 问题；07_shandong 9 事件 0 问题
```

`18_gumu` 现在的目标链：`902`(小龙女+鹿清笃) / `442`(Shiguan (1)) / `217`(李莫愁 0.5m) / `219`(石棺 0.3m)。
`07_shandong`：`837`(大雕 1.3m) / `838`(白骨 1.8m) / `836`(白骨 2.8m) / `394`(独孤求败 0.5m)。

## 八、下一步

- 第三章 绝情谷（`22_jueqinggu` 5 个交互点全空、无 NPC）：公孙止、公孙绿萼、樊一翁、裘千尺
- 第四章 程英居 / 铁掌山 / 黑龙潭 / 一灯居 / 百花谷（`47_yidengju` 事件 Id 全空，要 `--set-event` 分配）
- 第五章 华山派 / 思过崖；第六章 绝情谷底（`80_jueqinggudi`，小龙女+杨过已在场）
- 打包（Unity 导出 AB）留到所有章节写完后统一做



---

# 2026-10-28 凌晨：第三章《绝情谷》

## 一、踩到的新坑：`--move` 写的是**局部**坐标

`patch_scene_events.py --move <事件>=x,y,z` 改的是 Transform 的 `m_LocalPosition`，
**不是世界坐标**。`22_jueqinggu` 的事件宿主父节点带 `(-40.6, -13.2, 0)` 的偏移，
于是：

```
--move 399=34.2,5.5,25.6   ->   世界坐标 (-6.4, -7.7, 25.6)   ← y 掉到地下
audit 直接报 FAR(42.6m)，5 个事件全红
```

判断世界坐标的办法：`audit_scene_npcs.py` 输出的「触发器位置」是**世界坐标**
（它已经把父链算进去了）。写 `--move` 之前先跑一次 audit 抄数值，或者
「目标世界坐标 − audit 显示值 + 当前局部值」反推。

顺带修了一个误判：我用「局部 y − 玩家 y > 1.5」筛浮空触发器，
`22_jueqinggu` 的 6 个事件全被筛出来，其实它们的世界 y 是 5.3、完全正常。
**筛浮空必须用世界坐标**（父链求和），不能用局部 `m_LocalPosition`。

## 二、绝情谷的 5 个挂点（`22_jueqinggu`）

场景无 `NPC` 父节点，实例挂在 `Others`（Transform `145663892`）下。

| EventId | 世界坐标 | 目标 | 内容 |
| --- | --- | --- | --- |
| `399` | (-6.4, 5.3, 25.6) | 公孙止 `2150000002` | 谷口被请入谷，设 `入绝情谷` |
| `857` | (-7.9, 5.3, 2.2) | 公孙绿萼 `2150000005` | 情花有刺，设 `情花之毒` |
| `856` | (-8.1, 5.3, -2.9) | 樊一翁 `2150000008` | 盘问来历 + 两条禁令，设 `见谷主` |
| `400` | (18.8, 5.3, -6.4) | 木箱 `Box_3` `2933597162507430682` | 得【情花】122 与半封信，设 `得情花` |
| `401` | (24.4, 5.3, -6.4) | 裘千尺 `2150000011` | 枯井授破刀之法，**TryBattle(207)**，设 `击退公孙止`/`第三章完成` |

局部坐标（`--move` 用这个）= 世界坐标 + (40.6, 13.2, 0)：
`399=(34.2,18.5,25.6)`、`857=(32.7,18.5,2.2)`、`856=(32.5,18.5,-2.9)`、
`400=(59.4,18.5,-6.4)`、`401=(65,18.5,-6.4)`。

## 三、新人物 / 新战斗

| Id | 人物 | 造型 prefab | 说明 |
| --- | --- | --- | --- |
| 26 | 公孙止 | `Huangyaoshi.prefab` | 等级 42 / 血 2600 / 落英神剑掌 60；**有 ModelAsset**，要参战 |
| 27 | 公孙绿萼 | `EmeiDizi.prefab` | 等级 26 / 只说话 |
| 28 | 樊一翁 | `TiezhangDizi.prefab` | 等级 35 / 只说话 |
| 29 | 裘千尺 | `StoryNpc/Laotaitai.prefab` | 等级 40 / 暗器 97 |

- `Models/公孙止.asset`（GUID `2053dd30…`）的 `m_View` → `Huangyaoshi.prefab`
  根 GameObject `6071463157815892279`（guid `ddac0a77…`）
- `战斗.xlsx` 第 39 行：`207 斗公孙止 / 05_Battle / 3800 / 敌人 26`

## 四、验证

```
lint_lua --battle   -> 154 脚本 0 问题
check_story         -> 人物 67 / 战斗 35；154 脚本 0 错 0 提醒
check_scene_fileids -> 37 场景 0 问题
audit 22_jueqinggu  -> 5 事件 0 问题（399/857/856/401 目标 0.0m，400 木箱 0.7m）
```

## 五、下一步

第四章 程英居 / 铁掌山 / 黑龙潭 / 一灯居 / 百花谷 —— 注意 `47_yidengju`、
`21_heilongtan`、`81_siguoya`、`20_baihuagu` 里有大量 `m_*EventId: -1` 的空事件物体，
要用 `patch_scene_events.py --set-event <物体名>=<新Id>` 先分配 Id 再写 Lua。

---

# 2026-10-28 凌晨：第四章《南国旧友》

五个场景一次做完：程英居 `45`、一灯居 `47`、黑龙潭 `21`、百花谷 `20`、铁掌山 `48`。

## 一、这一轮修掉的两个工具 bug

### 1. `patch_scene_events.py` 不认 `m_EventTargets: []`

`21_heilongtan` 的 421 事件明明有 `m_InteractiveEventId: 421`，`--set-target 421=…`
却**静默跳过**（不报错、不算失败）。原因是空列表在 YAML 里写成

```yaml
  m_EventTargets: []
```

而旧正则是 `(^  m_EventTargets:\n)`，要求 `:` 后立刻换行 —— `[]` 形式永远匹配不上。
`subn` 返回 0 次替换，脚本照常打印"已写入"。

修复：`(^  m_EventTargets:)(?: \[\])?\n(...)`，改完 `--set-target` 对空列表事件也能生效，
`--clear-target` 同理（保留 `m_EventTargets:` + 空列表的合法写法）。

### 2. `edit_instance.py --name` 可能改到**子对象**的 m_Name

一个 prefab 实例的 `m_Modifications` 里可能有多条 `propertyPath: m_Name`
（根 GameObject 一条、内部子对象各一条）。`edit_instance.py` 取的是**第一条**，
于是 `45_chengyingju` 的程英改完名字后：

```
audit 仍显示 target "ChengYing"，并报「剧情点名但场上没有：程英(90)」
```

实际被改的是 target `2452833730956876070`（prefab 内部子对象）的 m_Name，
根 GameObject（`8267541098496238243`）还是 `ChengYing`。临时用脚本直接改 YAML 解决。

**遗留**：`edit_instance.py` 应当按「stripped Transform 的 m_CorrespondingSourceObject」
找到实例根 GameObject 的 fileID，只改 target 等于它的那条 m_Name。`resolve_target.py`
已经把根 GO 查出来了，接一下就行。改名前先跑 `audit` 或 `resolve_target --name` 复核。

## 二、重复 NPC 陷阱：模板里可能已经有这个模型

`20_baihuagu` 里本来就有 `zhoubotong`（`592901478`, (13, 4.96, 7)），
`48_tiezhangshan` 里本来就有 `qiuqianren`（`921350305`, (2.11, 0.39, 10.18)）。
用 `add_prefab` 再摆一个「周伯通」/「裘千仞」会**两只模型站在同一个点上**。

正确做法（本轮采用）：

1. `resolve_target.py --name <模板名>` 先确认有没有同款实例及其 instanceID；
2. 有 → `edit_instance.py --instance <id> --name 中文名` 改名即可（m_EventTargets 指向的是
   stripped GameObject，改名不影响已绑定的 target）；
3. 我多摆的那两个用 `remove_scene_node.py --instance` 删掉。

`48` 的 `qiuqianren` 改名成「铁掌帮弟子」后正好服务山门事件 `450`，
新加的「裘千仞」放山顶大殿服务 `453`。

## 三、空闲事件的分配（`--set-event`）

`47_yidengju` / `21_heilongtan` / `20_baihuagu` 里有大量 `m_*EventId: -1` 的空事件物体，
物体名就是序号（`0`、`1`、`4`…）。分配方式：

```powershell
python tools/shendiao/patch_scene_events.py --scene <scene.unity> \
    --set-event 0=424 --set-target 0=<strippedGO> \
    --collider 0=3.5,3.5,3.5 --set-layer 20 --trigger --apply
```

| 场景 | 物体名 → 事件 Id | 目标 |
| --- | --- | --- |
| `47_yidengju` | `0` → `424` | 一灯 `2150000002` |
| `21_heilongtan` | `4` → `421`、`1` → `422`、`2` → `423` | 瑛姑 `2150000002` |
| `20_baihuagu` | （`405` 原本就有） | 周伯通 `592901480` |

注意：`--set-event` 与 `--collider` 在同一次调用里时，`resolve()` 用的是**原始**事件 Id，
所以同一批里两者都要用**物体名**（或旧 Id）当 token，不能一个用新 Id 一个用旧名。

`21` 的 `423` 原本离瑛姑 3.1m（`audit` 判 `FAR`），`--move 423=2.0,4.5,-2.6` 拉到 1.6m。

## 四、第四章锚点

| 场景 | EventId | 内容 |
| --- | --- | --- |
| `45_chengyingju` | `402` | 程英疗伤、教「玉箫剑法」(71)，设 `程英相救` |
| `45_chengyingju` | `906` | 陆无双教「分花拂柳手」(181)，设 `遇陆无双` |
| `47_yidengju` | `424` | 一灯传「九阴疗伤篇」(32)、加血 120，设 `见一灯` |
| `21_heilongtan` | `421` | 瑛姑托话，设 `见瑛姑` |
| `21_heilongtan` | `422` | 淤泥旁白，设 `黑龙潭淤泥` |
| `21_heilongtan` | `423` | 白狐，得【玉蜂浆】37，设 `灵狐` |
| `20_baihuagu` | `405` | 周伯通·左右互搏（攻+20 轻功+10），设 `遇周伯通` |
| `48_tiezhangshan` | `450` | 山门弟子，设 `上铁掌山` |
| `48_tiezhangshan` | `448/449/454/907` | 寨墙、哨口、兵器库、界石旁白 |
| `48_tiezhangshan` | `453` | 斗裘千仞 **208**，设 `击退裘千仞` / `第四章完成` |

新人物：35 陆无双、36 周伯通、37 瑛姑、38 一灯、39 裘千仞（人物表 72-76 行）；
`Models/裘千仞.asset`（GUID `87e53210…` → `Qiuqianren.prefab`）；战斗 `208 斗裘千仞 / 02_Battle / 4200`。

## 五、验证

```
configs shendiao       -> 7 张表
lint_lua --battle      -> 158 脚本 0 问题
check_story            -> 人物 72 / 物品 75 / 武功 29 / 战斗 36；158 脚本 0 错 0 提醒
check_scene_fileids    -> 37 场景 0 问题
jyx2mod check shendiao -> [ok]
audit --all --quiet    -> 20/21/22/45/47/48 均 0 问题，NPC 全部在场
```

## 六、下一步

第五章 华山派 `57_huashanpai` / 思过崖 `81_siguoya`（洪七公与欧阳锋、华山论剑）
→ 第六章 绝情谷底 `80_jueqinggudi`（十六年之约，小龙女、杨过已在场）→ 最后统一打包 AB。


---

# 2026-10-28 凌晨：第五、六章（华山绝顶 / 十六年之约）—— 主线第一版走通

## 一、第五章 华山派 `57_huashanpai`

场景原本就摆了 5 个「华山弟子N」实例（`192` 的五个触发点各一个），
所以只补了三个真正需要露脸的 NPC 在 `NPC` 节点下：

| 实例 | prefab | 局部坐标 | strippedGO |
| --- | --- | --- | --- |
| 华山派弟子 | `HuashanDizi.prefab` | (26.6, 0, 0) | `2150000002` |
| 洪七公 | `Hongqigong.prefab` | (39.1, 0, 8.4) | `2150000005` |
| 欧阳锋 | `Ouyangfeng.prefab` | (42.4, 0, -2.0) | `2150000008` |

事件绑定（`--collider 3.5` + `--set-layer 20 --trigger` 一并刷）：

| EventId | 剧情 | flag |
| --- | --- | --- |
| `195` | 华山封山，弟子拦路（透露「两个老头打了三天三夜」） | `华山放行` |
| `192` | 雪道旁白（5 个触发点共用同一脚本） | `上华山` |
| `913` | 洪七公烤叫花鸡 → 学「打狗棒法」41 | `遇洪七公` |
| `914` | **UseItem 事件**：用物品（玉蜂浆）换酒，回赠玉蜂浆 + 体力 | — |
| `915` | 斗欧阳锋 **204**，洪七公点破「他是欧阳锋」 | `华山遇西毒` |

`914` 是 `UseItemEventId`（用物品触发），脚本里不判断具体物品 —— 反正玩家手里只有玉蜂浆。

## 二、第六章 思过崖 `81_siguoya` + 绝情谷底 `80_jueqinggudi`

`81_siguoya` 有 3 个事件：`282`/`283` 是 enter（踏入即触发），物体名 `2` 是空事件 → `--set-event 2=428`。
崖顶加了两尊「遗蜕」：洪七公 `2150000002` (15.8, 0, -6.5)、欧阳锋 `2150000005` (16.7, 0, -6.5)
（两人面向对方，`--rot-y 90 / 270`），`428` 的 target 绑洪七公。

`80_jueqinggudi` 只有 `435`(enter)、`436`(inter，target 已经是小龙女 `624508379`)。
场景里另有一个**与主角同名**的「杨过」实例 `1723773891`，十六年后重逢的戏不需要它 → 删除
（`436` 的 target 是小龙女，不受影响）。

| 场景 | EventId | 剧情 |
| --- | --- | --- |
| `81_siguoya` | `282` / `283` | 入思过崖、崖顶两人比掌（旁白，不打断） |
| `81_siguoya` | `428` | 洪七公与欧阳锋相拥而逝，`第五章完成` + 经验 800 + 品德 5 |
| `80_jueqinggudi` | `435` | 断肠崖跳下、地缝通向谷底，`入绝情谷底` |
| `80_jueqinggudi` | `436` | 竹屋前重逢、墙上刻满划痕，`重逢` + `全篇完成` + 经验 1000 |

新人物只有 1 个：`43 华山派弟子`（等级 22，只说话，不需要 ModelAsset）。

## 三、全篇 flag 链（已闭环）

```
序章完成 → 桃花岛学艺 → 蛤蟆功 → 郭芙欺凌 → 离岛赴终南 → 入全真 → 拜入全真 →
赵志敬收徒 → 赵志敬为难 → 决意出走 → 孙婆婆相救 → 击退李莫愁 → 玉女心经 →
第一章完成 → 入神雕洞 → 洞中爪印 → 神雕试剑 → 白骨遗刻 → 得玄铁重剑 → 第二章完成 →
入绝情谷 → 情花之毒 → 见谷主 → 得情花 → 击退公孙止 → 第三章完成 →
程英相救 → 遇陆无双 → 见一灯 → 见瑛姑 → 遇周伯通 → 上铁掌山 → 击退裘千仞 → 第四章完成 →
上华山 → 华山放行 → 遇洪七公 → 华山遇西毒 → 入思过崖 → 第五章完成 →
入绝情谷底 → 重逢 → 全篇完成
```

## 四、验证

```
configs shendiao       -> 7 张表
lint_lua --battle      -> 159 脚本 0 问题
check_story            -> 人物 73 / 物品 75 / 武功 29 / 战斗 36；159 脚本 0 错 0 提醒
check_scene_fileids    -> 37 场景 0 问题
jyx2mod check shendiao -> [ok]
audit 57_huashanpai    -> 8 事件 0 问题（华山派弟子 / 洪七公 / 欧阳锋 全在场）
audit 81_siguoya       -> 3 事件 0 问题（428 → 洪七公 0.8m）
audit 80_jueqinggudi   -> 2 事件 0 问题（436 → 小龙女 0.4m）
```


---

# 2026-10-28 凌晨：打包（AB 导出）与「Models/Skills 不进包」的坑

## 一、导出命令

```powershell
$env:JYX2_UNITY='C:\Program Files\Unity 2020.3.32f1c1\Editor\Unity.exe'
python tools/moddev/jyx2mod.py unity shendiao
```

产物 `Export/shendiao/`：`shendiao_maps` 363.2 MB、`shendiao_mod` 78.8 MB（时间 23:45-23:46）。
日志 `Logs/unity_build_shendiao.log` 里 `[Jyx2ModCli] 打包 shendiao_mod（289 个资源）`。

## 二、坑：`Models/*.asset` / `Skills/*.asset` 默认**不会**进包

第一次导出（23:39）时 `shendiao_mod` 只有 35.2 MB，manifest 里
`Assets/Mods/shendiao/Models/*.asset` 一条都没有。原因是这两个目录里的资源
**只被代码按名字查**，没有任何 prefab/场景引用它们：

```csharp
// Jyx2ResourceHelper.Init()
var allModels = await ResLoader.LoadAssets<ModelAsset>("Assets/Models/");
Jyx2SkillDisplayAsset.All = await ResLoader.LoadAssets<Jyx2SkillDisplayAsset>("Assets/Skills/");
// ResLoader 会把 "assets/" 重写成 "assets/mods/<modId>/"（ResLoader.cs:242）
```

Unity 的 AssetBundle 只收「显式打了 bundle 名」+「它们引用到的依赖」。
没人引用 `ModelAsset`，所以它们既不显式、也不依赖 → 不进包。
运行时 `ModelAsset.Get(roleName)` 找不到就 `LogError` 然后
`Tools.GetRandomElement(All)` —— **战斗里的敌人会变成别人**，而且不报显眼错误。

修法：给这些 `.meta` 显式写上 bundle 名（47 个 Models + 29 个 Skills，共 76 个）：

```yaml
NativeFormatImporter:
  ...
  assetBundleName: shendiao_mod
  assetBundleVariant:
```

改完 `jyx2mod check shendiao` 会显示 `AssetBundle: shendiao_maps(45), shendiao_mod(85)`，
重新导出后 `shendiao_mod` 从 **35.2 MB 涨到 78.8 MB**（模型依赖被带进来），
构建日志从 206 个资源变成 289 个 —— 这是「真的进包了」的直接证据。

> 注意：Unity 生成的 `*.manifest` 文本里 **不会**列出这些后来加进来的资源
> （它只写显式 + 部分依赖），所以别用「manifest 里有没有 Models」来判断，
> 要看 bundle 体积和构建日志的资源数。

## 三、还要在游戏里验的（明天）

1. 战斗 206（斗神雕）/ 207（斗公孙止）/ 208（斗裘千仞）的敌人模型是否正常 ——
   这三场分别依赖 `Models/神雕.asset`、`Models/公孙止.asset`、`Models/裘千仞.asset`。
2. 战斗 200-205 的老战斗是否也受影响（它们依赖上一轮加的 `Models/丘处机.asset` 等，
   这批这次一并打了 bundle）。
3. 第二~六章新 NPC 的朝向 / 贴地 / 是否挡路。
4. 华山 `81_siguoya` 崖顶、绝情谷底 `80` 的 NavMesh 可达性。
5. **用新存档**（旧档 `WorldMapSaveData.areaMask=0` 会让 NavMesh 失效）。

## 四、安装（已执行）

```powershell
$env:JYX2_GAME_DIR='C:\Program Files (x86)\Steam\steamapps\common\群侠传，启动！'
python tools/moddev/jyx2mod.py install shendiao --src Export
```

游戏目录是自动探测到的（`wuxia_launch.exe` 所在目录），`--src Export` 和
`--src Export/shendiao` 都能用（`resolve_export_dir()` 两个都认）。

结果：`<游戏>\wuxia_launch_Data\mods\shendiao` 共 442.0 MB

| 文件 | 大小 | 时间 |
| --- | --- | --- |
| `shendiao_maps` | 363.2 MB | 10-28 23:46 |
| `shendiao_mod` | 78.8 MB | 10-28 23:45 |
| `shendiao.xml` | 描述文件 | CreateTime 20261028 23:44:31 |

旧包（135.8 MB / 35.1 MB，21:46 那版**不含 Models**）已被 `rmtree` 覆盖清理；
`AppData\LocalLow\jynew\群侠传启动\mods` 下没有残留（`--persistent` 才是那个位置，本次没用）。
`jyx2mod list` 已能看到：`wuxia_launch_Data\mods: sample, shendiao`。

> 注意 `shendiao.xml` 里 `Version=""` 是空的（`ModSetting.asset` 没填版本号），
> 不影响加载，只是 MOD 选择界面不显示版本。

## 五、仍然没验证的（只能进游戏看）

- 强行进谷底/崖顶的**可达性**：`81_siguoya` 的 `282/283` 在 y=0、`428` 在 y=0.8，
  玩家出生 y≈0.16，数值上没问题，但华山那张图的 NavMesh 是否连到崖顶没实测过。
- 战斗 206（斗神雕）/ 207（斗公孙止）/ 208（斗裘千仞）的敌人模型能不能正常加载 ——
  三个都补了 ModelAsset，但只有 Unity 里实跑才知道。
- 新 NPC 的朝向、贴地高度、以及是否挡路。
- 存档：改动场景后必须用**新存档**（旧档 `areaMask=0` 会让 NavMesh 失效，人物看得见走不动）。

---

# 10-29 修复：进战斗「一个人都没有」

## 一、症状

第一场战斗（`202` 斗武氏兄弟）切进 `00_Battle` 后**战场空白**：BGM 变了，
但主角和敌人都没有，没有战斗 HUD，点哪里都没反应。

`Player.log`（09:36 那次）里只有三行有用信息：

```
-----------BattleLoader.InitBattle
目标技能展现配置不存在, 技能名:[=B5]
NullReferenceException
  at BattleRole.SwitchSkillTo (Jyx2.SkillInstance skill)
  at BattleRole+<RefreshModel>d__47.MoveNext ()
  at BattleLoader+<InitBattle>d__19.MoveNext ()
```

`=B5` 出现两次（我方杨过 + 敌方程各崩一次）。

## 二、根因（两层，缺一不可）

链路：`BattleLoader.CreateRole` → `BattleRole.RefreshModel()`
→ `DataInstance.SwitchAnimationToSkill(Wugongs[0])` → `SwitchSkillTo(skill)`
→ `skill.GetDisplay()` 返回 null → `display.weaponCode` 抛 NRE。

异常抛在 `InitBattle` 的**协程**里，协程当场中断 —— `roles.Add()`、
`BattleManager.Instance.StartBattle()` 全都没执行，所以是整场没人。

`GetDisplay()`：

```csharp
if(!string.IsNullOrWhiteSpace(Data.DisplayFileName))
    return Jyx2SkillDisplayAsset.Get(Data.DisplayFileName);   // 填了就必须真实存在
else
    return Jyx2SkillDisplayAsset.Get(Data.Name);
```

`Jyx2SkillDisplayAsset.Get` 是 `All.FirstOrDefault(s => s.name == skillName)`，找不到返回 null。

**第一层**：武功表「显示文件名」列整列是字面文本 `=B5`/`=B6`/…（当初想写成 Excel 公式
但从未求值，`data_type` 是 `s` 不是 `f`，所以 `data_only=True` 也读不出值）。
29 个技能全部对不上。

**第二层**：就算这列留空回退到技能名，也查不到 —— `Skills/` 目录是从 SAMPLE
整个复制过来的，29 个 asset 里只有 8 个是通用条目（普通攻击/野狼/黑熊/毒蛇/用毒/解毒/医疗/暗器），
shendiao 自己的 21 个技能（全真剑法、玉女剑法、蛤蟆功、打狗棒法、黯然销魂掌…）**一个都没有**。

## 三、修复

1. `tools/shendiao/gen_skill_displays.py --mod shendiao --apply`
   → 按显式映射表复制同武器类型的模板 asset（剑/刀/长柄/空手/医疗/暗器），改 `m_Name`、
   换新 GUID、写 `assetBundleName: shendiao_mod`，生成 21 个。
2. `tools/shendiao/gen_model_assets.py --mod shendiao --apply`
   → 顺带查出**另外 8 个角色也没有 ModelAsset**（公孙绿萼、樊一翁、裘千尺、陆无双、
   周伯通、瑛姑、一灯、华山派弟子）—— 这些在场景/战斗里会随机变成别人，已一并生成
   （模板：程英/庙祝/孙婆婆/郭芙/柯镇恶/李莫愁/寿眉大师/鹿清笃）。
3. `武功.xlsx` H 列改成静态技能名（29 行），重新 `jyx2mod.py configs shendiao`，
   `SkillConfig.lua` 里 `[[=B*]]` 已归零。
4. 重新导出：`shendiao_mod` 78.76 MB / **318 个资源**（289 + 21 skills + 8 models），
   `shendiao_maps` 363.21 MB / 45 个资源，已 install 到 Steam 目录（09:52）。

## 四、防回归

`tools/moddev/jyx2mod.py check <mod>` 新增第 5 步「战斗资源齐全性」：

- `SkillConfig.lua` 的每条技能，`DisplayFileName`（空则 Name）必须能在 `Skills/` 找到同名 `.asset`
  → 缺失 = **error**（进战斗必崩、战场空白）
- `CharacterConfig.lua` 的每个角色，`ModelFileKey`（空则 Name）必须能在 `Models/` 找到同名 `.asset`
  → 缺失 = **error**（随机变脸）
- 非内置 MOD 的 `Models/` `Skills/` 若「大部分打了 bundle 名、个别漏了」→ warning

四个 MOD 复核：shendiao「一切正常」，SAMPLE/JYX2/xiastart_roguelike 无错误；
`selftest.py` 三个内置 MOD 错误数仍为 0。

## 五、这次仍然只能进游戏验的

- 战斗里 21 个新技能的动作是否自然（现在全是借模板：剑法借扫叶/落红/翔云/醉灯，
  拳掌借罗汉/伏虎/牛角…，`weaponCode` 是对的，但动作不是专属的）。
- 8 个新角色借了别人的脸，看是否需要换更像的模板（改 `gen_model_assets.py`
  里的 `PREFERRED_TEMPLATES` 重跑即可）。
- 如果不满意某个技能的动画，改 `gen_skill_displays.py` 的 `PREFERRED_TEMPLATES`
  → 删掉对应 `Skills/<名>.asset(+.meta)` → 重跑 `--apply` → 重新导出。

---

# 10-30 修复：7 条玩家反馈

玩家一次性报了 7 个问题，全部定位到根因并修完，已重打 AB + 安装。

## 一、逐条根因

| # | 反馈 | 根因（证据） | 修法 |
| --- | --- | --- | --- |
| 1 | 欧阳锋教了蛤蟆功，武功列表里没有 | `923.lua` 只写了 `SetFlagInt("蛤蟆功", 1)`——Flag 只走剧情分支，`role.LearnMagic` 从没被调过 | 加 `LearnMagic2(0, 31, 0)`（31 = `SkillConfig` 里蛤蟆功的 Id，`Skills/蛤蟆功.asset` 已存在） |
| 2 | 古墓派门口有铁门，进不去 | `18_gumu.unity` 里 4 扇门挂着 `NavMeshObstacle` 且 `m_Carve: 1`，**运行时会挖掉门下的 NavMesh**；`Door_03.FBX` 的 `addColliders: 0`，所以 collider 工具查不到任何东西 | 4 处 `m_Carve` 改 0 |
| 3 | 破庙里郭靖黄蓉"坐在半空中"，后面只要有他俩都坐着 | 场景实例的 `m_Modifications` 把 `Animator.m_Controller` 覆盖成 `sit_on_chair.controller`，而场景里没给他们摆椅子。对照原版 `JYX2/…/75_taohuadao.unity` 的同一实例，覆盖项一模一样——原版就这样 | 5 处（破庙/桃花岛/重阳宫）换成 `GuojingController` / `HuangrongController`（默认态 `站立`） |
| 4 | 桃花岛门口进出都复述"船靠了岸…" | `465.lua` 挂在 `m_EnterEventId=465`（走进去就触发）而非交互，每次踩都播 | 加 `初到桃花岛` flag，只播一次 |
| 5 | 郭靖说去桃花岛就该直接送到门口 | `MapTeleportor.TransportTriggerName` 为空 → 落点 = 大地图上与地图名同名的触发器；破庙离开落到默认点 | 破庙 `Leave` 的 `TransportTriggerName = 桃花岛` |
| 6 | 去终南山也一样 | 同上 | 桃花岛 `Leave` 的 `TransportTriggerName = 重阳宫` |
| 7 | 头像乱安人头 / 对话转场生硬 | 见下面两节 | 31 张覆盖头像 + 28 处改内心独白 |

## 二、头像：为什么乱，怎么修

`ChatUIPanel.ShowCharacter(headId)` 拼的是 `Assets/BuildSource/head/{headId}.png`，
`headId` 就是 `Talk` 的 roleId，**不是**人物表的 `Pic` 字段。

而 shendiao 的角色 id 是自编的（0/10/11/20…43/60…90/111/123/140…190/610…619），
原版同号是别人：id=10 郭靖 → 原版 `10.png` = **范遥**，id=22 小龙女 → **左冷禅**，
id=41 郭芙 → **张三**。id>114 的角色（孙不二 123、野狼 140+、蓝隼士兵 610+）
干脆没有对应图，`LoadAsset` 返回 null —— 头像框显示上一张残留。

修法走 **MOD 覆盖 base 资源**：`ResLoader.LaunchMod` 里

```csharp
string prefix = $"assets/mods/{modId}/";
var url = assetName.Replace(prefix, "assets/");
_assetsMap[url] = (modId, assetName);   // 后登记覆盖先登记
```

所以 `Assets/Mods/shendiao/BuildSource/head/10.png` 会顶掉 base 的
`Assets/BuildSource/head/10.png`。

原版人物表里 55…69 号正好是神雕角色（55 郭靖、56 黄蓉、57 黄药师、58 杨过、
59 小龙女、60 欧阳锋、62 金轮法王、63 程英、64 周伯通、65 一灯、66 瑛姑、
67 裘千仞、68 丘处机、69 洪七公），同角色的直接借；原版没有的按性别/年龄/气质借。

**踩到的坑**：第一次打完包，`shendiao_mod.manifest` 里 `head/` 是 0 条 —— 因为
`Jyx2ModCli.CreateBundleBuild` 用 `AssetDatabase.GetAssetPathsFromAssetBundle` 收集，
**没标 `assetBundleName` 的资源压根不进包**。补上标签后 31 条齐了。

复制原版 `.meta` 时 `guid` 和 `spriteID` 都换了新值（撞 GUID 会让工程引用错乱，
撞 spriteID 会让 Unity 把两张图当成同一张）。

## 三、对话：红色重点 + 去掉弹框

- `MainContent_Text` 是 uGUI `Text`（`ChatUIPanel_UIData.cs:18`），支持 `<color=#FF0000>`。
- 但 `ShowText()` 在超过 `GameConst.MAX_CHAT_CHART_NUM = 156` 时按「！？，」切段，
  会把标签切断，所以每句控制在 156 字符内。
- 28 处 `ShowMessage("...往桃花岛走...")` 改成 `Talk(0, "（...）")` 内心独白，
  重点加红色；「得到物品」「学会武功」这类纯反馈保留弹框。

## 四、顺带修的

`check_guids.py` 报 `Skills/普通攻击.asset`、`卷山狂刀.asset` 各有一处悬空 guid
（`blockPartilePrefab` 指向不存在的 prefab）。进战斗实例化格挡特效会拿到 null，
和 pitfall 28 同一类。已清成 `{fileID: 0}`。

两个场景的悬空 guid（`18_gumu` / `62_pomiao`）经查是 `!u!157` **LightmapSettings**
的光照设置引用，不影响玩法，没动。

## 五、这轮仍然只能进游戏验的

1. 蛤蟆功学完，技能面板里是否出现、战斗里能否用（`Skills/蛤蟆功.asset` 在，但动画是借模板的）。
2. 古墓门口能否走进去（若仍走不动，说明 NavMesh 烘焙本身缺那块，需要在 Unity 里重烘）。
3. 郭靖黄蓉是否站起来了（原版也是坐姿覆盖，本 MOD 已偏离原版）。
4. 从破庙出来是否真的落在桃花岛渡口、从桃花岛出来是否在重阳宫山门。
5. 31 张头像是否都对上（原版没有的角色是我按气质借的，可能需要微调 `_make_heads.py` 的 `MAP`）。
6. `<color=#FF0000>` 在对话框里是否正常显示（若显示成裸标签，说明该 Text 的 `supportRichText` 被关了）。

## 六、本轮新增的脚本

`tools/shendiao/` 下（都支持 dry-run，加 `--apply` 才写盘）：

| 脚本 | 作用 |
| --- | --- |
| `_apply_story_fix.py` | 28 处 ShowMessage → 内心独白 + 红色；923 加 LearnMagic2；465 加一次性守卫 |
| `_fix_sitting_npc.py` | 全场景把郭靖/黄蓉的 `sit_on_chair` 覆盖换回站立 controller |
| `_nav_carve.py` | 列出/关闭场景里 `NavMeshObstacle.m_Carve`（空气墙） |
| `_set_transport.py` | 改子地图 `Leave` 的落点 |
| `_make_heads.py` | 生成 MOD 覆盖头像 |
| `_tag_assetbundle.py` | 给 MOD 资源 `.meta` 打 `assetBundleName`（漏了就不进包） |
| `_fix_skill_refs.py` | 清掉 Skills 里指向不存在资源的引用 |

诊断用：`_dump_instance.py`（看 prefab 实例的覆盖项）、`_node_pos.py`（世界坐标）、
`_inst_scan.py`（某 prefab 被哪些场景引用/摆在哪）、`_obstacles.py`、`_prefab_cols.py`。


## 七、2026-10 第二轮：门口空气墙 / 秘籍 / 杨过数值 / 练级区

### 1. 古墓门口"看不见但走不动"——薄片 NavMeshObstacle

`18_gumu` 里有两类 `NavMeshObstacle`：

- **薄片**：`m_Extents.y ≈ 0.04`（门槛 `y=0.043`、台阶 `y=0.10`），`m_Carve: 0`。
- 椅子/石棺：`y ≈ 0.25–0.34`。

`m_Carve: 0` 时 Unity 用的是"挤出"式避让：Agent 只要和盒子的 XZ 投影相交就被推开。
4cm 厚的门槛在 Y 上完全不影响判定，等于把整条门洞封死 —— 表现就是"看得见路，
人物原地打转"。

**结论：薄片障碍不是障碍，是空气墙。** 用 `tools/shendiao/_disable_sills.py`
按 `--max-y 0.12` 筛出来关掉 `m_Enabled`（椅子 0.25+ 不动）。`18_gumu` 关掉 4 个
（2 个台阶 `y=0.10`、2 个门槛 `y=0.043`），剩下 5 个（`y=0.5` 的椅子/石墩、柱子）保留。
静态墙体不靠 Obstacle，靠烘焙好的 NavMesh 挡人，不受影响。
`_obs.py <scene>` 可以列全场景 Obstacle 的 enabled/carve/extents 核对。

> 修这个脚本时踩的坑：正则漏了 `'--- !u!208 '` 这个块头前缀，导致一条都没匹配到，
> 却打印"已处理 0 个"看着像成功。

### 2. 蛤蟆功只能练到 1 级 —— 秘籍本来就有，只是没发

`蛤蟆功秘籍` 在 `ItemConfig` 里是 **item 35 / skill 31**，早就配好了；
`923.lua` 只调了 `LearnMagic2(0, 31, 0)`，没给书。

JYX2 的规则：**`LearnMagic2` 只给 1 级；要继续升级必须用 `ItemType == 2` 的经书**。
全 MOD 9 处 `LearnMagic2` 逐一对过秘籍表，每门都有对应的书。

`_add_books.py` 在每个 `LearnMagic2` 后补 `AddItem(<bookId>, 1)`，幂等判断看文件尾
160 字符（原先按"包含 AddItem"判断会重跑就重复插入）。8 个剧本文件共插入 9 行：

| 剧本 | 秘籍 item | 剧本 | 秘籍 item |
| --- | --- | --- | --- |
| 210 | 1 | 906 | 142 |
| 219 | 12 | 913 | 182 |
| 402 | 20 | 923 | 35（蛤蟆功） |
| 424 | 76 / 31 | 836 | 49 |

### 3. 杨过的初始数值

`RoleInstance.InitData()` 是**直接照抄配置表**（`Level = Data.Level`、
`MaxHp = Data.MaxHp`、`MaxMp = Data.MaxMp + 1000`），所以改 `Configs/人物.xlsx`
即可，不用动 Lua 生成物（`Configs/Lua/` 是 gitignore 的生成目录）。

原值 L1 / 38HP / 27 攻，而第一个拦路 BOSS 鹿清笃是 **L26 / 999HP / 攻 85**，
紧随其后的武氏兄弟（郭芙 L14 / 武敦儒 L12）也是 230HP / 攻 71–77 —— 原来的杨过
三招就倒，必输。改成：

| 项 | 原值 | 现值 |
| --- | --- | --- |
| Level | 1 | 13 |
| Exp | 0 | 4300 |
| 生命/MaxHp | 38 | 300 |
| MaxMp | 26 | 110 |
| 攻击 | 27 | 74 |
| 轻功 | 27 | 60 |
| 防御 | 27 | 68 |

对照：野狼 L10/200HP/攻70/防30，毒蛇 L10/200HP/攻80/防30，黑熊 L10/200HP/**防90**
（防太高，练级别用黑熊，磨人）。

### 4. 练级区（`_set_grind.py`）

JYX2 没有随机遇敌。导入的场景里有一批 **三个事件 ID 全是 -1 的空 GameEvent 宿主**
（原作者给装饰物挂的交互，剧情搬走后闲置），位置确定可达，正好改成"走过去就开打"：

```
m_InteractiveEventId: -1      # 不弹"交互"按钮
m_EnterEventId:      3001     # 踩进 BoxCollider 直接开战
BoxCollider: trigger, 4x3x4
```

| 地图 | 宿主 | 位置 | 事件 | 小怪 |
| --- | --- | --- | --- | --- |
| 百花谷 20_baihuagu | `6` | 16.5, 6.0, 8.5 | 3001 | 140 斗野狼 |
| 神雕山洞 07_shandong | `5` | 5.69, 0.5, -8.94 | 3002 | 180 斗毒蛇 |
| 黑龙潭 21_heilongtan | `3` | -4.5, 4.5, 41.23 | 3003 | 180 斗毒蛇 |
| 铁掌山 48_tiezhangshan | `16` | 34.25, 0.5, 5.02 | 3004 | 140 斗野狼 |
| 一灯居 47_yidengju | `1` | 10.28, 0.5, 20.4 | 3005 | 140 斗野狼 |
| 古墓 18_gumu | 克隆 `1` | -15, 0.5, -8.6 | 3006 | 180 斗毒蛇 |

`18_gumu` 没有空宿主，用 `--clone` 从 `217` 那个门触发器复制一份
（fileID 走 `2151000000` 段），沿 z 轴偏 1.6m —— 那个门洞只在 x=-15 这条线上，
横着偏会撞墙。

**踩到的坑**：`rebuild()` 直接拼块头，把文件开头的 `%YAML 1.1` + `%TAG !u! ...`
两行丢了，Unity 解析不了。现在 `rebuild(blocks, prefix)` 保留首块之前的文本。
已写的 6 个文件用 `_fixhead.py` 补回。

### 5. 这轮待进游戏验的

1. 古墓门口真的能走进去了（若还是走不动 → NavMesh 本身缺那块，要在编辑器里重烘）。
2. 蛤蟆功秘籍拿在包里，用一下能不能把「蛤蟆功」升到 2 级。
3. 杨过 L13 打鹿清笃仍然很难，但至少能撑几回合；剧情允许输。
4. 六张图的练级区：走过去是否会直接开战、战斗结束回到原地会不会反复触发。


## 八、AI 头像：一张九宫格设定图 → 切 9 张表情/视角（`gen_sheets.py`）

### 1. 为什么要九宫格

只画一张头像时，人物的情绪、姿态、全身比例全丢了，想"换个表情"就得重新描述、
重新抽卡，出来的还是另一个人。九宫格把同一个人画九遍（3×3 等分布局），
一次性得到：**正面三情绪 + 四分之三侧脸 + 全身正面 + 全身侧面 + 惊愕 + 悲愤 + 背身回望**。
九格画风强制一致，天然就是角色设定表。

### 2. 流水线

```
gen_sheets.py  --apply
  ├─ prompt = 角色原著描述 + 固定九格指令（每格内容、顺序、不得画网格线/文字）
  ├─ POST gateway /v1/images/generations  model=gemini-3-pro-image
  │     aspect_ratio=1:1  image_size=2K  → data[0].b64_json（2048×2048，约 4~5 MB）
  ├─ 落盘 Export/heads_sheet/<file>_sheet.png            （整张设定图）
  ├─ 按 3×3 等分切，每格四边内缩 2%                       （AI 总在格线处留细黑线）
  ├─ 每格 resize 到 512×512 RGBA → Export/heads_sheet/cells/<file>_1..9.png
  └─ 第 1 格（正面·平静）写进 jyx2/Assets/Mods/shendiao/BuildSource/head/<file>.png
        并同步写 .meta（沿用原头像的 sprite 设置，只换 guid）
```

- 九格是**固定顺序**的，所以切片文件名可以按序号直接对应（`SLOTS` 表）。
- 除第 1 格外，另外八格先存着 —— 以后若做「对话表情系统」（`Talk` 增加情绪参数、
  `ChatUIPanel` 换图），素材已经现成。
- 第 5/6 格是全身像，比例与半身像不同，**不要**直接塞进 512 头像框，否则脸会小一半。

### 3. 命令

```powershell
$env:TURBO_KEY = 'sk-...'          # 只走环境变量，绝不写进文件/日志
python tools/shendiao/gen_sheets.py --list              # 看名单
python tools/shendiao/gen_sheets.py --only 0            # 只做杨过（少年+中年两种）
python tools/shendiao/gen_sheets.py --apply --only 22   # 只做小龙女并写入 MOD
python tools/shendiao/gen_sheets.py --apply             # 全量（已有的设定图会走缓存，不重复花钱）
python tools/shendiao/gen_sheets.py --resplit --apply   # 只重切 + 重写头像，不调接口
python tools/shendiao/gen_sheets.py --contact           # 拼总览图 Export/heads_sheet/_contact.png
python tools/shendiao/gen_sheets.py --apply --force --only 22   # 重抽小龙女
```

**缓存规则**：只要 `Export/heads_sheet/<file>_sheet*.png` 在，就不调接口、直接重切；
`--force` 才重新出图。所以调内缩比例、调 512 尺寸都免费。

### 4. prompt 写法的三条经验

1. **必须逐格写清内容与顺序**（"第 1 格：正面·平静 —— 正视前方，神情平静…"），
   只写"九宫格多表情"会得到九张互不相干的脸。
2. 明确禁止"网格线、边框、序号、文字、标签、水印"。即便写了，模型仍会画**很细**的格线，
   所以裁切要内缩 2%。
3. 年龄/身份靠**具体描述**而不是数字：少年写"面庞带少年人的圆润稚气、下颌线条尚未硬朗"，
   中年写"三十余岁、两鬓斑白、独臂、黑袍"。只写"14 岁"/"36 岁"会出成年脸。

### 5. 这轮产出的坑位（sex/age 都不是随便写的）

- 杨过两种：`0`（十四五岁粗布短褐）+ `0_adult`（三十六岁神雕侠独臂黑袍）。
  `_adult` 只出设定图，**不写入 MOD**（游戏里只有一张头像，进谷时是少年）。
- 名单只收 Lua 里 `Talk(id)` 真正出现过的 roleId，避免给人物表里没人用的行白白花钱。
- 旧头像（借原版金庸人物）已备份到 `Export/heads_backup/`，不满意可整批回滚。



## 九、精致画风：角色设定卡（`gen_cards.py`）

用户判定第八节的「墨线平涂」**不够精致**，给了参考（国风游戏角色卡：写实 CG 立绘 +
右侧姓名/身长/色卡面板）。据此新增 `gen_cards.py`，与 `gen_sheets.py` 并存：

| 脚本 | 出什么 | 用途 |
| --- | --- | --- |
| `gen_sheets.py` | 3×3 九宫格（多情绪 + 全身 + 侧身），平涂画风 | 切 512 头像 / 表情素材 |
| `gen_cards.py` | 2:3 精修立绘 + PIL 排版的卡面 | 设定卡、头像的高清来源 |

### 做法要点

1. 立绘用 `aspect_ratio: 2:3`、`image_size: 2K` → 实测回 **1696×2528**（不是 1365×2048，
   网关按自己的档位取整）。`cover()` 等比填满后居中裁，不拉伸。
2. **中文绝不交给模型画**（必糊、必错字）。卡面文字全部用 PIL + Windows 字体：
   名字 `STZHONGS.TTF`（华文中宋）、信息/色卡 `msyh.ttc`。PIL 没有 letter-spacing，
   用 `draw_spaced()` 逐字画。
3. 色卡不是写死的：`sample_palette()` 剔除近白背景后 `MEDIANCUT` 量化 8 色，
   按亮度从浅到深排，再用 `name_of()` 映射到 15 个国风色名（月白/霜银/雾蓝/鸦青…），
   并跳过已用名，避免一栏里出现两个"月白"。
4. 角色资料（身长/体重/门派/兵器/身份/竖排台词）在 `PROFILE` 字典里按 roleId 配，
   没配的走默认，不会空着。
5. 立绘有 `Export/heads_card/<file>_portrait.png` 就 **REUSE**，只重排卡面不调接口 ——
   改字体、改色卡、改排版都是零成本。

### 命令

```powershell
$env:TURBO_KEY = 'sk-...'
python tools/shendiao/gen_cards.py --only 0            # 出一张（有立绘则只重排卡面）
python tools/shendiao/gen_cards.py --only 0 --force    # 重抽立绘
python tools/shendiao/gen_cards.py                     # 全量
# 产物：Export/heads_card/<file>_portrait.png（1696×2528）
#       Export/heads_card/<file>_card.png    （2100×2048）
```

卡面尺寸：左立绘 1365×2048，右面板 735×2048，中线 2px `#C6C9CF`。

### 待定（等用户拍板）

- 少年杨过当前偏"秀气"；嫌不够英气就在角色描述里加「眉骨略高、下颌角清晰、薄唇」。
- 参考图的华丽感（水晶流苏/银饰/泛光）来自角色本身是富贵仙子；粗布少年不该硬加饰品，
  若要求整批更华丽，需要按角色分档写 `ROSTER` 里的 description。
- 头像仍要从立绘脸部裁 512（下一步做自动定位）；九宫格保留给"表情系统"备用。
- 已按旧画风覆盖过 6 张头像（0/10/11/20/21/22），原图在 `Export/heads_backup/`，可整体回滚。

## 十、2026-10-29 定稿：精修画风 + 九宫格裁切（正式流水线）

用户看过设定卡后拍板：**画风要写实 CG 那套，但产物必须是每人一张九宫格、再切 9 张表情头像**。
于是 `gen_sheets.py` 不再是"平涂备用方案"，它是**唯一正式产物**，`gen_cards.py` 变成宣传卡/高清来源。

### 1. 画风的单一来源

```
gen_cards.STYLE_BODY        ← 只改这一处
   ├─ gen_cards.py  用它拼设定卡立绘 prompt
   └─ gen_sheets.py import gen_cards as CG，SHEET_STYLE = 九格约束 + CG.STYLE_BODY
```

以后要调"精致度/写实度/配色"，只动 `STYLE_BODY`，两套产物自动同步。

### 2. 4K 是默认该用的档

| image_size | 出图 | 单张耗时 | 每格像素 | 切 512 效果 |
| --- | --- | --- | --- | --- |
| 2K | 2048×2048 | 35~55s | 682 | 够用 |
| **4K** | **4096×4096** | **67~93s** | **1365** | 锐利、发丝细节保留 |

```powershell
python tools/shendiao/gen_sheets.py --apply --size 4K
```

4K 只是"下采样"，512 头像的清晰度上限由它决定 —— 值得多花 30 秒。

### 3. 九格固定内容（`SLOTS`）

| 格 | 内容 | 用途 |
| --- | --- | --- |
| 1 | 正面·平静 | **写进 MOD 头像**（`BuildSource/head/<id>.png`） |
| 2 | 正面·含怒 | 表情系统备用 |
| 3 | 正面·微笑 | 表情系统备用 |
| 4 | 侧面·沉思 | 立绘/剧情插图备用 |
| 5 | 全身·正面 | 立绘备用（**别塞进 512 头像框**，脸会小一半） |
| 6 | 全身·侧面 | 同上 |
| 7 | 惊愕 | 表情系统备用 |
| 8 | 悲恸·决绝 | 表情系统备用 |
| 9 | 背身回望 | 表情系统备用 |

4K 这一轮模型**没有画格线**（2K 平涂那轮画了），但裁切仍保留 2% 内缩兜底。

### 4. 这一轮踩到的两个新坑（都已修）

**(a) 模型会把"格位图例"翻译成字幕烧进画面**
`小龙女` 那张九宫格，每格底部都印着一行英文：`Frontal·Calm` / `Frontal·Angry` /
`Full Body·Side` … —— 因为我当时把 prompt 写成 `第1格：正面·平静 —— 正视前方…` 的图例格式，
模型把图例当成了"这页需要配文字说明"。两处修正：
- prompt 改成纯句子：`第一个方格画的是：正视前方，神情平静…`，不再给"名称：描述"的结构；
- 首尾各插一次 `NO_TEXT` 硬性禁令，并把 `Frontal·Calm` 这个**反面样例**直接写进去。
另外成品头像走 `avatar_crop()`：取第 1 格**上半 86% 的正方形**，即便模型又在格底烧字，
也被整块切掉；副作用是脸更大，更适合对话头像框。

**(b) `.meta` 被写成 0 字节**
`io.open(path,'w').write(meta_for(cid))` —— `open('w')` 先把文件截断，
`meta_for()` 又恰好拿这个文件当模板读，于是读回空串、写回空串，6 个头像的 `.meta` 全变成 0 字节。
Unity 会当成新资源重新生成 meta（导入设置 / AB 标记全丢）。
- 修法：`gen_sheets.ensure_meta()` —— **已存在且非空就一个字都不动**（guid 沿用原样最安全），
  缺了才复制模板；且**先取文本再 open('w')**。`gen_heads.py` 同处同样改掉。
- 已误伤的文件用 `git checkout -- <paths>` 恢复，别再手写。


### 6. 换模型：`gemini-nano-banana-2.1`

`gen_heads.gen_one()` 增加了 `model` 参数，`gen_sheets.py` 加了 `--model` 开关，其他参数完全不变：

```powershell
python tools/shendiao/gen_sheets.py --only 29,31,35 --size 4K --model gemini-nano-banana-2.1 --apply
```

两家的差异（实测）：

| 模型 | 4K 单张耗时 | 画风 | 备注 |
| --- | --- | --- | --- |
| `gemini-3-pro-image` | 67~93s | 更"仙侠海报"，皮肤通透、发饰华丽 | 偶发中途 SSL EOF |
| `gemini-nano-banana-2.1` | 65~195s | 更"游戏资产"，皮肤纹理/胡须更实 | 同一 prompt 下老年角色更准 |

当前成品的模型分布：`0, 0_adult, 10, 11, 20~28` 用 `gemini-3-pro-image`；
`29~111` 用 `gemini-nano-banana-2.1`。混用没有兼容问题，因为最终都被压成 512。
`裘千尺` 第一次跑碰到 `SSL: UNEXPECTED_EOF_WHILE_READING`（4K 长连接被掐），
自动重试 3 次仍失败，单独 `--only 29` 补跑即成功 —— **批量里看到 FAIL 先看是不是网络，别急着改 prompt**。

### 7. 归档 / 体积

- 平涂版九宫格整体归档到 `Export/heads_sheet_flat_1029/`（含旧 cells），要回滚直接用。
- 用旧"图例格式" prompt 生成的 6 张（`0_adult/10/11/20/21/22`）挪在
  `Export/heads_sheet/_superseded/`，不参与复用，等新 prompt 重出。
- 4K 设定图每张约 20 MB，28 张 ≈ 550 MB，全在 `Export/` 下 —— 已被 `.gitignore` 的 `/Export` 拦住，不会入库。
- 用户给的参考卡面存 `Export/refs/ref_card_shuangyue.jpg`（**第三方游戏美术，绝不入库**）。



## 十一、头像批量现状（2026-10-29）

- 26 个角色 + `杨过中年` 变体，全部 4K 九宫格出图、切 9 格；`BuildSource/head/<id>.png`
  统一为 **512×512 RGBA**，取第 1 格上半 86%（实现见 `gen_sheets.avatar_crop`）。
- 每格剩下的 8 张表情/全身图在 `Export/heads_sheet/cells/<id>_{1..9}.png`，
  将来做表情系统直接拿来用（文件名就是格号，1 是正面平静）。
- 已 `jyx2mod.py check shendiao` 通过 → `unity shendiao` 导出（173 MB，含地图包）→ `install` 装进游戏。
- 脚本自检结果：`pngs 31 bad [] empty_meta []` —— 无双通道错、无空 meta。
- 待用户在游戏里确认：MOD 头像是否正常显示（**要用新存档**），
  顺带复核古墓门洞、蛤蟆功书、杨过属性、6 个刷怪区。


## 十二、对话表情系统（2026-10-29）

### 1. 为什么能不改 C# 就做到

`ChatUIPanel.ShowCharacter(headId)` 取头像的路径是硬拼出来的：

```csharp
var url = $"Assets/BuildSource/head/{headId}.png";
```

**文件名就是 `Talk()` 的第一个参数**。所以"换表情"= 换一个 id，不必碰 C#：

```
表情虚拟 id = 9000000 + 角色id * 10 + 槽位号(1..9)
   小龙女·怒  -> 9000000 + 22*10 + 2 = 9000222
   杨过·沉思  -> 9000000 +  0*10 + 4 = 9000004
```

槽位号直接沿用 `gen_sheets.SLOTS` 的九宫格顺序：
`1 平静 / 2 怒 / 3 笑 / 4 沉思 / 5 全身正面 / 6 全身侧面 / 7 惊 / 8 悲恸 / 9 背身回望`。
槽位 1 就是默认头像 `<角色id>.png`，不额外占图。

### 2. 唯一必须打补丁的地方：`ChangePosition`

`ChatUIPanel.ChangePosition(headId, ShowName)` 用 `headId == 0` 判断"是不是主角"
（主角头像在右、姓名取玩家自定义名；NPC 在左、姓名查 `CharacterTable`）。
虚拟 id 进去会被当成 NPC，于是 `Lua/expr.lua` 用 **xLua 热更新**把它还原：

```lua
util.hotfix_ex(CS.ChatUIPanel, 'ChangePosition', function(self, headId, showName)
    hotfix_alive = true
    self:ChangePosition(ExprRealId(headId), showName)   -- hotfix_ex 内调用=原函数
end)
```

为什么这条路走得通（三个前提都已验证）：

- `Assets/Editor/HotfixConfig/HotfixConfigs.cs` 的 `by_property` 把 **Assembly-CSharp 全部类型**
  都登记成可热更新（黑名单只挡 UnityEngine/第三方），`ChatUIPanel` 在其中；
- 出货版确实注入了热更新代码 —— `Player.log` 里能看到 mod 模板 `hotfix.lua` 对
  `Jyx2LuaBridge.Talk` 的补丁在刷屏，即 `HOTFIX_ENABLE` 生效；
- `util.hotfix_ex` 的实现是"临时撤补丁 → 调你的函数 → 恢复"，所以函数体里
  `self:ChangePosition(...)` 调到的是**原函数**。必须同步、不能 yield，我们这个函数是纯同步的。

自检写在 `expr.lua` 里：每句 `Talk` 内部必然调一次 `ChangePosition`，如果说过一句之后
`hotfix_alive` 还是 false，就打一行
`[表情] ChangePosition 热更新未生效：玩家表情头像会显示在左侧（姓名仍正确）`。
**看到这行说明站位会错**（其余功能正常），此时要么查热更新注入，要么退回默认头像。

### 3. 兜底：`StoryIdNameFixes`

虚拟 id 不在 `CharacterTable` 里，`GetRoleName` 会 `KeyNotFoundException`。
正常路径下 `ChangePosition` 已经先还原成真实 id，查不到名字的情况不会发生；
但为了"热更新万一没生效也不崩"，`gen_expr_heads.py` 会把每个虚拟 id 的中文名写进
`ModSetting.asset` 的 `StoryIdNameFixes`（名字从 `Configs/人物.xlsx` 的 `Name` 列取）。

### 4. 文件与脚本

| 文件 | 作用 |
| --- | --- |
| `Lua/expr.lua` | 运行时层：`EXPR` 表、`Talk` 包装、`ChangePosition` 补丁、`HAVE_IDS` 清单 |
| `Lua/hotfix.lua` | 模板里的 `Talk` 调试打印已注释掉（1123 句台词会刷 1123 行日志） |
| `ModSetting.asset` | `PreloadedLua: [hotfix, expr]` + 34 条 `StoryIdNameFixes` |
| `tools/shendiao/tag_expr.py` | 按台词语气自动给 `Talk(id, "…")` 补第三参数（`--stats` / `--apply`） |
| `tools/shendiao/gen_expr_heads.py` | 从 `Export/heads_sheet/cells/` 裁表情头像写进 MOD，回填 `HAVE_IDS` 与 `StoryIdNameFixes` |
| `tools/shendiao/expr_selftest.py` | 用 `lupa` 真跑 `expr.lua`（桩掉 `CS`/`util`/`Talk`），不开游戏验证 id 路由与补丁还原 |

剧本写法：

```lua
Talk(22, "……那你要什么？")
Talk(0,  "我不要人可怜，也不要人推。", EXPR.sad)
Talk(0,  "（石室里空荡荡的。）",       EXPR.think)
```

- **Lua 标识符只认 ASCII**，所以键名是英文：`EXPR.calm/angry/smile/think/shock/sad/lookback`，
  要写中文就用 `EXPR['怒']`。
- 不写第三个参数 = 默认头像，老剧本完全不用改。
- 剧本里写了"没生成图"的表情不会变空白：`expr.lua` 查 `HAVE_IDS`，查不到就退回默认头像并打一行提示。

### 5. 自动打标策略（`tag_expr.py`）

1123 句逐句手标不现实，所以按台词做一次粗分类，宁缺毋滥：

1. **`（…）` 开头的旁白/内心独白 → 沉思**，且优先于关键词判定。
   旁白里的"笑/哭/怒"是**别人**的表情（"（他们笑着走开了。）"），套在说话人脸上全错。
   这类占四成多（506 句）；嫌多就把 `THINK_FOR_PAREN = False` 再跑一遍。
2. 其余按语气词：悲 → 怒 → 笑 → 惊（"罢了/可怜/对不起"、"叛徒/小贼/凭什么"、"笑/哈哈"、"大惊/愕/竟然"）。
3. 判不出来的**一律不动**（保持默认头像），留给以后手写。

首轮结果：1123 句里标了 531 句（think 506 / angry 11 / sad 9 / smile 4 / shock 1），
改动 78 个剧本文件；`used_combos()` 用到 34 组"角色+表情"，
所以 `--apply --used-only` 只出 34 张图（22.4 MB），**不要**默认全量出图（27×5=135 张 ≈ 45 MB）。

新增/改动表情后重跑：

```powershell
python tools/shendiao/expr_selftest.py                   # 不开游戏验证 expr.lua 的 id 路由
python tools/shendiao/tag_expr.py --stats                  # 先看报告 Logs/_tag_expr.txt
python tools/shendiao/tag_expr.py --apply                  # 写回剧本（幂等，已标的不会再改）
python tools/shendiao/gen_expr_heads.py --apply --used-only # 补图 + 回填 expr.lua / ModSetting.asset
python tools/shendiao/gen_expr_heads.py --check             # 体检：缺图/尺寸/meta/清单/名字修正
python tools/moddev/jyx2mod.py unity shendiao --with-base  # 打出体积正常的包（约 176 MB）
python tools/moddev/jyx2mod.py install shendiao --src Export\shendiao
```

### 6. 已踩的坑

- `rg -rn PATTERN` 里的 `-r` 是 `--replace`，会把匹配替换成 `n` —— 排查"代码被混淆"假象的元凶。
  要么去掉 `n`，要么用 `-n`。
- `ModSetting.asset` 里空列表是写成**单行**的 `StoryIdNameFixes: []`，
  不是 `Key:` 换行再 `[]`；脚本改它时必须兼容这两种写法。
- 往 `StoryIdNameFixes` 里塞条目的 YAML 层级必须是
  `  - Id: N` + **4 空格** `    Name: "…"`。写成 `  - - Id: N`（多打一个短横）或
  `Name` 只缩 2 格，Unity 反序列化会整块读不出来 —— 表现是名字回退成默认值、
  `PreloadedLua` 也变空，**而且打包过程一句错都不报**。`gen_expr_heads.py --check`
  现在逐行对齐校验这个块。
- `jyx2mod.py unity` 默认 `--no-base`（省 1.8GB 压缩），代价是**共享资源被复制进 MOD 包**：
  同一次改动 `shendiao_maps` 会是 363 MB；加 `--with-base` 重打 base 后只有 136 MB。
  本地反复调试用 `--no-base` 图快，**要装进游戏就带 `--with-base`**，
  否则 installed 体积会翻 2.5 倍。
- 打包是"起 Unity 前就判定要不要打"，判定看的是**源文件 mtime vs 产物 mtime**
  （`mod_is_fresh`）。边打包边改 Lua 会被判成"没改动"而打进旧内容 ——
  改完源码再打包，或者 `(Get-Item xxx).LastWriteTime = Get-Date` 摸一下再打。
- `lint_lua.py` 原来把 `for … do` 的 `do` 也算一层块，任何带 for 循环的 Lua 都误报
  "for 没有配对的 end"；已改成 `for/while` 头部的 `do` 不再计数，同时让它认得表情虚拟 id
  （`9000000+id*10+slot` 会先还原成真实 id 再查人物表）。
- 别用 `lupa` 之外的"纯 Python 猜测"校验 Lua：`lupa 2.8` 在环境里，
  `jyx2mod.check_lua_syntax()` 就是真编译一遍（168 个脚本 0 报错才算过）。



## 十三、2026-10-29：战斗数值重锚定 / NPC 统一朝心 / 桃花岛对话重写

本轮解决三个"玩起来不对劲"的问题，全部是**纯 Lua + 热更新**，没有改 C#，也不用重新编译游戏。

### 1. 战斗数值：等级涨了，血/真气却是 1 级值

**根因（两层，都要知道）**

- `RoleInstance.LevelUp()`（`Scripts/GameSave/RoleInstance.cs:272`）每升一级只给
  `MaxHp += (HpInc + Random(0,3)) * 3`，即 **9~27 点血**；`MaxMp += (9-a)*4`，12~32 点。
- 但剧本里大量用的是 `AddExp(0, N)`（`Jyx2LuaBridge.cs:1108` → `AddAttr(role,"Exp",…)`），
  **只加经验，不调 LevelUp**；真正升级只发生在 `BattleManager.cs:320` 战后的
  `while (role.CanLevelUp()) role.LevelUp();`。
- 于是任何"绕开那两处"改写 `Level` 的路径（`AddLevelreturnUper`、或读档时字段被覆盖）
  都会留下 **Level 很高、MaxHp 停在 1 级值** 的组合。

**修法**：`Lua/balance.lua` 的 `FixStats(r)` 给血量/真气一个**只补不降的地板**：

```
floorHp = 40 + (Level-1) * 6          -- 每级 6 点，是 LevelUp 真实增量(9~27)的保守下限
floorMp = 20 + (Level-1) * 3
```

低于地板才补，且 `MaxHp` 与 `Hp` **同步加同一个增量**，所以在战斗中途调用也等价于
"凭空多出来的上限直接回满"，不会出现"凭空回血"。

> 为什么斜率取得这么小：第一版用 `(HpInc+1)*3` 当斜率，结果杨过（Lv13 配表 300 血）没事，
> 但真气从配表 110 被抬到 116 —— 地板去改一个本来就合理的数值，属于越权。
> 现在斜率只够抓"完全停在 1 级"的情况，配表数值一律不动。

挂载点：`RoleInstance.InitData`（读档/建角色后）、`RoleInstance.LevelUp`（升级后），
外加伤害函数里对交战双方的顺手校正。

### 2. 战斗数值：郭芙一掌秒人 / 一场仗磨十几回合

**根因**：引擎公式（`Assets/LuaScripts/Jyx2Battle/DamageCaculator.lua:171-220`，属于 base 资产，
不在 MOD 里）是

```
v = (总攻击 - 总防御*3) * 2/3 + RND(20) - RND(20)
```

**防御被乘了 3 倍**。配表里杨过 Attack74/Defence60、郭芙 Attack77/Defence60：

- 双方打对方都只有 ~11 点伤害 → 230 血要打 **21 回合**（拖沓的来源）；
- 一旦某方防御稍低或对方有个高攻击技能，`v` 直接翻正成几十上百 → **秒杀**。

曲线在中间是断的，没有过渡段。

**修法**：不改引擎文件，在 MOD 里包一层 `Jyx2.Battle.DamageCaculator.GetSkillResult`
（`BattleInit.lua:22` 把它挂在 **全局表** `Jyx2.Battle` 上，所以直接赋值就能覆盖）：

```lua
local orig = dc.GetSkillResult
dc.GetSkillResult = function(caster, target, skill, bv)
    local rst = orig(caster, target, skill, bv)      -- 原公式照跑
    ... 只对 magic.DamageType == 0（普通伤害）重锚定 ...
end
```

重锚定方式：把伤害拉到**目标最大生命的某个比例**，比例由双方 `Power()` 之比决定。

```
Power(r) = Attack + Defence*0.9 + Level*5 + MaxHp*0.08
ratio    = 0.16 * k^1.15        clamp 到 [0.10, 0.40]
ratio   *= 1 + 0.5*(1 - 当前血/最大血)     -- 残血加速，防止磨血
最终     = hp2 * ratio * (1 ± 25%)         -- 原公式结果只做倾向修正
```

原公式结果没被丢掉，而是降级成 **±25% 的倾向修正**，所以武功等级、距离、体力、
武学常识仍然影响手感 —— 只是不再决定数量级。

`DamageType != 0` 的（吸内 / 用毒 / 解毒 / 治疗 / 暗器）**一律保持原样**。

**实测（`tools/shendiao/balance_selftest.py`，配表真值 + 原公式产出原始伤害）**

| 对战 | 胜者 | 回合数 |
|---|---|---|
| 杨过 vs 野狼 | 杨过 | 3 |
| 杨过 vs 武敦儒 | 杨过 | 5 |
| 杨过 vs 郭芙 | 杨过 | **7** |
| 杨过 vs 欧阳锋 | 欧阳锋 | 4 |

- 普通战 3~7 回合，落在"不拖沓"的区间；
- 郭芙不再秒人，但也不是软柿子（7 回合才拿下）—— 符合"同级对手"的定位；
- 欧阳锋（Lv31 / 885 血）4 回合打崩 13 级的杨过，属于剧情压制，玩家该跑而不是该打。

调参入口全在 `Lua/balance.lua` 顶部：`BASE_RATIO`(节奏)、`RATIO_MIN/MAX`(上下限)、
`LOW_HP_BOOST`(收尾加速)、`TILT/TILT_CAP`(原公式影响力)、`HP_PER_LEVEL`(血量地板斜率)。
改完跑 `python tools/shendiao/balance_selftest.py` 就能看到新曲线，不用进游戏。

#### 踩的坑

- `Jyx2.Battle` 可能比 MOD 的 `PreloadedLua` 更晚建好 → `TryPatchDamage()` 必须允许多次重试，
  现在在**模块加载时**试一次、**`RoleInstance.InitData`** 里再试一次（InitData 必发生在引擎
  Lua 初始化之后）。
- `Jyx2.Battle` 是**全局表中的 Lua 模块**（`BattleInit.lua` 里 `battle.DamageCaculator = prequire(...)`），
  不是 C# 方法，所以**不需要 `util.hotfix_ex`**，直接给字段赋值即可 —— 别去 hotfix 一个 C# 类型。
- 覆盖时用 `rawset(dc, "__shendiao_balance_patched", true)` 做幂等标记；
  重复包装会让伤害被连续重锚定两次（结果仍收敛，但会白跑一遍原公式）。

### 3. NPC 朝向：郭靖对着墙、欧阳锋盯着郭芙

**根因**：场景里 NPC 的旋转是编辑器手摆的，作者没摆准。实测 `62_pomiao.unity`：
郭靖在 `(0.8, 5.0, -6.0)`、黄蓉在 `(2.2, 5.0, -7.2)`，**两人都被摆成 yaw=90°**（朝 +X），
而庙内中心在 +Z 方向 —— 等于贴着东墙说话。

**修法**：`Lua/npc_face.lua`，热更新 `CS.LevelMaster.Start`（每个场景进入时都会跑一次）：

```lua
util.hotfix_ex(CS.LevelMaster, "Start", function(self)
    self:Start()                 -- 原逻辑
    pcall(fixSceneNpcs, self)    -- 之后统一转身
end)
```

`fixSceneNpcs` 的规则：

1. 在 `self.transform.root` 下递归找名为 `NPC` 的节点，取它的所有子对象；
2. 算出这些 NPC 水平坐标的**质心**；
3. 每个 NPC `Quaternion.LookRotation(质心 - 自己)`；
4. 自己就在质心 0.5 m 内 → 退化为朝玩家（`Player` 节点），再没有就朝 +Z。

"统一朝质心"等价于"大家围成一圈互相看着"，既不会面壁，也不会出现
"欧阳锋盯着郭芙"那种奇怪的凝视关系。

- `FACE_STYLE = "player"` 可切成"直接朝玩家"。
- `YAW_FIX["NPC名"] = 度数` 用于模型正面不是 +Z 的情况。
  已扫描 `BuildSource/ModelCharacters` 全部 prefab 的根节点 yaw，**只有 9 个非零**：
  `Suanmingxiansheng / Nanxian / 05_Nanxian / Chahuzhanggui / Zahuoshang / Zhanggui = 90`，
  `Huozhizhu = 180`，`Weixiaobao = 84.9`，`Xiexun = 81.3`；郭靖/黄蓉/欧阳锋/郭芙等全是 0。
- 不改 `.unity` 的理由：MOD 有 100+ 个场景（含大地图分块），手摆不可维护；
  prefab 实例的旋转藏在 `m_Modifications` 里，抽查改容易写坏文件。

### 4. 桃花岛对话：郭靖莫名其妙让我去重阳宫

`Lua/466.lua` 末段原本是"郭伯伯，为什么？"→"……你会蛤蟆功。"→ 直接宣布去重阳宫，
因果全靠玩家脑补，而且**黄蓉只在旁边说了句"孩子不懂事"**，读起来像郭靖突然赶人。

重写要点（仍在 `466.lua`，flag 链不变）：

- 先点明"昨日后院你打了敦儒、一掌撞裂石桌"，把**证据**摆出来，而不是抽象地说"你会蛤蟆功"；
- 郭靖明确表态"我信你"，是**柯公公不信** —— 赶人的压力来源落到第三方身上，
  郭靖的无奈和黄蓉的算计才立得住；
- 黄蓉的台词改成"你去那里是学正道武功，不是被赶出去"，紧接着杨过内心吐槽
  "她先让我背《论语》，又说我学不得武功" —— 呼应前一段，让读者看出她在借坡下驴；
- 结尾给出**行动指引**：`船还在码头——你上岸的地方`（原来是一句重复的"终南山，重阳宫"，
  玩家不知道下一步去哪；早期版本写的是"海边"，而"海边"是 `923` 欧阳锋那片礁石，
  真正的离场点 `Leave/Entrance` 在码头 `(47.11, 15)`，即上岸点 `(44.9, 14.9)` 旁 2.2m）。
- 情绪用上了表情槽位：郭靖 `EXPR.sad`（9000108 已生成）、杨过 `EXPR.think/sad/angry`。

### 5. 本轮新增 / 改动

| 文件 | 说明 |
|---|---|
| `Lua/balance.lua` | 新增，血量地板 + 伤害重锚定 + 生命周期钩子 |
| `Lua/npc_face.lua` | 新增，进入场景后 NPC 统一朝质心 |
| `Lua/466.lua` | 重写桃花岛末段对话 |
| `ModSetting.asset` | `PreloadedLua` 追加 `npc_face`、`balance` |
| `tools/shendiao/balance_selftest.py` | 新增，lupa 模拟对战量回合数 + FixStats 回归 |

验证：`lint_lua.py` 168 脚本 0 问题 / `check_story.py` 168 脚本 0 错 0 提醒 /
`jyx2mod.py check shendiao` 一切正常（Preloaded 识别 4 个）/ `balance_selftest.py` 全绿。

---

## 十四、2026-10-29 第二轮：剧情/场景的语义层审计（5 处修复）

静态检查（lint / check_story / flag 图）第一轮就全绿，但"绿"只代表**指针没断**，
不代表**话说得对**。这一轮把审计从"结构"下沉到"语义"，用两个新工具把
168 个脚本 × 37 个场景翻了一遍。

### 1. 新工具（`tools/shendiao/`）

| 工具 | 作用 |
|---|---|
| `audit_flags.py` | 建全 MOD 的 flag 图，报三类：**只读不写**（剧情永不触发／永久卡关）、只写不读（死 flag）、同名多处写不同值 |
| `find_event.py` | 事件 ↔ 场景 ↔ Lua 双向比对。`--all` 模式列出「写了脚本但没场景绑定」和「场景绑了但没脚本」 |

跑出来：**只读不写 0 个**（没有任何分支是死的）、只写不读 1 个（`全篇完成`，
结局标记，正常）；事件 162 个绑定／164 个脚本，孤立绑定 0 个。

> 踩坑：`find_event.py` 初版每个 GameEvent 只取第一个 id，把 `913 / 914 / -1`
> 这种「交互 + 用物品」双挂的物体误报成"914 无绑定"。必须三个字段逐个登记。

### 2. 修掉的 5 处

| # | 位置 | 问题 | 修法 |
|---|---|---|---|
| 1 | `922.lua` 武氏兄弟 | 输的分支说完"我摔在地上"，紧接着 `if` 外面又来一句"寡不敌众，我终究还是摔在地上"——同一件事连说两遍；赢的分支说"拳头砸在我脸上"再摔一次，也矛盾 | 赢：推开武敦儒 → 郭芙喊"一起上" → "推得开一个，推不开两个"；输：一记拳 + 郭芙嘲讽；共用句改成"被按在地上" |
| 2 | `401.lua` 公孙止 | 走"战败"分支后，公孙止还完好地站着，裘千尺却哈哈大笑"你也有今日！" | 战败分支补**枣核钉救场**：三枚枣核钉在他脚前 → "……裘千尺！" → "我不出手，我只数你的刀" → 转身出洞。两分支都能到"击退公孙止" |
| 3 | `466.lua` 桃花岛末段 | 郭靖说"我亲自送你上山"，但游戏里他根本不会出现；"船在**海边**"指的是 `923` 欧阳锋那片礁石，真正离场点 `Leave/Entrance` 在码头 `(47.11, 15)`，就在上岸点 `(44.9, 14.9)` 旁 2.2m | 改为"到了重阳宫，凡事听师父的""受了委屈，也别自己扛着"；指引改成"船还停在**码头**——你上岸的地方" |
| 4 | `4.lua` 旧庙祝 | 与 `559.lua` 是同一段剧情的旧版，却把玩家指向"去终南山重阳宫"，等于跳过郭靖相遇、桃花岛、古墓、绝情谷全部章节 | 整段改写成与 559 一致（引导去**佛堂**找白袍客）。该脚本绑在废弃场景 `00_mochuanlinju`（不在 MapConfig），玩家本来进不去，属于拆掉未来的坑 |
| 5 | `1001.lua` 郭靖相遇 | 无论有没有翻过木箱，都会说"（我摸了摸怀里的铁枪残片）"——没拿遗物的玩家怀里空空如也 | 按 `父亲遗物` 分流：没拿 → 郭靖指点"供桌上那口旧木箱，你爹的东西该由你收着"；拿了 → 保留原内心独白；结尾出门描写同样分流 |

### 3. 确认无需动的地方

- **地图 id 100–164 共 65 个"未开放"地点全部指向 `62_pomiao`（破庙）**：
  这是原版 jynew 的做法（未开放点复用破庙），名称自带"〔未开放〕"后缀，
  且节点坐标全堆在 `(0,0,0)`。不是本 MOD 引入的问题。
- **12 处 DANGLING／2 处"剧情点名但场上没有模型"全部落在 3 个废弃场景**
  （`00_mochuanlinju`、`01_moqiaoshanzhuang`、`02_wanzhushuyuan`），
  **14 个正式场景 0 问题**（桃花岛 466 分别挂在郭靖 0.1m 和黄蓉 0.1m 上、
  922 挂郭芙 1.6m、923 挂欧阳锋 1.6m，都对得很准）。
- `850.lua`、`851.lua`（"香烛木箱""半卷经文"）没有任何场景绑定，是无害的一句话装饰。

### 4. 验证与分发

- `lint_lua.py` 168 脚本 0 问题 / `check_story.py` 168 脚本 0 错 0 提醒 /
  `audit_flags.py` 65 flag 0 只读不写 / `find_event.py --all` 孤立 0
- `jyx2mod.py unity shendiao --with-base --force` → `install`：`shendiao_maps` 142 MB、
  `shendiao_mod` 42 MB，manifest 里确认 `4 / 401 / 466 / 914 / 922 / 1001.lua` 六个都在包内
- `jyx2mod.py check shendiao` 一切正常（Preloaded 4 个）

> **坑（重要）**：只跑 `unity shendiao`（不带 `--with-base`）会带 `-skipBase 1`，
> 共享资源被内联进 **maps** 包，`shendiao_maps` 会从 142 MB 涨到 380 MB。
> 改完 Lua 重新分发时务必 `--with-base --force` 全量打一次；
> `--force` 也必须有 —— 脚本按 mtime 判"没有检测到改动"会直接跳过构建。

### 5. 仍然只能进游戏验的

- 922 打赢／打输两种台词是否都通顺（平衡改动后玩家大概率会赢）
- 桃花岛结尾"码头"指引能否让玩家找到 `Leave` 点
- 序章不翻木箱直接找郭靖，是否还会出现"怀里空空却摸残片"

---

# 2026-10-29 晚：章节内容按原著丰满（李莫愁线打通）

## 一、动机与现状

用户反馈：「章节内容再丰满些，比如第一章有李莫愁的」。

摸底（新工具 `tools/shendiao/map_events.py`）显示 14 个正式场景共 **107 个事件**，
其中古墓只有 5 个（217/219/442/902/3006），而原著古墓占了整整六回
（求师终南、全真门下、活死人墓、玉女心经、重阳遗篇、白衣少女）。

更要紧的是：**李莫愁这条线断成了两截**——
455 里鹿清笃说「前些时候有个女魔头在山下出没」，此后直到古墓 217 才再见她一面，
说完「看在我师妹面上饶你一命」就退场，**伏笔从未兑现**；
之后的绝情谷、陆无双、程英全部与她无关地各自演完。
原著里她从第二回一路追杀到第三十二回，是前半部唯一的贯穿性反派。

## 二、约束：不能加事件，只能把脚本写长

`patch_scene_events.py` 只能改**已有的** GameEvent（layer / trigger / target / 位置 / EventId），
`add_scene_npc.py` 只能往场景里塞 prefab 实例（模型），**两者都不能新建 GameEvent**。
例如 `18_gumu.unity` 一共只有 5 个挂了 GameEvent 的物体，**没有空槽位**。

结论：扩容只能靠**把单个脚本写长** —— Jyx2 的 `Talk` 没有条数上限，
一个事件足以承载一回书的内容。本轮所有改动都遵守这条，**未改动任何 .unity**。

## 三、本轮改动（8 个脚本）

### 1. `217.lua` 重写：李莫愁闯墓（1.6kb → 5.1kb）

原来只有「墓门对峙 → 打一场 → 她走」三句话。现按原著第五回末 + 第九回重写：

| 原著节点 | 落到脚本 |
| --- | --- |
| 携弟子（洪凌波）闯墓 | 「身后跟着两个杏黄短打的年轻女子，垂着手，不敢抬头」 |
| 索要《玉女心经》 | 师妹／师伯的辈分、二十年旧怨 |
| 师门心结 | 李莫愁把欧阳锋引进墓，师父因此重伤而死；小龙女一直怪她 |
| 交手 | `TryBattle(203)` 胜负双分支 |
| 小龙女放断龙石 | 「师父把断龙石的机关交给你，是要我同归于尽？」 |
| 从水下秘道逃生 | 「墓后有水道。师父留的。」 |
| 师父的遗言 | 「她若回来，别杀她。」——为她后来屡次作恶却无人索命留依据 |

**顺手改掉一个语义硬伤**：旧版杨过上来就说「你杀了孙婆婆」，
但 902 明写孙婆婆是**全真道士一掌打死**（原著为郝大通误伤），李莫愁是被冤枉的。
现改为杨过说「孙婆婆死了」，李莫愁答「全真教打死的。这笔账别安到我头上」。

新增 flag `断龙石`（217 写、219 读），`audit_flags.py` 复核 66 flags / 0 只读不写。

### 2. `219.lua` 扩写：玉女心经

补进原著第六回的内容：石棺上刻的是林朝英的《玉女心经》，**前半篇写情、后半篇写剑**；
「心经须得两人同练，一阴一阳」——这是全书师徒情的起点。
另加 `断龙石` 分支：若已放下断龙石，开篇先说「这墓里的光，从那一夜起就是全部的光了」。

### 3. `906.lua` 扩写：陆无双交代李莫愁

原先她只出现一次，教完「分花拂柳手」就结束，**一句没提自己的师父是李莫愁**。
现补：爹娘是李莫愁杀的、被抱走养如犬马、左腿是逃跑时被打断的、
偷了《五毒秘传》出逃（她答「烧了」答得太快，留白）。
顺手修正原著关系错误：程英是她的**表姐**，原脚本写成「师姐」。

### 4. `455.lua` 补伏笔：女魔头有名有姓

鹿清笃原话只有「有个女魔头在山下出没」。现补郭靖追问「可是姓李？」→
「道号『赤练仙子』，一手拂尘，一手毒针。山下的猎户说她走过的地方，草都是黑的」，
让玩家**进古墓之前**就记住这个名字。

### 5. `399.lua` 补出场：绝情谷花丛中被渔网困住

原著李莫愁是被周伯通引到绝情谷、裘千尺命弟子用渔网阵困在情花丛。
入谷时补一段：她被细麻渔网罩在花丛里，「一根一根地扯网绳，扯断一根，又缠上两根」，
求杨过解网、承诺记人情，杨过没过去 —— 于是有了第三章结尾那句「那张网，你终究没替我解」。

### 6. `401.lua` 补结局：问世间情是何物

原第三章以击退公孙止收尾。现按原著第三十二回，在她被困之后补**火中葬身**：
情花丛起火，她在火里唱元好问《摸鱼儿·雁丘词》——
「问世间，情是何物，直教生死相许……渺万里层云，千山暮雪，只影向谁去？」
死前认出杨过，笑了一下：「也好。」

### 7. `428.lua` 补一笔：欧阳锋临死记起自己是谁

洪七公与欧阳锋相拥而逝本来已经写得克制到位，只缺原著最要命的一笔，补上：
「我……我是谁？」—「你是欧阳锋。」—「欧阳锋。」「我是欧阳锋。」
（原著里他疯癫半生，死前才想起自己。）

### 8. `836.lua` 补全剑冢四剑

原来只写了三柄剑，且删掉了独孤求败的刻字。现补成原著**四柄**，每柄都带刻石原文：

| 剑 | 刻石 |
| --- | --- |
| 青钢利剑 | 凌厉刚猛，无坚不摧，弱冠前以之与河朔群雄争锋 |
| 紫薇软剑 | 误伤义士，不祥，弃之深谷 |
| 玄铁重剑 | 重剑无锋，大巧不工，四十岁前恃之横行天下 |
| 木剑（已朽） | 四十岁后，不滞于物，草木竹石均可为剑……渐进于无剑胜有剑之境 |

## 四、新工具 `tools/shendiao/map_events.py`

把「正式场景 → 事件 id → 宿主物体 → 坐标 → 脚本首句」打成一张表，用来一眼看出哪一章太薄。

```powershell
$env:PYTHONIOENCODING='utf-8'
Start-Process python -ArgumentList 'tools/shendiao/map_events.py' `
  -RedirectStandardOutput Logs/_me.txt -RedirectStandardError Logs/_me.err -NoNewWindow -Wait
```

只统计 `MapConfig.lua` 里 id<100 的地图（废弃场景不进表）。
本轮产出的分布：破庙 7 / 重阳宫 10 / 古墓 5 / 神雕洞 7 / 绝情谷 5 / 绝情谷底 2 /
百花谷 3 / 华山 10 / 思过崖 3 / 铁掌山 15 / 黑龙潭 5 / 一灯居 2 / 程英居 2 / 桃花岛 5。

## 五、验证与分发

```
lint_lua.py     168 脚本 0 问题 0 条
check_story.py  168 脚本 0 错误 0 提醒
audit_flags.py  66 flags / 0 只读不写 / 1 只写不读（全篇完成）
unity shendiao --with-base --force  → shendiao_maps 135.8 MB + shendiao_mod 40.4 MB
install shendiao --src Export/shendiao  → [ok]
check shendiao  → 一切正常（maps 45 / mod 179 资源）
```

Unity 日志确认 8 个脚本均已入包（217 从 1.6kb 涨到 5.1kb）。

## 六、下一步候选（未做）

- 铁掌山（15 个事件，第四章）与百花谷 / 黑龙潭（瑛姑、一灯线）尚未按原著扩写
- **洪凌波在 `人物.xlsx` 里没有条目**（73 人里无此人），目前只能以旁白存在；
  要给她台词，得先加人物行 + 头像资源，再 `configs shendiao` 重新生成
- 郭芙断臂（原著第二十六回）目前只在 389 一句「右臂断了」带过，程英居 402 有善后，缺正面描写
- `00_mochuanlinju` 等 3 个废弃场景仍在工程里，不进包，可择日删除

---

# 2026-10-29 深夜：第一回《风月无情》按原著重做（开场不再是杨过）

## 一、动机

用户原话：「开头不是杨过的剧情，你做的太简单了，重做吧，先做第一回」。

旧版破庙序章是**杨过第一人称独白 + 庙祝一句指路 + 郭靖认亲**，等于把原著
第一回《风月无情》整回跳过了——李莫愁、陆家庄灭门、九口血手印、武三通刨坟、
程英陆无双、柯镇恶、破窑夜战，一样都没有。本轮把这一回补成一条完整章节。

## 二、约束与破题：旁白不需要头像

约束没变：`62_pomiao` 只有 7 个 GameEvent（557 进庙 / 558 木箱 / 559 庙祝 /
563 墓碑 / 564 用物品 / 1001 郭靖 / 1002 黄蓉），**不能新增事件**，场上也
只有老庙祝、郭靖、黄蓉三个模型。

破题靠 `BuildSource/Lua/main.lua`：

```lua
function Info(msg)
    Talk(0, msg, "", 2)   -- type=2：不显示头像与姓名，只出居中文字
end
```

`ChatUIPanel.Show()` 里 `type == 2 || type == 3` 时 `HeadAvataPre` 与 `Name`
都被隐藏（`ChatUIPanel.cs:147-152`）。所以第三人称楔子可以直接写：

```lua
Talk(0, "三天之后，城西陆家庄的白墙上，印了九个血手印。", "", 2)
```

注意 `expr.lua` 包了一层 `Talk`，第三参不是表情名时会**原样转发四参**，
所以这个用法不会破坏表情系统（它的注释里已写明这一点）。

## 三、事件 → 剧情映射（全部挂在原有事件上）

| 事件 | 旧内容 | 新内容 |
| --- | --- | --- |
| 557 进庙 | 杨过独白"爹死在铁枪庙" | **楔子（旁白）**：南湖采莲（程英/陆无双登场）→ 柳下李莫愁掌心血、青袍老者 → 陆家庄九个血手印逐个对命 → 一夜灭门、掘坟盗尸 → 疯汉刨坟骂"何沅君"、拗断槐树、柯镇恶赶到 → 镜头落回铁枪庙，杨过才开口 |
| 559 庙祝 | "你去重阳宫打听" | **三段说书**：①陆展元/何沅君/十年之约/九口血手印/武三通义女 ②见他手黑 → 冰魄银针 + 红花绿叶锦帕 ③指路佛堂 |
| 563 墓碑 | "蔡邕之墓"（无关） | **陆展元夫妇合葬墓**：坟被刨、空棺、棺盖铁器痕、拗断槐树、泥里十指印；第二次再来时**李莫愁亲至坟前**，点破银针有毒 |
| 564 用物品 | "挖不动" | 拨开棺底 → 断成两截的玉镯（内壁刻"沅君"）+ 发霉的馒头，坐实"掘墓人不要陪葬，只要人" |
| 1001 郭靖 | 认亲 | **黄蓉解冰魄银针毒**（九花玉露丸）+ 追问陆家庄火 → 认亲 → 邀去桃花岛（保留是/否选择） |
| 1002 黄蓉 | 上岛前闲聊 | **夜戏收束**：破窑里武三通与程英陆无双 → 李莫愁歌声 → 拂尘打倒武三通、柯镇恶赶到 → 杨过从背后抱住她 → 石子打落银针 → 掳走陆无双、青袍客（黄药师）救走程英 → 郭靖决定带他回岛 |

另外 558 木箱补了"烧剩的焦纸 + 缠红绳的铁钉"，让`父亲遗物`有实物感。

## 四、新增 flag（`audit_flags.py` 已核）

```
第一回_楔子    557 写 / 557 读
第一回_旧事    559 写 / 559 读
第一回_坟地    563 写 / 559、563 读
第一回_李莫愁  563 写 / 563 读
第一回_中毒    563 写 / 559、563、1001 读
第一回_求医    559 写 / 559 读
第一回_解毒    1001 写 / 563、1001、1002 读   ← "见过郭靖"总开关，没中毒也置位
第一回_玉镯    564 写 / 564、1002 读
第一回_完      1002 写 / 559 读
第一回_应允 / 第一回_拒辞 / 第一回_见过郭靖  1001 内部用
```

`序章完成` 的写入点从 1001 **挪到了 1002**：夜里那场戏才是本回收束，
否则玩家看完认亲就能直接去桃花岛，高潮会漏掉。466/922/923 的判定不受影响。

## 五、已知限制

- 武三通、洪凌波、陆立鼎夫妇在 `人物.xlsx` 里没有条目 → 只能出现在旁白里
  （用「」引出他们的原话），不能以头像对话形式出场
- 场上没有李莫愁模型，夜戏是"文字 + 头像"演出，不是立绘走位
- 原著第一回里"九个手印逐个对命"的长解释放在楔子；庙祝那段是复述 + 补充，
  两处都保留，重复感靠错开视角（旁白述事 / 庙祝讲人情）

## 六、验证

```
lint_lua.py     168 脚本 0 问题 0 条
check_story.py  168 脚本 0 错误 0 提醒
audit_flags.py  78 flags / 0 只读不写 / 1 只写不读（全篇完成，既有）
sim_lua.py --preset ch1   4 条线全部断言通过
```

`sim_lua.py` 是本轮新增的工具：用 lupa 真跑 Lua，把 `Talk / GetFlagInt /
SetFlagInt / AddItem / ModifyEvent / ShowYesOrNoSelectPanel` 打成桩，按顺序
执行脚本并把对白流水 + flag 快照写到 `Logs/_sim_out.txt`。`--preset ch1`
内置四条回归线（主线 / 跳过坟地 / 先挖坟 / 拒绝上岛），任何一条跑不通就抛错。

```powershell
python tools/shendiao/sim_lua.py --preset ch1
python tools/shendiao/sim_lua.py 557 559 563 559 1001 1002   # 自由组合
```

打包（Lua 在 `shendiao_mod` 这个 AB 里，改脚本必须重新导出 + 安装）：

```powershell
python tools/moddev/jyx2mod.py unity shendiao --with-base --force
python tools/moddev/jyx2mod.py install shendiao --src Export/shendiao
# → shendiao_maps 142,428,161 B / shendiao_mod 42,362,637 B（比上一轮 +41 KB）
# manifest 里确认 557/558/559/563/564/1001/1002.lua 全部在包内
```

`lint_lua.py` 只查括号与字符串配平、`check_story.py` 只查表引用，**都发现不了
"flag 分支写反 / goto 跳进死路 / 某条线走不到"**，这次靠它抓出的问题：
`1002` 原来只认 `第一回_解毒 == 1`，不中毒的玩家会卡死在「先去找靖哥哥」。

进游戏要验的：557 楔子是否自动播一次并关闭；563 第二次是否切到李莫愁；
中毒后 1001 是否先解毒再认亲；1002 是否只在见过郭靖后可触发；
`序章完成` 之后 559/1002 是否走收尾分支。



---

# 第一回改版 v2（2026-10）——三人坟前演出 + 必败战 + 冰魄银针 + 场景显隐

目标：把"旁白讲一遍"改成"人站在那儿演一遍"。楔子那段 72 句旁白全部拆掉，
核心戏搬到后山坟前，由 **李莫愁 / 程英 / 陆无双** 三个模型自己演；每场戏
压在 15 句以内；坟前打一场必败的仗，打完中毒、拿到暗器「冰魄银针」。

## 一、这次用到的引擎能力（都已在 Lua 侧验证存在）

| Lua 调用 | C# 位置 | 语义 |
| --- | --- | --- |
| `jyx2_ReplaceSceneObject("", "NPC/名字", "0"/"1")` | `LevelMasterBooster.ReplaceSceneObject` → `SetSceneInfo` → `RefreshSceneObjects` | 隐藏/显示 `Level/<路径>`，**写进存档**（`GameRuntimeData.GetSceneInfo`），重进地图仍然生效。对象不存在会 `Debug.LogError`，所以只对确定存在的 NPC 调 |
| `jyx2_CameraFollow("Level/NPC/李莫愁")` | `Jyx2LuaBridge.cs:413` → 改 Cinemachine vcam 的 `Follow` | 镜头锁到某个 NPC；`GameObject.Find` **要求对象是激活的**，所以先 `"1"` 再 follow |
| `jyx2_CameraFollowPlayer()` | 同上，等价 `Follow("Level/Player")` | 镜头收回主角 |
| `TryBattle(203)` | `main.lua` 里 `util.async_to_sync(luaBridge.TryBattle)` | 同步返回 true/false（胜/负）。**输了不会 GameOver**：`BattleManager.OnBattleEnd` 的 Lose/Surrender 分支只弹「战斗失败！」然后 `EndBattle()` 回地图，脚本继续跑 → 必败战斗可以放心写 |
| `luaBridge.RestTeam()` | `Jyx2LuaBridge.cs:1483` | 全队 `Recover()`（满血、清 Hurt/Poison）。`Rest()` 有 `Hurt<33` 门槛，战败后不生效，必须用 `RestTeam` |
| `DarkScene()` / `LightScene()` | `Jyx2LuaBridge.cs:305/325` | `BlackCover` 淡入淡出 1 秒，含回调 → 大跨度转场用 |
| `AddItem(71, 3)` | — | 物品 71 = 冰魄银针，`物品.xlsx` 里 **类型 4 = 暗器**（`Jyx2ItemType.Anqi`），战斗里走"暗器"页可投掷；-50 HP |

没有 CG/插图 API：`EndAmination` 是空实现，`ChangeScencePic` 只换 2D 场景贴图，
`UI` 里没有看图面板。所以"过场图"这一版先用 **转暗→旁白→转亮** 的过场卡代替，
真要上图得往场景里塞一个 `Canvas + Image` 的 prefab（见"未做"一节）。

## 二、场景布景（`62_pomiao.unity` → `Level/NPC`）

用 `tools/shendiao/add_prefab.py`（读 prefab 根 GO/根 Transform 的 fileID，手写
PrefabInstance + 两块 stripped，不依赖模板场景）加的：

```
李莫愁  (-3.8, 5, -12.2)  rotY 150   ← BattleNpc/Miejue.prefab
程英    (-5.0, 5, -12.9)  rotY 100   ← BattleNpc/Chengying.prefab
陆无双  (-2.7, 5, -13.5)  rotY 190   ← BattleNpc/Azi.prefab（阿紫的模型）
```

坐标依据：`Tomb` (1.21, 4.95, -13.41)、`mubei` (-1.86, 6.03, -13.18)，坟前地面
高度就是 y≈5.0；563 的触发盒在 (-1.9, 6.9, -13.2)，玩家从庙里（+z）走过来正好
看见三个人背对镜头站在坟前。

驱动脚本（中文名字经 PowerShell 传 argv 会变乱码，所以在进程内拼 argv）：
`tools/shendiao/add_grave_npcs.py`（默认 dry-run，`--apply` 才写盘；幂等性靠
`add_prefab.py` 每次重新读场景挑空段 fileID，重复跑会再摆一份，别手滑）。

**注意**：三个 prefab 在 `BuildSource/ModelCharacters/` 里属于 base_assets，
导出时要带 base：

```powershell
python tools/moddev/jyx2mod.py unity shendiao --with-base --force
python tools/moddev/jyx2mod.py install shendiao --src Export/shendiao
```

## 三、新的演出顺序（每场 ≤15 句，`sim_lua.py` 里有断言）

| 事件 | 场景 | 内容 | 句数 |
| --- | --- | --- | --- |
| 557 进庙 | 庙门 | 藏起坟前三人 + 郭靖黄蓉；杨过四句独白，指到庙祝 | 4 |
| 559① 庙祝 | 大殿 | 九个血手印 / 十年之期 / 后山坟被刨「土里的东西别用手碰」→ 收尾时把坟前三人 **放出来** | 15 |
| 563① 坟前 | 后山 | **三人演出**：李莫愁对碑、问陆无双名字、程英挡在前面、放她们走；镜头 `follow 李莫愁`，末尾 `CameraFollowPlayer` + 收起程英陆无双 | 15 |
| 563② 坟前 | 后山 | 杨过 ↔ 李莫愁（尸首谁搬的 / 为什么杀七个人）→ `TryBattle(203)` **必败** → `RestTeam()` | 13 |
| 563③ 坟前 | 后山 | 三点寒星 → 掌心中毒 → `AddItem(71,3)`「冰魄银针」→ 她留话给疯汉、走人、隐藏模型 | 9 |
| 559② 庙祝 | 大殿 | 看见黑手 → 冰魄银针 → 指路佛堂，**这时才放出郭靖/黄蓉** | 9 |
| 1001① 佛堂 | 佛堂 | 黄蓉解毒（九花玉露丸 ×2） | 15 |
| 1001② 佛堂 | 佛堂 | 认亲：姓杨 → 杨康 → 郭靖 | 13 |
| 1001③ 佛堂 | 佛堂 | 邀去桃花岛（是/否） | 4(+遗物 2) |
| 1002① 破窑 | 旁白 | 入窑、程英陆无双、疯汉、玉镯、歌声 | 15 |
| 1002② 破窑 | 旁白 | 李莫愁到、帕子、柯镇恶、抱人梗、银针被打落 | 15 |
| 1002③ 破窑 | 破窑→船 | 掳走陆无双 / 青袍客救程英 / 郭靖决定带他走 → **转暗·旁白·转亮** 的桃花岛过场 | 12 |

新增 flag：`第一回_夜` / `第一回_夜变`（1002 三段推进）、`第一回_认亲`
（1001 认亲 → 邀约分段）。`第一回_见过郭靖` 现在被 1001 的认亲开场读一次
（"毒清了？那好。"），不再是只写不读的死 flag。

## 四、这一版刻意没做的（留给下一轮）

1. **真正的过场图**：需要一个 `Canvas(ScreenSpace-Overlay) + Image` 的 prefab，
   塞进 `62_pomiao.unity`，CG 存成 sprite；显示仍可用
   `jyx2_ReplaceSceneObject("", "CG/去桃花岛", "1")`（它只做 SetActive，画布位置无关）。
   图可以走 `tools/shendiao/gen_heads.py` 那套 gemini 流程生成。
2. **武三通 / 洪凌波**：`人物.xlsx` 里没有条目（无头像、无模型），目前只有
   「」旁白原话。要上场就得加人物行 + `Models/xxx.asset` + 头像 PNG + 重新导出。
3. **柯镇恶**（人物 30，模型可借 `BattleNpc/Xiexun.prefab`）：夜戏里只有声音，
   因为破窑在地图上没有实体位置，摆哪儿都是"站在空气里"。等破窑场景定下来再加。
4. 坟前三人站的方位/朝向只能靠坐标推，**进游戏要亲眼看一下**（可能偏高/偏低
   半格，或背对镜头过度）。

## 五、验证

```
sim_lua.py --preset ch1    5 条线全过（主线 / 跳过坟地 / 先挖坟 / 拒绝上岛 / 坟前打赢）
lint_lua.py                168 脚本 0 问题
check_story.py             168 脚本 0 错误 0 提醒
check_scene_fileids.py     62_pomiao.unity 0 问题
check_refs.py              三个新 prefab 未出现在缺失清单里
jyx2mod.py check shendiao  [ok] 一切正常
```

`sim_lua.py` 这轮补了 `jyx2_ReplaceSceneObject / jyx2_CameraFollow / TryBattle /
DarkScene / LightScene / luaBridge.RestTeam` 的桩，并且会统计**每场戏的句数**，
`--preset ch1` 里直接断言 ≤16，防止以后再加旁白把节奏拖回去。
剧本流水导出：`python tools/shendiao/sim_lua.py 557 559 563 563 563 559 1001 1001 1001 1002 1002 1002`
跑完再 `python tools/shendiao/export_story_doc.py` → `docs/第一回-风月无情-剧本.txt`。


## 六、第二轮补完（人物 / 一张图 / 显隐坑）

### 1) 「藏起来再放出来」原本是坏的（重要）

`LevelMasterBooster.RefreshSceneObjects` 解析路径用的是
`GameObject.Find("Level/" + path)`，而 **GameObject.Find 只返回激活中的对象**。
所以 `jyx2_ReplaceSceneObject("", "NPC/李莫愁", "0")` 之后再调 `"1"` 只会 LogError，
人永远不回来 —— 上一版 557 藏、559/563 释放那三个人，运行时其实是走不通的。

解法：`Lua/hotfix.lua` 里加了全局函数 `ShowSceneNpc(path, on)`：
先用 `Transform.Find` 从 `Level` 逐段下钻（**它能找到 inactive 的子节点**）
`SetActive(true)`，再调 `jyx2_ReplaceSceneObject` 把状态记进存档。
`557/559/563/1001/1002` 的 34 处调用已全部换成 `ShowSceneNpc`，
`tools/shendiao/sim_lua.py` 也补了同名桩。

### 2) 武三通 / 洪凌波 真的上场了（柯镇恶也有了实体）

| 人物 | Id | Pic | 模型（`Models/<名字>.asset` 的 m_View） | 站位（`Level/NPC`） |
| --- | --- | --- | --- | --- |
| 武三通 | 44 | 44 | `StoryNpc/Zhuangjiahan.prefab`（庄稼汉） | (1.7, 5, -15.3) rotY195 |
| 洪凌波 | 73 | 73 | `BattleNpc/Chenglingsu.prefab` | (-4.7, 5, -11.3) rotY165 |
| 柯镇恶 | 30 | 30 | `BattleNpc/Xiexun.prefab` | (-1.5, 5, -16.8) rotY15 |

- `人物.xlsx` 新增第 78/79 行（id 44 / 73），数值照 武敦儒 / 陆无双 复制后调整；
  `ModelFileKey` = 武三通 / 洪凌波，配 `Models/武三通.asset`、`Models/洪凌波.asset`。
- 头像用 `gen_heads.py --only 44,73 --model gemini-nano-banana-2.1 --apply` 生成，
  和原有 65 张同一画风；`meta_for()` 现在同时换 `spriteID`
  （批量复制 meta 会撞，原来只有 `_tag_assetbundle.py` 全量重跑才修）。
- 场景实例由 `tools/shendiao/add_ch1_extra.py` 一次写入（默认 dry-run，`--apply` 才落盘）。
- 台词：武三通接「何沅君呢？何沅君到哪儿去了！」；洪凌波开场
  「师父，窑口窄，我堵着门。」；柯镇恶在他那句「李莫愁！你杀陆家满门」之前
  `ShowSceneNpc("NPC/柯镇恶", true)` 才现身。

### 3) 桃花岛那张图（不做 CG 系统，只有一个 Canvas+Image）

- 生成：`tools/shendiao/gen_scene_pic.py --only taohuadao --apply`
  → `BuildSource/cg/taohuadao.png`（1920×1080 水墨远景，gemini-nano-banana-2.1）。
- 显示：`Prefabs/CgTaohuadao.prefab`（ScreenSpace-Overlay Canvas
  `sortingOrder=-10` + 全屏 Image，preserveAspect），由 `add_cg_node.py`
  摆进 `62_pomiao.unity` 的 `Level/去桃花岛`。
- 开关：`ShowSceneNpc("去桃花岛", true/false)`；557 先藏，1002 末尾在
  `DarkScene/LightScene` 之后、两句旁白期间展示。`sortingOrder=-10` 让图排在
  对话 UI 下面，字不会被盖住。

### 4) 顺手修的工具问题

- `add_prefab.py` 现在认 RectTransform 根的 prefab（原来只匹配 `!u!4`，
  插入 UI prefab 直接报「找不到根 Transform」）。
- `add_model.py` 生成的 `.meta` 里 `assetBundleName` 原来是空的（资源不会进包），
  已补成 `shendiao_mod`。
- `_tag_assetbundle.py` 支持 `--only 44,73`，不必每次重写全部头像的 spriteID。
- `near_objects.py`（新）：列出 `<scene>` 里某个平面坐标附近的物体，
  摆 NPC 之前先看有没有墓碑/石头/触发点。
- 1002 第三段收尾时把 李莫愁 / 洪凌波 / 陆无双 / 程英 / 武三通 全部收起
  （人都不该还杵在坟前），柯镇恶留下。

### 5) 还没做 / 需要进游戏确认

1. `jyx2mod.py unity shendiao --with-base --force` + `install` 之后亲眼确认：
   三人朝向、武三通与柯镇恶有没有穿模、Canvas 图是否在对话框下方。
2. 破窑在地图上没有独立区域，武三通/洪凌波实际是站在坟地那一小块上
   （与 1002 的"庙后破窑"共用同一片场地）。
3. `ModSetting.asset` 的 `StoryIdNameFixes` 后面残留了一段坏 YAML
   （第 107 行起重复的 `Name:` 与 `- - Id:` 列表），目前不影响加载，有机会再清。


### 6) 导包时踩到的坑：.meta 被截断 → 头像不进包

第一次 `jyx2mod.py unity shendiao` 之后，`shendiao_mod.manifest` 里只有 65 个头像，
少了 `head/44.png`、`head/73.png`，Unity 日志报
"does not have a valid GUID and its corresponding Asset file will be ignored"。

根因是一条内联 python：`open(p,'w').write(re.sub(..., io.open(p).read()))`
—— `open('w')` 先把文件截断成 0 字节，再读就是空串，最后只写回 55 字节的尾巴。
`gen_heads.meta_for` 的注释里记着同一个坑，还是又踩了一次。

- 重建：`python tools/shendiao/fix_head_meta.py 44 73`
  （删掉坏 meta，从同目录其它头像 meta 复制，换 guid + spriteID）。
- 防呆：`_tag_assetbundle.py` 遇到不以 `fileFormatVersion:` 开头的 meta 直接跳过并提示。
- 复查：`Export/shendiao/shendiao_mod.manifest` 里应有 **67** 个
  `BuildSource/head/*.png`，以及 `CgTaohuadao` / `cg/taohuadao`。

### 7) 本轮导出与安装（已验证）

```
jyx2mod.py unity shendiao                  [ok] 导出完成（base_assets 无变化，自动 skipBase）
jyx2mod.py install shendiao --src Export   -> wuxia_launch_Data\mods\shendiao
    shendiao_mod 89.3MB / shendiao_maps 380.9MB
```

manifest 校验：head 67 个（含 44/73）、`CgTaohuadao.prefab`、`cg/taohuadao.png` 均在包内；
`check_scene_fileids.py 62_pomiao.unity` 0 问题；`sim_lua --preset ch1` 5 条线全过；
`lint_lua` 168 脚本 0 问题；`check_story` 0 错 0 提醒；`jyx2mod.py check` [ok]。

进游戏请用**新存档**（旧存档的 `WorldMapSaveData` 会带旧的 SceneInfo，
把本轮"默认隐藏"的几个人当成都该藏着）。


### 8) 头像补全（人物表 75 行 → 90 张头像，缺图 0）

之前 `人物.xlsx` 里有一批 Pic 在 MOD 的 `BuildSource/head/` 下没有图：
`61 伏格多`（最终 boss）、`62 将军府士兵`、`71 曼陀谷弟子`、`610 蓝隼士兵`
（base 里只有借来的原版人脸），以及**完全没图**的 `141-149/1410 野狼`、
`163-168 黑熊/巨型黑熊`、`181/182 毒蛇`。

- 新增 `gen_heads.py` 的 ROSTER 条目（画面风格与已有 65 张一致）。
- **动物必须用另一套提示词**：原来的 STYLE 写着"半身胸像、肩膀入画"，
  模型会把野狼画成披狼皮的汉子、毒蛇画成"肩上盘蛇的人"。
  `ANIMAL_STYLE` 明说"画面中只有这只动物，绝对不要出现人"之后才正常。
- `dup_head_pics.py`：同一个 Pic 代号只生成一张，再复制给其它代号
  （曼陀谷弟子 71→72、野狼 141→142…149/1410、黑熊 163→164…167、毒蛇 181→182）。
- 复查：`人物.xlsx` 的 Pic 集合 − `BuildSource/head/*.png` = **空**；
  `shendiao_mod.manifest` 里 `BuildSource/head/*.png` 共 **90** 个，与磁盘一致。

> 同一个"先 `open('w')` 再读文件"的坑这轮又踩了一次：`dup_head_pics.py` 里
> `io.open(meta,'w').write(G.meta_for(dst))` → 15 个 meta 变成 0 字节。
> 现在 `meta_for()` 会校验模板（必须 `fileFormatVersion:` 开头且 > 500 字节），
> 复制类脚本一律"先取文本再写文件"。

### 9) 本轮最终状态

| 项目 | 结果 |
| --- | --- |
| `人物.xlsx` | 75 行（新增 44 武三通 / 73 洪凌波），Pic 全部有头像 |
| `Models/` | 57 个 ModelAsset（新增 武三通 / 洪凌波） |
| `62_pomiao.unity` | `Level/NPC` 下 9 个实例 + `Level/去桃花岛`（Canvas 图） |
| `BuildSource/cg/` | `taohuadao.png` 1920×1080（nano-banana-2.1 生成） |
| 导出 | `Export/shendiao`：shendiao_mod ≈ 89MB / shendiao_maps ≈ 381MB |
| 安装 | `wuxia_launch_Data\mods\shendiao`（最后一次导出后已覆盖安装） |
| 校验 | lint 0 / check_story 0 / scene fileids 0 / mod check `[ok]` / sim 5 条线全过 |


### 10) 第二轮玩家反馈：郭靖/黄蓉 提前登场 + 朝向 + 飘在空中

玩家原话：「拿了铁枪、跟庙祝说完话，郭靖黄蓉就提前出现了（应该等李莫愁那一段之后）；
两人的朝向不对，而且是飘在空中的。」

**① 提前登场 —— 根因在 `559.lua` 的 `::label3::`**

559 的分支原本是：

- `::label1::` `第一回_旧事 == 0` → 讲九个血手印 / 十年之期，放出坟前三人；
- `::label2::` `第一回_中毒 == 1 and 第一回_求医 == 0` → 指路去佛堂，放出郭靖/黄蓉；
- `::label3::` `序章完成 == 0` → **无条件** `ShowSceneNpc("NPC/郭靖"|"NPC/黄蓉", true)`。

558（供桌上那只旧木箱＝铁枪残片）最后一句是「铁枪残片。去问<color=#FF0000>老庙祝</color>。」
玩家照着做，就会在**还没中毒**的状态下再点一次庙祝 → 落进 label3 → 两位客人提前登场，
而坟地那桩事（563）还没开始。

修法：label3 只在 `第一回_求医 == 1`（＝已经被指去佛堂）时才补显；否则只说
「后山那两座坟，你还没去看罢」。`sim_lua.py --preset ch1` 新增一条回归线
（`557 558 559 559 559`），断言此时日志里**没有** 郭靖/黄蓉 的「出现」事件。

**② 朝向 —— 场景里本来就写着 yaw=90（面朝东墙）**

`62_pomiao.unity` 里郭靖/黄蓉的 `m_Modifications` 都有 `m_LocalEulerAnglesHint.y: 90`，
两人并排面朝东侧墙。按剧情「站在铁枪（供桌）前」改：

| NPC | 位置 | 原 yaw | 新 yaw | 朝向 |
| --- | --- | --- | --- | --- |
| 郭靖 | (0.8, 5, -6) | 90 | **220** | 供桌 Table_17 (-1.6, 5.1, -8.8) |
| 黄蓉 | (2.2, 5, -7.2) | 90 | **247** | 东侧、同样望着供桌 |

- yaw 公式：`atan2(dx, dz)`（Unity 里 yaw 0 = +Z 朝玩家来的方向，90 = +X，180 = -Z，270 = -X）。
- `edit_instance.py --rot-y` 会同时写 `m_LocalRotation.w/y` 和 `m_LocalEulerAnglesHint.y`，不要手改四元数。
- 1001 收尾那句「黄蓉就在佛堂西首坐着」一并改掉：她其实在**东**首、而且**站**着
  （`sit_on_chair.controller` 已经在上一轮撤掉）。

**③「飘在空中」＝ 盘腿坐在半空（上一轮已修，玩家还在跑旧包）**

根因是早先给郭靖/黄蓉的实例套了 `sit_on_chair.controller`（在
`BuildSource/AnimationControllers/备份/` 下），场景里又没给她们摆椅子 → 悬空盘坐。
HEAD（`4e425e2f6`）已把 `62_pomiao.unity` 两个实例的 `m_Controller` 改回
`GuojingController`（`c1fb7eef…`）/ `HuangrongController`（`afb4f35a…`），
贴地高度 y=5.0 与同图另外 7 个 NPC 一致（佛堂家具 origin 全在 5.1，地面 ≈ 5.14）。

> **为什么改了还是不对：玩家跑的是旧包。**
> `Build\群侠传启动_Data\mods\shendiao\shendiao_mod` 时间戳 **10-28 20:00**，
> 比 HEAD 提交（10-29 11:06）和今天的导出都早；`Build\群侠传启动.exe` 也是 10-28 21:03。
> 排查「改了没效果」的第一步固定是比对三处时间戳：
> ① `jyx2/Assets/Mods/shendiao/{Lua,Maps}` ② `Export/shendiao` ③ `Build\群侠传启动_Data\mods\shendiao`。
> 注意 Lua 也在 `shendiao_mod` 这个 AB 里（manifest 里 175 条 `Lua/…`），
> 所以**只改 Lua 也必须重新导出**。

**④ 死代码清理：`Lua/npc_face.lua` 已删除**

它原本用 `util.hotfix_ex(CS.LevelMaster, "Start", …)` 在每次进场景后把 NPC 转向「所有 NPC 的质心」，
想一把修掉「郭靖面朝墙壁」这类穿帮。实测**从未生效**：`Player.log` 里只有
`preloading npc_face...` 与文件内容的回显，没有运行期的
`[npc_face] N 个 NPC 已转向场景中心` 一行（推测是 `LevelMaster.Start` 这条热更没挂上 ——
同一次运行里 `hotfix.lua` 里 `CS.GameMainMenu.OnCreate` 那句打印同样没出现过）。
朝向这种一次性的美术参数直接写在 `.unity` 里（`edit_instance.py --rot-y 220`）更可靠，
所以删掉该文件与 `.meta`。

**⑤ 本轮校验**

| 项目 | 结果 |
| --- | --- |
| `lint_lua.py` | 167 个脚本，0 问题（删掉 `npc_face.lua` 后少 1 个） |
| `check_story.py` | 0 错误 / 0 提醒 |
| `check_scene_fileids.py 62_pomiao.unity` | 1 个场景，0 问题 |
| `sim_lua.py --preset ch1` | 6 条线全过（含新增「铁枪残片线」） |
| 重新导出 / 安装 | `Export/shendiao` 12:06/12:08；已 `install` 到 Steam 版 `wuxia_launch_Data\mods\shendiao`，并手动同步到 `Build\群侠传启动_Data\mods\shendiao` |

> `jyx2mod.py install` 只认 **`wuxia_launch.exe`**（Steam 版根目录），
> `--game Build` 会被静默忽略（`is_game_dir` 找不到 `wuxia_launch.exe`，回落到 Steam 库）。
> 本地 `Build\群侠传启动.exe`（Player 构建）的 mods 目录要自己拷：
> `Copy-Item 'Export\shendiao\*' -Destination 'Build\群侠传启动_Data\mods\shendiao' -Recurse -Force`。

**⑥ 踩坑：`jyx2mod.py unity`（batchmode）不会重编译 C# 脚本**

这轮想加一个 `ShendiaoNavProbe.ProbePomiaoNpcs`（报每个 NPC 的 Renderer 脚底高度 vs
NavMesh 采样高度、controller 名、与供桌的夹角），验证"飘在空中/朝向"。结果 batchmode 里
`-executeMethod` 永远报 `method ... could not be found`：

- `Library/ScriptAssemblies/Assembly-CSharp-Editor.dll` 的时间戳还停在 **10-28 21:01**，
  今天的几次 `-executeMethod` 运行日志里都是 `AssetDatabase: script compilation time: 0.03s`
  ／ `CompileScripts: 30ms` —— **等于没编译**；
- 把 `Assembly-CSharp-Editor.dll` 删掉再跑，报错从 `method could not be found` 变成
  `class 'ShendiaoNavProbe' could not be found`，说明执行 `-executeMethod` 在脚本编译**之前**；
- 加 `-nographics` 与否、`-batchmode` 与否、清 `Temp/UnityLockfile` 都一样。

所以：**新增/修改 `.cs` 之后，必须先在 Unity 编辑器里打开一次工程让它编译**，
再跑 `jyx2mod.py unity`（导出本身不需要脚本，但 `Jyx2ModCli` 属于 Editor 程序集）。
顺带记住：`-batchmode` 进程崩溃后会**残留进程并占着 `jyx2/Temp/UnityLockfile`**，
下一次 batchmode 直接 `EditorMonoConsole ... HandleProjectAlreadyOpenInAnotherInstance`
然后挂死 —— 先 `Get-Process Unity` + `Get-CimInstance Win32_Process` 看命令行，
确认是自己起的那个再 `Stop-Process`，别把玩家开着的编辑器杀了。

> 这轮因此**放弃**了 C# 探针（无法验证的代码不留），改用纯文本手段核对（`62_pomiao.unity`）：
> - 郭靖实例的 `m_Modifications` 里 `m_Controller → c1fb7eef… = GuojingController`，
>   黄蓉 → `afb4f35a… = HuangrongController`（两条都在 **`AnimationControllers/备份/`** 下）；
>   全文 `sit_on_chair` 出现 **0** 次；
> - 两人的 `m_LocalPosition.y` 与另外 7 个 NPC 一样是 **5.0**；
> - `m_LocalEulerAnglesHint.y` 已是 **220 / 247**。


