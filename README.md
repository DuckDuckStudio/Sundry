# Sundry

[![GitHub Releases 最新版本](https://img.shields.io/github/release/DuckDuckStudio/Sundry)](https://github.com/DuckDuckStudio/Sundry/releases/latest) ![GitHub Releases 下载数](https://img.shields.io/github/downloads/DuckDuckStudio/Sundry/total.svg)  

sundry 是一个 WinGet 本地清单管理工具，让您更方便地移除清单、修改清单，还可以辅助更新清单。  

## 如何获取
### Windows
1. 前往 [GitHub Release](https://github.com/DuckDuckStudio/Sundry/releases) 页面下载安装程序或 zip/7z 归档。
2. 使用 WinGet 获取:  
```powershell
winget install --id DuckStudio.Sundry --source winget --exact
```

### Ubuntu
[从源构建](#ubuntu-1)。  

## 使用说明
当您获取本工具后，请先使用这个命令初始化配置文件:  

```bash
sundry config init
```

> 题外话: 这个配置文件就是我将其从我自己的工具变为这里的工具的方法 XD  

> [!TIP]  
> 在 **1.1.0** 之前，配置文件在程序目录下的 `config.json` 中；在 **1.1.0** 之后，配置文件在用户目录下的 `.config/DuckStudio/Sundry/config.json` 中。 - 这是为更新时不覆盖配置文件考虑的，如果配置文件不对，请再次使用 `sundry config init`。  
> ~~由于作者实在是太懒了~~，在卸载 Sundry 之后不会移除配置文件，如果需要可以手动移除。    

初始化完配置文件后用以下命令确认下:  

```bash
sundry config show
```

如果有任何地方不对，请使用这个命令修改对应键的值:  

```bash
sundry config "<条目>" "<值>"
```

更多可用命令请见下方示例。  

## 可用命令

> Sundry [1.3.4](https://github.com/DuckDuckStudio/Sundry/releases/tag/1.3.4)

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
- 用法:
  - 分析日志: `sundry logs-analyse <Azure Pipline Url> [是否保留日志文件] [是否显示一般错误/异常]`
  - 清理之前下载的日志: `sundry logs-analyse cleanup`
- 示例:
  - 分析日志
    > 这里的 Azure Validation Pipeline Run 是 https://github.com/microsoft/winget-pkgs/pull/267849#issuecomment-2998878757 的。
    - 最少参数: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464"` (需要用户输入)
    - 不保留日志文件: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" n`
    - 保留日志文件: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" y` (运行后将打开日志文件所在目录)
    - 不显示一般错误/异常: 默认，不需要传递额外参数。
    - 显示一般错误/异常: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" 占位 y`
    - 保留日志文件且不显示一般错误/异常: 默认不显示一般错误/异常，同保留日志文件的示例。
    - 保留日志文件且显示一般错误/异常: `sundry logs-analyse "https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_build/results?buildId=137464" y y`
  - 清理之前下载的日志: `sundry logs-analyse cleanup`

</details>

<details>
  <summary><code>sundry verify</code></summary>

![Sundry verify 命令展示图。该命令用于测试本地或 PR 上的清单的安装和卸载，并获取 ARP 条目变更。](docs/photos/README/Demo/Commands/verify.png)  

> 截图是在 Hyper-V Windows 10 x64 虚拟机上的测试。  

- 别名: `verify`, `test`, `验证`, `测试`
- 作用: **用于测试本地或 PR 上的清单的安装和卸载，并获取 ARP 条目变更。**
- 用法:
  - 本地清单: `sundry verify <软件包标识符> <软件包版本>`
  - PR 清单: `sundry verify <PR链接>`
- 示例:
  - 测试本地清单: `sundry verify DuckStudio.FufuTools 1.3.10`
  - 测试 PR 清单: `sundry verify <打开的PR>`

⚠ 注意
1. **它只能获取 HEAD 分支没被删除的 PR 的清单**，如果 HEAD 分支被删除了 GitHub API 会响应 404 Not Found。  
2. 它暂时**无法获取 `UpgradeCode`**。  
3. 对于本地清单，配置文件指向的 winget-pkgs 文件夹中**至少**要有以下文件:  
  \- Tools/Auth.csv  
  \- manifests/清单所在文件夹/清单文件 (例如 manifests/d/DuckStudio/Sundry/1.3.4/*)
4. 对于 PR 清单，它会将清单文件下载到 `%temp%/Sundry/Verify/PRManifest/PR编号` 下。  

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

### Ubuntu 支持

| 命令 | 是否支持 | 备注 |
|-----|-----|-----|
| help | ✓ |  |
| ver | ✓ |  |
| remove | ✕ | 验证阶段需要 WinGet，不确定如何读取 Token |
| modify | ✕ | 验证清单需要 WinGet，不确定如何读取 Token |
| logs-analyse | 部分支持 | 不支持自动打开日志文件夹 |
| verify | ✕ | 您只能在 Windows 上验证软件包 |
| ignore | ✕ | 不确定如何读取 Token |
| cat | ✓ |  |
| sync | ✓ |  |
| repr | ✓ |  |
| config | ✓ |  |
| revert | ✓ |  |
| fun | ✓ |  |

## 自己构建
### Windows

> [!TIP]
> 仓库下有一个适用于 Windows 的[构建流](https://github.com/DuckDuckStudio/Sundry/blob/main/.github/workflows/build.yaml)，你可以 fork 后直接运行，它会将结果上传为工件。  

1. 克隆后 `cd` 到项目所在目录
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
```
4. 转换图标格式 (可选)
```pwsh
python "自动化脚本/png-2-ico.py"
```
5. 构建
```pwsh
pyinstaller --onefile --distpath="Release" --name="sundry.exe" "src/sundry.py" --icon "icon/Sundry.ico"
# 如果前面没转换图标格式，参数中的图标请用 icon/Sundry.png，Pyinstaller 会尝试自己转换格式。
```
6. 复制所需文件
```pwsh
Copy-Item -Path "src/fun.txt" -Destination "Release" -Verbose
Copy-Item -Path "LICENSE" -Destination "Release" -Verbose
```
7. `Release` 下就是构建结果

### Ubuntu
```bash
set -e
echo "克隆源码..."
git clone https://github.com/DuckDuckStudio/Sundry.git -b Ubuntu
cd Sundry
echo "创建虚拟环境并安装依赖..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r "requirements.txt"
echo "构建二进制文件..."
python3 "自动化脚本/修改版本号.py" "2025.520.1314"
pyinstaller --onefile --distpath="Release" --name="sundry" "src/sundry.py"
deactivate
cp -v "src/fun.txt" "Release"
cp -v "LICENSE" "Release"
echo "整理文件..."
cd ..
cp -rv "Sundry/Release" "./Release"
rm -rvf Sundry
cd Release
echo "配置 Sundry..."
./sundry ver
./sundry config init
```

然后 `./Release` 下就是构建结果。  
