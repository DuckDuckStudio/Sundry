import pytest

from function.maintain import config


class Test配置信息:
    """
    对 `function.maintain.config` 模块中的 `配置信息` 类的测试。
    """

    def test_默认配置_should_be_immutable_at_every_level(self) -> None:
        """
        `配置信息.默认配置` 应在所有嵌套层级不可修改。
        """

        with pytest.raises(TypeError):
            config.配置信息.默认配置["debug"] = True  # pyright: ignore[reportIndexIssue]  # ty: ignore[invalid-assignment]

        with pytest.raises(TypeError):
            config.配置信息.默认配置["github"]["pr"]["maintainer_can_modify"] = True

    def test_get_a_copy_of_the_default_config_should_be_independently_mutable(self) -> None:
        """
        `get_a_copy_of_the_default_config` 函数应返回与默认配置相互独立的可变副本。
        """

        default_config_copy = config.配置信息.get_a_copy_of_the_default_config()
        default_config_copy["github"]["pr"]["maintainer_can_modify"] = True
        assert config.配置信息.默认配置["github"]["pr"]["maintainer_can_modify"] is False
