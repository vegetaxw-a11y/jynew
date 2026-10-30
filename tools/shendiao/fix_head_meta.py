# -*- coding: utf-8 -*-
"""修复被截断的头像 .meta（生成 44/73 时踩的坑）。

现象：`44.png.meta` / `73.png.meta` 只剩 55 字节（只有 assetBundleName 那两行），
Unity 报 "does not have a valid GUID and its corresponding Asset file will be ignored"，
于是头像不会进 AssetBundle（人名照旧，脸是空的）。

原因：一条 `open(p,'w').write(... p ...)` 的内联命令 —— 先 open('w') 把文件截断成 0 字节，
再读取时读到的就是空串，最后只写回了一点尾巴。
（gen_heads.meta_for 的注释里记着同一个坑：必须先取文本再打开文件写。）

做法：删掉坏 meta，用 gen_heads.meta_for() 从同目录其它头像 .meta 复制一份（换 guid + spriteID）。

用法: python tools/shendiao/fix_head_meta.py 44 73
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_heads as G  # noqa: E402

MIN_BYTES = 1000   # 正常的头像 meta 约 2.9KB；明显偏小就是坏的


def main():
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    if not ids:
        sys.exit(__doc__)
    for cid in ids:
        path = os.path.join(G.HEAD_DIR, '%d.png.meta' % cid)
        if not os.path.isfile(path):
            sys.exit('找不到 %s' % path)
        size = os.path.getsize(path)
        text = io.open(path, encoding='utf-8').read()
        if size >= MIN_BYTES and text.startswith('fileFormatVersion:'):
            print('%d.png.meta 正常（%d 字节），跳过' % (cid, size))
            continue
        os.remove(path)                     # meta_for 会去找同目录另一个头像当模板
        txt = G.meta_for(cid)
        io.open(path, 'w', encoding='utf-8', newline='\n').write(txt)
        print('%d.png.meta 已重建：%d 字节 -> %d 字节'
              % (cid, size, os.path.getsize(path)))


if __name__ == '__main__':
    main()
