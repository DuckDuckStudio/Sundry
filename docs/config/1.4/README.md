# Sundry 配置文件 版本 1.4

| jsonc | json schema |
|-----|-----|
| [config.jsonc](config.jsonc) | [1.4.json](https://github.com/DuckDuckStudio/yazicbs.github.io/blob/main/Tools/Sundry/config/schema/1.4.json) |

## 描述
这是 Sundry 的配置文件 (`~/DuckStudio/Sundry/config.json`) 的 1.4 版本。**有关配置文件的详细说明，请参见 jsonc 中的注释。**  

此版本的配置文件适用 Sundry 2.x 版本。

### 与 1.3 版本的区别

将 `github.token` 配置项的默认值从 `glm` 改为 `keyring`。  

> [!TIP]
> 这不影响 `sundry config update`，更新配置文件后会保留你原来设置的 Token 读取源。

这是因为 [GitHub Labels Manager](https://github.com/DuckDuckStudio/GitHub-Labels-Manager) 已弃用。  

如果你喜欢搭配 [Komac](https://github.com/russellbanks/Komac/) 使用 Sundry，将此配置设为 `komac` 可以直接读取你在 komac 设置的 Token。

你现在也可以直接用 `sundry config token <set/remove>` 命令管理 Token，而不是让 Sundry 去使用别的工具的 Token 或环境变量。

> [!NOTE]
> 要让 Sundry 使用 Sundry 自己设置的 Token，需要在设置完 Token 后通过命令修改 Token 读取源:
> ```bash
> sundry config github.token keyring
> ```

与此修改相关的议题: [DuckDuckStudio/Sundry#267](https://github.com/DuckDuckStudio/Sundry/issues/267)

---

添加了 `git.retry_interval` 配置项，用于配置命令重试的间隔。  
该配置项接受一个整数作为配置值:

- 负数表示不重试
- `0` 表示立即重试
- 正数表示在重试前等待 `n` 秒

默认配置值为 `50`（在重试前等待 `50` 秒），你可以根据你自己的网络状况调整重试间隔。

与此修改相关的议题: [DuckDuckStudio/Sundry#205](https://github.com/DuckDuckStudio/Sundry/issues/205)

---

允许 [winget-tools](https://github.com/DuckDuckStudio/winget-tools/) 仓库的路径和仓库信息配置为空（`null`）。  
如果你不打算使用 `sundry ignore`，可以设置 `winget-tools` 相关的配置为空（`null`）。

如果你未来又想使用 `sundry ignore`，只需要补全设置即可：
```bash
sundry config paths.winget-tools "仓库路径"
sundry config repos.winget-tools "owner/repo"
```
