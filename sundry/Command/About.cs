using sundry.Method;

namespace sundry.Command
{
    internal class About
    {
        public static void Show(string Version)
        {
            Print.PrintKey("版本", Version);
            Print.PrintKey("作者", "鸭鸭「カモ」");
            Print.PrintKey("许可证", "GNU Affero General Public License v3.0");
            Print.PrintKey("您可以在这里找到许可证", "https://github.com/DuckDuckStudio/Sundry/blob/main/LICENSE");
            Print.PrintKey("仓库", "https://github.com/DuckDuckStudio/Sundry/");
            Print.PrintKey("建议与反馈", "https://github.com/DuckDuckStudio/Sundry/issues");
        }
    }
}
