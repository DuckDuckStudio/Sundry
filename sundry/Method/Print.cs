namespace sundry.Method
{
    internal class Print
    {
        public static void PrintKey(string Key, string Value)
        {
            Console.Write(Key + ": ");
            Console.ForegroundColor = ConsoleColor.Blue;
            Console.WriteLine(Value);
            Console.ResetColor();
        }

        public static void PrintError(string Error)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine("✕" + Error);
            Console.ResetColor();
        }

        public static void PrintWarning(string Warning)
        {
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine("⚠" + Warning);
            Console.ResetColor();
        }

        public static void PrintInfo(string Info, bool ask=false)
        {
            Console.ForegroundColor = ConsoleColor.Blue;
            if (ask)
            {
                Console.Write("?" + Info); // 不换行
            }
            else
            {
                Console.WriteLine("[!]" + Info);
            }
            Console.ResetColor();
        }

        public static void PrintSuccess(string Success)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine("✓" + Success);
            Console.ResetColor();
        }

        public static void PrintLog(string Log, ConsoleColor color=ConsoleColor.Blue)
        {
            Console.ForegroundColor = color;
            Console.WriteLine(Log);
            Console.ResetColor();
        }
    }
}
