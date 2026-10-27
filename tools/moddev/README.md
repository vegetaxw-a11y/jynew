# moddev —— MOD 开发命令行工具

把「新建 MOD、改配置表、导出 Lua、体检、导出资源包、装进游戏、看日志」这一套流程从 Unity 编辑器里搬到命令行，
方便脚本化，也方便让 AI 参与 MOD 开发。

```
tools/moddev/
├── excel2lua.py    Excel(.xlsx) -> Lua 配置表（ExcelToLua.cs 的 Python 移植，不需要 Unity）
├── jyx2mod.py      命令行入口（new / configs / xml / check / install / uninstall / list / logs / run / unity）
├── selftest.py     自测：用 lupa 加载生成的 Lua，逐字段比对 Excel 原始值
└── README.md
```

## 环境准备

```powershell
python -m pip install openpyxl lupa
```

> 脚本可以在**任意工作目录**下运行（内部路径都以仓库根为基准）：
> `python C:\Games\jynew\tools\moddev\jyx2mod.py list` 等价于先 `cd C:\Games\jynew` 再用相对路径。
> 命令行里的相对路径参数（`--src`、`-o`、`--output`、`--dir`、`--game`）也按**仓库根**解析，不是当前目录。

* `openpyxl`：读写 xlsx（必需）
* `lupa`：内嵌 Lua 运行时，`check` 的语法检查和 `selftest.py` 需要（可选，缺了会自动跳过）

Python 3.9+。

## 子命令

| 命令 | 作用 | 需要 Unity |
| --- | --- | --- |
| `new` | 从模板（默认 `SAMPLE`）复制出新 MOD，重写所有 `.meta` 的 GUID、AssetBundle 名、`ModSetting.asset` | 否 |
| `configs` | `<Mod>/Configs/*.xlsx` -> `<Mod>/Configs/Lua/*Config.lua` | 否 |
| `xml` | 生成 `<id>.xml`（等价于 Unity 导出时的 `GameModInfo`） | 否 |
| `check` | 体检：`ModSetting`、AssetBundle 标记、配置表、Lua 语法 | 否 |
| `install` | 把导出目录装进游戏（`<游戏>/wuxia_launch_Data/mods/<id>`） | 否 |
| `uninstall` | 从游戏里删掉 MOD | 否 |
| `list` | 列出工程里的 MOD 和游戏里已装的 MOD | 否 |
| `logs` | 看 `Player.log`（`-f` 持续跟踪） | 否 |
| `run` | 启动游戏（可顺便跟踪日志） | 否 |
| `unity` | 调 Unity batchmode 导出 AssetBundle + xml | **是** |

所有命令都可以加 `--help` 看详细参数。

> `unity` 走的是 `-executeMethod Jyx2Editor.BuildTool.Jyx2ModCli.BuildMod`，
> 实现在 `jyx2/Assets/Editor/BuildTools/Jyx2ModCli.cs`，逻辑与 Unity 里的「Game Tools/Mod导出」窗口一致。

### `unity` 的增量策略（重要）

全量导出一次约 **10 分钟**，其中绝大部分时间花在给 `base_assets`（1.8 GB 未压缩）做序列化 + LZ4 压缩。
但 `base_assets` 是**游戏本体**的资源包，游戏运行时从 `StreamingAssets` 读取，跟你装进游戏的 MOD 无关
（`ResLoader.LoadModAb()` 是直接 `AssetBundle.LoadFromFileAsync("<id>_mod")`，不解析 manifest 依赖）。
所以只有「改了本体资源、要连 base_assets 一起分发」时才需要重打它。

`unity` 默认按下面的规则自动跳过：

| 判定 | 依据 | 效果 |
| --- | --- | --- |
| MOD 没改动 | `<id>.xml`、`<id>_mod` 都比 `Assets/Mods/<Mod>/` 下所有文件新 | 连 Unity 都不启动，秒回 |
| `base_assets` 没变化 | `Export/.base_assets.stamp` 记录的指纹（`Assets` 下除 `Mods` 外每个文件的路径+大小）与当前一致 | 不重建 base_assets，只打 `<id>_mod` / `<id>_maps` |

想强制重建：

```powershell
python tools/moddev/jyx2mod.py unity mymod --force      # 忽略一切缓存，全量重建
python tools/moddev/jyx2mod.py unity mymod --with-base  # 只强制重建 base_assets
python tools/moddev/jyx2mod.py unity mymod --no-base    # 只强制跳过 base_assets
```

> 指纹用「路径 + 大小」而不是 mtime：Unity 每次打包都会顺手重写几个 `.mat`，用 mtime 会导致永远判定「资源变了」，跳过逻辑直接失效。
> 反过来的风险是「改了本体资源但文件大小恰好没变」，这种情况用 `--with-base` 强制即可。

实测（`SAMPLE`）：

| 场景 | 耗时 |
| --- | --- |
| 全量（含 `base_assets`） | ~10 分钟 |
| 改了 MOD，自动跳过 `base_assets` | **2~3 分钟**（Unity 启动+导入 ~50s，AssetBundle 构建 82~133s） |
| 完全没改 | **0.3 秒**（不启动 Unity） |

跳过的代价：没有 `base_assets` 参与时，原本被它提供的共享资源（贴图/材质/Shader）会被复制进 `<id>_mod` / `<id>_maps`，
所以包体积会明显变大（`SAMPLE` 的 `sample_maps` 从 114 MB 涨到 287 MB）。自己迭代时无所谓，
**最终分发想要小包就用 `--with-base` 全量打一次**。

## 完整流程

```powershell
# 1. 新建 MOD（目录名 = MOD Id，会统一转小写）
python tools/moddev/jyx2mod.py new mymod --name 我的MOD --author 我 --desc "一句话简介"

# 2. 改配置表：jyx2/Assets/Mods/mymod/Configs/*.xlsx（可以直接用 Excel 打开）
#    注意每个工作簿里 A1 必须是 LuaConfigGen，B1 是表名（最终生成 <表名>Config.lua）

# 3. 导出 Lua（改完表随时可以重跑，纯 Python，秒级）
python tools/moddev/jyx2mod.py configs mymod

# 4. 体检
python tools/moddev/jyx2mod.py check mymod

# 5. 回 Unity 里做资源（场景/预制体/立绘），给要打包的资源标好 AssetBundle（见下）
#    然后用命令行导出
python tools/moddev/jyx2mod.py unity mymod --output Export

# 6. 装进游戏并试玩
python tools/moddev/jyx2mod.py install mymod --src Export/mymod
python tools/moddev/jyx2mod.py run --follow
```

`new` 之后的产出：

```
jyx2/Assets/Mods/mymod/
├── ModSetting.asset   ModId / ModName / Author / Desc / ModRootDir 已改好，IsNativeMod=0
├── Configs/           从模板复制来的 xlsx（开箱即用）
├── Lua/               剧本脚本（story id .lua）与 hotfix.lua
├── Maps/ Models/ Prefabs/ Skills/ ...  美术资源
└── *.meta             全部换成了新 GUID（不会和模板冲突）
```

## 约定与坑

### AssetBundle 名

游戏只认两个包，名字由 MOD Id 小写拼出来（见 `Jyx2ModTool.GetModMainBundleName`）：

| 包名 | 放什么 |
| --- | --- |
| `<id>_mod` | 预制体、模型、贴图、图集、`Configs`、`Lua` 等 |
| `<id>_maps` | `Maps/` 下的大地图场景 |

`new` 会自动把模板的 `sample_mod` / `sample_maps` 换成新名字；**之后在 Unity 里新增的资源要自己标**，
否则 `check` 会报「没有任何资源标记为 AssetBundle」。

### 配置表 Lua

* `Configs/*.xlsx` 里 A1 = `LuaConfigGen`，B1 = 表名，生成 `<表名>Config.lua`
* 生成的 Lua 必须放在 MOD 的 `Configs/Lua/`，游戏按 `Configs/Lua/<表名>Config.lua` 加载
* 表名重复会互相覆盖，`check` 会报错

### 剧本 Lua / PreloadedLua

* `ModSetting.asset` 里的 `PreloadedLua` 列出的脚本（如 `hotfix`）会在进入 MOD 时预加载，
  对应文件必须存在：`Lua/<名字>.lua`
* `Lua/<story id>.lua` 是按需加载的剧本，文件名就是剧情 Id

### 导出产物

`unity` 导出的目录结构跟游戏「手动安装 MOD」读取的一致：

```
Export/mymod/
├── mymod.xml        GameModInfo（Id/Name/Author/Version/ClientVersion/ModMD5/MapsMD5/CreateTime/Desc/Welcome）
├── mymod_mod        主资源包
└── mymod_maps       地图资源包
```

`install` 会把整个目录拷到 `<游戏>/wuxia_launch_Data/mods/mymod/`；
加 `--persistent` 则装到 `%USERPROFILE%\AppData\LocalLow\<公司>\<产品>\mods\mymod\`
（`Application.persistentDataPath`，两个位置游戏都会扫）。

Android 上游戏扫描的是 `/storage/emulated/0/jynew/mods/`，`install` 只处理 Windows 目录，
导出后把整个 `<id>/` 目录（xml + 两个包）拷过去即可。

### 环境变量

| 变量 | 用途 |
| --- | --- |
| `JYX2_GAME_DIR` | 游戏根目录（含 `wuxia_launch.exe`），找不到 Steam 库时用 |
| `JYX2_UNITY` | `Unity.exe` 路径，默认按 `ProjectSettings/ProjectVersion.txt` 在 Unity Hub 目录里找 |

## 自测

```powershell
python tools/moddev/selftest.py                      # 测 JYX2 / SAMPLE / xiastart_roguelike
python tools/moddev/selftest.py jyx2\Assets\Mods\SAMPLE
```

它会用 `lupa` 起一个假的 `Jyx2` / `jy_utils` 运行时，把导出的 `*Config.lua` 真的执行一遍，
再逐字段和 xlsx 原始值比对：

* 语法错误、字段缺失、类型不符都会报出来
* 某些列的数据本身就和声明类型冲突（游戏里会写出非法/空值），这类列会被 `collect_bad_cols` 跳过并给 warning

改了 `excel2lua.py` 之后请务必跑一次，确保三个内置 MOD 全部「错误 0」。

## 常见问题

**`check` 报「没有生成 XxxConfig.lua」**
先跑 `configs`。另外确认 xlsx 的 A1 是 `LuaConfigGen`。

**`check` 报「ModSetting.asset 里 ModId 与目录名不一致」**
`new` 之后手动改过目录名或 ModId。两者必须一致（大小写不敏感），否则游戏找不到 MOD 根目录。

**游戏里看不到 MOD**
1. `list` 看是否装到了游戏目录；
2. 看 `<游戏>/wuxia_launch_Data/mods/<id>/` 里有没有 `<id>.xml`，没有 xml 不会被识别；
3. `logs -f` 看加载报错（AssetBundle 名不对、MD5 不符、缺 `_maps` 包等）。

**`unity` 报找不到 Unity**
用 `--unity "…\Unity.exe"` 或设置 `JYX2_UNITY`；需要与 `ProjectSettings/ProjectVersion.txt` 同版本的编辑器。
