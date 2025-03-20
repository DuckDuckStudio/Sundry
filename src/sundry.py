import os
import sys

def main():
    try:
        tool = sys.argv[1].lower()
        args = sys.argv[2:]
    except IndexError:
        tool = "help"
        args = []

    script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    version = "develop"

    if tool in ["移除", "remove"]:
        import remove
        return remove.main(args)
    elif tool in ["config", "配置"]:
        import config
        return config.main(args)
    elif tool in ["sync", "同步", "synchronize", "sync-fork"]:
        import sync
        return sync.main()
    elif tool == "cat":
        import cat
        return cat.main(args)
    elif tool == "repr":
        import repr
        return repr.main(args)
    # ==========================================
    elif tool in ["ver", "版本", "version", "Version", "--version", "--ver", "-v"]:
        print(f"版本: {version}")
        print(f"安装在: {script_path}")
        return 0
    else:
        print("Sundry 使用帮助")
        print("    移除软件包版本: sundry remove <软件包标识符> <软件包版本> [跳过检查(只接受true)/理由(默认为GitHub Action中返回404)]")
        # print("    修改检测忽略字段: sundry ignore [add/remove/list] [忽略字段] [理由]")
        print("    修改 Sundry 配置:")
        print("        初始化: sundry config init")
        print("        修改值: sundry config <条目> <值>")
        print("    其他辅助命令:")
        # print("        多版本辅助修改: sundry change")
        # print("        新版本辅助修改: sundry new")
        print("        查看清单: sundry cat <软件包标识符> <版本> <清单类型> [区域设置(如果是locale类型)]")
        print("        同步本地: sundry sync")
        print("        格式化字符串: sundry repr <文件路径/文本内容> [编码(默认 UTF-8)]")
        print("    其他 Sundry 命令:")
        print("        查看版本: sundry ver")
        print("        查看帮助: sundry help")
        return 0

if __name__ == "__main__":
    sys.exit(main())
