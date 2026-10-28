# -*- coding: utf-8 -*-
"""把官方 JYX2 MOD 的地图场景导入 shendiao。

做三件事：
  1) 复制 <scene>.unity 与 <scene>/NavMesh.asset（大地图另带 SampleSettings.lighting）
  2) 给所有复制过来的 .meta 重新生成 GUID（否则和 JYX2 撞车）
  3) 同步重写场景内部对这些 GUID 的引用，并把 assetBundleName 改成 shendiao_maps

场景里引用的模型/贴图/脚本绝大多数是 GLOBAL 资源（随游戏本体 base_assets 走），
不需要搬运，这也是这套导入能成立的前提。

用法:
    python tools/shendiao/import_jyx2_maps.py --dry-run
    python tools/shendiao/import_jyx2_maps.py
    python tools/shendiao/import_jyx2_maps.py 19_chongyanggong 75_taohuadao
"""
import io
import os
import re
import shutil
import sys
import uuid

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(REPO, "jyx2", "Assets", "Mods", "JYX2", "Maps", "GameMaps")
DST = os.path.join(REPO, "jyx2", "Assets", "Mods", "shendiao", "Maps", "GameMaps")

# 神雕主线要用的场景（顺序即线性路线的建议顺序，大地图放最后单独处理）
SCENES = [
    "62_pomiao",          # 铁枪庙（破庙）—— 序章
    "19_chongyanggong",   # 重阳宫（全真教）
    "18_gumu",            # 古墓（活死人墓）
    "81_siguoya",         # 思过崖（终南山后山）
    "45_chengyingju",     # 程英居（陆家庄一线）
    "22_jueqinggu",       # 绝情谷
    "80_jueqinggudi",     # 绝情谷底
    "48_tiezhangshan",    # 铁掌山
    "21_heilongtan",      # 黑龙潭（瑛姑）
    "47_yidengju",        # 一灯居
    "20_baihuagu",        # 百花谷（周伯通）
    "75_taohuadao",       # 桃花岛
    "57_huashanpai",      # 华山派（华山论剑）
    "07_shandong",        # 神雕山洞（独孤剑冢）
]

WORLDMAP = "1000_daditu"
# 只有大地图引用了共享光照设置
SHARED_LIGHTING = "SampleSettings.lighting"

GUID_RE = re.compile(r"^guid:\s*([0-9a-f]{32})", re.M)
AB_RE = re.compile(r"^(\s*assetBundleName:\s*)(\S*)\s*$", re.M)


def read_meta_guid(path):
    with io.open(path, encoding="utf-8") as f:
        m = GUID_RE.search(f.read(200))
    return m.group(1) if m else None


def plan(scenes):
    """返回 [(src_file, dst_file)]，scene 文件在前、依赖在后。"""
    items = []
    for s in scenes:
        unity = s + ".unity"
        nav = os.path.join(s, "NavMesh.asset")
        for rel in (unity, nav):
            src = os.path.join(SRC, rel)
            dst = os.path.join(DST, rel)
            if not os.path.isfile(src):
                raise SystemExit("缺少源文件: " + src)
            items.append((src, dst))
    if WORLDMAP in scenes:
        src = os.path.join(SRC, SHARED_LIGHTING)
        items.append((src, os.path.join(DST, SHARED_LIGHTING)))
    return items


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    scenes = argv or (SCENES + [WORLDMAP])

    os.makedirs(DST, exist_ok=True)
    items = plan(scenes)

    # 1) 先为每个待复制资源生成新 GUID
    remap = {}
    for src, _dst in items:
        old = read_meta_guid(src + ".meta")
        if not old:
            raise SystemExit("源 meta 没有 guid: " + src + ".meta")
        remap[old] = uuid.uuid4().hex
    print("待导入资源 %d 个，生成新 GUID %d 个" % (len(items), len(remap)))

    # 2) 复制文件正文并改写内部 GUID 引用
    dst_of = {}
    for src, dst in items:
        with io.open(src, "rb") as f:
            raw = f.read().decode("utf-8", "surrogateescape")
        hits = 0
        for old, new in remap.items():
            if old in raw:
                hits += raw.count(old)
                raw = raw.replace(old, new)
        if not dry:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with io.open(dst, "wb") as f:
                f.write(raw.encode("utf-8", "surrogateescape"))
        dst_of[src] = dst
        print("  %-46s 引用改写 %d 处" % (os.path.relpath(dst, DST), hits))

    # 3) 写 meta：换 GUID + 改 AssetBundle 名
    for src, dst in items:
        guid = remap[read_meta_guid(src + ".meta")]
        with io.open(src + ".meta", encoding="utf-8") as f:
            meta = f.read()
        meta = GUID_RE.sub("guid: " + guid, meta, count=1)
        # 场景本身归 shendiao_maps；NavMesh/lighting 不标包，靠被引用自动进包
        is_scene = dst.endswith(".unity")
        meta = AB_RE.sub(lambda m: m.group(1) + ("shendiao_maps" if is_scene else ""), meta, count=1)
        if not dry:
            with io.open(dst + ".meta", "w", encoding="utf-8", newline="") as f:
                f.write(meta)

    print()
    print("完成%s：%d 个资源已落到 %s" % ("（dry-run，未写盘）" if dry else "", len(items), DST))


main()
