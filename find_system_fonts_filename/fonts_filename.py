from platform import system
from os import environ
from test.support import is_android
from typing import Set
from .exceptions import OSNotSupported


def get_system_fonts_filename() -> Set[str]:
    system_name = system()

    if system_name == "Windows":
        from .windows_fonts import WindowsFonts
        return WindowsFonts.get_system_fonts_filename()

    elif system_name == "Linux":

        print(f"is the system android ?{is_android}")

        # ANDROID_ROOT or ANDROID_BOOTLOGO - https://stackoverflow.com/a/66174754/15835974
        if any(t in environ.keys() for t in ("ANDROID_ROOT", "ANDROID_BOOTLOGO")):
            from .android_fonts import AndroidFonts
            print("get_system_fonts_filename - AndroidFonts")
            return AndroidFonts.get_system_fonts_filename()
        else:
            from .linux_fonts import LinuxFonts
            print("get_system_fonts_filename - LinuxFonts")
            return LinuxFonts.get_system_fonts_filename()

    elif system_name == "Darwin":
        from .mac_fonts import MacFonts
        return MacFonts.get_system_fonts_filename()

    else:
        raise OSNotSupported("FindSystemFontsFilename only works on Windows, Mac and Linux.")
