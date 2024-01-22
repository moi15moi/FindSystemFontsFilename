from ctypes import byref, c_bool, c_char_p, c_long, c_uint32, c_void_p, cdll, create_string_buffer, util
from enum import IntEnum
from pathlib import Path
from platform import mac_ver
from typing import Set
from .exceptions import OSNotSupported
from .system_fonts import SystemFonts


class CTFontFormat(IntEnum):
    # https://developer.apple.com/documentation/coretext/ctfontformat?language=objc
    kCTFontFormatUnrecognized = 0
    kCTFontFormatOpenTypePostScript = 1
    kCTFontFormatOpenTypeTrueType = 2
    kCTFontFormatTrueType = 3
    kCTFontFormatPostScript = 4
    kCTFontFormatBitmap = 5


class CFURLPathStyle(IntEnum):
    # https://developer.apple.com/documentation/corefoundation/cfurlpathstyle?language=objc
    kCFURLPOSIXPathStyle = 0
    kCFURLHFSPathStyle = 1
    kCFURLWindowsPathStyle = 2


class CFStringBuiltInEncodings(IntEnum):
    # https://developer.apple.com/documentation/corefoundation/cfstringbuiltinencodings?language=objc
    kCFStringEncodingMacRoman = 0
    kCFStringEncodingWindowsLatin1 = 0x0500
    kCFStringEncodingISOLatin1 = 0x0201
    kCFStringEncodingNextStepLatin = 0x0B01
    kCFStringEncodingASCII = 0x0600
    kCFStringEncodingUnicode = 0x0100
    kCFStringEncodingUTF8 = 0x08000100
    kCFStringEncodingNonLossyASCII = 0x0BFF
    kCFStringEncodingUTF16 = 0x0100
    kCFStringEncodingUTF16BE = 0x10000100
    kCFStringEncodingUTF16LE = 0x14000100
    kCFStringEncodingUTF32 = 0x0c000100
    kCFStringEncodingUTF32BE = 0x18000100
    kCFStringEncodingUTF32LE = 0x1c000100


class CFNumberType(IntEnum):
    # https://developer.apple.com/documentation/corefoundation/cfnumbertype?language=objc
    kCFNumberSInt8Type = 1
    kCFNumberSInt16Type = 2
    kCFNumberSInt32Type = 3
    kCFNumberSInt64Type = 4
    kCFNumberFloat32Type = 5
    kCFNumberFloat64Type = 6
    kCFNumberCharType = 7
    kCFNumberShortType = 8
    kCFNumberIntType = 9
    kCFNumberLongType = 10
    kCFNumberLongLongType = 11
    kCFNumberFloatType = 12
    kCFNumberDoubleType = 13
    kCFNumberCFIndexType = 14
    kCFNumberNSIntegerType = 15
    kCFNumberCGFloatType = 16
    kCFNumberMaxType = 16


class MacFonts(SystemFonts):
    _core_foundation = None
    _core_text = None
    _kCTFontURLAttribute = None
    _kCTFontFormatAttribute = None
    # CoreText has an API to get the format of the font: https://developer.apple.com/documentation/coretext/ctfontformat
    # But, the API is "semi-broken" since it says .dfont are TrueType. This is kinda true, but it is not a behaviour that we want.
    # So, we also need to check the file extension to see if the file is valid.
    VALID_FONT_FORMATS = ["ttf", "otf", "ttc", "otc"]

    def get_system_fonts_filename() -> Set[str]:
        if MacVersionHelpers.is_mac_version_or_greater(10, 6):
            if MacFonts._core_foundation is None or MacFonts._core_text is None:
                MacFonts._load_core_library()

            fonts_filename = set()

            font_collection = MacFonts._core_text.CTFontCollectionCreateFromAvailableFonts(None)
            font_array = MacFonts._core_text.CTFontCollectionCreateMatchingFontDescriptors(font_collection)
            font_count = MacFonts._core_foundation.CFArrayGetCount(font_array)

            for i in range(font_count):
                font_descriptor = MacFonts._core_foundation.CFArrayGetValueAtIndex(font_array, i)

                font_format_ptr = MacFonts._core_text.CTFontDescriptorCopyAttribute(font_descriptor, MacFonts._kCTFontFormatAttribute)
                font_format = CTFontFormat(MacFonts._cfnumber_to_uint32(font_format_ptr))
                MacFonts._core_foundation.CFRelease(font_format_ptr)

                if font_format not in (
                    CTFontFormat.kCTFontFormatOpenTypePostScript,
                    CTFontFormat.kCTFontFormatOpenTypeTrueType,
                    CTFontFormat.kCTFontFormatTrueType,
                    CTFontFormat.kCTFontFormatPostScript
                ):
                    continue

                url_ptr = MacFonts._core_text.CTFontDescriptorCopyAttribute(font_descriptor, MacFonts._kCTFontURLAttribute)
                path_ptr = MacFonts._core_text.CFURLCopyFileSystemPath(url_ptr, CFURLPathStyle.kCFURLPOSIXPathStyle)
                filename = MacFonts._cfstring_to_string(path_ptr)
                MacFonts._core_foundation.CFRelease(path_ptr)
                MacFonts._core_foundation.CFRelease(url_ptr)

                if Path(filename).suffix.lstrip(".").strip().lower() not in MacFonts.VALID_FONT_FORMATS:
                    continue

                fonts_filename.add(filename)

            MacFonts._core_foundation.CFRelease(font_array)
            MacFonts._core_foundation.CFRelease(font_collection)
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
        size = MacFonts._core_foundation.CFStringGetMaximumSizeForEncoding(length, CFStringBuiltInEncodings.kCFStringEncodingUTF8)
        buffer = create_string_buffer(size + 1)
        result = MacFonts._core_foundation.CFStringGetCString(cfstring, buffer, len(buffer), CFStringBuiltInEncodings.kCFStringEncodingUTF8)
        if result:
            return str(buffer.value, "utf-8")
        else:
            raise Exception("An unexpected error has occurred while decoding the CFString.")


    @staticmethod
    def _cfnumber_to_uint32(cfnumber: c_void_p) -> int:
        """
        Parameters:
            cfnumber (c_void_p): An CFNumber instance.
        Returns:
            The decoded CFNumber.
            If the CFNumber is not an int, it will raise an exception
        """
        value = c_uint32()
        success = MacFonts._core_foundation.CFNumberGetValue(cfnumber, CFNumberType.kCFNumberIntType, byref(value))
        if success:
            return value.value
        else:
            raise Exception("The CFNumber doesn't seems to be an kCFNumberIntType.")


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
        CFNumberRef = c_void_p
        CFNumberType = c_long

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

        # https://developer.apple.com/documentation/corefoundation/1543114-cfnumbergetvalue?language=objc
        MacFonts._core_foundation.CFNumberGetValue.restype = c_bool
        MacFonts._core_foundation.CFNumberGetValue.argtypes = [CFNumberRef, CFNumberType, c_void_p]

        # https://developer.apple.com/documentation/coretext/1509907-ctfontcollectioncreatefromavaila?language=objc
        MacFonts._core_text.CTFontCollectionCreateFromAvailableFonts.restype = c_void_p
        MacFonts._core_text.CTFontCollectionCreateFromAvailableFonts.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/coretext/1511091-ctfontcollectioncreatematchingfo?language=objc
        MacFonts._core_text.CTFontCollectionCreateMatchingFontDescriptors.restype = c_void_p
        MacFonts._core_text.CTFontCollectionCreateMatchingFontDescriptors.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/coretext/1510346-ctfontdescriptorcopyattribute?language=objc
        MacFonts._core_text.CTFontDescriptorCopyAttribute.restype = c_void_p
        MacFonts._core_text.CTFontDescriptorCopyAttribute.argtypes = [c_void_p, c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1541581-cfurlcopyfilesystempath?language=objc
        MacFonts._core_text.CFURLCopyFileSystemPath.restype = c_void_p
        MacFonts._core_text.CFURLCopyFileSystemPath.argtypes = [c_void_p, CFIndex]

        MacFonts._kCTFontURLAttribute = c_void_p.in_dll(MacFonts._core_text, "kCTFontURLAttribute")
        MacFonts._kCTFontFormatAttribute = c_void_p.in_dll(MacFonts._core_text, "kCTFontFormatAttribute")


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
