using sundry.Command;

namespace sundry
{
    internal class Program
    {
        public const string Version = "develop";

        static async Task Main(string[] args)
        {
            string configFilePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".config", "DuckStudio", "Sundry", "config.json");
            if (args.Length > 0)
            {
                switch (args[0].ToLowerInvariant()) // 开头的命令不区分大小写
                {
                    case "v":
                    case "--version":
                    case "ver":
                    case "version":
                    case "-v":
                        Command.Version.Show(Version);
                        break;
                    case "about":
                        About.Show(Version);
                        break;
                    case "help":
                    case "--help":
                    case "-h":
                        Help.Show();
                        break;
                    // -------------------
                    case "repr":
                        // 判断是文件路径还是文本内容
                        if (args.Length == 2 && File.Exists(args[1]))
                        {
                            // 处理文件
                            Repr.ReprFile(args[1]);
                        }
                        else if (args.Length == 2)
                        {
                            // 处理文本
                            Repr.ReprText(args[1]);
                        }
                        else
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine("✕ 请提供文件路径或文本内容");
                            Console.ResetColor();
                        }
                        break;
                    case "config":
                        if (args.Length < 2)
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine("✕ 缺少参数");
                            Console.ForegroundColor = ConsoleColor.Blue;
                            Console.WriteLine("[!] 运行 sundry --help 来获取命令帮助");
                            Console.ResetColor();
                            Environment.Exit(2);
                        }

                        if (args[1] == "init")
                        {
                            await Config.InitConfigFile(configFilePath);
                        }
                        else if (args[1] == "show")
                        {
                            Config.ShowConfigFile(configFilePath);
                        }
                        else if (args.Length == 4)
                        {
                            string entry = args[2];
                            string value = args[3];
                            Config.ModifyConfigEntry(configFilePath, entry, value);
                        }
                        else
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine($"✕ 无效的操作: {args[1]}");
                            Console.ForegroundColor = ConsoleColor.Blue;
                            Console.WriteLine("[!] 运行 sundry --help 来获取命令帮助");
                            Console.ResetColor();
                            Environment.Exit(2);
                        }
                        break;

                    // ...更多命令...

                    default:
                        Console.ForegroundColor = ConsoleColor.Red;
                        Console.WriteLine("无效的命令。");
                        Console.ResetColor();
                        break;
                }
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("请提供一个命令。");
                Console.ResetColor();
            }
        }
    }
}
