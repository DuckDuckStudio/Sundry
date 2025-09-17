# Sundry 配置文件 版本 0.3

| jsonc | json schema |
|-----|-----|
| [config.jsonc](config.jsonc) | [0.3.json](https://github.com/DuckDuckStudio/yazicbs.github.io/blob/main/Tools/Sundry/config/schema/0.3.json) |

## 描述
这是 Sundry 的配置文件 (`~/DuckStudio/Sundry/config.json`) 的 0.3 版本。**有关配置文件的详细说明，请参见 jsonc 中的注释。**  

此版本的配置文件适用 Sundry 1.1.11 - Sundry 1.1.14。

### 与 0.2 版本的区别
0.3 版本的配置文件修改了 `signature` 配置项接受的值:
```diff
- "signature": false // boolean
+ "signature": "no" // string
```

其他没有变化。  
