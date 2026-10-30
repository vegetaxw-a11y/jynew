# -*- coding: utf-8 -*-
"""给 MOD 里的头像 .meta 打上 AssetBundle 名（否则 Unity 不会把它们打进 <mod>_mod 包）。

Unity 打 AB 只收「在 AssetDatabase 里标了 assetBundleName 的资源」，
Jyx2ModCli.CreateBundleBuild 用的就是 GetAssetPathsFromAssetBundle。

用法: python tools/shendiao/_tag_assetbundle.py [--apply]
"""
import io
import os
import re
import sys
import uuid

ROOT = r'c:\Games\jynew'
TARGET_DIR = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao', 'BuildSource', 'head')
BUNDLE = 'shendiao_mod'
APPLY = '--apply' in sys.argv

# --only 44,73  只处理这几个（新生成的头像 .meta 是从同目录模板复制来的，
# spriteID 会跟模板撞，全量重跑又会把所有 spriteID 都换掉，所以支持挑文件）。
ONLY = None
if '--only' in sys.argv:
    ONLY = set(x.strip() for x in sys.argv[sys.argv.index('--only') + 1].split(',') if x.strip())

report = []
for name in sorted(os.listdir(TARGET_DIR)):
    if not name.endswith('.png.meta'):
        continue
    if ONLY is not None and name[:-9] not in ONLY:
        continue
    fp = os.path.join(TARGET_DIR, name)
    t = io.open(fp, encoding='utf-8').read()
    if not t.startswith('fileFormatVersion:'):
        # 坏掉的 meta（被截断 / 空文件）不要去 patch，patch 只会把错误固化下来
        print('[skip] %s 不是合法 meta（%d 字节），先用 fix_head_meta.py 重建'
              % (name, len(t)))
        continue
    orig = t
    # 1) 打 bundle 名
    t = re.sub(r'(?m)^  assetBundleName:.*$', '  assetBundleName: ' + BUNDLE, t, count=1)
    if 'assetBundleName:' not in t:
        t = t.rstrip('\n') + '\n  assetBundleName: ' + BUNDLE + '\n  assetBundleVariant: '
    # 2) spriteID 必须唯一（批量复制 meta 会撞）
    sid = uuid.uuid4().hex
    t = re.sub(r'(?m)^    spriteID: [0-9a-f]{32}$', '    spriteID: ' + sid, t, count=1)
    if t != orig:
        report.append(name[:-5])
        if APPLY:
            io.open(fp, 'w', encoding='utf-8', newline='\n').write(t)

out = ['%s 处理 %d 个 meta' % ('已写入' if APPLY else '预演', len(report)), 'bundle=%s' % BUNDLE] + report
io.open(os.path.join(ROOT, 'Logs', '_tag_ab.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print(out[0])
