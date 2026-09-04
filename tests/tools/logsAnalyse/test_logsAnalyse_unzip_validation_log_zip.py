import zipfile
from pathlib import Path

import pytest

from tools.logsAnalyse import unzip_validation_log_zip


def test_unzip_validation_log_zip_extracts_files_and_deletes_zip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    validation_logs_dir = tmp_path / "ValidationLogs"
    zip_file_path = tmp_path / "WinGetSvc-Validation-12345-6-artifacts.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        zip_file.writestr("ValidationResult/result.json", '{"OverallResult": "Success"}')

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_DIR", validation_logs_dir)

    result = unzip_validation_log_zip(zip_file_path)

    assert result == validation_logs_dir / "WinGetSvc-Validation-12345-6-artifacts"
    assert (result / "ValidationResult" / "result.json").read_text() == '{"OverallResult": "Success"}'
    assert not zip_file_path.exists()


def test_unzip_validation_log_zip_raises_when_existing_directory_is_not_overwritten(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    validation_logs_dir = tmp_path / "ValidationLogs"
    existing_dir = validation_logs_dir / "WinGetSvc-Validation-12345-6-artifacts"
    existing_dir.mkdir(parents=True)
    existing_file = existing_dir / "existing.txt"
    existing_file.write_text("keep")
    zip_file_path = tmp_path / "WinGetSvc-Validation-12345-6-artifacts.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        zip_file.writestr("new.txt", "new")

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_DIR", validation_logs_dir)
    monkeypatch.setattr("builtins.input", lambda *args: "n")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    with pytest.raises(FileExistsError):
        unzip_validation_log_zip(zip_file_path)

    assert existing_file.read_text() == "keep"
    assert zip_file_path.exists()


def test_unzip_validation_log_zip_overwrites_existing_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    validation_logs_dir = tmp_path / "ValidationLogs"
    existing_dir = validation_logs_dir / "WinGetSvc-Validation-12345-6-artifacts"
    existing_dir.mkdir(parents=True)
    (existing_dir / "old.txt").write_text("old")
    zip_file_path = tmp_path / "WinGetSvc-Validation-12345-6-artifacts.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        zip_file.writestr("new.txt", "new")

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_DIR", validation_logs_dir)
    monkeypatch.setattr("builtins.input", lambda *args: "y")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    result = unzip_validation_log_zip(zip_file_path)

    assert result == existing_dir
    assert not (result / "old.txt").exists()
    assert (result / "new.txt").read_text() == "new"
    assert not zip_file_path.exists()


def test_unzip_validation_log_zip_overwrites_existing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    validation_logs_dir = tmp_path / "ValidationLogs"
    validation_logs_dir.mkdir()
    existing_path = validation_logs_dir / "WinGetSvc-Validation-12345-6-artifacts"
    existing_path.write_text("old")
    zip_file_path = tmp_path / "WinGetSvc-Validation-12345-6-artifacts.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        zip_file.writestr("new.txt", "new")

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_DIR", validation_logs_dir)
    monkeypatch.setattr("builtins.input", lambda *args: "y")  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]

    result = unzip_validation_log_zip(zip_file_path)

    assert result == existing_path
    assert (result / "new.txt").read_text() == "new"
    assert not zip_file_path.exists()


def test_unzip_validation_log_zip_raises_when_existing_path_is_neither_file_nor_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    validation_logs_dir = tmp_path / "ValidationLogs"
    existing_path = validation_logs_dir / "WinGetSvc-Validation-12345-6-artifacts"
    existing_path.mkdir(parents=True)
    zip_file_path = tmp_path / "WinGetSvc-Validation-12345-6-artifacts.zip"

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_DIR", validation_logs_dir)
    monkeypatch.setattr("pathlib.Path.is_file", lambda path: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("pathlib.Path.is_dir", lambda path: False)  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
    monkeypatch.setattr("builtins.input", lambda *args: "y")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    with pytest.raises(ValueError, match="既不是文件也不是目录"):
        unzip_validation_log_zip(zip_file_path)

    assert existing_path.exists()
