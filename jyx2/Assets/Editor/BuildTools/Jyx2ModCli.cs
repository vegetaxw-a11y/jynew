using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Editor;
using Jyx2.MOD.ModV2;
using UnityEditor;
using UnityEngine;
using Tools = Jyx2.Middleware.Tools;

namespace Jyx2Editor.BuildTool
{
    /// <summary>
    /// MOD 导出的命令行入口，供 tools/moddev/jyx2mod.py 的 unity 子命令调用：
    ///
    /// Unity.exe -batchmode -nographics -quit -projectPath &lt;jyx2&gt; -executeMethod
    /// Jyx2Editor.BuildTool.Jyx2ModCli.BuildMod -modId mymod -exportPath D:\Export -buildTarget StandaloneWindows64
    ///
    /// 做的事情和 "Game Tools/Mod导出" 窗口一致：生成配置表 Lua -> 写 &lt;id&gt;.xml ->
    /// 打包 base_assets + &lt;id&gt;_mod + &lt;id&gt;_maps -> 把本 MOD 的包挪进 &lt;exportPath&gt;/&lt;id&gt;/。
    /// </summary>
    public static class Jyx2ModCli
    {
        private const string BaseBundleName = "base_assets";
        private const string ModsAssetRoot = "Assets/Mods";

        /// <summary>Unity -executeMethod 入口</summary>
        public static void BuildMod()
        {
            var exitCode = 1;
            try
            {
                Run();
                exitCode = 0;
            }
            catch (Exception e)
            {
                Debug.LogError($"[Jyx2ModCli] MOD 导出失败：{e}");
            }

            if (Application.isBatchMode)
            {
                EditorApplication.Exit(exitCode);
            }
        }

        private static void Run()
        {
            var modId = (GetArgument("-modId") ?? string.Empty).Trim().ToLower();
            if (string.IsNullOrEmpty(modId))
            {
                throw new ArgumentException("缺少 -modId 参数");
            }

            var target = ParseBuildTarget(GetArgument("-buildTarget"));
            var exportPath = ResolveExportPath(GetArgument("-exportPath"));

            var config = FindModConfig(modId);
            if (config == null)
            {
                throw new FileNotFoundException($"在 {ModsAssetRoot} 下找不到 ModId 为 {modId} 的 ModSetting.asset");
            }

            var allBundles = AssetDatabase.GetAllAssetBundleNames().ToList();
            if (!allBundles.Contains(BaseBundleName))
            {
                throw new FileNotFoundException($"未找到基础资源包 {BaseBundleName}，无法导出（请检查 AssetBundle 标记）");
            }

            var modBundleName = $"{modId}_mod";
            var mapBundleName = $"{modId}_maps";
            foreach (var bundleName in new[] {modBundleName, mapBundleName})
            {
                if (!allBundles.Contains(bundleName))
                {
                    throw new FileNotFoundException(
                        $"未找到资源包 {bundleName}，请把 {modId} 的资源标记到名为 {bundleName} 的 AssetBundle 里");
                }
            }

            Directory.CreateDirectory(exportPath);

            // 生成配置表 Lua（等价于编辑器里点"生成配置表"按钮）
            config.GenerateConfigs();

            // 先生成 <id>.xml，内容和游戏里手动安装读取的一致
            var modFolder = Path.Combine(exportPath, modId);
            Directory.CreateDirectory(modFolder);
            var modInfo = JynewBuilder.CreateModInfo(config, target);
            var xmlPath = Path.Combine(modFolder, modId + ".xml");
            File.WriteAllText(xmlPath, Tools.SerializeXML(modInfo));
            Debug.Log($"[Jyx2ModCli] 写出 {xmlPath}");

            var builds = new List<AssetBundleBuild>();
            if (IsTruthy(GetArgument("-skipBase")))
            {
                // base_assets 是游戏本体的资源包，游戏运行时从 StreamingAssets 里读，导出目录里这份
                // 只有"改了本体资源、需要连 base_assets 一起分发"时才有意义。
                // 跳过它能省掉约 1.8GB 的序列化 + 压缩，是打包提速的主要来源。
                Debug.Log($"[Jyx2ModCli] 跳过 {BaseBundleName}（未检测到变化）");
            }
            else
            {
                builds.Add(CreateBundleBuild(BaseBundleName));
            }
            builds.Add(CreateBundleBuild(modBundleName));
            builds.Add(CreateBundleBuild(mapBundleName));

            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            var manifest = BuildPipeline.BuildAssetBundles(exportPath, builds.ToArray(),
                BuildAssetBundleOptions.ChunkBasedCompression, target);
            if (manifest == null)
            {
                throw new Exception("BuildPipeline.BuildAssetBundles 失败，请查看上面的 Unity 日志");
            }
            Debug.Log($"[Jyx2ModCli] AssetBundle 构建耗时 {stopwatch.Elapsed.TotalSeconds:F1} 秒");

            stopwatch.Restart();
            MoveModBundlesToModFolder(exportPath, modFolder, modId);
            Debug.Log($"[Jyx2ModCli] 归档耗时 {stopwatch.Elapsed.TotalSeconds:F1} 秒");
            Debug.Log($"[Jyx2ModCli] 导出完成：{modFolder}");
        }

        private static AssetBundleBuild CreateBundleBuild(string bundleName)
        {
            var assetPaths = AssetDatabase.GetAssetPathsFromAssetBundle(bundleName)
                .Where(path => Path.GetExtension(path) != ".cs")
                .ToArray();
            if (assetPaths.Length == 0)
            {
                Debug.LogWarning($"[Jyx2ModCli] AssetBundle {bundleName} 里没有资源");
            }

            Debug.Log($"[Jyx2ModCli] 打包 {bundleName}（{assetPaths.Length} 个资源）");
            return new AssetBundleBuild
            {
                assetBundleName = bundleName,
                assetNames = assetPaths,
            };
        }

        private static void MoveModBundlesToModFolder(string exportPath, string modFolder, string modId)
        {
            foreach (var file in Directory.GetFiles(exportPath, "*" + modId + "*", SearchOption.TopDirectoryOnly))
            {
                var destination = Path.Combine(modFolder, Path.GetFileName(file));
                if (File.Exists(destination))
                {
                    File.Delete(destination);
                }

                File.Move(file, destination);
            }
        }

        private static MODRootConfig FindModConfig(string modId)
        {
            foreach (var guid in AssetDatabase.FindAssets("t:MODRootConfig", new[] {ModsAssetRoot}))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var config = AssetDatabase.LoadAssetAtPath<MODRootConfig>(path);
                if (config != null && string.Equals(config.ModId, modId, StringComparison.OrdinalIgnoreCase))
                {
                    return config;
                }
            }

            return null;
        }

        private static string ResolveExportPath(string exportPath)
        {
            var projectRoot = Directory.GetParent(Application.dataPath)?.Parent?.FullName ?? Application.dataPath;
            if (string.IsNullOrEmpty(exportPath))
            {
                exportPath = Path.Combine(projectRoot, "Export");
            }

            return Path.GetFullPath(Path.IsPathRooted(exportPath) ? exportPath : Path.Combine(projectRoot, exportPath));
        }

        private static BuildTarget ParseBuildTarget(string value)
        {
            switch ((value ?? string.Empty).Trim().ToLower())
            {
                case "android":
                    return BuildTarget.Android;
                case "ios":
                    return BuildTarget.iOS;
                case "macos":
                case "mac":
                case "standaloneosx":
                    return BuildTarget.StandaloneOSX;
                default:
                    return BuildTarget.StandaloneWindows64;
            }
        }

        private static bool IsTruthy(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                return false;
            }

            switch (value.Trim().ToLower())
            {
                case "1":
                case "true":
                case "yes":
                case "on":
                    return true;
                default:
                    return false;
            }
        }

        private static string GetArgument(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i < args.Length - 1; i++)
            {
                if (string.Equals(args[i], name, StringComparison.OrdinalIgnoreCase))
                {
                    return args[i + 1];
                }
            }

            return null;
        }
    }
}
