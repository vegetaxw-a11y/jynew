# -*- coding: utf-8 -*-
"""生成「精致角色设定卡」：左侧次世代 CG 立绘 + 右侧姓名/身长/门派/色卡面板。

参考样式：国风游戏（如《霜月》类）的角色设定卡 —— 极度精致的写实 CG 立绘，
右边一栏是排版过的信息面板（名字、拼音、身长体重、门派兵器、色卡、台词）。

和 gen_sheets.py 的分工：
  gen_sheets.py  → 九宫格（多表情/多视角）+ 512 游戏头像（够用，但画风偏平涂）
  gen_cards.py   → 一张精修设定卡（画风向写实 CG 靠），文字用 PIL 真排，
                   不指望模型画中文（模型画中文必糊）

用法:
  $env:TURBO_KEY = 'sk-...'
  python tools/shendiao/gen_cards.py --only 0            # 只做杨过（少年）
  python tools/shendiao/gen_cards.py --only 0 --force    # 重抽
"""
import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_heads as G  # noqa: E402

CARD_DIR = os.path.join(G.ROOT, 'Export', 'heads_card')
LOG = os.path.join(G.ROOT, 'Logs', '_cards_gen.log')

# ---- 画风：这一段决定了"精致度"，改风格只改这里 -------------------------
# 名字叫 STYLE_BODY 是因为 gen_sheets.py（九宫格）也要 import 这一段，
# 保证"设定卡"和"九宫格"两套产物是同一个画风。REFINED 是同义别名。
STYLE_BODY = (
    '次世代高品质中国风游戏角色立绘，虚幻引擎 5 级写实 CG 渲染质感，极致精细：'
    '根根分明的发丝与自然高光、银质与水晶质地的发饰、珍珠与水晶流苏的透明折射、'
    '琉璃般通透细腻的皮肤、水润唇部、纤长睫毛与瞳孔中的细碎光点、'
    '妆容里极淡的腮红与皮肤绒毛、织物上的金银丝刺绣与暗纹、'
    '电影级柔和布光、轻微 HDR 泛光、冷调银白配色、'
    '8K 超高清细节、专业游戏宣发立绘水准；'
    '画面通透干净、无噪点、不要线稿描边感。'
)
REFINED = STYLE_BODY
COMPOSE = (
    '构图：单人半身立绘，从头顶画到腰胯，人物居中、微微侧身 15 度面向观者，'
    '身体完整落在画面内不被裁切；纯净的浅灰白渐变背景，'
    '背景中绝对不要出现任何文字、字母、数字、符号、logo、水印、边框、分割线。'
)

# ---- 右侧面板要用的资料（按 roleId 补充，缺的走默认） --------------------
PROFILE = {
    0: dict(pinyin='YANG GUO', rows=[('身长', '178 cm'), ('体重', '62 kg'),
                                     ('门派', '古墓派'), ('兵器', '玄铁重剑'),
                                     ('身份', '神雕侠')],
            quote='重剑无锋·大巧不工'),
    22: dict(pinyin='XIAO LONG NV', rows=[('身长', '166 cm'), ('体重', '46 kg'),
                                          ('门派', '古墓派'), ('兵器', '金铃索'),
                                          ('身份', '古墓传人')],
             quote='玉女心经·清冷如霜'),
    70: dict(pinyin='LI MO CHOU', rows=[('身长', '170 cm'), ('体重', '50 kg'),
                                        ('门派', '古墓派'), ('兵器', '拂尘'),
                                        ('身份', '赤练仙子')],
             quote='情之所钟·不疯魔不成活'),
}

# ---- 国风色名表：把采样到的颜色映射成有名字的传统色 ----------------------
COLOR_NAMES = [
    ('月白', (240, 244, 246)), ('素白', (250, 250, 248)), ('霜银', (203, 208, 213)),
    ('雾蓝', (170, 190, 205)), ('冰青', (198, 214, 210)), ('藕荷', (214, 199, 208)),
    ('灰蓝', (140, 155, 170)), ('石青', (96, 120, 140)), ('黛色', (74, 78, 86)),
    ('鸦青', (58, 66, 74)), ('墨黑', (32, 34, 38)), ('苍绿', (120, 138, 120)),
    ('琥珀', (196, 158, 110)), ('赭石', (150, 110, 88)), ('朱砂', (168, 68, 64)),
]

FONTS = [
    'C:/Windows/Fonts/STZHONGS.TTF',    # 华文中宋：名字用，最像设定卡
    'C:/Windows/Fonts/STSONG.TTF',
    'C:/Windows/Fonts/NotoSerifSC-VF.ttf',
    'C:/Windows/Fonts/simsun.ttc',
]
FONTS_UI = ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/Deng.ttf',
            'C:/Windows/Fonts/simhei.ttf']


def log(msg):
    print(msg)
    sys.stdout.flush()


def pick_font(cands, size):
    from PIL import ImageFont
    for p in cands:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:  # noqa: BLE001
                continue
    return ImageFont.load_default()


def build_prompt(label, desc):
    return ('请绘制一张%s。\n角色设定：%s\n\n%s\n\n%s'
            % (label, desc, REFINED, COMPOSE))


def sample_palette(im, n=8):
    """从立绘里提 n 个主色（剔除接近纯白的背景），按亮度从浅到深排序。"""
    from PIL import Image
    from collections import Counter
    small = im.convert('RGB').resize((220, 220))
    px = [p for p in small.getdata() if not (p[0] > 236 and p[1] > 236 and p[2] > 236)]
    if not px:
        return []
    strip = Image.new('RGB', (len(px), 1))
    strip.putdata(px)
    q = strip.quantize(colors=n, method=Image.Quantize.MEDIANCUT).convert('RGB')
    cnt = Counter(q.getdata())
    cols = [c for c, _ in cnt.most_common(n)]
    cols.sort(key=lambda c: -(0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]))
    return cols


def name_of(rgb, used=None):
    """给颜色找最接近的国风色名；used 里已用过的名字跳过，避免一栏里出现两个"月白"。"""
    used = used or set()
    order = sorted(COLOR_NAMES,
                   key=lambda kv: (kv[1][0] - rgb[0]) ** 2 + (kv[1][1] - rgb[1]) ** 2
                   + (kv[1][2] - rgb[2]) ** 2)
    for nm, _c in order:
        if nm not in used:
            return nm
    return order[0][0]


def cover(im, w, h):
    """等比放大填满 w×h 后居中裁切（不拉伸）。"""
    from PIL import Image
    iw, ih = im.size
    s = max(w / float(iw), h / float(ih))
    nw, nh = max(w, int(iw * s + 0.5)), max(h, int(ih * s + 0.5))
    im = im.resize((nw, nh), Image.LANCZOS)
    x, y = (nw - w) // 2, (nh - h) // 2
    return im.crop((x, y, x + w, y + h))


def draw_spaced(dr, xy, text, font, fill, spacing=0):
    """逐字画，模拟字距（PIL 没有 letter-spacing）。"""
    x, y = xy
    for ch in text:
        dr.text((x, y), ch, font=font, fill=fill)
        x += dr.textlength(ch, font=font) + spacing
    return x


def vert_text(dr, xy, text, font, fill, spacing=8):
    """竖排文字，从 xy 往下写。"""
    x, y = xy
    for ch in text:
        w = dr.textlength(ch, font=font)
        dr.text((x - w / 2.0, y), ch, font=font, fill=fill)
        y += font.size + spacing
    return y


def build_card(im, cid, label, fname):
    from PIL import Image, ImageDraw
    PW, H, PANEL = 1365, 2048, 735
    W = PW + PANEL
    card = Image.new('RGB', (W, H), (243, 244, 246))
    card.paste(cover(im, PW, H), (0, 0))

    dr = ImageDraw.Draw(card)
    # 右栏背景：极浅的竖向渐变，比纯色更像"卡面"
    for y in range(H):
        t = y / float(H - 1)
        dr.line([(PW, y), (W, y)],
                fill=(int(242 - 12 * t), int(243 - 12 * t), int(246 - 11 * t)))
    dr.line([(PW, 0), (PW, H)], fill=(198, 201, 207), width=2)

    prof = PROFILE.get(cid, {})
    name = label.split('（')[0]
    pinyin = prof.get('pinyin', 'SHENDIAO')
    rows = prof.get('rows', [('门派', '神雕侠侣'), ('身份', '江湖人')])
    quote = prof.get('quote', '情之所至·一往而深')

    ink, gray, line = (40, 42, 48), (122, 126, 134), (198, 201, 207)
    f_big = pick_font(FONTS, 130)
    f_pinyin = pick_font(FONTS_UI, 28)
    f_row_l = pick_font(FONTS_UI, 29)
    f_row_v = pick_font(FONTS_UI, 33)
    f_lab = pick_font(FONTS_UI, 23)

    # 名字（大字距）+ 拼音
    draw_spaced(dr, (PW + 66, 128), name, f_big, ink, spacing=14)
    draw_spaced(dr, (PW + 72, 300), pinyin, f_pinyin, gray, spacing=8)
    dr.line([(PW + 66, 372), (W - 66, 372)], fill=line, width=1)

    # 信息行
    y = 424
    for k, v in rows:
        dr.text((PW + 66, y + 4), k, font=f_row_l, fill=gray)
        dr.text((PW + 216, y), v, font=f_row_v, fill=ink)
        y += 74

    # 色卡
    y += 24
    dr.text((PW + 66, y), '色卡', font=f_lab, fill=gray)
    draw_spaced(dr, (PW + 128, y), 'COLOR', font=f_lab, fill=gray, spacing=4)
    y += 54
    cols = sample_palette(im, 8) or [(230, 232, 236)] * 8
    used = set()
    for c in cols:
        dr.ellipse([PW + 66, y, PW + 66 + 46, y + 46], fill=c, outline=(206, 209, 214))
        nm = name_of(c, used)
        used.add(nm)
        dr.text((PW + 128, y + 8), nm, font=f_pinyin, fill=ink)
        y += 70

    # 竖排台词（右侧，靠下）
    f_q = pick_font(FONTS, 30)
    qy = max(H - 250 - len(quote) * 38, 1500)
    vert_text(dr, (W - 96, qy), quote, f_q, (96, 100, 108), spacing=8)
    dr.text((PW + 66, H - 76), '神雕侠侣 · SHENDIAO', font=f_lab, fill=gray)
    return card


def main():
    argv = sys.argv[1:]
    force = '--force' in argv
    only = None
    if '--only' in argv:
        only = set(x.strip() for x in argv[argv.index('--only') + 1].split(',') if x.strip())
    aspect = argv[argv.index('--aspect') + 1] if '--aspect' in argv else '2:3'
    todo = [r for r in G.ROSTER
            if only is None or r[1] in only or str(r[0]) in only]
    if not todo:
        sys.exit('没有匹配到人物，检查 --only')

    key = G.api_key()
    os.makedirs(CARD_DIR, exist_ok=True)
    with io.open(LOG, 'a', encoding='utf-8') as fh:
        fh.write('\n==== %s 设定卡 %d 张 aspect=%s\n'
                 % (time.strftime('%Y-%m-%d %H:%M:%S'), len(todo), aspect))

    for row in todo:
        cid, fname, label, desc = row[0], row[1], row[2], row[3]
        t0 = time.time()
        por = os.path.join(CARD_DIR, '%s_portrait.png' % fname)
        try:
            if os.path.isfile(por) and not force:
                raw = io.open(por, 'rb').read()
                src = 'REUSE'
            else:
                raw = G.gen_one(key, build_prompt(label, desc), aspect=aspect)
                io.open(por, 'wb').write(raw)
                src = 'NEW  '
            from PIL import Image
            im = Image.open(io.BytesIO(raw)).convert('RGB')
            card = build_card(im, cid, label, fname)
            dst = os.path.join(CARD_DIR, '%s_card.png' % fname)
            card.save(dst, 'PNG', optimize=True)
            msg = ('%s %-18s 立绘 %dx%d -> 卡面 %dx%d  %3.0fs'
                   % (src, label, im.size[0], im.size[1],
                      card.size[0], card.size[1], time.time() - t0))
            log(msg)
            with io.open(LOG, 'a', encoding='utf-8') as fh:
                fh.write(msg + '  ' + os.path.basename(dst) + '\n')
        except Exception as e:  # noqa: BLE001
            msg = 'FAIL %-18s %s' % (label, e)
            log(msg)
            with io.open(LOG, 'a', encoding='utf-8') as fh:
                fh.write(msg + '\n')


if __name__ == '__main__':
    main()

