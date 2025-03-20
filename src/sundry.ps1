param(
    [string]$tool,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$Script_Path = Split-Path -Parent $MyInvocation.MyCommand.Path
$sundry = Join-Path $Script_Path "sundry.py"

# 要用虚拟环境请往下翻

if ($tool -in "移除", "remove") {
    $command = "remove"
# } elseif ($tool -in "忽略", "ignore") {
#     $command = "ignore"
} elseif ($tool -in "config", "配置") {
    $command = "config"
# } elseif ($tool -in "修改", "modify", "change", "changes") {
#     Write-Warning("请在确保修改脚本已编辑完毕再使用!")
#     $command = "change"
# } elseif ($tool -in "更新", "update", "new", "新", "新版本") {
#     Write-Warning("请在确保修改脚本已编辑完毕再使用!")
#     $command = "new"
} elseif ($tool -in "sync", "同步", "synchronize", "sync-fork") {
    $command = "sync"
} elseif ($tool -eq "cat") {
    $command = "cat"
} elseif ($tool -eq "repr") {
    $command = "repr"
# ========================================================
} elseif ($tool -in "ver", "版本", "version", "Version", "--version", "--ver", "-v") {
    $command = "ver"
} else {
    # 原样传递，让 py 脚本去处理
    $command = $tool
}

# 此处可以将 python 改为你自己的虚拟环境中的 python.exe
# 例如 python -> & "D:\...\.venv\Scripts\python.exe"
# 注意最前面有个 &
python $sundry $command $Args
