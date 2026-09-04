from pathlib import Path

import pytest

from tools.logsAnalyse import find_explanation_for_error_code


def test_find_explanation_for_error_code_reads_local_exit_codes_csv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    exit_codes_csv_path = tmp_path / "Tools" / "ManualValidation" / "ExitCodes.csv"
    exit_codes_csv_path.parent.mkdir(parents=True)
    exit_codes_csv_path.write_text(
        '"Hex","Dec","InvDec","Symbol","Description"\n"0000002A","42","-4294967254","ERROR_EXAMPLE","Example description."\n',
        encoding="utf-8",
    )

    monkeypatch.setattr("tools.logsAnalyse.读取配置", lambda *args, **kwargs: str(tmp_path))  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    find_explanation_for_error_code(42)

    output = capsys.readouterr().out
    assert "0000002A" in output
    assert "42" in output
    assert "ERROR_EXAMPLE" in output
    assert "Example description." in output


def test_find_explanation_for_error_code_falls_back_to_github_when_local_csv_is_not_readable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    exit_codes_csv_path = tmp_path / "Tools" / "ManualValidation" / "ExitCodes.csv"
    exit_codes_csv_path.parent.mkdir(parents=True)
    exit_codes_csv_path.write_text("unreadable", encoding="utf-8")
    csv_content = '"Hex","Dec","InvDec","Symbol","Description"\n"0000002A","42","-4294967254","ERROR_EXAMPLE","Example description."\n'

    def raise_permission_error(*args: object, **kwargs: object) -> None:
        raise PermissionError("local CSV is not readable")

    monkeypatch.setattr("tools.logsAnalyse.读取配置", lambda *args, **kwargs: str(tmp_path))  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("builtins.open", raise_permission_error)
    monkeypatch.setattr("tools.logsAnalyse.获取GitHub文件内容", lambda *args, **kwargs: csv_content)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    find_explanation_for_error_code(42)

    output = capsys.readouterr().out
    assert "ERROR_EXAMPLE" in output
    assert "Example description." in output


def test_find_explanation_for_error_code_falls_back_to_github(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    csv_content = '"Hex","Dec","InvDec","Symbol","Description"\n"0000002A","42","-4294967254","ERROR_EXAMPLE","Example description."\n'
    calls: list[tuple[str, str, object]] = []

    def fake_get_file_content(repository: str, file_path: str, token: object) -> str:
        calls.append((repository, file_path, token))
        return csv_content

    monkeypatch.setattr("tools.logsAnalyse.读取配置", lambda *args, **kwargs: None)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.获取GitHub文件内容", fake_get_file_content)
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: "token")

    find_explanation_for_error_code("ERROR_EXAMPLE")

    output = capsys.readouterr().out
    assert "ERROR_EXAMPLE" in output
    assert "Example description." in output
    assert calls == [("microsoft/winget-pkgs", "Tools/ManualValidation/ExitCodes.csv", "token")]


@pytest.mark.parametrize("exit_code", ["missing", 999])
def test_find_explanation_for_error_code_does_not_print_when_code_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    exit_code: str | int,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("tools.logsAnalyse.读取配置", lambda *args, **kwargs: str(tmp_path))  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)
    monkeypatch.setattr("tools.logsAnalyse.获取GitHub文件内容", lambda *args, **kwargs: None)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    find_explanation_for_error_code(exit_code)

    assert capsys.readouterr().out == ""
