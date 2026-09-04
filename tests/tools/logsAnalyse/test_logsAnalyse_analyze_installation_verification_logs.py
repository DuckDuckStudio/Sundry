from pathlib import Path

import pytest

from tools.logsAnalyse import analyze_installation_verification_logs


def test_analyze_installation_verification_logs_returns_false_when_directory_is_missing(tmp_path: Path):
    assert analyze_installation_verification_logs(tmp_path / "InstallationVerificationLogs", detailed=False) is False


def test_analyze_installation_verification_logs_reports_keywords_screenshots_and_renames_txt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    logs_dir = tmp_path / "InstallationVerificationLogs"
    logs_dir.mkdir()
    log_file = logs_dir / "nested" / "install.txt"
    log_file.parent.mkdir()
    log_file.write_text("Installation failed with exit code -42\n")
    (logs_dir / "ErrorScreenshot.png").write_bytes(b"png")
    (logs_dir / "abc.png").write_bytes(b"png")
    explained_codes: list[int | str] = []

    monkeypatch.setattr(
        "tools.logsAnalyse.find_explanation_for_error_code",
        explained_codes.append,
    )

    assert analyze_installation_verification_logs(logs_dir, detailed=False) is True

    output = capsys.readouterr().out
    assert not log_file.exists()
    assert log_file.with_suffix(".log").exists()
    assert "ErrorScreenshot.png" in output
    assert "abc.png" not in output
    assert "Installation failed with exit code" in output
    assert explained_codes == ["-42"]


def test_analyze_installation_verification_logs_uses_detailed_keywords_and_exclusions(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    logs_dir = tmp_path / "InstallationVerificationLogs"
    logs_dir.mkdir()
    (logs_dir / "install.log").write_text("MSIX installer failed: -7\nerror.exe was launched\nStandard error: expected output\n")

    assert analyze_installation_verification_logs(logs_dir, detailed=True) is True

    output = capsys.readouterr().out
    assert "MSIX installer failed" in output
    assert "error.exe" not in output
    assert "Standard error: expected output" not in output


@pytest.mark.parametrize(
    ("file_name", "expected_found"),
    [
        ("Log_InstallationClient.log", True),
        ("Other.log", False),
    ],
)
def test_analyze_installation_verification_logs_respects_keyword_file_limit(
    tmp_path: Path,
    file_name: str,
    expected_found: bool,
    capsys: pytest.CaptureFixture[str],
):
    logs_dir = tmp_path / "InstallationVerificationLogs"
    logs_dir.mkdir()
    (logs_dir / file_name).write_text("CmdTool: Failed with hr = 0x8050111c. Check C:\\Users\\VALIDA~1\\AppData\\Local\\Temp\\MpCmdRun.log for more information\n")

    assert analyze_installation_verification_logs(logs_dir, detailed=False) is expected_found

    output = capsys.readouterr().out
    if expected_found:
        assert "Defender 扫描失败，这不是误报，这可能和 https://github.com/microsoft/winget-pkgs/issues/399077 有关" in output
    else:
        assert output == ""


def test_analyze_installation_verification_logs_reports_extended_hints(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    logs_dir = tmp_path / "InstallationVerificationLogs"
    logs_dir.mkdir()
    (logs_dir / "installer.log").write_text(
        "Installation failed with exit code -2147467260\n"
        "Installation failed with exit code NaN\n"
        "ShellExecute installer failed: -5\n"
        "ShellExecute installer failed: NaN\n"
        "MSIX installer failed: -6\n"
        "Package failed updates, dependency or conflict validation.\n"
        "Installer error 0x8050111c\n"
        "Installer error 0xNaN\n"
    )
    explained_codes: list[int | str] = []

    monkeypatch.setattr(
        "tools.logsAnalyse.find_explanation_for_error_code",
        explained_codes.append,
    )

    assert analyze_installation_verification_logs(logs_dir, detailed=True) is True

    output = capsys.readouterr().out
    assert explained_codes == [
        "-2147467260",
        "-5",
        "-6",
        "80073CF3",
        "0x8050111c",
    ]
    assert "https://github.com/microsoft/winget-pkgs/issues/323120" in output
    assert "这可能是因为你在清单中指定的包依赖在 winget 源中并不存在，请检查并提交依赖清单。" in output
    assert "NaN" in output


@pytest.mark.xfail
def test_analyze_installation_verification_logs_reports_extended_hints_0x(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # 当前判断日志行中是否有 0x 的逻辑，是在先匹配到错误关键词的情况下才会触发
    # 而预期是只要匹配到 0x 就会触发
    # 所以这个测试当前必定失败

    logs_dir = tmp_path / "InstallationVerificationLogs"
    logs_dir.mkdir()
    (logs_dir / "installer.log").write_text("Installer return 0x8050111c\n")
    explained_codes: list[int | str] = []

    monkeypatch.setattr(
        "tools.logsAnalyse.find_explanation_for_error_code",
        explained_codes.append,
    )

    assert analyze_installation_verification_logs(logs_dir, detailed=True) is True
    assert explained_codes == ["0x8050111c"]
