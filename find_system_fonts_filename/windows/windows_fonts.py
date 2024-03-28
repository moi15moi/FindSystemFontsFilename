from .directwrite import (
    DWRITE_FACTORY_TYPE,
    DWRITE_FONT_FILE_TYPE,
    DWRITE_LOCALITY,
    DWRITE_FONT_SIMULATIONS,
    IDWriteFontFileLoader,
    IDWriteLocalFontFileLoader,
    IDWriteFontFile,
    IDWriteFontFaceReference,
    IDWriteFontSet,
    IDWriteFontFace,
    IDWriteFont,
    IDWriteFontList,
    IDWriteFontFamily,
    IDWriteFontCollection,
    IDWriteFontCollection1,
    IDWriteFontSetBuilder,
    IDWriteGdiInterop,
    IDWriteFactory,
    IDWriteFactory1,
    IDWriteFactory2,
    IDWriteFactory3,
    DirectWrite,
)
from .gdi import GDI, LOGFONTW, ENUMLOGFONTEXW, TEXTMETRIC, CharacterSet
from .gdiplus import FontStyle, GDIPlus, GdiplusStartupInput, GdiplusStartupOutput
from .version_helpers import WindowsVersionHelpers
from comtypes import COMError, GUID, HRESULT, IUnknown, STDMETHOD
from ctypes import addressof, byref, create_unicode_buffer, POINTER, py_object, windll, wintypes
from os.path import isfile
from sys import getwindowsversion
from typing import List, Set
from ..exceptions import OSNotSupported
from ..system_fonts import SystemFonts

__all__ = [
    "WindowsFonts"
]


def enum_font_families_w(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRIC, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value

    hfont = enum_data.gdi.CreateFontIndirectW(byref(logfont.elfLogFont))
    enum_data.gdi.SelectObject(enum_data.dc, hfont)

    error = False
    try:
        font_face = POINTER(IDWriteFontFace)()
        enum_data.gdi_interop.CreateFontFaceFromHdc(enum_data.dc, byref(font_face))
    except COMError:
        error = True
    
    if not error:
        font_files = POINTER(IDWriteFontFile)()
        font_face.GetFiles(byref(wintypes.UINT(1)), byref(font_files))

        font_file_reference_key = wintypes.LPCVOID()
        font_file_reference_key_size = wintypes.UINT()
        font_files.GetReferenceKey(byref(font_file_reference_key), byref(font_file_reference_key_size))

        loader = POINTER(IDWriteFontFileLoader)()
        font_files.GetLoader(byref(loader))

        local_loader = loader.QueryInterface(IDWriteLocalFontFileLoader)

        path_len = wintypes.UINT()
        local_loader.GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, byref(path_len))

        buffer = create_unicode_buffer(path_len.value + 1)
        local_loader.GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, buffer, len(buffer))
        
        enum_data.fonts_filename.add(buffer.value)
        enum_data.gdi.DeleteObject(hfont)

    return True


def enum_fonts_w(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRIC, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value

    if not (font_type & enum_data.gdi.RASTER_FONTTYPE):
        enum_data.gdi.EnumFontFamiliesW(enum_data.dc, logfont.elfLogFont.lfFaceName, enum_data.gdi.ENUMFONTFAMEXPROC(enum_font_families_w), lparam)

    return True


class EnumData:
    def __init__(self, gdi, gdi_interop, fonts_filename, dc, already):
        self.gdi = gdi
        self.gdi_interop = gdi_interop
        self.fonts_filename = fonts_filename
        self.dc = dc
        self.already = already


class WindowsFonts(SystemFonts):
    VALID_FONT_FORMATS = [
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_CFF,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_TRUETYPE,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_OPENTYPE_COLLECTION,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_TRUETYPE_COLLECTION,
    ]

    def get_system_fonts_filename() -> Set[str]:
        windows_version = getwindowsversion()
        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater(windows_version):
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        gdi = GDI()
        dwrite = DirectWrite()
        fonts_filename = set()

        dwrite_factory = POINTER(IDWriteFactory)()
        dwrite.DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, dwrite_factory._iid_, byref(dwrite_factory))

        dc = gdi.CreateCompatibleDC(None)

        gdi_interop = POINTER(IDWriteGdiInterop)()
        dwrite_factory.GetGdiInterop(byref(gdi_interop))

        enum_data = EnumData(gdi, gdi_interop, fonts_filename, dc, False)
        object_enum_data = py_object(enum_data)

        gdi.EnumFontsW(dc, None, gdi.ENUMFONTFAMEXPROC(enum_fonts_w), addressof(object_enum_data))
        gdi.DeleteDC(dc)

        return fonts_filename
