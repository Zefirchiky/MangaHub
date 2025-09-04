from __future__ import annotations

from pathlib import Path

from config import CM
from loguru import logger
from PySide6.QtCore import QByteArray, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel, QSizePolicy
from resources.enums import IconsEnum
from utils import SVGManipulator
from config import Config


class SVGIcon(QLabel):
    """SVGIcon is a QLabel that displays an svg icon.
    It can be colored, hovered and changed to another icon on click.
    It can also have a second icon that can be changed to at any time."""

    _pixmap_cache: dict[str, QPixmap] = {}
    _default_size = ()

    pressed = Signal()

    def __init__(
        self,
        svg_path: Path | None = None,
        svg_content: str | None = None,
        default=True,
        parent=None,
    ):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )  # TODO: Will probably change pos at hover, simplify with SVGManipulator

        self.set_icon(svg_path, svg_content)

        self.color = CM().icon
        self.bg_color: QColor | None = None

        self._hover_effect = False
        self._hover_color: QColor | None = None
        self._hover_size_factor = 1.1
        self._is_hovered = False

        self.second_icon: SVGManipulator | None = None
        self._is_second_icon = False
        self._change_connected = False

        self.change_icon_on_click = False

        if default:
            self.set_size(*self._default_size)
            self.set_color(self.color)

    def set_icon(
        self, svg_path: Path | None = None, svg_content: str | None = None
    ) -> "SVGIcon":
        if not svg_path and not svg_content:
            raise ValueError("Either svg_path or svg_content must be provided")
        self.svg = SVGManipulator(svg_file_path=svg_path, svg_content=svg_content)
        return self

    def set_second_icon(self, icon: SVGIcon | SVGManipulator) -> "SVGIcon":
        """Sets a second icon, that can be changed to at any time"""
        self.second_icon = icon.svg if isinstance(icon, SVGIcon) else icon
        self.set_change_icon_on_click(True)
        return self

    def set_size(self, w: int = 32, h: int = 32) -> "SVGIcon":
        self.setFixedSize(w, h)
        return self

    def set_color(
        self,
        color: CM.color_type | None = None,
        target_color: CM.color_type | None = None,
        fill: bool = True,
        fill_if_none: bool = False,
        stroke: bool = True,
        stroke_if_none: bool = False,
        update=True,
    ) -> "SVGIcon":
        self.color = QColor(color or self.color)
        if target_color:
            target_color = QColor(target_color)
        self.svg.change_color(
            self.color.name(),
            target_color.name() if target_color else None,
            fill,
            fill_if_none,
            stroke,
            stroke_if_none,
        )
        if update:
            self.setPixmap(self.get_pixmap())
        return self

    def set_bg_color(
        self, color: CM.color_type | None = None, update=False
    ) -> "SVGIcon":
        self.bg_color = QColor(color or self.bg_color)
        self.svg.add_background(self.bg_color.name())
        if update:
            self.setPixmap(self.get_pixmap())
        return self

    def set_hover(
        self,
        color: CM.color_type | None = None,
        size_factor: float = 1.1,
        change_to: bool = True,
        update=False,
    ) -> "SVGIcon":
        """Sets hover effect on the icon

        Args:
            color (str, optional): Hover color. Defaults to ColorManager.icon.hover
            size_factor (float, optional): Icon dimensions will be multiplied by. Defaults to 1.1.
            change_to (bool, optional): Is hover effect active. Defaults to True.
            update (bool, optional): Update pixmap. If True will reconstruct the pixmap. Takes resources. Defaults to False.
        """
        self._hover_effect = change_to
        if change_to:
            self.set_hover_color(color)
            self.set_hover_size_factor(size_factor)
        if update:
            self.setPixmap(self.get_pixmap())
        return self

    def set_hover_color(self, color=None, update=False) -> "SVGIcon":
        self._hover_color = QColor(color or CM().icon)
        self._hover_effect = True
        if update:
            self.setPixmap(self.get_pixmap())
        return self

    def set_hover_size_factor(self, factor: float, update=False) -> "SVGIcon":
        self._hover_size_factor = factor
        self._hover_effect = True
        if update:
            self.setPixmap(self.get_pixmap())
        return self

    def change_icon(self, icon_n=-1) -> "SVGIcon":
        """
        Change icon to the second icon if it exists

        Args:
            icon_n (int): If -1, change to the opposite icon. If 0, change to the first icon. If 1, change to the second icon.
        """
        if icon_n == -1:
            self._is_second_icon = not self._is_second_icon
        else:
            self._is_second_icon = bool(icon_n)
        self.setPixmap(self.get_pixmap())
        return self

    def set_change_icon_on_click(self, change=False) -> "SVGIcon":
        self.change_icon_on_click = change
        if not self.second_icon:
            raise ValueError("No second icon set")
        if not self._change_connected:
            self._change_connected = True
            self.pressed.connect(self.change_icon)
        return self

    def enterEvent(self, event):
        if self._hover_effect:
            self._is_hovered = True
            self.setPixmap(self.get_pixmap())
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._hover_effect:
            self._is_hovered = False
            self.setPixmap(self.get_pixmap())
        super().leaveEvent(event)

    def mousePressEvent(self, ev):
        self.pressed.emit()
        return super().mousePressEvent(ev)

    def get_pixmap(self, w: int = 0, h: int = 0, icon_n: int = -1) -> QPixmap:
        """Creates a pixmap from the svg content

        Args:
            w (int, optional): Width of the pixmap. If 0 will use the default width. Defaults to 0.
            h (int, optional): Height of the pixmap. If 0 will use the default height. Defaults to 0.
            icon_n (int, optional): Pixmap of which icon to give. If -1 will use the current icon, 0 will use the first icon, 1 will use the second icon. Defaults to -1.

        Returns:
            QPixmap: _description_
        """
        base_w, base_h = self.width(), self.height()
        if self._is_hovered and self._hover_effect:
            size = (
                int(base_w * self._hover_size_factor),
                int(base_h * self._hover_size_factor),
            )
        else:
            size = (w or base_w, h or base_h)

        if icon_n == -1:
            svg_content = (
                self.svg.get_svg_string(pretty=False)
                if not self._is_second_icon or not self.second_icon
                else self.second_icon.get_svg_string(pretty=False)
            )
        elif icon_n == 0:
            svg_content = self.svg.get_svg_string(pretty=False)
        elif icon_n == 1 and self.second_icon:
            svg_content = self.second_icon.get_svg_string(pretty=False)
        elif icon_n == 1 and not self.second_icon:
            raise ValueError("No second icon set")
        else:
            raise ValueError("Invalid icon_n")

        cache_key = f"{hash(svg_content)}_{size[0]}_{size[1]}_{self.color.name()}"

        if cache_key not in self._pixmap_cache.keys():
            renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))

            pixmap = QPixmap(*size)
            pixmap.fill(CM.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            self._pixmap_cache[cache_key] = pixmap

        return self._pixmap_cache[cache_key]

    def get_qicon(self) -> QIcon:
        icon = QIcon(self.get_pixmap(icon_n=0))
        if self.second_icon:
            icon.addPixmap(self.get_pixmap(icon_n=1))
        return icon

    def reset(self) -> "SVGIcon":
        """Reset icon to its original state"""
        self.svg = SVGManipulator()
        self._hover_effect = False
        self._is_hovered = False
        self.setPixmap(self.get_pixmap())
        return self

    def copy(self) -> "SVGIcon":
        icon = (
            SVGIcon(svg_content=self.svg.get_svg_string(pretty=False))
            .set_size(self.width(), self.height())
            .set_color(self.color, update=False)
        )
        if self.second_icon:
            icon.set_second_icon(self.second_icon).set_change_icon_on_click(
                self.change_icon_on_click
            )
        if self._hover_effect:
            icon.set_hover(self._hover_color, self._hover_size_factor)
        icon.setPixmap(icon.get_pixmap())
        return icon


class IconRepo:
    """Stores and manages icons. Prevents loading the same icon multiple times."""

    _instance: IconRepo | None = None
    _initialized = False
    _icons: dict[str, SVGIcon] = {}

    Icons = IconsEnum

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True

    @classmethod
    def add_icon(cls, icon_name: str | IconsEnum, icon: SVGIcon):
        icon_name = icon_name.value if isinstance(icon_name, IconsEnum) else icon_name
        cls._icons[icon_name] = icon
        return cls

    @classmethod
    def get(cls, icon_name: str | IconsEnum, copy=True) -> SVGIcon:
        icon_name = icon_name.value if isinstance(icon_name, IconsEnum) else icon_name
        if icon_name not in cls._icons:
            logger.warning(
                f"Icon {icon_name} not found in the repo. Loading from {Config.Dirs.RESOURCES.ICONS}"
            )
            cls._icons[icon_name] = SVGIcon(
                svg_path=Config.Dirs.RESOURCES.ICONS / f"{icon_name}.svg"
            )
        return cls._icons[icon_name].copy() if copy else cls._icons[icon_name]

    @classmethod
    def get_icon_with_color(self, icon_name: str | IconsEnum, color: str) -> SVGIcon:
        icon = self.get(icon_name)
        icon.set_color(color)
        return icon

    @staticmethod
    def init_default_icons():
        SVGIcon._default_size = (32, 32)

        for icon in IconsEnum:
            IconRepo.add_icon(icon, SVGIcon(Config.Dirs.RESOURCES.ICONS / f"{icon.value}.svg"))

        # UTILS
        IconRepo.get(IconRepo.Icons.EYE, False).set_size(20, 20).set_second_icon(
            IconRepo.get(IconRepo.Icons.NOT_EYE).set_color("grey")
        )

        full_menu = IconRepo.get(IconRepo.Icons.MENU)
        full_menu.svg.change_color(full_menu.color.name(), fill_if_none=True)
        IconRepo.get(IconRepo.Icons.MENU, False).set_second_icon(full_menu)
