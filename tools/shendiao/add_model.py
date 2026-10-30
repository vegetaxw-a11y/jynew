#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 MOD 新增一个 CharacterModel 资源（Models/<中文名>.asset）

    python tools/shendiao/add_model.py 杨过 BattleNpc/Yangguo
    python tools/shendiao/add_model.py 郭靖 BattleNpc/Guojing --force

模型引用有两种写法：
    "Tongsier"             -> Mods/shendiao/Prefabs/Tongsier.prefab
    "BattleNpc/Yangguo"    -> Assets/BuildSource/ModelCharacters/BattleNpc/Yangguo.prefab

m_View 要指向 prefab 的**根 GameObject**（不是 Transform），这是 Jyx2 的读取方式。
生成的 .asset 与已有资源完全同构，武器槽沿用项目默认的三把。
"""
import io
import os
import re
import sys
import uuid

ROOT = "jyx2/Assets/Mods/shendiao"
PREFABS = os.path.join(ROOT, "Prefabs")
MODELS = os.path.join(ROOT, "Models")
SHARED = "jyx2/Assets/BuildSource/ModelCharacters"

# 项目默认武器部件（与 童四二.asset / 王远.asset 一致）
WEAPON_SLOTS = """  m_SwordWeapon:
    id: 0
  m_KnifeWeapon:
    id: 1
  m_SpearWeapon:
    id: 2
  references:
    version: 1
    00000000:
      type: {class: SwordPart, ns: Jyx2, asm: Assembly-CSharp}
      data:
        m_Id: 1
        m_BindBone: QuickRigCharacter_RightHand
        m_PartView: {fileID: 1216378884712654, guid: 536d2078b40d14b489a9adc6f0819951,
          type: 3}
        m_OffsetPosition: {x: 0, y: 0, z: 0}
        m_OffsetRotation: {x: 0, y: 0, z: 0}
        m_OffsetScale: {x: 1, y: 1, z: 1}
    00000001:
      type: {class: KnifePart, ns: Jyx2, asm: Assembly-CSharp}
      data:
        m_Id: 2
        m_BindBone: QuickRigCharacter_RightHand
        m_PartView: {fileID: 1991866320728406, guid: 9a87103d420e21d48afd6c71f13b21c8,
          type: 3}
        m_OffsetPosition: {x: 0, y: 0, z: 0}
        m_OffsetRotation: {x: 0, y: 0, z: 0}
        m_OffsetScale: {x: 1, y: 1, z: 1}
    00000002:
      type: {class: SpearPart, ns: Jyx2, asm: Assembly-CSharp}
      data:
        m_Id: 3
        m_BindBone: QuickRigCharacter_RightHand
        m_PartView: {fileID: 1225507566611884, guid: e4a8b328034504848b4373bbdaaefd04,
          type: 3}
        m_OffsetPosition: {x: 0, y: 0, z: 0}
        m_OffsetRotation: {x: 0, y: 0, z: 0}
        m_OffsetScale: {x: 1, y: 1, z: 1}"""

MODEL_TMPL = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!114 &11400000
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 0}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: 2a9c03694ddf4928b28528d7ab9dd03c, type: 3}}
  m_Name: "{escaped}"
  m_EditorClassIdentifier: 
  m_View: {{fileID: {view}, guid: {guid}, type: 3}}
{weapons}
"""

META_TMPL = """fileFormatVersion: 2
guid: {guid}
NativeFormatImporter:
  externalObjects: {{}}
  mainObjectFileID: 11400000
  userData: 
  assetBundleName: shendiao_mod
  assetBundleVariant: 
"""


def read(path):
    with io.open(path, encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", errors="surrogateescape", newline="\n") as f:
        f.write(text)


def escape_yaml(s):
    """非 ASCII 一律转成 \\uXXXX（Unity 的 YAML 就是这么写的）"""
    return "".join(c if ord(c) < 128 else "\\u%04X" % ord(c) for c in s)


def role_prefab(ref):
    if "/" in ref:
        return os.path.join(SHARED, ref.replace("/", os.sep) + ".prefab")
    return os.path.join(PREFABS, ref + ".prefab")


def root_game_object(prefab_text):
    """根 GameObject = 它的 Transform 的 m_Father 为 0 的那个对象"""
    docs = {}
    blocks = re.split(r"(?m)^--- !u!(\d+) &(-?\d+)(?: stripped)?\r?\n", prefab_text)
    for i in range(1, len(blocks), 3):
        docs[blocks[i + 1]] = (blocks[i], blocks[i + 2])
    for fid, (cls, body) in docs.items():
        if cls != "4":
            continue
        if not re.search(r"m_Father: \{fileID: 0\}", body):
            continue
        m = re.search(r"m_GameObject: \{fileID: (\d+)\}", body)
        if m:
            return m.group(1)
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 2
    name, ref = args
    pf = role_prefab(ref)
    if not os.path.exists(pf):
        print("[error] prefab 不存在：%s" % pf)
        return 1
    guid = re.search(r"guid: ([0-9a-f]{32})", read(pf + ".meta")).group(1)
    view = root_game_object(read(pf))
    if not view:
        print("[error] %s 里找不到根 GameObject" % pf)
        return 1

    out = os.path.join(MODELS, name + ".asset")
    if os.path.exists(out) and not force:
        print("[skip] 已存在：%s（要覆盖加 --force）" % out)
        return 1
    write(out, MODEL_TMPL.format(escaped=escape_yaml(name), view=view,
                                 guid=guid, weapons=WEAPON_SLOTS))
    write(out + ".meta", META_TMPL.format(guid=uuid.uuid4().hex))
    print("[ok] %s -> %s  (m_View fileID=%s)" % (name, ref, view))
    return 0


if __name__ == "__main__":
    sys.exit(main())
