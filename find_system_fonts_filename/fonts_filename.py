import sys
from pathlib import Path
from platform import system
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

    if system_name == "Windows" or sys.platform == "cygwin":
        from .windows import WindowsFonts
        return WindowsFonts

    elif system_name == "Linux":
        if hasattr(sys, "getandroidapilevel"):
            from .android import AndroidFonts
            return AndroidFonts
        else:
            from .linux import LinuxFonts
            return LinuxFonts

    elif system_name == "Darwin":
        from .mac import MacFonts
        return MacFonts

    else:
        raise OSNotSupported(f"FindSystemFontsFilename only works on Windows, Mac, Linux and Android. You're on \"{system_name}\"")


def get_system_fonts_filename() -> Set[str]:
    return get_system_fonts_class().get_system_fonts_filename()


def install_font(font_filename: Path, add_font_to_registry: bool = False) -> None:
    """Install a font from its filename

    Args:
        add_font_to_registry: It will add the font in the Windows Registry.
            This argument is Windows Only.
            It adds the font to the Windows Registry only if the Windows version is 10.0.17083 (also known as version 1803) or later.
            Prior to this version, Windows did not support font registration in the registry.
    """
    if not font_filename.is_file():
        raise FileNotFoundError(f"The file \"{font_filename}\" doesn't exist")

    return get_system_fonts_class().install_font(font_filename, add_font_to_registry)


def uninstall_font(font_filename: Path, remove_font_in_registry: bool = False) -> None:
    """Uninstall a font from its filename

    Args:
        remove_font_in_registry: It will also remove the Windows Registry entry that has been added
            when install_font with add_font_to_registry set to True has been called.
            This argument is Windows Only.
            It adds the font to the Windows Registry only if the Windows version is 10.0.17083 (also known as version 1803) or later.
            Prior to this version, Windows did not support font registration in the registry.
    """
    if not font_filename.is_file():
        raise FileNotFoundError(f"The file \"{font_filename}\" doesn't exist")

    return get_system_fonts_class().uninstall_font(font_filename, remove_font_in_registry)
