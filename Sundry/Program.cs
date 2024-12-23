using System.Net.Http.Json;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

/*
Sundry (c) 2024 by 鸭鸭「カモ」 is licensed under CC BY-NC 4.0.
To view a copy of this license, visit https://creativecommons.org/licenses/by-nc/4.0/
*/

namespace Sundry
{
    internal class Program
    {
        private static readonly HttpClient client = new();
        private static readonly string token = Environment.GetEnvironmentVariable("TOKEN") ?? string.Empty;
        private static readonly List<string> IGNORED_PACKAGE = ["xxx"];
        private static readonly List<int> EXCLUDED_CODE = [429];

        static async Task Main(string[] args)
        {
            if (args.Length < 1)
            {
                throw new Exception("[ERROR] 请提供要扫描的 manifests 子目录。");
            }
            string subdirectory = args[0];

            // 全局搜索 winget-pkgs 文件夹
            var origin = new List<DirectoryInfo>();
            var currentDir = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
            while (currentDir != null)
            {
                origin.AddRange(currentDir.GetDirectories().Where(d => d.Name.Contains("winget-pkgs")));
                if (origin.Count > 0) break;
                currentDir = currentDir.Parent;
            }
            if (origin.Count == 0)
            {
                throw new Exception("[ERROR] 找不到 winget-pkgs 文件夹");
            }
            var folder = new DirectoryInfo(Path.Combine(origin[0].FullName, "manifests", subdirectory));
            Console.WriteLine($"[INFO] 在 {folder.FullName} 找到了文件夹");

            // 扫描
            await Scanner(folder);
        }

        private static async Task Scanner(DirectoryInfo path)
        {
            var tasks = new List<Task>();
            foreach (var each in path.GetFileSystemInfos())
            {
                if (each is DirectoryInfo dir)
                {
                    tasks.Add(Scanner(dir));
                }
                else if (each is FileInfo file && file.Name.EndsWith(".installer.yaml"))
                {
                    tasks.Add(Task.Run(async () =>
                    {
                        var deserializer = new DeserializerBuilder()
                            .WithNamingConvention(CamelCaseNamingConvention.Instance)
                            .Build();
                        var yaml = deserializer.Deserialize<Dictionary<string, object>>(await File.ReadAllTextAsync(file.FullName));
                        await Scan(yaml);
                    }));
                }
            }
            await Task.WhenAll(tasks);
        }

        private static async Task Scan(Dictionary<string, object> yaml)
        {
            string id = yaml["PackageIdentifier"]?.ToString() ?? string.Empty;
            string version = yaml["PackageVersion"]?.ToString() ?? string.Empty;
            int error = 0;

            if (IGNORED_PACKAGE.Any(id.Contains))
            {
                Console.WriteLine($"[WARNING] 跳过 {id}(版本 {version})");
                return;
            }

            try
            {
                if (yaml["Installers"] is not List<object> installers)
                {
                    Console.WriteLine($"[ERROR] {id}(版本 {version}) 的 Installers 字段为空");
                    return;
                }

                foreach (var each in installers.Cast<Dictionary<string, object>>())
                {
                    Console.WriteLine($"[INFO] 开始检查 {id}(版本 {version})");
                    string installerUrl = each["InstallerUrl"]?.ToString() ?? string.Empty;
                    HttpResponseMessage response;

                    try
                    {
                        response = await client.SendAsync(new HttpRequestMessage(HttpMethod.Head, installerUrl), HttpCompletionOption.ResponseHeadersRead);
                        if ((int)response.StatusCode >= 400 && !EXCLUDED_CODE.Contains((int)response.StatusCode))
                        {
                            error++;
                        }
                        else if ((int)response.StatusCode >= 300 && (int)response.StatusCode < 400)
                        {
                            Console.WriteLine($"[WARNING] 收到 {installerUrl} 的 {(int)response.StatusCode} 状态码，使用 GET 请求跟随重定向");
                            response = await client.GetAsync(installerUrl, HttpCompletionOption.ResponseHeadersRead);
                            if ((int)response.StatusCode >= 400 && !EXCLUDED_CODE.Contains((int)response.StatusCode))
                            {
                                error++;
                            }
                        }
                    }
                    catch (HttpRequestException)
                    {
                        Console.WriteLine($"[INFO] HEAD 请求失败，使用 GET 请求重试 {installerUrl}");
                        try
                        {
                            response = await client.GetAsync(installerUrl, HttpCompletionOption.ResponseHeadersRead);
                            if ((int)response.StatusCode >= 400 && !EXCLUDED_CODE.Contains((int)response.StatusCode))
                            {
                                error++;
                            }
                        }
                        catch (HttpRequestException)
                        {
                            Console.WriteLine($"[INFO] GET 请求也失败了 {installerUrl}");
                            error++;
                        }
                    }
                }

                if (error == installers.Count)
                {
                    string command = $"komac remove --identifier {id} --version {version} --reason 'It returns code over 400 in all urls' --submit --token {token}";
                    string url = "https://api.github.com/repos/microsoft/winget-pkgs/pulls";
                    client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("token", token);
                    client.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("application/vnd.github.v3+json"));
                    var response = await client.GetAsync($"{url}?state=open&base=master");
                    response.EnsureSuccessStatusCode();
                    var pulls = await response.Content.ReadFromJsonAsync<List<Dictionary<string, object>>>();
                    if (pulls != null && pulls.Any(pr => pr["title"] != null && pr["title"]?.ToString()?.Contains(id) == true && pr["title"]?.ToString()?.Contains(version) == true))
                    {
                        var existingPr = pulls.FirstOrDefault(pr => pr["title"] != null && pr["title"]?.ToString()?.Contains(id) == true && pr["title"]?.ToString()?.Contains(version) == true);
                        if (existingPr != null)
                        {
                            Console.WriteLine($"[WARNING] 找到现有的 PR {id} {version} - {existingPr["html_url"]}");
                        }
                    }
                    else
                    {
                        //await Task.Run(() => System.Diagnostics.Process.Start("pwsh", $"-Command {command}"));
                        Console.WriteLine($"[ERROR] {id}(版本 {version}) 检查失败（返回错误代码），运行 {command} 以移除它");
                        // 以退出代码 404 直接结束程序
                        Environment.Exit(404);
                    }
                    //Console.WriteLine($"[INFO] {id}(版本 {version}) 检查失败（返回错误代码），运行 {command} 以移除它");
                }
                else
                {
                    Console.WriteLine($"[INFO] {id}(版本 {version}) 检查成功");
                }
            }
            catch (Exception e)
            {
                Console.WriteLine($"[ERROR] {id} 检查失败: {e}");
            }
        }
    }
}
