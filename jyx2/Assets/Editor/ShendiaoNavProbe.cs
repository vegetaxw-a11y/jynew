using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;

/// <summary>
/// 神雕 MOD 场景 NavMesh 探针。
///
/// 为什么需要它：玩家寻路完全走 NavMesh（Jyx2_PlayerAutoWalk.PlayerWarkFromTo
/// 里 SamplePosition 失败就直接 return，表现为"点地面不动" = 空气墙）。
/// NavMesh.asset 是二进制，Python 读不了，只能让 Unity 自己报。
///
/// 用法（batchmode）：
///   Unity.exe -batchmode -quit -projectPath jyx2 ^
///     -executeMethod ShendiaoNavProbe.Probe -logFile Logs/nav.log
///
/// 输出：C:/Games/jynew/_nav.txt（UTF-8）
/// 场景/关键点改这里，不要在外面写死另一份。
/// </summary>
public static class ShendiaoNavProbe
{
    const string ScenePath = "Assets/Mods/shendiao/Maps/GameMaps/19_chongyanggong.unity";
    const string OutPath = "C:/Games/jynew/_nav.txt";

    // 关键点：label -> 世界坐标
    static readonly (string label, Vector3 p)[] Points =
    {
        ("弟子位(32.3,11.4)",   new Vector3(32.3f, 0f, 11.4f)),
        ("玩家交互位(33.5,11.4)", new Vector3(33.5f, 0f, 11.4f)),
        ("墙缺口(31.6,11.5)",   new Vector3(31.6f, 0f, 11.5f)),
        ("缺口西侧(30.5,11.5)", new Vector3(30.5f, 0f, 11.5f)),
        ("宫内深处(28,11)",     new Vector3(28.0f, 0f, 11.0f)),
        ("Leave处(36.6,11.5)",  new Vector3(36.6f, 0f, 11.5f)),
        ("场景中心(18,8)",      new Vector3(18.0f, 0f, 8.0f)),
    };

    public static void Probe()
    {
        var sb = new StringBuilder();
        sb.AppendLine("=== ShendiaoNavProbe ===");
        sb.AppendLine("scene: " + ScenePath);

        var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        sb.AppendLine("loaded: " + scene.name + "  rootCount=" + scene.rootCount);

        // 1) area 索引（Unity 2020.3 没有 NavMesh.GetAreaName，只能按名字反查）
        sb.AppendLine();
        sb.AppendLine("=== NavMesh Areas ===");
        foreach (var nm in new[] { "Walkable", "Not Walkable", "Jump" })
            sb.AppendLine(string.Format("  {0,-14} = {1}", nm, NavMesh.GetAreaFromName(nm)));
        int walkableIdx = NavMesh.GetAreaFromName("Walkable");
        sb.AppendLine("Walkable index = " + walkableIdx);

        // 2) 三角化：确认 NavMesh 真的加载了、覆盖到哪
        var tri = NavMesh.CalculateTriangulation();
        sb.AppendLine();
        sb.AppendLine("=== Triangulation ===");
        sb.AppendLine(string.Format("vertices={0} indices={1} areas={2}",
            tri.vertices.Length, tri.indices.Length, tri.areas.Length));

        if (tri.vertices.Length > 0)
        {
            var min = tri.vertices[0];
            var max = tri.vertices[0];
            foreach (var v in tri.vertices)
            {
                min = Vector3.Min(min, v);
                max = Vector3.Max(max, v);
            }
            sb.AppendLine(string.Format("bounds min=({0:F2},{1:F2},{2:F2}) max=({3:F2},{4:F2},{5:F2})",
                min.x, min.y, min.z, max.x, max.y, max.z));

            var hist = new Dictionary<int, int>();
            foreach (var a in tri.areas)
                hist[a] = hist.TryGetValue(a, out var c) ? c + 1 : 1;
            foreach (var kv in hist)
                sb.AppendLine(string.Format("  area[{0}] = {1} tris", kv.Key, kv.Value));
        }
        else
        {
            sb.AppendLine("!! 三角化为空 —— 场景 NavMesh 根本没加载 / 已丢失");
        }

        // 3) 逐点采样（AllAreas 与 Walkable 对比，能区分"没网格"和"网格被标成不可走"）
        sb.AppendLine();
        sb.AppendLine("=== SamplePosition (radius 5) ===");
        foreach (var (label, p) in Points)
        {
            bool okAll = NavMesh.SamplePosition(p, out var hAll, 5f, NavMesh.AllAreas);
            bool okWalk = NavMesh.SamplePosition(p, out var hWalk, 5f, 1 << walkableIdx);
            sb.AppendLine(string.Format("{0,-24} AllAreas={1}  Walkable={2}",
                label,
                okAll ? string.Format("hit({0:F2},{1:F2},{2:F2}) d={3:F2} mask={4}", hAll.position.x, hAll.position.y, hAll.position.z, hAll.distance, hAll.mask) : "MISS",
                okWalk ? string.Format("hit{0:F2}", hWalk.distance) : "MISS"));
        }

        // 4) 连通性：这是"空气墙"的判定依据
        sb.AppendLine();
        sb.AppendLine("=== CalculatePath (from 玩家交互位, Walkable) ===");
        var from = new Vector3(33.5f, 0f, 11.4f);
        foreach (var (label, p) in Points)
        {
            var path = new NavMeshPath();
            bool calc = NavMesh.CalculatePath(from, p, 1 << walkableIdx, path);
            sb.AppendLine(string.Format("{0,-24} calc={1} status={2} corners={3}",
                label, calc, path.status, path.corners.Length));
        }

        // 5) 反向也测一遍（宫内 -> 门口），确认是不是单向断
        sb.AppendLine();
        sb.AppendLine("=== CalculatePath (from 宫内深处, Walkable) ===");
        var back = new Vector3(28.0f, 0f, 11.0f);
        foreach (var (label, p) in Points)
        {
            var path = new NavMeshPath();
            bool calc = NavMesh.CalculatePath(back, p, 1 << walkableIdx, path);
            sb.AppendLine(string.Format("{0,-24} calc={1} status={2} corners={3}",
                label, calc, path.status, path.corners.Length));
        }

        File.WriteAllText(OutPath, sb.ToString(), new UTF8Encoding(false));
        Debug.Log("[ShendiaoNavProbe] written to " + OutPath);
    }

    /// <summary>
    /// 验证鹿清笃的"让路"装配：FixWithGameRuntime 是否挂上了、Flag/MoveTo 对不对、
    /// NavMeshObstacle 的 carve 是否已关掉（carve=1 会在运行时把山门缺口的 NavMesh 挖穿，
    /// 表现为"空气墙"）。
    /// 用法：-executeMethod ShendiaoNavProbe.VerifyLetway
    /// </summary>
    public static void VerifyLetway()
    {
        var sb = new StringBuilder();
        sb.AppendLine("=== VerifyLetway ===");
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        var npc = GameObject.Find("Level/NPC/QZhenDiZi");
        sb.AppendLine("Level/NPC/QZhenDiZi found = " + (npc != null));
        if (npc != null)
        {
            sb.AppendLine("  worldPos = " + npc.transform.position);
            foreach (var c in npc.GetComponents<Component>())
            {
                if (c == null) continue;
                sb.AppendLine("  comp: " + c.GetType().Name);

                var fix = c as FixWithGameRuntime;
                if (fix != null)
                {
                    sb.AppendLine("     Flag   = " + fix.Flag);
                    sb.AppendLine("     MoveTo = " + (fix.MoveTo == null
                        ? "NULL (会让 Reload 报错)"
                        : fix.MoveTo.name + " @ " + fix.MoveTo.position));
                }

                var obs = c as NavMeshObstacle;
                if (obs != null)
                {
                    sb.AppendLine("     carving = " + obs.carving + "   (必须 False，True 会在运行时挖穿 NavMesh)");
                    sb.AppendLine("     shape   = " + obs.shape);
                    sb.AppendLine("     size    = " + obs.size + "  center = " + obs.center);
                }
            }
        }

        sb.AppendLine();
        var anchor = GameObject.Find("Level/NPC/弟子让路点");
        sb.AppendLine("Level/NPC/弟子让路点 found = " + (anchor != null));
        if (anchor != null) sb.AppendLine("  worldPos = " + anchor.transform.position);

        sb.AppendLine();
        var trig = GameObject.Find("Level/Triggers/1");
        sb.AppendLine("Level/Triggers/1 found = " + (trig != null));
        if (trig != null)
        {
            sb.AppendLine("  worldPos = " + trig.transform.position);
            var fix = trig.GetComponent<FixWithGameRuntime>();
            if (fix != null)
            {
                sb.AppendLine("  FixWithGameRuntime Flag = " + fix.Flag);
                sb.AppendLine("  MoveTo = " + (fix.MoveTo == null ? "NULL" : fix.MoveTo.name + " @ " + fix.MoveTo.position));
            }
            var ge = trig.GetComponent<GameEvent>();
            if (ge != null)
                sb.AppendLine("  GameEvent: interactive=" + ge.m_InteractiveEventId
                              + " enter=" + ge.m_EnterEventId
                              + " targets=" + (ge.m_EventTargets == null ? 0 : ge.m_EventTargets.Length));
        }

        File.WriteAllText("C:/Games/jynew/_letway.txt", sb.ToString(), new UTF8Encoding(false));
        Debug.Log("[ShendiaoNavProbe] VerifyLetway written");
    }
}
