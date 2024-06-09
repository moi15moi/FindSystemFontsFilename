from .core_foundation import CFNumberType, CFStringBuiltInEncodings, CFURLPathStyle, CoreFoundation
from .core_text import CoreText, CTFontFormat, CTFontManagerScope
from .version_helpers import MacVersionHelpers
from ctypes import byref, c_uint32, c_void_p, create_string_buffer
from pathlib import Path
from typing import Set
from ..exceptions import FindSystemFontsFilenameException, OSNotSupported, SystemApiError
from ..system_fonts import SystemFonts

__all__ = ["MacFonts"]


class MacFonts(SystemFonts):
    # CoreText has an API to get the format of the font: https://developer.apple.com/documentation/coretext/ctfontformat
    # But, the API is "semi-broken" since it says .dfont are TrueType. This is kinda true, but it is not a behaviour that we want.
    # So, we also need to check the file extension to see if the file is valid.
    VALID_FONT_FORMATS = ["ttf", "otf", "ttc", "otc"]

    def get_system_fonts_filename() -> Set[str]:
        if not MacVersionHelpers.is_mac_version_or_greater(10, 6):
            raise OSNotSupported("FindSystemFontsFilename only works on Mac 10.6 or more")

        fonts_filename = set()
        core_foundation = CoreFoundation()
        core_text = CoreText()

        font_collection = core_text.CTFontCollectionCreateFromAvailableFonts(None)
        font_array = core_text.CTFontCollectionCreateMatchingFontDescriptors(font_collection)
        font_count = core_foundation.CFArrayGetCount(font_array)

        for i in range(font_count):
            font_descriptor = core_foundation.CFArrayGetValueAtIndex(font_array, i)

            font_format_ptr = core_text.CTFontDescriptorCopyAttribute(font_descriptor, core_text.kCTFontFormatAttribute)
            font_format = CTFontFormat(MacFonts._cfnumber_to_uint32(font_format_ptr))
            core_foundation.CFRelease(font_format_ptr)

            if font_format not in (
                CTFontFormat.kCTFontFormatOpenTypePostScript,
                CTFontFormat.kCTFontFormatOpenTypeTrueType,
                CTFontFormat.kCTFontFormatTrueType,
                CTFontFormat.kCTFontFormatPostScript
            ):
                continue

            url_ptr = core_text.CTFontDescriptorCopyAttribute(font_descriptor, core_text.kCTFontURLAttribute)
            path_ptr = core_text.CFURLCopyFileSystemPath(url_ptr, CFURLPathStyle.kCFURLPOSIXPathStyle)
            filename = MacFonts._cfstring_to_string(path_ptr)
            core_foundation.CFRelease(path_ptr)
            core_foundation.CFRelease(url_ptr)

            if Path(filename).suffix.lstrip(".").strip().lower() not in MacFonts.VALID_FONT_FORMATS:
                continue

            fonts_filename.add(filename)

        core_foundation.CFRelease(font_array)
        core_foundation.CFRelease(font_collection)

        return fonts_filename


    def install_font(font_filename: Path, windows_flags: bool) -> None:
        if not MacVersionHelpers.is_mac_version_or_greater(10, 6):
            raise OSNotSupported("FindSystemFontsFilename only works on Mac 10.6 or more")

        core_foundation = CoreFoundation()
        core_text = CoreText()

        file_path_string_ref = core_foundation.CFStringCreateWithCString(None, str(font_filename).encode("utf-8"), CFStringBuiltInEncodings.kCFStringEncodingUTF8)
        url = core_foundation.CFURLCreateWithFileSystemPath(None, file_path_string_ref, CFURLPathStyle.kCFURLPOSIXPathStyle, False)

        is_success = core_text.CTFontManagerRegisterFontsForURL(url, CTFontManagerScope.kCTFontManagerScopeUser, None)

        core_foundation.CFRelease(url)
        core_foundation.CFRelease(file_path_string_ref)

        if not is_success:
            raise FindSystemFontsFilenameException(f"The font file \"{font_filename}\" could not be installed.")


    def uninstall_font(font_filename: Path, windows_flags: bool) -> None:
        if not MacVersionHelpers.is_mac_version_or_greater(10, 6):
            raise OSNotSupported("FindSystemFontsFilename only works on Mac 10.6 or more")

        core_foundation = CoreFoundation()
        core_text = CoreText()

        file_path_string_ref = core_foundation.CFStringCreateWithCString(None, str(font_filename).encode("utf-8"), CFStringBuiltInEncodings.kCFStringEncodingUTF8)
        url = core_foundation.CFURLCreateWithFileSystemPath(None, file_path_string_ref, CFURLPathStyle.kCFURLPOSIXPathStyle, False)

        is_success = core_text.CTFontManagerUnregisterFontsForURL(url, CTFontManagerScope.kCTFontManagerScopeUser, None)

        core_foundation.CFRelease(url)
        core_foundation.CFRelease(file_path_string_ref)

        if not is_success:
            raise FindSystemFontsFilenameException(f"The font file \"{font_filename}\" could not be uninstalled.")


    @staticmethod
    def _cfstring_to_string(cfstring: c_void_p) -> str:
        """
        Parameters:
            cfstring (c_void_p): An CFString instance.
        Returns:
            The decoded CFString.
        """
        core_foundation = CoreFoundation()

        length = core_foundation.CFStringGetLength(cfstring)
        size = core_foundation.CFStringGetMaximumSizeForEncoding(length, CFStringBuiltInEncodings.kCFStringEncodingUTF8)
        buffer = create_string_buffer(size + 1)
        result = core_foundation.CFStringGetCString(cfstring, buffer, len(buffer), CFStringBuiltInEncodings.kCFStringEncodingUTF8)
        if result:
            return str(buffer.value, "utf-8")
        else:
            raise SystemApiError("An unexpected error has occurred while decoding the CFString.")


    @staticmethod
    def _cfnumber_to_uint32(cfnumber: c_void_p) -> int:
        """
        Parameters:
            cfnumber (c_void_p): An CFNumber instance.
        Returns:
            The decoded CFNumber.
            If the CFNumber is not an int, it will raise an exception
        """
        core_foundation = CoreFoundation()

        value = c_uint32()
        success = core_foundation.CFNumberGetValue(cfnumber, CFNumberType.kCFNumberIntType, byref(value))
        if success:
            return value.value
        else:
            raise SystemApiError("The CFNumber doesn't seems to be an kCFNumberIntType.")
