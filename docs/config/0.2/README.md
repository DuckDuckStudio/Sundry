# Sundry 配置文件 版本 0.2

| jsonc | json schema |
|-----|-----|
| [config.jsonc](config.jsonc) | [0.2.json](https://github.com/DuckDuckStudio/yazicbs.github.io/blob/main/Tools/Sundry/config/schema/0.2.json) |

## 描述
这是 Sundry 的配置文件 (`config.json`) 的 0.2 版本。**有关配置文件的详细说明，请参见 jsonc 中的注释。**  

此版本的配置文件适用 Sundry 1.0.2 - Sundry 1.1.10。

### 与 0.1 版本的区别
0.2 版本的配置文件添加了 `signature` 配置项:
```jsonc
"signature": false // 是否对提交签名
```

其他没有变化。  
