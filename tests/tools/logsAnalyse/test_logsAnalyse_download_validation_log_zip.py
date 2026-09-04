from pathlib import Path
from typing import Any, NoReturn

import pytest
from requests import HTTPError

from tools.logsAnalyse import download_validation_log_zip


class FakeResponse:
    """
    模拟 requests.Response 对象的类，用于测试下载验证日志 zip 文件的功能。
    """

    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self) -> None:
        pass


@pytest.mark.parametrize("download_url", [None, ""])
def test_download_validation_log_zip_returns_none_without_url(download_url: None | str):
    assert download_validation_log_zip(download_url) is None


def test_download_validation_log_zip_raises_for_invalid_url():
    with pytest.raises(ValueError, match="验证日志 zip 的下载链接不匹配预期正则"):
        download_validation_log_zip("https://example.com/validation.zip")


def test_download_validation_log_zip_downloads_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    download_url = "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip"
    response = FakeResponse(b"zip content")

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_ZIP_DIR", tmp_path / "Zips")

    def fake_get(url: str, timeout: Any) -> FakeResponse:
        del url, timeout
        return response

    monkeypatch.setattr("tools.logsAnalyse.requests.get", fake_get)

    result = download_validation_log_zip(download_url)

    expected_path = tmp_path / "Zips" / "WinGetSvc-Validation-12345-6-artifacts.zip"
    assert result == expected_path
    assert expected_path.read_bytes() == b"zip content"


def test_download_validation_log_zip_returns_none_when_existing_file_is_not_overwritten(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    download_url = "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip"
    zip_directory = tmp_path / "Zips"
    existing_path = zip_directory / "WinGetSvc-Validation-12345-6-artifacts.zip"
    zip_directory.mkdir()
    existing_path.write_bytes(b"existing content")

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_ZIP_DIR", zip_directory)
    monkeypatch.setattr("builtins.input", lambda *args: "n")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert download_validation_log_zip(download_url) is None
    assert existing_path.read_bytes() == b"existing content"


def test_download_validation_log_zip_overwrites_existing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    download_url = "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip"
    response = FakeResponse(b"new content")
    zip_directory = tmp_path / "Zips"
    existing_path = zip_directory / "WinGetSvc-Validation-12345-6-artifacts.zip"
    zip_directory.mkdir()
    existing_path.write_bytes(b"existing content")

    def fake_get(url: str, timeout: Any) -> FakeResponse:
        del url, timeout
        return response

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_ZIP_DIR", zip_directory)
    monkeypatch.setattr("tools.logsAnalyse.requests.get", fake_get)
    monkeypatch.setattr("builtins.input", lambda *args: "y")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert download_validation_log_zip(download_url) == existing_path
    assert existing_path.read_bytes() == b"new content"


def test_download_validation_log_zip_returns_none_for_http_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    download_url = "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip"

    def raise_http_error(*args: Any, **kwargs: Any) -> NoReturn:
        raise HTTPError("download failed")

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_ZIP_DIR", tmp_path / "Zips")
    monkeypatch.setattr("tools.logsAnalyse.requests.get", raise_http_error)

    assert download_validation_log_zip(download_url) is None


def test_download_validation_log_zip_returns_none_when_writing_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    download_url = "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip"
    response = FakeResponse(b"zip content")

    monkeypatch.setattr("tools.logsAnalyse.VALIDATION_LOGS_ZIP_DIR", tmp_path / "Zips")

    def fake_get(url: str, timeout: Any) -> FakeResponse:
        del url, timeout
        return response

    def raise_write_error(*args: Any, **kwargs: Any) -> NoReturn:
        raise OSError("write failed")

    monkeypatch.setattr("tools.logsAnalyse.requests.get", fake_get)
    monkeypatch.setattr("builtins.open", raise_write_error)

    assert download_validation_log_zip(download_url) is None
