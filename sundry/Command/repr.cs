using System.Text;

namespace sundry.Command
{
    public class Repr
    {
        public static int ReprFile(string path, string encode = "utf-8")
        {
            try
            {
                // 根据编码读取文件内容
                Encoding encoding = Encoding.GetEncoding(encode);
                string content = File.ReadAllText(path, encoding);

                // 输出文本的 repr 形式
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine(GetRepr(content));
                Console.ResetColor();
                return 0;
            }
            catch (UnauthorizedAccessException)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("✕ 没有权限");
                Console.ResetColor();
                return 1;
            }
            catch (FileNotFoundException)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("✕ 文件不存在");
                Console.ResetColor();
                return 1;
            }
            catch (ArgumentException e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"✕ 编码错误: {e.Message}");
                Console.ResetColor();
                return 1;
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"✕ 未知错误: {e.Message}");
                Console.ResetColor();
                return 1;
            }
        }

        public static int ReprText(string text, string encode = "utf-8")
        {
            try
            {
                // 将文本编码为字节数组并输出 repr 形式
                Encoding encoding = Encoding.GetEncoding(encode);
                byte[] encodedBytes = encoding.GetBytes(text);

                // 输出文本的 repr 形式
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine(GetRepr(text)); // 直接将文本传给 GetRepr
                Console.ResetColor();
                return 0;
            }
            catch (ArgumentException e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"✕ 编码错误: {e.Message}");
                Console.ResetColor();
                return 1;
            }
            catch (Exception e)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"✕ 未知错误: {e.Message}");
                Console.ResetColor();
                return 1;
            }
        }

        // 生成 repr 输出
        private static string GetRepr(string str)
        {
            // 对字符串中的特殊字符进行转义处理
            StringBuilder result = new("\"");

            foreach (char c in str)
            {
                // 如果是需要转义的字符
                switch (c)
                {
                    case '\"': result.Append("\\\""); break;
                    case '\n': result.Append("\\n"); break;
                    case '\r': result.Append("\\r"); break;
                    case '\t': result.Append("\\t"); break;
                    default:
                        // 对其他不可见字符（如 ASCII 控制字符）进行转义
                        if (char.IsControl(c))
                        {
                            result.Append($"\\x{(int)c:x2}");
                        }
                        else
                        {
                            result.Append(c);
                        }
                        break;
                }
            }

            result.Append('"');
            return result.ToString();
        }
    }
}
