using sundry.Method;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace sundry.Command
{
    internal class Config
    {
        // 初始化配置文件
        public static async Task InitConfigFile(string configFilePath)
        {
            if (!File.Exists(configFilePath) || AskToOverwrite())
            {
                var defaultConfig = new
                {
                    version = "develop",
                    winget_pkgs = "",
                    winget_tools = "",
                    fork = "",
                    signature = false
                };

                var config = defaultConfig;

                // 获取 winget-pkgs
                while (true)
                {
                    Console.ForegroundColor = ConsoleColor.Blue;
                    Console.Write("? 您的本地 winget-");
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    Console.WriteLine("pkgs 仓库在哪里: ");
                    Console.ResetColor();
                    string? wingetPkgs = Console.ReadLine()?.Replace("\\", "/");
                    if (Directory.Exists(wingetPkgs))
                    {
                        config = new { config.version, winget_pkgs = wingetPkgs, config.winget_tools, config.fork, config.signature };
                        break;
                    }
                    else
                    {
                        Print.PrintError("指定的路径不存在");
                    }
                }

                // 获取 winget-tools
                while (true)
                {
                    Console.ForegroundColor = ConsoleColor.Blue;
                    Console.Write("? 您的本地 winget-");
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    Console.WriteLine("tools 仓库在哪里: ");
                    Console.ResetColor();
                    string? wingetTools = Console.ReadLine()?.Replace("\\", "/");
                    if (Directory.Exists(wingetTools))
                    {
                        config = new { config.version, config.winget_pkgs, winget_tools = wingetTools, config.fork, config.signature };
                        break;
                    }
                    else
                    {
                        Print.PrintError("指定的路径不存在");
                    }
                }

                // 获取 fork 仓库
                while (true)
                {
                    Print.PrintInfo("您的 winget-pkgs 仓库的 fork 仓库是什么: ", true);
                    string? fork = Console.ReadLine();

                    // 定义一个 GitHub 仓库 URL 正则表达式，用来验证 URL 是否有效
                    string githubUrlPattern = @"^(https://github\.com/)?(?<owner>[^/]+)/(?<repo>[^/]+)(\.git)?$";
                    Regex regex = new(githubUrlPattern);

                    if (!string.IsNullOrWhiteSpace(fork))
                    {
                        // 如果是相对路径格式（owner/repo），则添加 GitHub 的前缀
                        if (!fork.StartsWith("https://github.com/"))
                        {
                            fork = "https://github.com/" + fork;
                        }

                        Match match = regex.Match(fork);

                        if (match.Success)
                        {
                            string owner = match.Groups["owner"].Value;
                            string repo = match.Groups["repo"].Value;

                            // 构造 API URL
                            string apiUrl = $"https://api.github.com/repos/{owner}/{repo}";

                            // 调用 GitHub API
                            HttpClient client = new();
                            client.DefaultRequestHeaders.Add("User-Agent", "Sundry");
                            HttpResponseMessage response = await client.GetAsync(apiUrl);

                            if (response.IsSuccessStatusCode)
                            {
                                config = new { config.version, config.winget_pkgs, config.winget_tools, fork, config.signature };
                                break;
                            }
                            else
                            {
                                Print.PrintError("指定的 fork 仓库不存在或没有权限访问");
                            }
                        }
                        else
                        {
                            Print.PrintError("请输入正确的 fork 仓库格式，例如: owner/repo");
                        }
                    }
                    else
                    {
                        Print.PrintError("请输入正确的 fork 仓库格式，例如: owner/repo");
                    }
                }

                // 获取 Git 提交签名
                Console.ForegroundColor = ConsoleColor.Blue;
                Console.Write("? 是否要为 Git 提交签名: (默认为");
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("否): ");
                Console.ResetColor();
                string? signInput = Console.ReadLine()?.ToLower();
                bool signature = signInput == "y" || signInput == "yes" || signInput == "要" || signInput == "是";

                config = new { config.version, config.winget_pkgs, config.winget_tools, config.fork, signature };

                // 写入配置文件
                JsonSerializerOptions options = new() { WriteIndented = true, Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
                await File.WriteAllTextAsync(configFilePath, JsonSerializer.Serialize(config, options));

                Print.PrintSuccess("成功初始化配置文件");
            }
        }

        // 展示配置文件
        public static void ShowConfigFile(string configFilePath)
        {
            if (File.Exists(configFilePath))
            {
                try
                {
                    string configContent = File.ReadAllText(configFilePath);
                    string formattedJson = JsonSerializer.Serialize(JsonSerializer.Deserialize<object>(configContent), new JsonSerializerOptions { WriteIndented = true });
                    Console.WriteLine(formattedJson);
                }
                catch (JsonException e)
                {
                    Print.PrintError($"读取配置文件失败，配置文件不是有效的 json 字段:\n{e.Message}");
                    Print.PrintInfo("请考虑运行 sundry config init 来覆盖现有的配置文件");
                }
            }
            else
            {
                Print.PrintError("配置文件不存在");
                Print.PrintInfo("运行 sundry config init 来初始化配置文件");
            }
        }

        // 修改配置文件中的某一项
        public static void ModifyConfigEntry(string configFilePath, string entry, string value)
        {
            if (File.Exists(configFilePath))
            {
                try
                {
                    string json = File.ReadAllText(configFilePath);
                    JsonObject? jsonObject = JsonSerializer.Deserialize<JsonObject>(json);
                    if (jsonObject != null)
                    {
                        jsonObject[entry] = value;
                        File.WriteAllText(configFilePath, jsonObject.ToString());
                        Print.PrintSuccess($"成功更新 {entry} 为 {value}");
                    }
                    else
                    {
                        Print.PrintError("更新条目失败: 配置文件内容为空");
                    }
                }
                catch (JsonException e)
                {
                    Print.PrintError($"更新条目失败: \n{e.Message}");
                }
            }
            else
            {
                Print.PrintError("配置文件不存在");
                Print.PrintInfo("运行 sundry config init 来初始化配置文件");
            }
        }

        // 确认是否覆盖配置文件
        private static bool AskToOverwrite()
        {
            Print.PrintWarning("已经存在了一份配置文件，要覆盖它吗: ");
            string? input = Console.ReadLine()?.ToLower();
            return input == "y" || input == "yes" || input == "要" || input == "覆盖" || input == "force";
        }
    }
}
