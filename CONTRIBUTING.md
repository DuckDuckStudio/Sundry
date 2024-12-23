# 贡献指南
感谢您对本项目感兴趣！以下是一些帮助您开始贡献的步骤。

## 如何贡献

1. Fork 仓库并克隆到本地：
    ```bash
    git clone https://github.com/DuckDuckStudio/Sundry.git
    cd Sundry
    ```

2. 创建一个新的分支：
    ```bash
    git checkout -b feature/your-feature-name
    ```

3. 进行代码修改并提交：
    ```bash
    git add .
    git commit -m "描述您的更改"
    ```

4. 推送到您的仓库：
    ```bash
    git push origin feature/your-feature-name
    ```

5. 创建一个 Pull Request 到主仓库的 `develop` 分支。

## 本地调试
1. 安装依赖：
    ```bash
    dotnet add Sundry package YamlDotNet
    ```

2. 构建项目：
    ```bash
    dotnet build Sundry
    ```

3. 运行扫描：
    ```bash
    git clone https://github.com/microsoft/winget-pkgs
    # 或任意其他 winget fork
    dotnet run --project Sundry <manifests 子目录>
    ```

## 使用 Docker 运行测试
1. 构建 Docker 镜像：
    ```bash
    docker build -t sundry:latest .
    ```

2. 运行 Docker 容器：
    ```bash
    docker run --rm -it sundry:latest
    ```

3. 运行测试：
    ```bash
    docker run --rm -it sundry:latest dotnet test
    ```

## 代码规范

- 请确保您的代码符合项目的编码规范。
- 提交前请运行所有测试并确保它们通过。

## 报告问题

如果您发现了一个 bug 或有一个功能请求，请通过 GitHub Issues 报告。

感谢您的贡献！
