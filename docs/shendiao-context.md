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


