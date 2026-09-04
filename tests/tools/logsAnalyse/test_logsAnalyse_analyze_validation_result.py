import json
from pathlib import Path

import pytest

from tools.logsAnalyse import analyze_validation_result


def test_analyze_validation_result_returns_false_when_directory_is_missing(tmp_path: Path):
    assert analyze_validation_result(tmp_path / "ValidationResult") is False


def test_analyze_validation_result_ignores_json_with_unexpected_name(tmp_path: Path):
    validation_result_dir = tmp_path / "ValidationResult"
    validation_result_dir.mkdir()
    (validation_result_dir / "other.json").write_text("not valid JSON")

    assert analyze_validation_result(validation_result_dir) is False


def test_analyze_validation_result_returns_false_for_successful_result(tmp_path: Path):
    validation_result_dir = tmp_path / "ValidationResult"
    validation_result_dir.mkdir()
    (validation_result_dir / "InstallationVerification_Result.json").write_text('{"OverallResult": "Success", "AnalysisResults": []}')

    assert analyze_validation_result(validation_result_dir) is False


def test_analyze_validation_result_ignores_non_exe_run_info_results(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    validation_result_dir = tmp_path / "ValidationResult"
    validation_result_dir.mkdir()
    (validation_result_dir / "InstallationVerification_Result.json").write_text(
        json.dumps(
            {
                "OverallResult": "Failure",
                "AnalysisResults": [
                    {
                        "AnalysisType": "Not ExeRunInfo",
                        "Diagnostics": {
                            "ignored.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 999,
                            },
                        },
                    }
                ],
            }
        )
    )

    assert analyze_validation_result(validation_result_dir) is False
    assert capsys.readouterr().out == ""


def test_analyze_validation_result_reports_nonzero_exe_run_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    validation_result_dir = tmp_path / "ValidationResult"
    validation_result_dir.mkdir()
    (validation_result_dir / "InstallationVerification_Result.json").write_text(
        json.dumps(
            {
                "OverallResult": "Failure",
                "AnalysisResults": [
                    {
                        "AnalysisType": "ExeRunInfo",
                        "Diagnostics": {
                            "installer.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 999,
                                "ErrorStream": "installer error",
                            },
                            "installer0.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 123,
                                "ErrorStream": "installer error",
                            },
                            "installer1.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 123,
                                "ErrorStream": "installer error",
                            },
                            "installer2.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 123,
                                "ErrorStream": "installer error",
                            },
                            "installer3.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 123,
                                "ErrorStream": "installer error",
                            },
                            "invalid.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": "not an int",
                                "ErrorStream": "invalid error",
                            },
                            "passed.exe": {
                                "ExecutionStatusResult": "Pass",
                                "ExitCode": 0,
                            },
                            "failed_with_zero.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 0,
                                "ErrorStream": "installer error",
                            },
                        },
                    }
                ],
            }
        )
    )
    explained_codes: list[int | str] = []

    monkeypatch.setattr(
        "tools.logsAnalyse.find_explanation_for_error_code",
        explained_codes.append,
    )

    assert analyze_validation_result(validation_result_dir) is True

    output = capsys.readouterr().out
    assert "installer.exe" in output
    assert "installer error" in output
    assert "退出代码" in output
    assert explained_codes == [999, 123]


def test_analyze_validation_result_reports_output_stream(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    validation_result_dir = tmp_path / "ValidationResult"
    validation_result_dir.mkdir()
    (validation_result_dir / "InstallationVerification_Result.json").write_text(
        json.dumps(
            {
                "OverallResult": "Failure",
                "AnalysisResults": [
                    {
                        "AnalysisType": "ExeRunInfo",
                        "Diagnostics": {
                            "installer.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 999,
                                "OutputStream": "installer output",
                            },
                        },
                    }
                ],
            }
        )
    )

    assert analyze_validation_result(validation_result_dir) is True

    output = capsys.readouterr().out
    assert "installer.exe" in output
    assert "输出:" in output
    assert "installer output" in output


def test_analyze_validation_result_combines_error_and_output_streams(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    validation_result_dir = tmp_path / "ValidationResult"
    validation_result_dir.mkdir()
    (validation_result_dir / "InstallationVerification_Result.json").write_text(
        json.dumps(
            {
                "OverallResult": "Failure",
                "AnalysisResults": [
                    {
                        "AnalysisType": "ExeRunInfo",
                        "Diagnostics": {
                            "installer.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 999,
                                "ErrorStream": "installer error",
                                "OutputStream": "installer output",
                            },
                        },
                    }
                ],
            }
        )
    )

    assert analyze_validation_result(validation_result_dir) is True

    output = capsys.readouterr().out
    assert "installer error" in output
    assert "installer output" in output
    assert output.index("installer error") < output.index("installer output")


def test_analyze_validation_result_does_not_print_when_nonzero_result_has_no_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    validation_result_dir = tmp_path / "ValidationResult"
    validation_result_dir.mkdir()
    (validation_result_dir / "InstallationVerification_Result.json").write_text(
        json.dumps(
            {
                "OverallResult": "Failure",
                "AnalysisResults": [
                    {
                        "AnalysisType": "ExeRunInfo",
                        "Diagnostics": {
                            "installer.exe": {
                                "ExecutionStatusResult": "Fail",
                                "ExitCode": 999,
                            },
                        },
                    }
                ],
            }
        )
    )

    assert analyze_validation_result(validation_result_dir) is True
    output = capsys.readouterr().out
    assert "输出:" not in output
