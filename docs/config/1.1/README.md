# Sundry 配置文件 版本 1.1

| jsonc | json schema |
|-----|-----|
| [config.jsonc](config.jsonc) | [1.1.json](https://github.com/DuckDuckStudio/yazicbs.github.io/blob/main/Tools/Sundry/config/schema/1.1.json) |

## 描述
这是 Sundry 的配置文件 (`~/DuckStudio/Sundry/config.json`) 的 1.1 版本。**有关配置文件的详细说明，请参见 jsonc 中的注释。**  

此版本的配置文件适用 Sundry 1.4.2 及后续版本。

### 与 1.0 版本的区别
> [!WARNING]  
> 1.1 版本的配置文件与 1.0 版本的配置文件 **不兼容**，也 **不** 与 sundry-old 的配置文件兼容。  
> 如果您之前使用的是旧版本的配置文件，请重新运行 `sundry config init`。  
> 如果您实在想要同时使用新旧版本的 Sundry，请使用 `sundry config <配置项> <配置值>` 来设置旧版本的 Sundry 的配置项。

1.1 版本的配置文件更加细化了每个配置项的分类，例如:
```diff
- winget-pkgs
+ paths.winget-pkgs
```

并添加了多个可选配置。  

---

以下是 1.0 版本的配置项在 1.1 版本的配置文件中的对应:

| 1.0 | 1.1 | 含义 |
|-----|-----|-----|
| `version` | 一致 | 在 1.0 中表示 Sundry 的版本；在 1.1 中表示配置文件的版本。 |
| `winget-pkgs` | `paths.winget-pkgs` | 您的 winget-pkgs 本地仓库路径 |
| `winget-tools` | `paths.winget-tools` | 您的 winget-tools 本地仓库路径 |
| `pkgs-repo` | `repos.winget-pkgs` | 您的 winget-pkgs 仓库 |
| `tools-repo` | `repos.winget-tools` | 您的 winget-tools 仓库 |
| `signature` | `git.signature` | 是否对提交签名 |
