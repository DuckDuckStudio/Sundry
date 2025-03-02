import os
import sys
import subprocess

# 这是打包后使用的
# 对于源码，请查看 sundry.ps1

def main():
    try:
        tool = sys.argv[1].lower()
        args = sys.argv[2:]
    except IndexError:
        print("无效的调用")
        print("可用调用: [remove/移除] [ignore/忽略] [ver/版本]")
        return 1
    script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    version = "develop"

    if tool in ["移除", "remove"]:
        tool_path = "remove.exe"
    elif tool in ["忽略", "ignore"]:
        tool_path = "ignore.exe"
    elif tool in ["config", "配置"]:
        tool_path = "config.exe"
    elif tool in ["sync", "同步", "syncronize", "sync-fork"]:
        tool_path = "sync.exe"
    # ==========================================
    elif tool in ["ver", "版本", "version", "Version", "--version", "--ver", "-v"]:
        print(f"版本: {version}")
        print(f"安装在: {script_path}")
        return 0
    elif tool in ["h", "help", "-h", "-help", "--help", "/?", "帮助"]:
        print("Sundry 使用帮助")
        print("    移除软件包版本: sundry remove [软件包标识符] [软件包版本] [跳过检查(只接受true)/理由(默认为GitHub Action中返回404)]")
        # print("    修改检测忽略字段: sundry ignore [add/remove/list] [忽略字段] [理由]")
        print("    同步本地仓库 (master 分支): sundry sync")
        print("    修改 Sundry 配置:")
        print("        初始化: sundry config init")
        print("        修改值: sundry config [条目] [值]")
        # print("    其他辅助命令:")
        # print("        多版本辅助修改: sundry change")
        # print("        新版本辅助修改: sundry new")
        print("    其他 Sundry 命令:")
        print("        查看版本: sundry ver")
        print("        查看帮助: sundry help")
        return 0
    else:
        print("无效的调用")
        print("可用调用: [remove/移除] [ignore/忽略] [ver/版本]")
        return 1

    subprocess.run([f"{script_path}\\{tool_path}"] + args, check=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
