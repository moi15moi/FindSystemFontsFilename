from ctypes import c_bool, c_char_p, c_long, c_void_p, cdll, create_string_buffer, util
from os import pathconf
from pathlib import Path
from platform import mac_ver
from typing import Set
from .exceptions import OSNotSupported
from .system_fonts import SystemFonts


class MacFonts(SystemFonts):
    _core_foundation = None
    _core_text = None
    # CoreText has an API to get the format of the font: https://developer.apple.com/documentation/coretext/ctfontformat
    # But, the API is "semi-broken" since it says .dfont are TrueType. This is kinda true, but it is not a behaviour that we want.
    # So, we only check the file extension and see if it is valid.
    VALID_FONT_FORMATS = ["ttf", "ttc", "otf"]

    def get_system_fonts_filename() -> Set[str]:
        if MacVersionHelpers.is_mac_version_or_greater(10, 6):
            if MacFonts._core_foundation is None or MacFonts._core_text is None:
                MacFonts._load_core_library()

            fonts_filename = set()

            font_urls = MacFonts._core_text.CTFontManagerCopyAvailableFontURLs()
            font_count = MacFonts._core_foundation.CFArrayGetCount(font_urls)

            max_length = pathconf("/", "PC_PATH_MAX")

            for i in range(font_count):
                url = MacFonts._core_foundation.CFArrayGetValueAtIndex(font_urls, i)

                file_name_ptr = create_string_buffer(max_length)
                no_error = MacFonts._core_foundation.CFURLGetFileSystemRepresentation(url, True, file_name_ptr, max_length)

                if no_error:
                    filename = file_name_ptr.value.decode()

                    if Path(filename).suffix.lstrip(".").strip() in MacFonts.VALID_FONT_FORMATS:
                        fonts_filename.add(filename)
                else:
                    raise Exception("An unexpected error has occurred while decoded the CFURL.")

            MacFonts._core_foundation.CFRelease(font_urls)
        else:
            raise OSNotSupported("FindSystemFontsFilename only works on Mac 10.6 or more")

        return fonts_filename

    @staticmethod
    def _load_core_library():
        core_foundation_library_name = util.find_library("CoreFoundation")
        # Hack for compatibility with macOS greater or equals to 11.0.
        # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L10-L14
        if core_foundation_library_name is None:
            core_foundation_library_name = "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        MacFonts._core_foundation = cdll.LoadLibrary(core_foundation_library_name)

        core_text_library_name = util.find_library("CoreText")
        # Hack for compatibility with macOS greater or equals to 11.0.
        # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L520-L524
        if core_text_library_name is None:
            core_text_library_name = "/System/Library/Frameworks/CoreText.framework/CoreText"
        MacFonts._core_text = cdll.LoadLibrary(core_text_library_name)

        CFIndex = c_long

        MacFonts._core_foundation.CFRelease.restype = c_void_p
        MacFonts._core_foundation.CFRelease.argtypes = [c_void_p]

        MacFonts._core_foundation.CFArrayGetCount.restype = CFIndex
        MacFonts._core_foundation.CFArrayGetCount.argtypes = [c_void_p]

        MacFonts._core_foundation.CFArrayGetValueAtIndex.restype = c_void_p
        MacFonts._core_foundation.CFArrayGetValueAtIndex.argtypes = [c_void_p, CFIndex]

        MacFonts._core_foundation.CFURLGetFileSystemRepresentation.restype = c_bool
        MacFonts._core_foundation.CFURLGetFileSystemRepresentation.argtypes = [c_void_p, c_bool, c_char_p, CFIndex]

        MacFonts._core_text.CTFontManagerCopyAvailableFontURLs.restype = c_void_p
        MacFonts._core_text.CTFontManagerCopyAvailableFontURLs.argtypes = []


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
