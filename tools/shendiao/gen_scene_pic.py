# -*- coding: utf-8 -*-
"""生成 MOD 里用到的"一张图"（过场插图 / 场景远景），不做 CG 系统。

第一回结尾"转场去桃花岛"用的就是这里产出的 taohuadao.png：
桃花岛远眺的 16:9 水墨风插画，塞进场景里那个 Canvas+Image（Prefabs/CgTaohuadao.prefab），
由 1002.lua 用 ShowSceneNpc("去桃花岛", true/false) 开关。

约定与 gen_heads.py 一致：
  * 密钥只从环境变量读（TURBO_KEY / OPENAI_API_KEY / ANTHROPIC_AUTH_TOKEN）
  * 大图存 Export/scene_raw/（gitignore），成品缩到 1920x1080 写进 BuildSource/cg/
  * .meta 复制 MOD 里已有贴图的导入设置（sprite / 2048 / shendiao_mod 分包）

用法:
  python tools/shendiao/gen_scene_pic.py --list
  python tools/shendiao/gen_scene_pic.py --only taohuadao
  python tools/shendiao/gen_scene_pic.py --only taohuadao --apply --force
"""
import io
import os
import re
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_heads as G  # noqa: E402

CG_DIR = os.path.join(G.MOD, 'BuildSource', 'cg')
RAW_DIR = os.path.join(G.ROOT, 'Export', 'scene_raw')
META_TMPL_SRC = os.path.join(G.MOD, 'bg.png.meta')   # 同一套 Sprite 导入设置
LOG = os.path.join(G.ROOT, 'Logs', '_scene_gen.log')

MODEL = 'gemini-nano-banana-2.1'
WIDTH, HEIGHT = 1920, 1080

STYLE = (
    '国风水墨与工笔结合的写意插画，南宋江湖气韵，淡彩设色，'
    '层次分明的前中远景，空气透视与薄雾，画面干净不杂乱；'
    '不要出现任何文字、字母、数字、落款、印章、logo、水印、边框。'
)

PICS = [
    ('taohuadao', '桃花岛远景',
     '从海面远望东海中的桃花岛：岛上层叠的桃林正开得漫山浅粉，'
     '林间露出几角青瓦竹亭与曲折石阶，岛边一块临海巨岩上立着一个孤独的'
     '青衫身影（背影，很小），礁石外一只小船正驶近；'
     '时间是清晨薄雾，海面平静泛光，几只白鸥掠过；'
     '整体气氛旷远、清寂、带着"从今往后与世隔绝"的清冷。'),
]


def log(msg):
    print(msg)
    sys.stdout.flush()


def to_size(png_bytes, w=WIDTH, h=HEIGHT):
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes)).convert('RGB')
    # 等比缩放到目标宽度，再裁/补到 16:9
    scale = min(float(w) / im.size[0], float(h) / im.size[1])
    im = im.resize((max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))),
                   Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), (12, 14, 18))
    canvas.paste(im, ((w - im.size[0]) // 2, (h - im.size[1]) // 2))
    buf = io.BytesIO()
    canvas.save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def meta_text():
    text = io.open(META_TMPL_SRC, encoding='utf-8').read()
    text = re.sub(r'(?m)^guid: [0-9a-f]{32}$', 'guid: ' + uuid.uuid4().hex, text, count=1)
    text = re.sub(r'(?m)^    spriteID: [0-9a-f]{32}$', '    spriteID: ' + uuid.uuid4().hex,
                  text, count=1)
    return text


def main():
    argv = sys.argv[1:]
    apply_ = '--apply' in argv
    force = '--force' in argv
    only = None
    if '--only' in argv:
        only = set(x.strip() for x in argv[argv.index('--only') + 1].split(',') if x.strip())

    if '--list' in argv:
        for key, label, _ in PICS:
            log('%-14s %s' % (key, label))
        return

    todo = [p for p in PICS if only is None or p[0] in only]
    if not todo:
        sys.exit('没有匹配到要生成的图，检查 --only')

    key_api = G.api_key()
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(CG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)

    for key, label, desc in todo:
        dst = os.path.join(CG_DIR, '%s.png' % key)
        if os.path.isfile(dst) and not force and not apply_:
            pass
        if os.path.isfile(dst) and not force:
            log('-- 跳过 %s（已有 %s.png，加 --force 覆盖）' % (label, key))
            continue
        prompt = '请绘制一张%s。\n场景：%s\n\n%s' % (label, desc, STYLE)
        t0 = time.time()
        try:
            raw = G.gen_one(key_api, prompt, aspect='16:9', image_size='2K', model=MODEL)
            stamp = time.strftime('%m%d_%H%M%S')
            raw_path = os.path.join(RAW_DIR, '%s_%s.png' % (key, stamp))
            io.open(raw_path, 'wb').write(raw)
            png = to_size(raw)
            msg = 'OK   %-16s %dx%d %6.1fKB %4.0fs' % (label, WIDTH, HEIGHT,
                                                      len(png) / 1024.0, time.time() - t0)
            if apply_:
                io.open(dst, 'wb').write(png)
                io.open(dst + '.meta', 'w', encoding='utf-8', newline='\n').write(meta_text())
                msg += '  -> BuildSource/cg/%s.png + .meta' % key
            else:
                io.open(os.path.join(RAW_DIR, 'preview_%s.png' % key), 'wb').write(png)
                msg += '  (预演，未写入 MOD)'
            log(msg)
            with io.open(LOG, 'a', encoding='utf-8') as fh:
                fh.write('%s  raw=%s\n' % (msg, os.path.basename(raw_path)))
        except Exception as e:  # noqa: BLE001
            log('FAIL %-16s %s' % (label, e))


if __name__ == '__main__':
    main()
