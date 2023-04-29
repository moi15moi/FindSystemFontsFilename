from platform import system
from .exceptions import OSNotSupported


def get_system_fonts_filename():
    system_name = system()

    if system_name == "Windows":
        from .windows_fonts import WindowsFonts
        return WindowsFonts.get_system_fonts_filename()

    elif system_name == "Linux":
        from .linux_fonts import LinuxFonts
        return LinuxFonts.get_system_fonts_filename()

    elif system_name == "Darwin":
        from .mac_fonts import MacFonts
        return MacFonts.get_system_fonts_filename()

    else:
        raise OSNotSupported("FindSystemFontsFilename only works on Windows, Mac and Linux.")
