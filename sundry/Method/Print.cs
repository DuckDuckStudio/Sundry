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
    }
}
