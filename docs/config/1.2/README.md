# Sundry 配置文件 版本 1.2

| jsonc | json schema |
|-----|-----|
| [config.jsonc](config.jsonc) | [1.2.json](https://github.com/DuckDuckStudio/yazicbs.github.io/blob/main/Tools/Sundry/config/schema/1.2.json) |

## 描述
这是 Sundry 的配置文件 (`~/DuckStudio/Sundry/config.json`) 的 1.2 版本。**有关配置文件的详细说明，请参见 jsonc 中的注释。**  

此版本的配置文件适用 Sundry 1.5.x 版本。

### 与 1.1 版本的区别

1.2 版本的配置文件添加了几个可选配置:  

| 配置项 | 作用 | 默认值 |
|-----|-----|-----|
| `debug` | 调试模式开关，打开后会输出一些调试信息，除非需要不建议打开 | `false` (bool) |
| `cache.*` | 缓存开关，用于控制是否自动缓存某些内容 | / |
| `cache.validate.schema` | 控制是否缓存验证清单时使用的 yaml schema | `true` (bool) |
