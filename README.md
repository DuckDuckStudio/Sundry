# Sundry
sundry 是一个 WinGet 本地清单管理工具，让您更方便地移除清单、修改清单，还可以辅助更新清单。  

## 使用说明
当您获取本工具后，请先使用这个命令初始化配置文件:  

```bash
sundry config init
```

> 题外话: 这个配置文件就是我将其从我自己的工具变为这里的工具的方法 XD  

> [!TIP]  
> 在 **1.1.0** 之前，配置文件在程序目录下的 `config.json` 中；在 **1.1.0** 之后，配置文件在用户目录下的 `.config/DuckStudio/Sundry/config.json` 中。 - 这是为更新时不覆盖配置文件考虑的，如果配置文件不对，请再次使用 `sundry config init`。  
> ~~由于作者实在是太懒了~~，在卸载 Sundry 之后不会移除配置文件。    

(可选) 初始化完配置文件后用以下命令确认下:  

```bash
sundry config show
```

(可选) 如果有任何地方不对，请使用这个命令修改对应值:  

```bash
sundry config [条目] [值]
```

更多可用命令请见下方示例。  

## 可用命令

> Sundry [1.2.7](https://github.com/DuckDuckStudio/Sundry/releases/tag/1.2.7)

<details>
  <summary><code>sundry help</code></summary>

![Sundry help 命令展示图。该命令用于输出 Sundry 帮助内容。](docs/photos/README/Demo/Commands/help.png)  

- 别名: 任何非命令字符
- 作用: 显示 Sundry 帮助

</details>


<details>
  <summary><code>sundry ver</code></summary>

![Sundry ver 命令展示图。该命令用于输出 Sundry 的版本和安装位置。](docs/photos/README/Demo/Commands/ver.png)  

- 别名: `ver`, `版本`, `version`, `Version`, `--version`, `--ver`, `-v`
- 作用: 显示 Sundry 版本和安装位置

</details>


<details>
  <summary><code>sundry remove</code></summary>

![Sundry remove 命令展示图。该命令用于从上游仓库（microsoft/winget-pkgs）中移除一个指定的软件包的指定版本，并带上理由（如果有）后自动创建拉取请求。](docs/photos/README/Demo/Commands/remove.png)  

> 截图来自拉取请求: https://github.com/microsoft/winget-pkgs/pull/265074  

- 别名: `移除`, `remove`
- 作用: **移除一个指定的软件包的指定版本**，并在移除前自动检查该版本是否确实存在问题。可以指定理由或跳过自动检查。**默认理由为“安装程序URL在GitHub Action上返回了404”。**
- 用法: `sundry remove <软件包标识符> <软件包版本> [是否跳过自动检查] [理由]`
- 示例:
  - 最少参数: `sundry remove DuckStudio.FufuTools 1.3.10`
  - 跳过自动检查: `sundry remove DuckStudio.FufuTools 1.3.10 True`
  - 指定理由: `sundry remove DuckStudio.FufuTools 1.3.10 "该版本存在一个已知问题"`
  - 指定理由的同时跳过自动检查: `sundry remove DuckStudio.FufuTools 1.3.10 True "该版本存在一个已知问题"`

</details>


<details>
  <summary><code>sundry modify</code></summary>

![Sundry modify 命令展示图。该命令用于帮助用户打开需要修改的那个软件包的那个版本，并在修改完毕后自动向上游仓库（microsoft/winget-pkgs）提交拉取请求。](docs/photos/README/Demo/Commands/modify.png)  

- 别名: `单改`, `单修改`, `modify`
- 作用: **修改一个指定的软件包的指定版本的清单**，并在修改完后自动提交拉取请求。
- 用法: `sundry modify <软件包标识符> <版本> [理由/解决的议题]`
- 示例:
  - 最少参数: `sundry modify XBMCFoundation.Kodi 18.2.0.0 ` (https://github.com/microsoft/winget-pkgs/pull/267613)
  - 指定理由: `sundry modify XBMCFoundation.Kodi 18.3.0.0 "替换 HTTP 为 HTTPS"` (https://github.com/microsoft/winget-pkgs/pull/267614)
  - 链接议题:
    - 使用议题 URL: `sundry modify DuckStudio.Sundry 1.2.6 "https://github.com/microsoft/winget-pkgs/issues/267539"`
    - 使用议题纯数字编号: `sundry modify DuckStudio.Sundry 1.2.6 "267539"`
    - 使用议题编号: `sundry modify DuckStudio.Sundry 1.2.6 "#267539"`
  - 指定理由的同时链接议题: 
    ```pwsh
    sundry modify DuckStudio.Sundry 1.2.6 "一些修改。
    - Resolves https://github.com/microsoft/winget-pkgs/issues/267539"
    ```
    > GitHub Docs: [使用关键词将拉取请求链接到议题](https://docs.github.com/zh/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)  

</details>


<details>
  <summary><code>sundry logs-analyse</code></summary>

![Sundry logs-analyse 命令展示图。该命令用于分析 Azure Validation Pipeline Run 失败时的日志，来自动查找具体哪里失败了。](docs/photos/README/Demo/Commands/logs-analyse.png)  

- 别名: `日志分析`, `logs-analyse`, `logs_analyse`, `Azure日志分析`
- 作用: **分析 [Azure Validation Pipeline Run](https://duckduckstudio.github.io/Articles/#/信息速查/终端/WinGet/参考信息?id=验证管道日志在哪看？) 失败时的日志，来自动查找具体哪里失败了。**
- 用法: `sundry logs-analyse <Azure Pipline Url> [是否保留日志文件] [是否显示一般错误/异常]`
- 示例:
  > 这里的 Azure Validation Pipeline Run 是 https://github.com/microsoft/winget-pkgs/pull/267849#issuecomment-2998878757 的。
  - 最少参数: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464"` (需要用户输入)
  - 不保留日志文件: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" n`
  - 保留日志文件: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" y` (运行后将打开日志文件所在目录)
  - 不显示一般错误/异常: 默认，不需要传递额外参数。
  - 显示一般错误/异常: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" 占位 y`
  - 保留日志文件且不显示一般错误/异常: 默认不显示一般错误/异常，同保留日志文件的示例。
  - 保留日志文件且显示一般错误/异常: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" y y`

</details>


<details>
  <summary><code>sundry ignore</code></summary>

![Sundry ignore 命令展示图。该命令用于管理 winget-tools 中的检测脚本的忽略字段。](docs/photos/README/Demo/Commands/ignore.png)  

- 别名: `忽略`, `检查忽略`, `ignore`
- 作用: **管理 [winget-tools](https://github.com/DuckDuckStudio/winget-tools/) 中的检测脚本的忽略字段。**
- 用法: `sundry ignore <add/remove/edit/list> [忽略字段] [理由]`
- 示例:
  - 添加忽略字段: `sundry ignore add "https://www.argyllcms.com/" "服务器冲不动咖啡 (418)"`
  - 移除忽略字段: `sundry ignore remove "https://www.argyllcms.com/" "又冲得动了"`
  - 编辑忽略字段: `sundry ignore edit`
  - 列出所有忽略字段: `sundry ignore list`

</details>


<details>
  <summary><code>sundry cat</code></summary>

![Sundry cat 命令展示图。该命令用于获取指定软件包标识符的指定版本的清单，可以指定获取所有清单或某个类型的清单。](docs/photos/README/Demo/Commands/cat.png)  

- 别名: 没有别名，只能用 `cat`。
- 作用: **获取指定软件包标识符的指定版本的清单**，可以指定获取所有清单或某个类型的清单。
- 用法: `sundry cat <软件包标识符> <版本> [清单类型] [区域设置(如果是locale类型)]`
- 示例:
  - 获取所有清单: `sundry cat DuckStudio.Sundry 1.2.3`
    - 亦可使用 `sundry cat DuckStudio.Sundry 1.2.3 all`
    - 除 `all` 外还可用 `全部`, `所有`
  - 获取指定类型的清单:
    - 安装程序清单: `sundry cat DuckStudio.Sundry 1.2.3 i`
      - 可以用 `installer`, `安装程序`, `安装`, `i`
    - 区域清单: `sundry cat DuckStudio.Sundry 1.2.3 l zh-CN`
      - 可以用 `locale`, `区域`, `区域设置`, `l`
      - 必须指定具体哪个区域设置的清单
    - 版本清单: `sundry cat DuckStudio.Sundry 1.2.3 v`
      - 可以用 `version`, `ver`, `v`, `版本`

</details>


<details>
  <summary><code>sundry sync</code></summary>

![Sundry sync 命令展示图。该命令用于同步 fork 仓库和上游仓库的修改。](docs/photos/README/Demo/Commands/sync.png)  

- 别名: `sync`, `同步`, `synchronize`, `sync-fork`
- 作用: **同步 fork 仓库和上游仓库的修改。**
- 用法: `sundry sync`
- 示例: `sundry sync`

</details>


<details>
  <summary><code>sundry repr</code></summary>

![Sundry repr 命令展示图。该命令用于显示字符串的真面目，就像\n那种。](docs/photos/README/Demo/Commands/repr.png)  

- 别名: 没有别名，只能用 `repr`。
- 作用: 等效于 Python 的 `repr()`，用于获取字符串真实的样子。
- 用法: `sundry repr <文件路径/文本内容> [编码(默认 UTF-8)]`
- 示例:
  - 文本:
    ```pwsh
    sundry repr "第一行
    第二行"
    ```
  - 文件 (假设编码为 gbk): `sundry repr "D:/文件路径/文件.txt" "gbk"`

</details>


<details>
  <summary><code>sundry config</code></summary>

![Sundry config 命令展示图。该命令用于初始化和修改 Sundry 配置。](docs/photos/README/Demo/Commands/config.png)  

- 别名: `config`, `配置`
- 作用: 初始化和修改 Sundry 配置。
- 用法: `sundry config <参数...>`
- 示例:
  - 初始化配置: `sundry config init`
  - 显示当前配置: `sundry config show`
  - 修改配置项: `sundry config signature no`

</details>


<details>
  <summary><code>sundry revert</code></summary>

![Sundry revert 命令展示图。该命令用于还原本地仓库的修改，如果 Sundry 在修改的某个过程中崩溃了，则可以使用此命令还原 Sundry 做的修改。](docs/photos/README/Demo/Commands/revert.png)  

- 别名: `还原`, `revert`
- 作用: **还原本地仓库的修改**，如果 Sundry 在修改的某个过程中崩溃了，则可以使用此命令还原 Sundry 做的修改。
- 用法: `sundry revert <仓库> <是否已提交> <是否丢弃>`
- 示例:
  - 还原所有仓库、未提交、丢弃: `sundry revert all n y`
  - 其他类似

</details>


<details>
  <summary><code>sundry fun</code></summary>

![Sundry fun 命令展示图。该命令用于管理 Sundry 的 fun.txt](docs/photos/README/Demo/Commands/fun.png)  

- 别名: 没有别名，只能用 `fun`。
- 作用: **管理 Sundry 的 `fun.txt`。**
- 用法: `sundry fun <random/list/edit/add/remove/import> [参数...]`
- 示例:
  - 随机一个: `sundry fun` 或 `sundry fun random`
    - 还可以使用 `sundry fun 随机`
  - 列出所有: `sundry fun list`
    - 可以用 `获取`, `读取`, `get`, `list`
  - 编辑 fun.txt: `sundry fun edit`
    - 可以用 `编辑`, `edit`, `打开`, `open`
  - 添加新的: `sundry fun add "提问: 罗浮六御中谁最幸福? 答案: 符玄。因为她姓符。"`
    - 可以用 `add`, `添加`
  - 移除原来的: `sundry fun remove "Ciallo～(∠・ω< )⌒☆"`
    - 可以用 `remove`, `移除`
  - 从其他文件导入(覆盖): `sundry import "D:/文件路径/另一个fun.txt"`
    - 可以用 `import`, `导入`

</details>

## 自己构建
仓库下有一个[构建流](https://github.com/DuckDuckStudio/Sundry/blob/main/.github/workflows/build.yml)，你可以 fork 后直接运行，它会将结果上传为工件。  
大概步骤是:  
1. `cd` 到项目所在目录
2. 更新代码中的版本号
```pwsh
python "自动化脚本/修改版本号.py" "2025.520.1314"
```
3. 安装依赖
```pwsh
python -m venv .venv
& ".venv\Scripts\Activate.ps1"
python.exe -m pip install --upgrade pip
pip install -r "requirements.txt"
pip install pyinstaller
```
4. 构建
```pwsh
pyinstaller --onefile --distpath="Release/pack" --name="sundry.exe" "src/sundry.py"
```
5. 复制所需文件
```bash
cp -v src/fun.txt Release/pack
cp -v LICENSE Release/pack
```
