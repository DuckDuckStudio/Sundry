import pytest
from colorama import Fore

from function.constant.logsAnalyse import Explanation, LogKeyWord


def test_explanation_returns_message_without_color():
    explanation = Explanation("explanation")

    assert explanation.get_colored_message() == "explanation"


def test_explanation_returns_colored_message():
    explanation = Explanation("explanation", Fore.YELLOW)

    assert explanation.get_colored_message() == f"{Fore.YELLOW}explanation{Fore.RESET}"


@pytest.mark.parametrize(
    ("content", "file_name", "file", "expected"),
    [
        ("keyword", None, None, True),
        ("KEYWORD appears", None, None, True),
        ("other text", None, None, False),
        ("keyword", "actual.log", "expected.log", False),
        ("keyword", "path/Expected.LOG", "expected.log", True),
    ],
)
def test_log_keyword_matching(content: str, file_name: str | None, file: str | None, expected: bool):
    keyword = LogKeyWord("Keyword", Explanation("explanation"), file=file)

    assert keyword.matched(content, file_name=file_name) is expected
