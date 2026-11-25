set windows-shell := ["pwsh.exe", "-c"]

build:
    uv sync --group "build"
    uv run "自动化脚本/png-2-ico.py"
    uv run pyinstaller --onefile --distpath="Release" --name="sundry.exe" "src/sundry.py" --collect-data "ajaw" -i "icon/Sundry.ico"
    cp -v "src/fun.txt" "Release"
    cp -v "LICENSE" "Release"
    ./Release/sundry.exe --version

lint:
    uv sync --all-groups
    -uv run mypy .
    -uv run pylint src tests "自动化脚本"
    -uv run pyright
    -uv run ruff check
    -uv run ty check
