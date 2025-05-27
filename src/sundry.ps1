param(
    [string]$command,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$Script_Path = Split-Path -Parent $MyInvocation.MyCommand.Path
$sundry = Join-Path $Script_Path "sundry.py"

# 此处可以将 python 改为你自己的虚拟环境中的 python.exe
# 例如 python -> & "D:\...\.venv\Scripts\python.exe"
# 注意最前面有个 &
python $sundry $command $Args
