import pytest

from tools.logsAnalyse import match_validation_log_download_url


@pytest.mark.parametrize("check_text", [None, "", "Validation completed without a log download link."])
def test_match_validation_log_download_url_returns_none_when_url_is_missing(check_text: None | str):
    assert match_validation_log_download_url(check_text) is None


def test_match_validation_log_download_url_returns_url_from_check_text():
    assert (
        match_validation_log_download_url("Validation logs are available at https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip")
        == "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip"
    )


@pytest.mark.parametrize(
    "check_text",
    [
        "https://example.com/artifacts/WinGetSvc-Validation-12345-6-artifacts.zip",
        "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-artifacts.zip",
        "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-12345-678-90-artifacts.zip",
    ],
)
def test_match_validation_log_download_url_returns_none_for_invalid_url(check_text: str):
    assert match_validation_log_download_url(check_text) is None
