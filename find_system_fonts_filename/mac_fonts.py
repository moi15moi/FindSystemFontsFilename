from CoreText import CTFontManagerCopyAvailableFontURLs
from pathlib import Path
from platform import mac_ver
from typing import Set
from .exceptions import OSNotSupported
from .system_fonts import SystemFonts


class MacFonts(SystemFonts):
    # CoreText has an API to get the format of the font: https://developer.apple.com/documentation/coretext/ctfontformat
    # But, the API is "semi-broken" since it says .dfont are TrueType. This is kinda true, but it is not a behaviour that we want.
    # So, we only check the file extension and see if it is valid.
    VALID_FONT_FORMATS = [".ttf", ".ttc", ".otf"]

    def get_system_fonts_filename() -> Set[str]:
        if MacVersionHelpers.is_mac_version_or_greater(10, 6):
            fonts_filename = set()
            fontURLs = CTFontManagerCopyAvailableFontURLs()

            for url in fontURLs:
                if Path(url.path()).suffix.lower() in MacFonts.VALID_FONT_FORMATS:
                    fonts_filename.add(str(url.path()))
        else:
            raise OSNotSupported("FindSystemFontsFilename only works on Mac 10.6 or more")

        return fonts_filename


class MacVersionHelpers:
    @staticmethod
    def is_mac_version_or_greater(minimum_major: int, minimum_minor: int) -> bool:
        """
        Parameters:
            major (int): The minimum major OS version number.
            minor (int): The minimum minor OS version number.
        Returns:
            True if the specified version matches or if it is greater than the version of the current Mac OS. Otherwise, False.
        """

        system_major, system_minor = mac_ver()[0].split(".")[:2]

        system_major = int(system_major)
        system_minor = int(system_minor)

        return minimum_major > system_major or (system_major == minimum_major and system_minor >= minimum_minor)
