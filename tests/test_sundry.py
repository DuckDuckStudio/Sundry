import pytest  # noqa: I001 - 和 isort 冲突

from sundry import _can_it_run_on_non_windows_systems  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize(
    ("tool", "args", "excepted"),
    [
        ("remove", [], False),
        ("ignore", [], False),
        ("ignore", ["add", "xxx"], False),
        ("ignore", ["list"], True),
        ("version", [], True)
    ]
)
def test_can_it_run_on_non_windows_systems(tool: str, args: list[str], excepted: bool) -> None:
    assert _can_it_run_on_non_windows_systems(tool, args) == excepted
