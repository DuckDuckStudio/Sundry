using System.Diagnostics;

namespace sundry.Method
{
    internal class RunCommand
    {
        public static async Task RunGitCommandAsync(params string[] args)
        {
            ProcessStartInfo startInfo = new()
            {
                FileName = "git",
                Arguments = string.Join(" ", args),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            Process process = Process.Start(startInfo) ?? throw new InvalidOperationException("无法启动 Git 进程");
            string output = await process.StandardOutput.ReadToEndAsync();
            string error = await process.StandardError.ReadToEndAsync();

            if (!string.IsNullOrEmpty(output)) Console.WriteLine(output);
            if (!string.IsNullOrEmpty(error)) throw new Exception(error);

            await process.WaitForExitAsync();
        }
    }
}
