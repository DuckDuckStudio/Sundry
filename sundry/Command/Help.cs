namespace sundry.Command
{
    internal class Help
    {
        public static void Show()
        {
            Console.WriteLine("Sundry 使用帮助");
            Console.WriteLine("移除软件包版本: sundry remove [软件包标识符] [软件包版本] [跳过检查(只接受true)/ 理由(默认为GitHub Action中返回404)]");
            // Console.WriteLine("修改检测忽略字段: sundry ignore [add / remove / list] [忽略字段] [理由]");
            Console.WriteLine("同步本地仓库(master 分支): sundry sync");
            Console.WriteLine("修改 Sundry 配置:");
            Console.WriteLine("    初始化: sundry config init");
            Console.WriteLine("    修改值: sundry config [条目] [值]");
            Console.WriteLine("其他辅助命令:");
            // Console.WriteLine("    多版本辅助修改: sundry change");
            // Console.WriteLine("    新版本辅助修改: sundry new");
            Console.WriteLine("    查看清单: sundry cat");
            Console.WriteLine("    同步本地: sundry sync");
            Console.WriteLine("其他 Sundry 命令:");
            Console.WriteLine("    查看版本: sundry ver");
            Console.WriteLine("    查看帮助: sundry help");
        }
    }
}
