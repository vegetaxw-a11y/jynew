"""修复 shendiao MOD 内部断裂的 GUID 引用。

`jyx2mod.py new` 复制模板时给每个 .meta 换了新 GUID，但没有同步更新资源文件
里对这些 GUID 的引用（prefab 里的组件、场景里的 NPC、Models/*.asset 的
m_View 等），于是 MOD 内部引用全部指向模板 SAMPLE。

打包后 shendiao 的 bundle 里找不到被引用的资源，运行时表现为：
角色模型变空气、NPC 隐形、贴图丢失。

这里按「相对路径」把 SAMPLE 的 GUID 映射成 shendiao 自己的 GUID 并就地替换。
shendiao 里没有同名资源的引用（比如被删掉的 Scripts/*.cs）保持原样，仍指向
SAMPLE，因为 SAMPLE 也在工程内，Unity 能正常解析。

用法：
    python tools/shendiao/fix_guids.py          # 预演，只报告
    python tools/shendiao/fix_guids.py --apply  # 实际写入
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODS = os.path.join(ROOT, "jyx2", "Assets", "Mods")
SAMPLE = os.path.join(MODS, "SAMPLE")
SHENDIAO = os.path.join(MODS, "shendiao")

GUID_RE = re.compile(r"guid: ([0-9a-fA-F]{32})")
META_GUID_RE = re.compile(r"^guid: ([0-9a-fA-F]{32})\s*$", re.M)


def collect_guids(mod_dir: str) -> dict:
    """相对路径 -> GUID（键统一用小写、正斜杠）"""
    result = {}
    for dirpath, _dirs, files in os.walk(mod_dir):
        for name in files:
            if not name.endswith(".meta"):
                continue
            meta = os.path.join(dirpath, name)
            try:
                text = open(meta, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            m = META_GUID_RE.search(text)
            if not m:
                continue
            asset = meta[: -len(".meta")]
            rel = os.path.relpath(asset, mod_dir).replace("\\", "/").lower()
            result[rel] = m.group(1).lower()
    return result


def build_mapping() -> dict:
    sample = collect_guids(SAMPLE)
    shen = collect_guids(SHENDIAO)
    mapping = {}
    for rel, old in sample.items():
        new = shen.get(rel)
        if new and new != old:
            mapping[old] = new
    return sample, shen, mapping


def iter_text_assets(mod_dir: str):
    """遍历 MOD 下的文本资源（跳过 .meta），二进制文件解码失败会自动跳过"""
    for dirpath, _dirs, files in os.walk(mod_dir):
        for name in files:
            if name.endswith(".meta"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8", newline="") as f:
                    text = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            if "guid: " not in text:
                continue
            yield path, text


def main() -> int:
    apply = "--apply" in sys.argv
    sample, shen, mapping = build_mapping()
    print(f"SAMPLE 资源 {len(sample)} 个，shendiao 资源 {len(shen)} 个，可映射 GUID {len(mapping)} 个")

    if not mapping:
        print("没有需要修复的引用")
        return 0

    changed_files = 0
    total_refs = 0
    leftover = {}
    for path, text in iter_text_assets(SHENDIAO):
        replaced = 0

        def repl(m: re.Match) -> str:
            nonlocal replaced
            guid = m.group(1).lower()
            new = mapping.get(guid)
            if new:
                replaced += 1
                return f"guid: {new}"
            if guid in sample.values():
                leftover[os.path.relpath(path, SHENDIAO)] = leftover.get(os.path.relpath(path, SHENDIAO), 0) + 1
            return m.group(0)

        new_text = GUID_RE.sub(repl, text)
        if replaced:
            changed_files += 1
            total_refs += replaced
            if apply:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new_text)

    print(f"{'已修复' if apply else '待修复'}：{changed_files} 个文件，{total_refs} 处引用")
    if leftover:
        print(f"仍指向 SAMPLE 的引用（shendiao 内无同名资源，保留不动）：{len(leftover)} 个文件")
        for rel, count in sorted(leftover.items(), key=lambda kv: -kv[1])[:10]:
            print(f"  {rel}: {count} 处")

    if not apply:
        print("\n这是预演，加 --apply 才会写入")
    return 0


if __name__ == "__main__":
    sys.exit(main())
