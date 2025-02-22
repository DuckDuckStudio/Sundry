# Sundry
sundry 是一个 WinGet 本地清单管理工具，让您更方便的移除清单、修改清单，还可以辅助更新清单。  

## 代码说明
本仓库仅提供打包后的二进制文件，不提供源代码。  
### 为什么有些简介中的功能在发行版中没有
简介中的功能我都在本地写好了，这个工具本来是我自己本地用的，传之前需要一段时间“脱敏”和“优化”。  
#### 当前公开版实现
- [x] 配置文件及其处理
- [x] 版本清单移除
#### 接下来
- [ ] 版本清单修改
- [ ] [winget-tools](https://github.com/DuckDuckStudio/winget-tools) 检测忽略
- [ ] 基本文档

## 使用说明
当您获取本工具后，请先使用这个命令初始化配置文件:  
```bash
sundry config init
```

> 题外话: 这个配置文件就是我将其从我自己的工具变为这里的工具的方法 XD  

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
