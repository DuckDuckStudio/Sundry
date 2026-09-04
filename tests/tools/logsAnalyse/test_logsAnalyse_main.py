from pathlib import Path

import ajaw
import pytest

from tools.logsAnalyse import main


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ([], "以下参数是必需的：pr"),
        (["123", "--d"], "无法识别的参数：--d"),
    ],
)
def test_main_returns_error_for_invalid_argument_count(args: list[str], message: str, capsys: pytest.CaptureFixture[str]):
    ajaw.load_translations(lang="zh_CN")

    assert main(args) == 1
    assert message in capsys.readouterr().err


def test_main_returns_error_when_validation_logs_cannot_be_downloaded(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("tools.logsAnalyse.get_validation_log_zip_from_args", lambda args: None)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    assert main(["123"]) == 1


def test_main_returns_success_when_no_possible_problem_is_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr("tools.logsAnalyse.get_validation_log_zip_from_args", lambda args: tmp_path / "logs.zip")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.unzip_validation_log_zip", lambda file_path: tmp_path)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_validation_result", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_installation_verification_logs", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    assert main(["123", "--no-keep-logs"]) == 0
    output = capsys.readouterr().out
    assert "来查看一般错误/异常" in output  # 给出启用详细模式的提示


def test_main_returns_success_without_hint_in_detailed_mode_when_no_problem_is_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr("tools.logsAnalyse.get_validation_log_zip_from_args", lambda args: tmp_path / "logs.zip")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.unzip_validation_log_zip", lambda file_path: tmp_path)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_validation_result", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_installation_verification_logs", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    assert main(["123", "--detailed", "--no-keep-logs"]) == 0
    output = capsys.readouterr().out
    assert "来查看一般错误/异常" not in output  # 在已启用详细模式时，不给出启用了详细模式的提示


def test_main_returns_error_and_passes_detailed_mode_when_a_problem_is_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    calls: list[tuple[str, bool]] = []
    monkeypatch.setattr("tools.logsAnalyse.get_validation_log_zip_from_args", lambda args: tmp_path / "logs.zip")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.unzip_validation_log_zip", lambda file_path: tmp_path)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr(
        "tools.logsAnalyse.analyze_validation_result",
        lambda path, detailed: calls.append(("validation", detailed)) or True,  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    )
    monkeypatch.setattr(
        "tools.logsAnalyse.analyze_installation_verification_logs",
        lambda path, detailed: calls.append(("installation", detailed)) or False,  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    )

    assert main(["123", "--detailed", "--no-keep-logs"]) == 1
    assert calls == [("validation", True), ("installation", True)]


def test_main_asks_to_keep_logs_when_option_is_not_specified(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    opened_files: list[Path] = []
    monkeypatch.setattr("tools.logsAnalyse.get_validation_log_zip_from_args", lambda args: tmp_path / "logs.zip")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.unzip_validation_log_zip", lambda file_path: logs_dir)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_validation_result", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_installation_verification_logs", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("builtins.input", lambda prompt: "y")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.open_file", lambda file: opened_files.append(file) or 0)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    assert main(["123"]) == 0
    assert logs_dir.is_dir()
    assert opened_files == [str(logs_dir)]


def test_main_deletes_logs_when_no_keep_logs_option_is_given(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    monkeypatch.setattr("tools.logsAnalyse.get_validation_log_zip_from_args", lambda args: tmp_path / "logs.zip")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.unzip_validation_log_zip", lambda file_path: logs_dir)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_validation_result", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_installation_verification_logs", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    assert main(["123", "--no-keep-logs"]) == 0
    assert not logs_dir.exists()


def test_main_keep_logs_when_keep_logs_option_is_given(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    opened_files: list[Path] = []
    monkeypatch.setattr("tools.logsAnalyse.get_validation_log_zip_from_args", lambda args: tmp_path / "logs.zip")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.unzip_validation_log_zip", lambda file_path: logs_dir)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_validation_result", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.analyze_installation_verification_logs", lambda path, detailed: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.open_file", lambda file: opened_files.append(file) or 0)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    assert main(["123", "--keep-logs"]) == 0
    assert logs_dir.exists()
    assert opened_files == [str(logs_dir)]
