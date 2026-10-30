# -*- coding: utf-8 -*-
"""用 AI 网关的 gemini-3-pro-image（Nano-Banana-Pro）生成 shendiao 人物头像。

为什么要有这个脚本（见 docs/shendiao-context.md 第八节）：
  * 现有 BuildSource/head/*.png 是 _make_heads.py 从原版金庸群侠传里"借"的图，
    借来的脸和人物对不上，画风也不统一。
  * 游戏里头像按 512x512、textureType=Sprite、maxTextureSize=512 显示，
    所以 1K/2K 原图必须缩到 512 并保留 RGBA。
  * MOD 包把 assets/mods/shendiao/xxx 登记成 assets/xxx 并覆盖 base_assets，
    所以只要往 Assets/Mods/shendiao/BuildSource/head/<id>.png 丢图就生效。

约定：
  * 密钥只从环境变量 TURBO_KEY / OPENAI_API_KEY 读，绝不写进文件、不写进日志。
  * 大图另存 Export/heads_raw/（gitignore），512 成品写入 MOD 目录。
  * .meta 复制同目录已有头像的导入设置，只换 guid（与 _make_heads.py 一致）。

用法:
  $env:TURBO_KEY = 'sk-...'
  python tools/shendiao/gen_heads.py --list
  python tools/shendiao/gen_heads.py --only 0          # 试一张，看看效果
  python tools/shendiao/gen_heads.py --only 0,22 --apply
  python tools/shendiao/gen_heads.py --apply           # 全量
  python tools/shendiao/gen_heads.py --apply --force    # 覆盖已有成品
"""
import base64
import io
import json
import os
import re
import sys
import time
import uuid
import urllib.request

ROOT = r'c:\Games\jynew'
MOD = os.path.join(ROOT, 'jyx2', 'Assets', 'Mods', 'shendiao')
HEAD_DIR = os.path.join(MOD, 'BuildSource', 'head')
RAW_DIR = os.path.join(ROOT, 'Export', 'heads_raw')
LOG = os.path.join(ROOT, 'Logs', '_heads_gen.log')

URL = 'https://gateway.theturbo.ai/v1/images/generations'
MODEL = 'gemini-3-pro-image'
FINAL = 512          # 游戏里要的成品尺寸
IMAGE_SIZE = '2K'    # 网关支持 1K / 2K / 4K；2K 缩到 512 更细腻
TIMEOUT = 420
RETRY = 3

# 全套统一的画风指令：和原版头像一样是"白底半身像"，放进立绘框里才不突兀。
STYLE = (
    '要求：手绘的国风武侠插画，半身胸像构图，人物头部位于画面上方、约占画面三分之二，'
    '肩膀入画；纯白或极浅的米白色背景，背景不画任何景物、纹样、边框、logo、文字或水印；'
    '线条干净利落、粗细有致的墨线勾边，赛璐璐平涂配合柔和渐变的阴影，'
    '五官刻画精致写实而不夸张，皮肤与头发质感细腻，眼神有神采；'
    '南宋时期的服饰与发式，符合金庸《神雕侠侣》原著的人物设定；'
    '正方形构图，正视或四分之三侧脸。'
)

# 动物用另一套构图指令：上面那套 STYLE 要求"半身胸像 / 肩膀入画"，
# 模型会顺手画个人出来（野狼→披狼皮的汉子，毒蛇→肩上盘条蛇），必须明说不要人。
ANIMAL_STYLE = (
    '画面中只有这只动物本身，绝对不要出现人、人脸、人的手、兵器、衣服或任何人形轮廓；'
    '动物的头部与颈肩（或头颈部位）入画、占据画面大部分空间；'
    '纯白或极浅的米白色背景，背景不画任何景物、纹样、边框、logo、文字或水印；'
    '线条干净利落的墨线勾边，赛璐璐平涂配合柔和渐变的阴影，'
    '毛发或鳞片质感细腻写实；正方形构图，正视或四分之三侧脸。'
)

# (人物 id, 成品文件名, 显示名, 人物描述[, 画风覆盖])

# 只收录剧本里真正出场的角色（按 Talk(id) 出现次数统计），未出场的配置行不生成。
ROSTER = [
    (0, '0', '杨过（少年）',
     '金庸《神雕侠侣》男主角杨过的少年时期，十四五岁，面庞还带着少年人的圆润稚气、'
     '下颌线条尚未完全硬朗。面容清秀俊美、眉眼灵动，'
     '眼神里带着寄人篱下的倔强、敏感与不服气，嘴角微抿；黑发用青布半束，'
     '几缕碎发垂在脸侧；身穿灰蓝色粗布短褐，颈间系旧布巾，身形单薄清瘦。'),
    (0, '0_adult', '杨过（中年·神雕侠）',
     '杨过三十六岁、人称"神雕侠"的时期。面容清癯英俊，眉宇沉毅，'
     '眼角与鬓边已有风霜痕迹，眼神深邃平静；长发束起、掺着几缕花白；'
     '右臂已断，右侧衣袖空荡垂落；身穿玄黑窄袖长袍，气质孤高冷峻。'),
    (22, '22', '小龙女',
     '古墓派传人小龙女，约二十岁。容貌绝色清丽，肌肤白皙近乎透明，'
     '眉如远山、眼若寒星，神情淡漠清冷、无喜无怒；长发及腰，'
     '只用一条素白丝带轻轻束住；一袭纯白衣衫，颈间无饰，气质出尘不食人间烟火。'),
    (10, '10', '郭靖',
     '大侠郭靖，三十五六岁。浓眉大眼，方脸阔额，肤色黝黑泛红，'
     '面容质朴敦厚，目光沉静坚毅；唇上短须；身材魁梧厚实，'
     '穿灰蓝粗布长衫束黑色腰带，衣料朴素、有风尘感。'),
    (11, '11', '黄蓉',
     '女诸葛黄蓉，三十出头。明艳美丽，眉目灵动，眼波流转间带着慧黠与几分俏皮；'
     '乌发挽成雅致发髻，插一支素白珠钗；身穿淡黄绿的丝绸衣衫，'
     '颈间点缀细小银饰，聪慧干练又从容。'),
    (20, '20', '赵志敬',
     '全真教道士赵志敬，四十岁左右。面容瘦削、颧骨偏高，三绺修剪整齐的黑须，'
     '双眼细长、习惯斜着看人，神情阴鸷刻薄、带着算计与轻蔑；'
     '头戴玄色道冠，身穿灰蓝色道袍，束腰带。'),
    (21, '21', '孙婆婆',
     '古墓派的孙婆婆，六十五岁左右。满脸深刻的皱纹，颧骨突出，'
     '花白头发在脑后挽成小髻、插一根木簪，眼神慈和里带着倔强护短；'
     '身穿灰褐色粗布衣裳，身姿佝偻但精神。'),
    (23, '23', '丘处机',
     '全真七子之首丘处机，五十五岁上下。面容刚毅方正，浓眉入鬓，'
     '长须半白垂胸，目光如电、正气凛然，气质仙风道骨；'
     '头戴玄色道冠，身穿深蓝道袍，衣纹整肃。'),
    (24, '24', '神雕',
     '一头巨大的神雕，体型比人还高大。它像秃鹫与鹰的结合，'
     '羽毛稀疏、呈暗褐灰黑色，脖颈处裸露着深色皱皮，弯钩状的巨喙锐利，'
     '双目金黄、凶悍之中透着通人性，气质苍古孤傲；画面里不出现任何人物。'),
    (26, '26', '公孙止',
     '绝情谷主公孙止，四十五岁左右。面容儒雅白皙、保养得很好，'
     '下巴蓄三绺修剪整齐的黑须，眉眼温和，但眼神深处藏着阴冷与算计；'
     '头戴玉冠，身穿玄青锦袍，衣饰讲究。'),
    (27, '27', '公孙绿萼',
     '公孙止之女公孙绿萼，十八岁。清秀温婉，眉目柔和，眼含淡淡轻愁；'
     '乌黑长发垂落双肩，额前留整齐刘海；身穿浅绿色衣裙，'
     '素净无华，气质柔弱而澄澈。'),
    (28, '28', '樊一翁',
     '绝情谷的老仆樊一翁，六十五岁左右。身材高大魁梧，白眉如霜，'
     '白须垂至胸前，头顶半秃，面色红润，笑起来豪爽憨直；'
     '身穿褐色粗布短打，露出结实的臂膀。'),
    (29, '29', '裘千尺',
     '裘千尺，五十多岁却形销骨立、苍老枯槁。头发花白稀落散乱，'
     '牙齿残缺，双颊深陷，眼睛凸出、目光怨毒凌厉，笑容狰狞；'
     '身穿破旧灰黑布衣，肤色黄黑，气质凄厉如鬼。'),
    (30, '30', '柯镇恶',
     '江南七怪之首柯镇恶，六十五岁左右。双目失明，眼珠呈灰白的死色，'
     '面部横着一道旧伤疤，花白短须，神情刚烈暴躁、不怒自威；'
     '身穿灰布长袍，手握一根竹制盲杖。'),
    (31, '31', '洪七公',
     '九指神丐洪七公，七十多岁。白发白须蓬乱地披散，面色红润有光，'
     '笑容爽朗慈和、嘴里像含着一丝馋意；衣衫破旧打着补丁，'
     '肩上斜挎一只旧酒葫芦，一副老叫花子的洒脱模样。'),
    (35, '35', '陆无双',
     '陆无双，十八岁。俏丽明艳，杏眼微挑，嘴角带着一丝刁蛮任性的讥诮；'
     '身穿古墓派白衣，乌黑长发用素色布带束起，腰间佩剑，活泼又带刺。'),
    (36, '36', '周伯通',
     '老顽童周伯通，七十多岁。满头白发散乱成团，白须稀疏，'
     '眉毛又长又白垂在眼侧，眼睛圆而明亮，满是孩子气的促狭与顽皮；'
     '身穿破旧灰白长袍，衣襟歪斜不整。'),
    (37, '37', '瑛姑',
     '瑛姑，五十多岁。头发半白、蓬乱地挽起，面容憔悴清瘦，'
     '眼眶发暗，眉间深锁，眼神又怨又痴、带着偏执；'
     '身穿素色旧衣，鬓边还残存一支旧银钗，气质凄楚。'),
    (38, '38', '一灯大师',
     '一灯大师（段智兴），七十多岁的老僧。已剃度，光头，'
     '白眉长垂，面容慈和清癯，双目微闭、透着悲悯与看破；'
     '身穿褐色僧袍，颈挂念珠，端坐如钟。'),
    (39, '39', '裘千仞',
     '铁掌帮帮主裘千仞，五十多岁。面容阴狠沉鸷，眉骨突出，'
     '下颌蓄短黑须，目光凌厉如刀、杀气外露；'
     '身穿深褐色劲装，小臂缠着护腕，体格精悍。'),
    (40, '40', '欧阳锋',
     '西毒欧阳锋，六十五岁左右。西域白驼山人，高鼻深目、鼻梁如鹰钩，'
     '肤色偏白，白发披散，眼神阴冷凶狠、似笑非笑；'
     '身穿一袭白衣，腰间缠着软鞭与蛇囊，气质诡秘毒辣。'),
    (41, '41', '郭芙',
     '郭芙，十六岁。娇艳明媚，眉目精致，下巴微微抬起，神情骄纵任性；'
     '乌发挽成双髻、插着珠花，身穿绯红锦衣，衣饰华贵。'),
    (42, '42', '武敦儒',
     '少年武敦儒，十七岁。圆脸浓眉，眼神老实憨厚，'
     '黑发束成发髻，身穿青灰色粗布短打劲装，拘谨地拱手，一副没心机的模样。'),
    (43, '43', '华山派弟子',
     '华山派的青年弟子，二十五岁左右。面容清瘦，目光锐利机警，'
     '鬓发梳理整齐，身穿青布道袍，背负长剑，气质正派而谨慎。'),
    (60, '60', '鹿清笃',
     '全真教弟子鹿清笃，二十六岁。面容油滑猥琐，鼠目小而游移，'
     '薄唇上留两撇细胡须，笑起来带着谄媚与恶意的混合；'
     '身穿青色道袍，腰悬令牌。'),
    (70, '70', '李莫愁',
     '"赤练仙子"李莫愁，三十岁上下。容貌艳美，眉梢眼角尽是风情，'
     '眼底却藏着冷酷的杀意，唇边挂着讥诮的笑；'
     '乌黑长发挽成道髻、斜插素钗，身穿杏黄道袍，手握一柄拂尘，妖艳而危险。'),
    (90, '90', '程英',
     '程英，十八岁。清雅端庄、温婉秀美，眉眼柔和，笑意浅淡；'
     '乌黑长发挽成简单的发式、以素色发带束住，身穿淡青色长衫，'
     '手持一支竹笛，气质静雅而有书卷气。'),
    (111, '111', '庙祝',
     '破庙里的老庙祝，六十多岁。身形瘦削，脸颊凹陷，'
     '花白山羊须，眼窝深陷、眼神浑浊却藏着一丝精明与迟疑；'
     '身穿洗得发白的灰布短褐，肩背微驼。'),
    (44, '44', '武三通',
     '一灯大师的弟子"农夫"武三通，五十岁上下。身材高大粗壮、肩背厚实，'
     '肤色黝黑粗糙，满脸乱蓬蓬的花白胡须、头发散乱打结如野人，'
     '双目赤红、眼神疯癫执拗而痛苦，眉心紧锁；'
     '身穿破烂沾泥的灰褐色农家短褐，衣襟半敞露出胸膛，'
     '手臂青筋虬结，像个在坟地里刨了几天土的疯子。'),
    (73, '73', '洪凌波',
     '古墓派李莫愁的弟子洪凌波，二十岁。面容清秀、眉眼明净，'
     '眼神里藏着几分对师父的畏惧与顺从，神情拘谨端肃；'
     '乌黑长发挽成简单道髻、只插一根木钗，几缕碎发落在颊边；'
     '身穿素净的淡黄布道袍，腰束布带，气质干净而寡淡。'),
    # ---- 战斗单位：原版只有借来的"人脸"，动物更是完全没图 ----
    (61, '61', '伏格多',
     '西域来的武士伏格多，四十岁上下。深目高鼻、鼻梁如鹰钩，肤色黑红，'
     '络腮胡修剪成短须，眼神凶狠阴沉；头戴皮帽，'
     '身穿镶铁片的皮甲、外罩深褐斗篷，颈挂兽牙，体格魁梧结实。'),
    (62, '62', '将军府士兵',
     '金国将军府的亲兵，二十五岁上下。方脸浓眉、肤色黝黑，神情木讷驯顺；'
     '头戴铁盔、盔缨残旧，身穿暗红与铁灰相间的札甲，'
     '肩甲有磨损划痕，颈下系一条旧布巾。'),
    (71, '71', '曼陀谷弟子',
     '曼陀谷的年轻弟子，二十岁左右。面容清秀冷淡，眉眼细长，'
     '神情戒备；黑发在头顶束成一个利落的髻，'
     '身穿靛青窄袖劲装、腰间束着暗红布带，肩后露出一截刀柄。'),
    (610, '610', '蓝隼士兵',
     '蓝隼帮的喽啰兵，二十五岁上下。面容粗野、下颌留着短髭，'
     '咧嘴带着凶气；头上裹深蓝布巾，'
     '身穿藏蓝短打、胸前斜挎皮索，肩头落着一只蓝灰色隼的羽毛纹样。'),
    (141, '141', '野狼',
     '一头荒野中的灰狼。头部与肩颈入画，两耳竖立，'
     '灰褐色的毛粗硬蓬乱、颈侧有一片颜色更深的鬃毛，'
     '双眼泛着幽绿的凶光，露出的獠牙泛黄；画面里不出现任何人物。', ANIMAL_STYLE),
    (163, '163', '黑熊',
     '一头成年的黑熊。头部与厚实的肩背入画，'
     '全身乌黑浓密的硬毛，鼻头湿润发亮，'
     '小而圆的眼睛透出凶性，嘴边挂着白沫；画面里不出现任何人物。', ANIMAL_STYLE),
    (168, '168', '巨型黑熊',
     '一头比寻常黑熊巨大得多的老黑熊。头部与肩背入画，'
     '鬃毛粗硬如铁刺、颈侧与脸颊留着几道陈年抓痕，'
     '一只耳朵残缺，獠牙粗长，双目赤红；画面里不出现任何人物。', ANIMAL_STYLE),
    (181, '181', '毒蛇',
     '一条剧毒的青花蛇。头部与颈身入画，'
     '鳞片青黑相间、泛着湿润的油光，眼睛是竖瞳的金黄色，'
     '蛇信吐出，颈部微微鼓成兜状；画面里不出现任何人物。', ANIMAL_STYLE),
]

BY_FILE = {r[1]: r for r in ROSTER}


def log(msg):
    print(msg)
    sys.stdout.flush()


def api_key():
    # ANTHROPIC_AUTH_TOKEN 也走同一个网关（https://gateway.theturbo.ai），
    # 但它是 Cline 自己注入的环境变量，优先级放在最后，免得盖掉专门的出图 key。
    for k in ('TURBO_KEY', 'OPENAI_API_KEY', 'AIG_API_KEY', 'ANTHROPIC_AUTH_TOKEN'):
        v = os.environ.get(k)
        if v and v.strip():
            return v.strip()
    sys.exit('缺少密钥：请先设置环境变量 TURBO_KEY（本脚本不读任何配置文件）')


def gen_one(key, prompt, aspect='1:1', image_size=None, model=None):
    """调网关出一张图，返回 PNG bytes。

    aspect: 1:1 / 2:3 / 3:4 …（gemini-3-pro-image 的 aspect_ratio）
    image_size: 默认 IMAGE_SIZE（2K）
    model: 默认 MODEL；可传 'gemini-nano-banana-2.1' 之类换模型，其他参数不变
    """
    body = {
        'model': model or MODEL,
        'prompt': prompt,
        'response_format': 'b64_json',
        'aspect_ratio': aspect,
        'image_size': image_size or IMAGE_SIZE,
    }
    data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    last = None
    for i in range(RETRY):
        req = urllib.request.Request(URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('Authorization', 'Bearer ' + key)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                payload = json.loads(r.read().decode('utf-8'))
            item = (payload.get('data') or [{}])[0]
            b64 = item.get('b64_json')
            if not b64:
                raise RuntimeError('返回里没有 b64_json：%s' % str(payload)[:300])
            return base64.b64decode(b64)
        except Exception as e:  # noqa: BLE001
            last = e
            wait = 5 * (i + 1)
            log('   ! 第 %d 次失败：%s（%ds 后重试）' % (i + 1, e, wait))
            time.sleep(wait)
    raise RuntimeError('重试 %d 次仍失败：%s' % (RETRY, last))


def to_512(png_bytes):
    """缩到 512x512 RGBA —— 游戏里就是这么用的。"""
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes))
    im = im.convert('RGBA')
    if im.size != (FINAL, FINAL):
        im = im.resize((FINAL, FINAL), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return buf.getvalue(), im.size


def meta_for(cid):
    """复制同目录头像的 .meta，只换 guid，保证导入设置 / AB 标记一致。"""
    def usable(path):
        # 模板必须真的是个 meta：0 字节 / 被截断的文件当模板会写出一堆空 meta
        try:
            head = io.open(path, encoding='utf-8').read(64)
        except OSError:
            return False
        return head.startswith('fileFormatVersion:') and os.path.getsize(path) > 500

    src = os.path.join(HEAD_DIR, '%d.png.meta' % cid)
    if not usable(src):
        cands = sorted(f for f in os.listdir(HEAD_DIR) if f.endswith('.png.meta'))
        cands = [f for f in cands if usable(os.path.join(HEAD_DIR, f))]
        if not cands:
            raise RuntimeError('找不到可复用的 .meta 模板')
        src = os.path.join(HEAD_DIR, cands[0])
    text = io.open(src, encoding='utf-8').read()
    text = re.sub(r'(?m)^guid: [0-9a-f]{32}$', 'guid: ' + uuid.uuid4().hex, text, count=1)
    # spriteID 也必须唯一：批量复制同一个模板 meta 会让多个贴图共用一个 spriteID，
    # Unity 打 AB 时会互相串（_tag_assetbundle.py 里踩过这个坑）。
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
    model = argv[argv.index('--model') + 1] if '--model' in argv else MODEL

    if '--list' in argv:
        for row in ROSTER:
            log('%3d  %-8s %s' % (row[0], row[1], row[2]))
        return

    todo = [r for r in ROSTER if only is None or r[1] in only or str(r[0]) in only]
    if not todo:
        sys.exit('没有匹配到要生成的人物，检查 --only')

    key = api_key()
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with io.open(LOG, 'a', encoding='utf-8') as fh:
        fh.write('\n==== %s  生成 %d 张（%s  model=%s）\n' % (
            time.strftime('%Y-%m-%d %H:%M:%S'), len(todo), 'apply' if apply_ else 'dry', model))

    ok = fail = skip = 0
    for row in todo:
        cid, fname, label, desc = row[0], row[1], row[2], row[3]
        style = row[4] if len(row) > 4 else STYLE
        dst_png = os.path.join(HEAD_DIR, '%s.png' % fname)
        dst_meta = dst_png + '.meta'
        if apply_ and os.path.isfile(dst_png) and not force and not fname.endswith('_adult'):
            log('-- 跳过 %s（已有 %s.png，加 --force 覆盖）' % (label, fname))
            skip += 1
            continue
        prompt = '请绘制一张中国武侠风格的头像插画：%s。\n%s\n%s' % (label, desc, style)
        t0 = time.time()
        try:
            raw = gen_one(key, prompt, model=model)
            png, size = to_512(raw)
            stamp = time.strftime('%m%d_%H%M%S')
            raw_path = os.path.join(RAW_DIR, '%s_%s.png' % (fname, stamp))
            io.open(raw_path, 'wb').write(raw)
            msg = 'OK   %-18s %dx%d %6.1fKB %4.0fs' % (label, size[0], size[1],
                                                      len(png) / 1024.0, time.time() - t0)
            if fname.endswith('_adult'):
                io.open(os.path.join(RAW_DIR, 'preview_%s.png' % fname), 'wb').write(png)
                msg += '  (变体，只存 Export/heads_raw)'
            elif apply_:
                io.open(dst_png, 'wb').write(png)
                # 注意顺序：meta_for() 可能去读 dst_meta 当模板，必须先取文本再打开文件写，
                # 否则 'w' 已经把文件截断，读回来是空字符串（曾经把 6 个 .meta 写成 0 字节）。
                meta_txt = meta_for(cid)
                io.open(dst_meta, 'w', encoding='utf-8', newline='\n').write(meta_txt)
                msg += '  -> %s.png + .meta' % fname
            else:
                io.open(os.path.join(RAW_DIR, 'preview_%s.png' % fname), 'wb').write(png)
                msg += '  (预演，未写入 MOD)'
            log(msg)
            with io.open(LOG, 'a', encoding='utf-8') as fh:
                fh.write(msg + '  raw=' + os.path.basename(raw_path) + '\n')
            ok += 1
        except Exception as e:  # noqa: BLE001
            msg = 'FAIL %-18s %s' % (label, e)
            log(msg)
            with io.open(LOG, 'a', encoding='utf-8') as fh:
                fh.write(msg + '\n')
            fail += 1

    log('')
    log('完成：成功 %d，失败 %d，跳过 %d' % (ok, fail, skip))
    log('日志：%s' % LOG)
    log('大图：%s' % RAW_DIR)


if __name__ == '__main__':
    main()

