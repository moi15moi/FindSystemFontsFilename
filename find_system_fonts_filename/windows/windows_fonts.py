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
from .gdi import GDI, LOGFONTW
from .gdiplus import FontStyle, GDIPlus, GdiplusStartupInput, GdiplusStartupOutput
from .version_helpers import WindowsVersionHelpers
from comtypes import COMError, GUID, HRESULT, IUnknown, STDMETHOD
from ctypes import byref, create_unicode_buffer, POINTER, windll, wintypes
from os.path import isfile
from sys import getwindowsversion
from typing import List, Set
from ..exceptions import OSNotSupported
from ..system_fonts import SystemFonts

__all__ = [
    "WindowsFonts"
]

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
        gdi_plus = GDIPlus()
        dwrite = DirectWrite()
        fonts_filename = set()

        token = wintypes.ULONG()
        startup_in = GdiplusStartupInput(1, None, False, False)
        startup_out = GdiplusStartupOutput()
        gdi_plus.GdiplusStartup(byref(token), byref(startup_in), byref(startup_out))

        gdi_font_collection = wintypes.LPVOID()
        gdi_plus.GdipNewInstalledFontCollection(byref(gdi_font_collection))

        gdi_family_count = wintypes.INT()
        gdi_plus.GdipGetFontCollectionFamilyCount(gdi_font_collection, byref(gdi_family_count))

        gdi_families = (wintypes.LPVOID * gdi_family_count.value)()
        num_found = wintypes.INT()
        gdi_plus.GdipGetFontCollectionFamilyList(gdi_font_collection, gdi_family_count, gdi_families, byref(num_found))

        dc = gdi.CreateCompatibleDC(None)
        graphics = wintypes.LPVOID()
        gdi_plus.GdipCreateFromHDC(dc, byref(graphics))

        dwrite_factory = POINTER(IDWriteFactory)()
        dwrite.DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, dwrite_factory._iid_, byref(dwrite_factory))

        gdi_interop = POINTER(IDWriteGdiInterop)()
        dwrite_factory.GetGdiInterop(byref(gdi_interop))

        font_styles_possibility = [
            FontStyle.FontStyleRegular,
            FontStyle.FontStyleBold,
            FontStyle.FontStyleItalic,
            FontStyle.FontStyleBoldItalic,
        ]

        for family in gdi_families:
            for font_style in font_styles_possibility:
                is_style_available = wintypes.BOOL()
                gdi_plus.GdipIsStyleAvailable(family, font_style, byref(is_style_available))

                if not is_style_available:
                    continue

                gdi_font = wintypes.LPVOID()
                # The emSize AND Unit doesn't mather
                gdi_plus.GdipCreateFont(family, 16, font_style, gdi_plus.UnitPoint, byref(gdi_font))

                logfont = LOGFONTW()
                gdi_plus.GdipGetLogFontW(gdi_font, graphics, byref(logfont))

                dwrite_font = POINTER(IDWriteFont)()
                gdi_interop.CreateFontFromLOGFONT(logfont, byref(dwrite_font))

                gdi_plus.GdipDeleteFont(gdi_font)

                # big simulations = font_face.GetSimulations()

                # We need to convert the IDWriteFont back to IDWriteFontFamily
                # because GDI can miss discard a font if 2 font file are identical.
                dwrite_family = POINTER(IDWriteFontFamily)()
                dwrite_font.GetFontFamily(byref(dwrite_family))

                for j in range(dwrite_family.GetFontCount()):
                    try:
                        font = POINTER(IDWriteFont)()
                        dwrite_family.GetFont(j, byref(font))
                    except COMError:
                        # If the file doesn't exist, DirectWrite raise an exception
                        continue

                    if font.GetSimulations() != DWRITE_FONT_SIMULATIONS.DWRITE_FONT_SIMULATIONS_NONE:
                        continue

                    font_face = POINTER(IDWriteFontFace)()
                    font.CreateFontFace(byref(font_face))

                    file_count = wintypes.UINT()
                    font_face.GetFiles(byref(file_count), None)

                    font_files = (POINTER(IDWriteFontFile) * file_count.value)()
                    font_face.GetFiles(byref(file_count), font_files)

                    for font_file in font_files:
                        font_file_reference_key = wintypes.LPCVOID()
                        font_file_reference_key_size = wintypes.UINT()
                        font_file.GetReferenceKey(byref(font_file_reference_key), byref(font_file_reference_key_size))

                        loader = POINTER(IDWriteFontFileLoader)()
                        font_file.GetLoader(byref(loader))

                        local_loader = loader.QueryInterface(IDWriteLocalFontFileLoader)

                        is_supported_font_type = wintypes.BOOLEAN()
                        font_file_type = wintypes.UINT()
                        font_face_type = wintypes.UINT()
                        number_of_faces = wintypes.UINT()
                        font_file.Analyze(byref(is_supported_font_type), byref(font_file_type), byref(font_face_type), byref(number_of_faces))

                        if DWRITE_FONT_FILE_TYPE(font_file_type.value) not in WindowsFonts.VALID_FONT_FORMATS:
                            continue

                        path_len = wintypes.UINT()
                        local_loader.GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, byref(path_len))

                        buffer = create_unicode_buffer(path_len.value + 1)
                        local_loader.GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, buffer, len(buffer))

                        fonts_filename.add(buffer.value)

        gdi_plus.GdipDeleteGraphics(graphics)
        gdi.DeleteDC(dc)
        gdi_plus.GdiplusShutdown(token)

        return fonts_filename
