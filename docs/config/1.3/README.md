# Sundry 配置文件 版本 1.3

| jsonc | json schema |
|-----|-----|
| [config.jsonc](config.jsonc) | [1.3.json](https://github.com/DuckDuckStudio/yazicbs.github.io/blob/main/Tools/Sundry/config/schema/1.3.json) |

## 描述
这是 Sundry 的配置文件 (`~/DuckStudio/Sundry/config.json`) 的 1.3 版本。**有关配置文件的详细说明，请参见 jsonc 中的注释。**  

此版本的配置文件适用 Sundry 1.6.x 版本。

### 与 1.2 版本的区别

1.3 版本的配置文件添加了几个配置项。  
新增了这几个配置项:  

| 配置项 | 作用 | 默认值 | 接受值 |
|-----|-----|-----|-----|
| `github.token` | 设置 Token 读取源 | `glm` (读取 [GitHub Labels Manager](https://github.com/DuckDuckStudio/GitHub-Labels-Manager) 设置的 Token) | `glm`、`env` (从环境变量 `GITHUB_TOKEN` 读取)、`komac` |
| `tools.autoremove.open_in_browser` | 设置是否在浏览器中打开安装程序链接以供检查 | `false` | _bool_ |
