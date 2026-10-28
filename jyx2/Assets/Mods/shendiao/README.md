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
Models/             角色模型资源
Skills/             武功资源
Terrain/ Timeline/ Skybox/ ...  美术资源（沿用模板）
```

## 开发流程

```bash
# 1. 改配置表 / 剧情（推荐走脚本，见下）
python tools/shendiao/apply_configs.py     # 地图/人物/武功/物品改名 + 大地图 GameObject 同步改名
python tools/shendiao/gen_story.py         # 重排事件 Id、写剧情脚本、给未开发事件写占位

# 2. 导出 Excel -> Lua 并体检
python tools/moddev/jyx2mod.py configs shendiao
python tools/moddev/jyx2mod.py check shendiao

# 3. 导出 AssetBundle（首次/工程本体资源变动时才需要 base，慢约 10 分钟）
python tools/moddev/jyx2mod.py unity shendiao --output Export --no-base

# 4. 安装到游戏
python tools/moddev/jyx2mod.py install shendiao --src Export
```

- `tools/shendiao/apply_configs.py`：声明式表，改地图名/角色名/武功名/物品名只改字典即可。
- `tools/shendiao/gen_story.py`：`STORY` 字典里按事件 Id 写剧情；没写的事件自动生成「尚未探明」占位。
- `tools/moddev/_scene_scan.py`：扫描场景里的交互点/NPC/传送点，编排剧情时用来查事件 Id。

> Excel 注意：工程里的 `Excel.dll` 是老版 ExcelDataReader，只认 sharedStrings，
> 所以 xlsx 必须用 xlsxwriter 重写（`apply_configs.py` 已处理），不能直接用 openpyxl 保存。

## 第一章测试清单

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
