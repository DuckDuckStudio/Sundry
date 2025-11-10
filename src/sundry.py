import os
import sys
from function.print.print import 消息头

def main() -> int:
    try:
        tool = sys.argv[1].lower()
        args = sys.argv[2:]
    except IndexError:
        tool = "help"
        args = []

    script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    version = "develop"

    if (sys.platform != "win32") and (tool in [
        "移除", "remove", "自动移除", "autoremove", # 验证阶段需要 WinGet，不确定如何读取 Token
        "单改", "单修改", "modify", "hash-update", # 验证清单需要 WinGet，不确定如何读取 Token
        "忽略", "检查忽略", "ignore", # 不确定如何读取 Token
        "verify", "test", "验证", "测试", # 仅 Windows
    ]):
        from colorama import Fore
        print(f"{消息头.错误} 该操作仅可在 Windows 上运行")
        return 1

    # 开源的
    if tool in ["移除", "remove"]:
        import tools.remove as remove
        return remove.main(args)
    elif tool in ["自动移除", "autoremove"]:
        import tools.autoremove as autoremove
        return autoremove.main(args)
    elif tool in ["单改", "单修改", "modify"]:
        import tools.modify as modify
        return modify.main(args)
    elif tool in ["忽略", "检查忽略", "ignore"]:
        import tools.ignore as ignore
        return ignore.main(args)
    elif tool in ["sync", "同步", "synchronize", "sync-fork"]:
        import tools.sync as sync
        return sync.main()
    elif tool in ["prune"]:
        import tools.prune as prune
        return prune.main()
    elif tool == "cat":
        import tools.cat as cat
        return cat.main(args)
    elif tool == "repr":
        import tools.repr
        return tools.repr.main(args)
    elif tool in ["日志分析", "logs-analyse", "log-analyse", "logs_analyse", "Azure日志分析"]:
        import tools.logsAnalyse as logsAnalyse
        return logsAnalyse.main(args)
    elif tool in ["verify", "验证"]:
        import tools.verify as verify
        return verify.main(args)
    # 未开源的
    # elif tool in ["更新", "update", "new", "新", "新版本"]:
    #     import tools.update as update
    #     return update.main(args)
    # elif tool == "hash-update":
    #     import tools.hashUpdate as hashUpdate
    #     return hashUpdate.main(args)
    # elif tool == "validate":
    #     import tools.validate as validate
    #     return validate.main(args)
    # 维护
    elif tool in ["config", "配置"]:
        import tools.maintain.config as config
        return config.main(args)
    elif tool in ["还原", "revert"]:
        import tools.maintain.revert as revert
        return revert.main(args)
    elif tool in ["fun"]:
        import tools.maintain.fun as fun
        # 将 script_path 作为 args 的第一个参数
        args.insert(0, script_path)
        return fun.main(args)
    elif tool in ["清理", "cleanup"]:
        import tools.maintain.cleanup as cleanup
        arg = args[0] if args else ""
        return cleanup.main(arg) # 仅接受单个 str 参数
    # 其他
    elif tool in ["ver", "版本", "version", "Version", "--version", "--ver", "-v"]:
        print(f"版本: {version}")
        print(f"安装在: {script_path}")
        return 0
    else:
        print("Sundry 使用帮助")
        print("    移除软件包版本:")
        print("        指定版本: sundry remove <软件包标识符> <软件包版本> [跳过检查(只接受true)/理由(默认为GitHub Action中返回404)]")
        print("        自动检查: sundry autoremove <软件包标识符> [是否跳过检查]")
        # print("    新版本辅助修改: sundry new <软件包标识符> <版本> [解决的议题(没有则使用urls占位)] <urls...>")
        # print("    多版本辅助修改: sundry change (多改)")
        print("    单版本辅助修改: sundry modify <软件包标识符> <版本> [理由/解决的议题] (单改)")
        # print("    安装程序哈希值更新: sundry hash-update <软件包标识符> <软件包版本> [解决的议题]")
        print("    Azure Pipline 日志分析:")
        print("        日志分析: sundry logs-analyse <GitHub PR 或 Azure 管道运行链接> [是否保留日志文件] [是否显示一般错误/异常]")
        print("        清理下载的日志文件: sundry logs-analyse cleanup (等效于 sundry cleanup logs-analyse)")
        print("    清单验证:")
        # print("        验证清单内容: sundry validate <清单路径> / sundry validate <包标识符> <包版本>")
        print("        测试本地清单: sundry verify <软件包标识符> <软件包版本>")
        print("        测试 PR 修改: sundry verify <PR链接>")
        print("    winget-tools 检查忽略: sundry ignore <add/remove/edit/list> [忽略字段] [理由]")
        print("    其他辅助命令:")
        print("        查看清单: sundry cat <软件包标识符> <版本> [清单类型] [区域设置(如果是locale类型)]")
        print("        同步本地: sundry sync")
        print("        清理远程已删除分支: sundry prune")
        print("        格式化字符串: sundry repr <文件路径/文本内容> [编码(默认 UTF-8)]")
        print("    维护:")
        print("        配置:")
        print("            初始化: sundry config init")
        print("            显示当前配置: sundry config show")
        print("            修改值: sundry config <条目> <值>")
        print("            更新配置文件: sundry config update")
        print("        还原本地仓库修改: sundry revert <仓库> <是否已提交> <是否丢弃>")
        print("        清理产生的文件: sundry cleanup <工具名>")
        print("        fun.txt: sundry fun <random/list/edit/add/remove/import> [参数...]")
        print("    其他 Sundry 命令:")
        print("        查看版本: sundry ver")
        print("        查看帮助: sundry help")
        return 0

if __name__ == "__main__":
    sys.exit(main())
