# Sundry
sundry 是一个 WinGet 本地清单管理工具，让您更方便的移除清单、修改清单，还可以辅助更新清单。  

## 代码说明
### 为什么有些简介中的功能在发行版中没有
简介中的功能我都在本地写好了，这个工具本来是我自己本地用的，传之前需要一段时间修改。  
#### 当前公开版实现
- [x] 配置文件及其处理
- [x] 版本清单移除
- [x] 一些新的命令 - 例如 repr、sync 等
#### 接下来
- [ ] 版本清单修改
- [ ] [winget-tools](https://github.com/DuckDuckStudio/winget-tools) 检测忽略

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

更多可用命令可以使用此命令查看:  
```bash
sundry help
```

## Demo
这些 PR 是通过 Sundry 创建的:  
- https://github.com/microsoft/winget-pkgs/pull/232363 (Remove)
- https://github.com/microsoft/winget-pkgs/pull/229554 (Modify)
- https://github.com/microsoft/winget-pkgs/pull/223814 (New version)
- https://github.com/DuckDuckStudio/winget-tools/pulls?q=is%3Apr+is%3Aclosed+label%3Aauto (winget-tools)
