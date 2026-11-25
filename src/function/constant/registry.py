"""
和注册表相关的常量
"""

from dataclasses import dataclass, fields
from typing import Final

import yaml
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import YamlLexer  # pyright: ignore[reportMissingTypeStubs]


@dataclass
class REGISTRY_ENTRY:  # pylint: disable=too-many-instance-attributes / R0902
    """
    安装程序注册表信息类。

    Attributes:
        RegistryPath: 注册表路径。
        ProductCode: 产品代码。
        Scope: 安装范围。
        DisplayName: 显示名称。
        DisplayVersion: 显示版本。
        Publisher: 发布者。
        UninstallString: 卸载字符串。
        HelpLink: 帮助链接。
        InstallLocation: 安装位置。
        SystemComponent: 是否为系统组件。
        WindowsInstaller: 是否使用 Windows Installer 卸载。
        NoRemove: 是否禁用卸载。
        NoModify: 是否禁用修改。
        InstallSource: 安装包位置。
        EstimatedSize: 占用空间。
        URLInfoAbout: 官方网站。
        Comments: 注释。
    """

    RegistryPath: str
    ProductCode: str
    Scope: str
    DisplayName: str | None = None
    DisplayVersion: str | None = None
    Publisher: str | None = None
    UninstallString: str | None = None
    HelpLink: str | None = None
    InstallLocation: str | None = None
    SystemComponent: str | None = None
    WindowsInstaller: str | None = None
    NoRemove: str | None = None
    NoModify: str | None = None
    InstallSource: str | None = None
    EstimatedSize: str | None = None
    URLInfoAbout: str | None = None
    Comments: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str | None]):
        """
        将读到的注册表条目字典转为 REGISTRY_ENTRY 类。

        Args:
            data: 从注册表读取的条目数据字典。

        Returns:
            REGISTRY_ENTRY 类的实例。
        """

        # 只保留 class 需要的 k: v
        cls_fields: list[str] = [f.name for f in fields(cls)]
        needed_data: dict[str, str] = {
            k: v
            for k, v in data.items()
            if (v is not None) and (k in cls_fields)
        }
        return cls(**needed_data)

    def to_yaml(self) -> str:
        """
        将 REGISTRY_ENTRY 实例的数据转换为 YAML 格式的字符串。

        Returns:
            YAML 格式的字符串。
        """

        AppsAndFeaturesEntries: dict[str, str] = {
            "ProductCode": self.ProductCode
        }
        OtherEntries: dict[str, str] = {

        }

        for field in REGISTRY_FIELDS:
            field_value: str | None = getattr(self, field)
            if not field_value:
                continue

            if field in ("DisplayName", "DisplayVersion", "Publisher"):
                AppsAndFeaturesEntries[field] = field_value
            else:
                OtherEntries[field] = field_value

        data: dict[str, str | list[dict[str, str]]] = {
            "Scope": self.Scope,
            "AppsAndFeaturesEntries": [AppsAndFeaturesEntries],
        }
        if OtherEntries:
            data["OtherEntries"] = [OtherEntries]

        return yaml.dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            indent=4
        )

    def print_yaml(self) -> None:
        """
        以高亮 YAML 的形式输出 REGISTRY_ENTRY 实例。
        """

        print(self.RegistryPath)
        print(
            highlight(
                self.to_yaml(),
                YamlLexer(),
                TerminalFormatter(),  # pyright: ignore[reportUnknownArgumentType]
            )
        )


REGISTRY_FIELDS: Final = tuple(
    f.name
    for f in fields(REGISTRY_ENTRY)
    if f.name not in ("Scope", "ProductCode", "RegistryPath")
)
"""
`REGISTRY_ENTRY` 类中除 `Scope`、`ProductCode` 和 `RegistryPath` 外的所有属性名。

注意，这里是属性名（`str`），不是字段（`Field`）。
"""
