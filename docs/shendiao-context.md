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
