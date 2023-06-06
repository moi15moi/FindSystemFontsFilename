from ctypes import c_bool, c_char_p, c_int, c_long, c_uint32, c_void_p, cdll, create_string_buffer, util
from enum import IntEnum
from pathlib import Path
from platform import mac_ver
from typing import Set
from .exceptions import OSNotSupported
from .system_fonts import SystemFonts


class CFURLPathStyle(IntEnum):
    # https://developer.apple.com/documentation/corefoundation/cfurlpathstyle?language=objc
    kCFURLPOSIXPathStyle = 0
    kCFURLHFSPathStyle = 1
    kCFURLWindowsPathStyle = 2


class MacFonts(SystemFonts):
    _core_foundation = None
    _core_text = None
    # CoreText has an API to get the format of the font: https://developer.apple.com/documentation/coretext/ctfontformat
    # But, the API is "semi-broken" since it says .dfont are TrueType. This is kinda true, but it is not a behaviour that we want.
    # So, we only check the file extension and see if it is valid.
    VALID_FONT_FORMATS = ["ttf", "otf", "ttc"]
    kCFStringEncodingUTF8 = 0x08000100 # https://developer.apple.com/documentation/corefoundation/cfstringbuiltinencodings/kcfstringencodingutf8?language=objc

    def get_system_fonts_filename() -> Set[str]:
        if MacVersionHelpers.is_mac_version_or_greater(10, 6):
            if MacFonts._core_foundation is None or MacFonts._core_text is None:
                MacFonts._load_core_library()

            fonts_filename = set()

            font_urls = MacFonts._core_text.CTFontManagerCopyAvailableFontURLs()
            font_count = MacFonts._core_foundation.CFArrayGetCount(font_urls)

            for i in range(font_count):
                url = MacFonts._core_foundation.CFArrayGetValueAtIndex(font_urls, i)

                filename = MacFonts._cfstring_to_string(MacFonts._core_text.CFURLCopyFileSystemPath(url, CFURLPathStyle.kCFURLPOSIXPathStyle))

                if Path(filename).suffix.lstrip(".").strip().lower() in MacFonts.VALID_FONT_FORMATS:
                    fonts_filename.add(filename)

            MacFonts._core_foundation.CFRelease(font_urls)
        else:
            raise OSNotSupported("FindSystemFontsFilename only works on Mac 10.6 or more")

        return fonts_filename

    @staticmethod
    def _cfstring_to_string(cfstring: c_void_p) -> str:
        """
        Parameters:
            cfstring (c_void_p): An CFString instance.
        Returns:
            The decoded CFString.
        """
        length = MacFonts._core_foundation.CFStringGetLength(cfstring)
        size = MacFonts._core_foundation.CFStringGetMaximumSizeForEncoding(length, MacFonts.kCFStringEncodingUTF8)
        buffer = create_string_buffer(size + 1)
        result = MacFonts._core_foundation.CFStringGetCString(cfstring, buffer, len(buffer), MacFonts.kCFStringEncodingUTF8)
        if result:
            return str(buffer.value, 'utf-8')
        else:
            raise Exception("An unexpected error has occurred while decoded the CFString.")

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
        CFStringEncoding = c_uint32
        CFURLPathStyle = c_int

        # https://developer.apple.com/documentation/corefoundation/1521153-cfrelease
        MacFonts._core_foundation.CFRelease.restype = c_void_p
        MacFonts._core_foundation.CFRelease.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1388772-cfarraygetcount?language=objc
        MacFonts._core_foundation.CFArrayGetCount.restype = CFIndex
        MacFonts._core_foundation.CFArrayGetCount.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1388767-cfarraygetvalueatindex?language=objc
        MacFonts._core_foundation.CFArrayGetValueAtIndex.restype = c_void_p
        MacFonts._core_foundation.CFArrayGetValueAtIndex.argtypes = [c_void_p, CFIndex]

        # https://developer.apple.com/documentation/corefoundation/1542853-cfstringgetlength?language=objc
        MacFonts._core_foundation.CFStringGetLength.restype = CFIndex
        MacFonts._core_foundation.CFStringGetLength.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1542143-cfstringgetmaximumsizeforencodin?language=objc
        MacFonts._core_foundation.CFStringGetMaximumSizeForEncoding.restype = CFIndex
        MacFonts._core_foundation.CFStringGetMaximumSizeForEncoding.argtypes = [c_void_p, CFStringEncoding]

        # https://developer.apple.com/documentation/corefoundation/1542721-cfstringgetcstring?language=objc
        MacFonts._core_foundation.CFStringGetCString.restype = c_bool
        MacFonts._core_foundation.CFStringGetCString.argtypes = [c_void_p, c_char_p, CFIndex, CFStringEncoding]

        # https://developer.apple.com/documentation/coretext/1499478-ctfontmanagercopyavailablefontur?language=objc
        MacFonts._core_text.CTFontManagerCopyAvailableFontURLs.restype = c_void_p
        MacFonts._core_text.CTFontManagerCopyAvailableFontURLs.argtypes = []

        # https://developer.apple.com/documentation/corefoundation/1541581-cfurlcopyfilesystempath?language=objc
        MacFonts._core_text.CFURLCopyFileSystemPath.restype = c_void_p
        MacFonts._core_text.CFURLCopyFileSystemPath.argtypes = [c_void_p, CFURLPathStyle]

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

        return system_major > minimum_major or (system_major == minimum_major and system_minor >= minimum_minor)
