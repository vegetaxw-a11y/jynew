# -*- coding: utf-8 -*-
"""给 19_chongyanggong 的鹿清笃挂上"让路"能力。

踩过的坑（别再踩）：
  - NPC 不能被 Lua 移动，jyx2_WalkFromTo 只驱动玩家。
  - 引擎里唯一"按 flag 移动物体"的机制是 FixWithGameRuntime：
        Reload() -> transform.position = MoveTo.position
    它移动的是**挂载者自己**，所以必须挂在 NPC 身上；挂在 Triggers/1 上
    只会把触发器搬走（历史上就是这么错的，弟子从未动过）。
  - 对话里 jyx2_FixMapObject("重阳宫大门弟子让路", 1) 会立刻对 Flag 匹配的
    FixWithGameRuntime 调 Reload()，无需重进场景。
  - QuanzhenDizi 1.prefab 被 19_chongyanggong / 01_moqiaoshanzhuang 共用
    （133 个实例），所以只改**本场景的 prefab instance**，不碰 prefab 源文件。

做的事（手工 YAML + 校验，校验不过就不落盘）：
  1. Level/NPC 下建空锚点 "弟子让路点" (32.0, 0, 12.9)
     山门缺口 z[9.7,13.6]，站到北侧 12.9 才真让出通道；y=0 避免浮空
  2. 给弟子 prefab instance 的 stripped GameObject 加 FixWithGameRuntime
  3. PrefabInstance 的 m_Modification 登记 m_AddedComponents
  4. NPC Transform 的 m_Children 追加新锚点

用法: python tools/shendiao/add_letway_npc.py [--dry-run]
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from list_prefab_instances import split_blocks  # noqa: E402

SCENE = 'jyx2/Assets/Mods/shendiao/Maps/GameMaps/19_chongyanggong.unity'

# 场景里已确认的锚点（场景结构变了要同步）
NPC_TRANSFORM = '495782820'
NPC_ROOT = '173614895'
DIZI_GO = '2139027071'          # 弟子实例的 stripped GameObject
DIZI_TRANSFORM = '2139027072'   # 弟子实例的 stripped Transform
DIZI_PREFAB_INSTANCE = '1070426209'
DIZI_SRC_ROOT_GO = '1668298488315685554'
DIZI_PREFAB_GUID = 'f03b76862fbbf7e4ea7cca0fc066c097'
FIX_SCRIPT_GUID = '4f6a8d73bfe6fbf44bf8b99fea40f05c'

NEW_GO = '168814833'
NEW_TRANSFORM = '168814834'
NEW_COMPONENT = '168814835'

FLAG_NAME = r'\u91CD\u9633\u5BAB\u5927\u95E8\u5F1F\u5B50\u8BA9\u8DEF'
ANCHOR_NAME = r'\u5F1F\u5B50\u8BA9\u8DEF\u70B9'


def build_gameobject(anchor_go, anchor_tr, parent_tr, root_order, pos):
    return (
        '--- !u!1 &{go}\n'
        'GameObject:\n'
        '  m_ObjectHideFlags: 0\n'
        '  m_CorrespondingSourceObject: {{fileID: 0}}\n'
        '  m_PrefabInstance: {{fileID: 0}}\n'
        '  m_PrefabAsset: {{fileID: 0}}\n'
        '  serializedVersion: 6\n'
        '  m_Component:\n'
        '  - component: {{fileID: {tr}}}\n'
        '  m_Layer: 0\n'
        '  m_Name: "{name}"\n'
        '  m_TagString: Untagged\n'
        '  m_Icon: {{fileID: 0}}\n'
        '  m_NavMeshLayer: 0\n'
        '  m_StaticEditorFlags: 0\n'
        '  m_IsActive: 1\n'
        '--- !u!4 &{tr}\n'
        'Transform:\n'
        '  m_ObjectHideFlags: 0\n'
        '  m_CorrespondingSourceObject: {{fileID: 0}}\n'
        '  m_PrefabInstance: {{fileID: 0}}\n'
        '  m_PrefabAsset: {{fileID: 0}}\n'
        '  m_GameObject: {{fileID: {go}}}\n'
        '  m_LocalRotation: {{x: 0, y: 0.7071068, z: 0, w: 0.7071068}}\n'
        '  m_LocalPosition: {{x: {px}, y: {py}, z: {pz}}}\n'
        '  m_LocalScale: {{x: 1, y: 1, z: 1}}\n'
        '  m_Children: []\n'
        '  m_Father: {{fileID: {parent}}}\n'
        '  m_RootOrder: {order}\n'
        '  m_LocalEulerAnglesHint: {{x: 0, y: 90, z: 0}}\n'
    ).format(go=anchor_go, tr=anchor_tr, name=ANCHOR_NAME, px=pos[0], py=pos[1],
             pz=pos[2], parent=parent_tr, order=root_order)


def build_component(comp_fid, target_go, move_to_transform):
    return (
        '--- !u!114 &{fid}\n'
        'MonoBehaviour:\n'
        '  m_ObjectHideFlags: 0\n'
        '  m_CorrespondingSourceObject: {{fileID: 0}}\n'
        '  m_PrefabInstance: {{fileID: 0}}\n'
        '  m_PrefabAsset: {{fileID: 0}}\n'
        '  m_GameObject: {{fileID: {go}}}\n'
        '  m_Enabled: 1\n'
        '  m_EditorHideFlags: 0\n'
        '  m_Script: {{fileID: 11500000, guid: {guid}, type: 3}}\n'
        '  m_Name:\n'
        '  m_EditorClassIdentifier:\n'
        '  FixType: 0\n'
        '  Flag: "{flag}"\n'
        '  MoveTo: {{fileID: {moveto}}}\n'
    ).format(fid=comp_fid, go=target_go, guid=FIX_SCRIPT_GUID,
             flag=FLAG_NAME, moveto=move_to_transform)


def main():
    dry = '--dry-run' in sys.argv
    text = io.open(SCENE, encoding='utf-8', errors='surrogateescape').read()
    blocks = split_blocks(text)
    by = {b['fid']: b for b in blocks}

    # ---- 校验锚点 ----
    for fid, why in ((NPC_TRANSFORM, 'NPC Transform'),
                     (DIZI_GO, '弟子 stripped GameObject'),
                     (DIZI_TRANSFORM, '弟子 stripped Transform'),
                     (DIZI_PREFAB_INSTANCE, '弟子 PrefabInstance')):
        if fid not in by:
            sys.exit('!! 找不到 %s (fid %s)，场景结构可能已变，停止' % (why, fid))
    for fid in (NEW_GO, NEW_TRANSFORM, NEW_COMPONENT):
        if fid in by:
            sys.exit('!! fileID %s 已被占用，换一个' % fid)
    if 'FixWithGameRuntime' in by[DIZI_PREFAB_INSTANCE]['body']:
        sys.exit('!! 弟子上已经挂过 FixWithGameRuntime，停止（幂等保护）')

    # ---- 1) NPC Transform 的 m_Children 追加锚点 ----
    npc_body = by[NPC_TRANSFORM]['body']
    if '- {fileID: %s}' % NEW_TRANSFORM in npc_body:
        sys.exit('!! NPC 子节点里已有该锚点，停止')
    marker = '  m_Father: {fileID: %s}' % NPC_ROOT
    if npc_body.count(marker) != 1:
        sys.exit('!! NPC Transform 的 m_Father 定位失败，停止')
    new_npc_body = npc_body.replace(
        marker, '  - {fileID: %s}\n%s' % (NEW_TRANSFORM, marker))

    # ---- 2) PrefabInstance 登记 m_AddedComponents ----
    pi_body = by[DIZI_PREFAB_INSTANCE]['body']
    added = (
        '    m_AddedComponents:\n'
        '    - targetCorrespondingSourceObject: {fileID: %s, guid: %s, type: 3}\n'
        '      insertIndex: -1\n'
        '      addedObject: {fileID: %s}\n'
        '    m_RemovedComponents: []\n'
    ) % (DIZI_SRC_ROOT_GO, DIZI_PREFAB_GUID, NEW_COMPONENT)
    old_tail = '    m_RemovedComponents: []\n'
    if pi_body.count(old_tail) != 1:
        sys.exit('!! PrefabInstance 的 m_RemovedComponents 定位失败，停止')
    new_pi_body = pi_body.replace(old_tail, added)

    # ---- 应用替换（每处都要求唯一命中）----
    for old, new, label in ((npc_body, new_npc_body, 'NPC.m_Children'),
                            (pi_body, new_pi_body, 'PrefabInstance.m_AddedComponents')):
        if text.count(old) != 1:
            sys.exit('!! %s 替换点不唯一 (%d 处)，停止' % (label, text.count(old)))
        text = text.replace(old, new, 1)

    if not text.endswith('\n'):
        text += '\n'
    text += build_gameobject(NEW_GO, NEW_TRANSFORM, NPC_TRANSFORM, 7, ('32', '0', '12.9'))
    text += build_component(NEW_COMPONENT, DIZI_GO, NEW_TRANSFORM)

    print('锚点 "弟子让路点"  -> GameObject %s / Transform %s  pos (32, 0, 12.9)  父=NPC'
          % (NEW_GO, NEW_TRANSFORM))
    print('FixWithGameRuntime -> MonoBehaviour %s  挂在弟子 %s 上' % (NEW_COMPONENT, DIZI_GO))
    print('Flag   = 重阳宫大门弟子让路')
    print('MoveTo = 弟子让路点 Transform %s' % NEW_TRANSFORM)

    if dry:
        print('\n[dry-run] 未写入')
        return

    old_len = os.path.getsize(SCENE)
    with io.open(SCENE, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
        f.write(text)
    print('\n文件 %d -> %d 字节' % (old_len, os.path.getsize(SCENE)))
    print('已写入 %s' % SCENE)


if __name__ == '__main__':
    main()

