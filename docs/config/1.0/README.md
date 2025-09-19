# Sundry 配置文件 版本 1.0

| jsonc | json schema |
|-----|-----|
| [config.jsonc](config.jsonc) | [1.0.json](https://github.com/DuckDuckStudio/yazicbs.github.io/blob/main/Tools/Sundry/config/schema/1.0.json) |

## 描述
这是 Sundry 的配置文件 (`~/DuckStudio/Sundry/config.json`) 的 1.0 版本。**有关配置文件的详细说明，请参见 jsonc 中的注释。**  

此版本的配置文件适用 Sundry 1.2.0 - Sundry 1.4.1。

### 与 0.3 版本的区别
> [!TIP]  
> 如果您使用 Sundry 1.3.2 至 1.4.1，您可以在初始化配置文件时选择兼容 Sundry-old 的配置文件 (配置文件版本 0.3)。

1.0 版本的配置文件细分了仓库的配置:
```diff
- fork
+ pkgs-repo
+ tools-repo
```

其他没有变化。  

---

以下是 0.3 版本的配置项在 1.0 版本的配置文件中的对应:

| 0.3 | 1.0 | 含义 |
|-----|-----|-----|
| `fork` | `pkgs-repo` | 您的 winget-pkgs 仓库 |
