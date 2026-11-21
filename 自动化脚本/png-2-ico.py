import os
import sys

from PIL import Image

# 将 icon\Sundry.png 转为 icon\Sundry.ico

图标文件路径 = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), "icon", "Sundry.png"))
png = Image.open(图标文件路径)
png.save(os.path.join(os.path.dirname(图标文件路径), "Sundry.ico"), "ico", sizes=[(256, 256)])
print("🎉 成功转换图标格式")
