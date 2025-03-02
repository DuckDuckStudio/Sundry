param(
    [string]$tool,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$Script_Path = Split-Path -Parent $MyInvocation.MyCommand.Path
$version = "develop"
$flag = 0

# 要用虚拟环境请往下翻

# 这是源码用的，对于打包后的请查看 sundry.py

if ($tool -in "移除", "remove") {
    $pythonScript = Join-Path $Script_Path "remove.py"
# } elseif ($tool -in "忽略", "ignore") {
#     $pythonScript = Join-Path $Script_Path "ignore.py"
} elseif ($tool -in "config", "配置") {
    $pythonScript = Join-Path $Script_Path "config.py"
# } elseif ($tool -in "修改", "modify", "change", "changes") {
#     Write-Warning("请在确保修改脚本已编辑完毕再使用!")
#     $pythonScript = Join-Path $Script_Path "change.py"
# } elseif ($tool -in "更新", "update", "new", "新", "新版本") {
#     Write-Warning("请在确保修改脚本已编辑完毕再使用!")
#     $pythonScript = Join-Path $Script_Path "NewVersion.py"
} elseif ($tool -in "sync", "同步", "syncronize", "sync-fork") {
    $pythonScript = Join-Path $Script_Path "sync.py"
# ========================================================
} elseif ($tool -in "ver", "版本", "version", "Version", "--version", "--ver", "-v") {
    Write-Output "版本: $version"
    Write-Output "安装在: $Script_Path"
    $flag = 1
} elseif ($tool -in "h", "help", "-h", "-help", "--help", "/?", "帮助") {
    Write-Output "Sundry 使用帮助"
    Write-Output "    移除软件包版本: sundry remove [软件包标识符] [软件包版本] [跳过检查(只接受true)/理由(默认为GitHub Action中返回404)]"
    # Write-Output "    修改检测忽略字段: sundry ignore [add/remove/list] [忽略字段] [理由]"
    Write-Output "    同步本地仓库 (master 分支): sundry sync"
    Write-Output "    修改 Sundry 配置:"
    Write-Output "        初始化: sundry config init"
    Write-Output "        修改值: sundry config [条目] [值]"
    # Write-Output "    其他辅助命令:"
    # Write-Output "        多版本辅助修改: sundry change"
    # Write-Output "        新版本辅助修改: sundry new"
    Write-Output "    其他 Sundry 命令:"
    Write-Output "        查看版本: sundry ver"
    Write-Output "        查看帮助: sundry help"
    $flag = 1
} else {
    Write-Warning "无效的调用"
    Write-Output "可用调用: [remove/移除] [ignore/忽略] [ver/版本]"
    $flag = 1
}

if ($flag -ne 1) {
    # 此处将 python 改为你自己的虚拟环境中的 python.exe
    # 例如 python -> & "D:\...\.venv\Scripts\python.exe"
    # 注意最前面有个 &
    python $pythonScript $Args
}
