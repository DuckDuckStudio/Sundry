import os
import sys

# ===========================================================
# 本项目使用了 芙芙工具箱
# 芙芙工具箱作者：鸭鸭「カモ」
# 作者网站：https://duckduckstudio.github.io/yazicbs.github.io/
# 芙芙工具箱网站：https://duckduckstudio.github.io/yazicbs.github.io/Tools/Fufu_Tools/

# 开源许可证文本可在以下链接找到：
# https://github.com/DuckDuckStudio/Fufu_Tools/blob/main/LICENSE
# ===========================================================

def 替换文件内容(文件路径, 原文本, 新文本):
    try:
        # 读取文件内容
        with open(文件路径, 'r', encoding='utf-8') as f:
            内容 = f.read()

        # 替换文本
        内容 = 内容.replace(原文本, 新文本)

        # 写回文件
        with open(文件路径, 'w', encoding='utf-8') as f:
            f.write(内容)
    except Exception as e:
        print(f"[ERROR] 处理 {文件路径} 时出错: {e}")
        sys.exit(1)

if len(sys.argv) != 2:
    print("[ERROR] 使用示例: python xxx.py <新版本号>")
    sys.exit(1)

新版本号 = sys.argv[1]
if (not 新版本号) or (新版本号.startswith('v')):
    print(f"[ERROR] 新版本号为空或格式不正确，获取到的新版本号: {新版本号}")
    sys.exit(1)
print(f"[INFO] 新版本号: {新版本号}")

# 文件路径和替换规则
文件和替换规则 = [
    (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), "src", "tools", "maintain", "config.py"), '"version": "develop",', f'"version": "{新版本号}",'),
    (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), "src", "sundry.py"), 'version = "develop"', f'version = "{新版本号}"'),
    (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), "installer.iss"), 'develop', 新版本号)
]

# 执行替换操作
for 文件路径, 原文本, 新文本 in 文件和替换规则:
    替换文件内容(文件路径, 原文本, 新文本)

print("[INFO] 🎉 成功处理所有文件")
sys.exit(0)
