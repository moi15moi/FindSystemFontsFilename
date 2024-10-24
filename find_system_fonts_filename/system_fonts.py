from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Set


class SystemFonts(ABC):
    @staticmethod
    @abstractmethod
    def get_system_fonts_filename() -> Set[str]:
        """
        Return an set of all the installed fonts filename.
        """
        pass

    @staticmethod
    @abstractmethod
    def install_font(font_filename: Path, add_font_to_registry: bool = False) -> None:
        """
        Install a font from it's filename.
        """
        pass

    @staticmethod
    @abstractmethod
    def uninstall_font(font_filename: Path, remove_font_in_registry: bool) -> None:
        """
        Uninstall a font from it's filename.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_font_fallback(family_name: str, font_weight: int, is_italic: bool, characters: str) -> Optional[Path]:
        """
        TODO.
        """
        pass
