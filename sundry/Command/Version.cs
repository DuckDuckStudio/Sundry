using sundry.Method;

namespace sundry.Command
{
    internal class Version
    {
        public static void Show(string Version)
        {
            Print.PrintKey("版本", Version);
            Print.PrintKey("作者", "鸭鸭「カモ」");
            Print.PrintKey("许可证", "GNU Affero General Public License v3.0");
            Print.PrintKey("如需获取更多信息，请使用", "sundry about");
        }
    }
}
