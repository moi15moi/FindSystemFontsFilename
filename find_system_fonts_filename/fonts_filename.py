from pathlib import Path
from platform import system
from os import environ
from typing import Set
from .exceptions import OSNotSupported
from .system_fonts import SystemFonts

__all__ = [
    "get_system_fonts_filename",
    "install_font",
    "uninstall_font",
]


def get_system_fonts_class() -> SystemFonts:
    system_name = system()

    if system_name == "Windows":
        from .windows import WindowsFonts
        return WindowsFonts

    elif system_name == "Linux":
        # ANDROID_ROOT or ANDROID_BOOTLOGO - https://stackoverflow.com/a/66174754/15835974
        if any(t in environ.keys() for t in ("ANDROID_ROOT", "ANDROID_BOOTLOGO")):
            from .android_fonts import AndroidFonts
            return AndroidFonts
        else:
            from .linux_fonts import LinuxFonts
            return LinuxFonts

    elif system_name == "Darwin":
        from .mac import MacFonts
        return MacFonts

    else:
        raise OSNotSupported("FindSystemFontsFilename only works on Windows, Mac, Linux and Android.")


def get_system_fonts_filename() -> Set[str]:
    return get_system_fonts_class().get_system_fonts_filename()


def install_font(font_filename: Path, add_font_to_registry: bool = False) -> None:
    """Install a font from its filename

    Args:
        add_font_to_registry: It will add the font in the Windows Registry.
            This argument is Windows Only.
    """
    return get_system_fonts_class().install_font(font_filename, add_font_to_registry)


def uninstall_font(font_filename: Path, remove_font_in_registry: bool = False) -> None:
    """Uninstall a font from its filename

    Args:
        remove_font_in_registry: It will also remove the Windows Registry entry that has been added
            when install_font with add_font_to_registry set to True has been called.
            This argument is Windows Only.
    """
    return get_system_fonts_class().uninstall_font(font_filename, remove_font_in_registry)
