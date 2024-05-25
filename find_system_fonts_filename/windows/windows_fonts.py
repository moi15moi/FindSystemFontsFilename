from .gdi import ENUMLOGFONTEXW, FontFileInfo, FontRealizationInfo, GDI, TEXTMETRICW
from .msvcrt import MSVCRT
from .version_helpers import WindowsVersionHelpers
from ..exceptions import OSNotSupported
from ..system_fonts import SystemFonts
from ctypes import addressof, byref, cast, create_string_buffer, create_unicode_buffer, POINTER, py_object, sizeof, wintypes, wstring_at
from sys import getwindowsversion
from typing import Set

__all__ = ["WindowsFonts"]


def enum_font_families_w(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRICW, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value

    # It seems that font_type can be 0. In those case, the font format is .fon
    # We also discard RASTER_FONTTYPE which are bitmap font
    if not (font_type & enum_data.gdi.RASTER_FONTTYPE) and font_type:
        lfFaceName = create_unicode_buffer(enum_data.gdi.LF_FACESIZE)
        enum_data.msvcrt.wcsncpy_s(lfFaceName, enum_data.gdi.LF_FACESIZE, logfont.elfFullName, enum_data.msvcrt.TRUNCATE)
        logfont.elfLogFont.lfFaceName = lfFaceName.value

        hfont = enum_data.gdi.CreateFontIndirectW(byref(logfont.elfLogFont))
        enum_data.gdi.SelectObject(enum_data.dc, hfont)

        # GetFontRealizationInfo and GetFontFileInfo aren't documented by Microsoft.
        # With both method, it is possible to get the font file path with GDI.
        # Inspired by https://gitlab.winehq.org/wine/wine/-/blob/b210a204137dec8d2126ca909d762454fd47e963/dlls/dwrite/gdiinterop.c#L784-805
        font_realization_info = FontRealizationInfo()
        font_realization_info.size = sizeof(FontRealizationInfo)
        enum_data.gdi.GetFontRealizationInfo(enum_data.dc, byref(font_realization_info))

        needed = wintypes.DWORD(0)
        enum_data.gdi.GetFontFileInfo(font_realization_info.instance_id, 0, None, needed, byref(needed))
        if not needed.value:
            raise Exception("Failed to get font file info size")
        
        font_file_info_buffer = create_string_buffer(needed.value)
        if not enum_data.gdi.GetFontFileInfo(font_realization_info.instance_id, 0, font_file_info_buffer, needed, byref(needed)):
            raise Exception("GetFontFileInfo failed")

        font_file_info = cast(font_file_info_buffer, POINTER(FontFileInfo))
        path_offset = getattr(FontFileInfo, "path").offset
        path = wstring_at(addressof(font_file_info.contents) + path_offset)
        enum_data.fonts_filename.add(path)

        enum_data.gdi.DeleteObject(hfont)

    return True


def enum_fonts_w(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRICW, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value
    enum_data.gdi.EnumFontFamiliesW(enum_data.dc, logfont.elfLogFont.lfFaceName, enum_data.gdi.ENUMFONTFAMEXPROC(enum_font_families_w), lparam)

    return True


class EnumData:
    def __init__(self, gdi: GDI, msvcrt: MSVCRT, dc: wintypes.HDC, fonts_filename: Set[str]):
        self.gdi = gdi
        self.msvcrt = msvcrt
        self.dc = dc
        self.fonts_filename = fonts_filename


class WindowsFonts(SystemFonts):

    def get_system_fonts_filename() -> Set[str]:
        windows_version = getwindowsversion()
        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater(windows_version):
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        gdi = GDI()
        msvcrt = MSVCRT()
        fonts_filename = set()

        dc = gdi.CreateCompatibleDC(None)

        enum_data = EnumData(gdi, msvcrt, dc, fonts_filename)
        object_enum_data = py_object(enum_data)

        # See this link to understand why we do call EnumFontsW and then a EnumFontFamiliesW
        # https://stackoverflow.com/a/62405274/15835974
        gdi.EnumFontsW(dc, None, gdi.ENUMFONTFAMEXPROC(enum_fonts_w), addressof(object_enum_data))
        gdi.DeleteDC(dc)

        return fonts_filename
