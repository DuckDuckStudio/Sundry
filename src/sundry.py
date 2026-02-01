import sys
from colorama import init
from catfood.functions.print import 消息头
from function.constant.paths import SUNDRY_LOCATION
from function.constant.general import SUNDRY_VERSION

def main() -> int:
    init(autoreset=True)

    try:
        tool = sys.argv[1].lower()
        args = sys.argv[2:]
    except IndexError:
        tool = "help"
        args = []

    if (sys.platform != "win32") and (tool in (
        "移除", "remove", "自动移除", "autoremove", # 验证阶段需要 WinGet，不确定如何读取 Token
        "单改", "单修改", "modify", "hash-update", # 验证清单需要 WinGet，不确定如何读取 Token
        "忽略", "检查忽略", "ignore", # 不确定如何读取 Token
        "verify", "test", "验证", "测试", # 仅 Windows
    )):
        print(f"{消息头.错误} 该操作仅可在 Windows 上运行")
        return 1

    # 开源的
    if tool in ("移除", "remove"):
        import tools.remove as remove
        return remove.main(args)
    elif tool in ("自动移除", "autoremove"):
        import tools.autoremove as autoremove
        return autoremove.main(args)
    elif tool in ("单改", "单修改", "modify"):
        import tools.modify as modify
        return modify.main(args)
    elif tool in ("忽略", "检查忽略", "ignore"):
        import tools.ignore as ignore
        return ignore.main(args)
    elif tool in ("sync", "同步", "synchronize", "sync-fork"):
        import tools.sync as sync
        return sync.main()
    elif tool in ("prune"):
        import tools.prune as prune
        return prune.main()
    elif tool == "cat":
        import tools.cat as cat
        return cat.main(args)
    elif tool == "repr":
        import tools.repr
        return tools.repr.main(args)
    elif tool in ("日志分析", "logs-analyse", "log-analyse", "logs_analyse", "azure日志分析"):
        import tools.logsAnalyse as logsAnalyse
        return logsAnalyse.main(args)
    elif tool in ("verify", "验证"):
        import tools.verify as verify
        return verify.main(args)
    # 维护
    elif tool in ("config", "配置"):
        import tools.maintain.config as config
        return config.main(args)
    elif tool in ("还原", "revert"):
        import tools.maintain.revert as revert
        return revert.main(args)
    elif tool in ("fun"):
        import tools.maintain.fun as fun
        return fun.main(args)
    elif tool in ("清理", "cleanup", "clean"):
        import tools.maintain.cleanup as cleanup
        arg = args[0] if args else ""
        return cleanup.main(arg) # 仅接受单个 str 参数
    # 其他
    elif tool in ("ver", "版本", "version", "Version", "--version", "--ver", "-v"):
        print("Sundry by 鸭鸭「カモ」")
        print(f"版本: {SUNDRY_VERSION}")
        print(f"安装在: {SUNDRY_LOCATION}")
        return 0
    else:
        print("Sundry 使用帮助")
        print("    移除包版本:")
        print("        指定版本: sundry remove <包标识符> <包版本> [跳过检查(只接受true)/理由(默认为GitHub Action中返回404)]")
        print("        自动检查: sundry autoremove <包标识符> [是否跳过检查]")
        print("    单版本辅助修改: sundry modify <包标识符> <版本> [理由/解决的议题] (单改)")
        print("    Azure Pipeline 日志分析:")
        print("        日志分析: sundry logs-analyse <GitHub PR 或 Azure 管道运行链接> [是否保留日志文件] [是否显示一般错误/异常]")
        print("        清理下载的日志文件: sundry logs-analyse cleanup (等效于 sundry cleanup logs-analyse)")
        print("    清单验证:")
        print("        测试本地清单: sundry verify <包标识符> <包版本>")
        print("        测试 PR 修改: sundry verify <PR链接>")
        print("    winget-tools 检查忽略: sundry ignore <add/remove/edit/list> [忽略字段] [理由]")
        print("    其他辅助命令:")
        print("        查看清单: sundry cat <包标识符> <版本> [清单类型] [区域设置(如果是locale类型)]")
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
