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
