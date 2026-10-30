# -*- coding: utf-8 -*-
"""把一张头像复制给"同一个 Pic 代号"的其它人物（只换 guid/spriteID）。

人物表里很多行共用同一个 Pic（蓝隼士兵 611-619 都是 Pic 610、野狼几行分别是
141…149/1410 等）。逐个去 AI 生成没意义 —— 同一个物种/兵种就该是同一张脸。
所以这里只生成"每个 Pic 一张"，再把图复制到其它代号。

用法:
    python tools/shendiao/dup_head_pics.py            # dry-run
    python tools/shendiao/dup_head_pics.py --apply
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_heads as G  # noqa: E402

# 源 Pic -> 需要同一张图的其它 Pic
DUP = {
    71: [72],                          # 曼陀谷弟子
    141: [142, 143, 144, 145, 146, 147, 148, 149, 1410],   # 野狼
    163: [164, 165, 166, 167],         # 黑熊
    181: [182],                        # 毒蛇
}


def main():
    apply_ = '--apply' in sys.argv
    for src, targets in sorted(DUP.items()):
        src_png = os.path.join(G.HEAD_DIR, '%d.png' % src)
        if not os.path.isfile(src_png):
            print('跳过 %d：源文件不存在（先跑 gen_heads.py --only %d --apply）' % (src, src))
            continue
        raw = io.open(src_png, 'rb').read()
        for dst in targets:
            dst_png = os.path.join(G.HEAD_DIR, '%d.png' % dst)
            if os.path.isfile(dst_png) and not apply_:
                print('  %d.png 已存在（dry-run 不覆盖）' % dst)
                continue
            print('  %d -> %d' % (src, dst))
            if not apply_:
                continue
            io.open(dst_png, 'wb').write(raw)
            meta = dst_png + '.meta'
            # 必须先取文本再 open('w')：open('w') 会先把文件截断，meta_for() 再去读
            # 这个文件当模板，就会写出 0 字节的 meta（44/73 就是这么坏的）。
            meta_txt = G.meta_for(dst)
            io.open(meta, 'w', encoding='utf-8', newline='\n').write(meta_txt)
    print('%s 完成' % ('已写入' if apply_ else 'dry-run，加 --apply 生效'))


if __name__ == '__main__':
    main()
