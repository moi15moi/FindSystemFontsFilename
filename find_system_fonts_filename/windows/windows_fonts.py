import winreg
from .user32 import User32
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
from .gdi import GDI, ENUMLOGFONTEXW, TEXTMETRIC
from .gdiplus import FontStyle, GDIPlus, GdiplusStartupInput, GdiplusStartupOutput
from .msvcrt import MSVCRT
from .version_helpers import WindowsVersionHelpers
from ..exceptions import OSNotSupported
from ..system_fonts import SystemFonts
from os.path import isfile
from comtypes import COMError
from ctypes import addressof, byref, create_unicode_buffer, POINTER, py_object, wintypes
from sys import getwindowsversion
from typing import Set

__all__ = ["WindowsFonts"]

def get_filepath_from_IDWriteFontFace(font_face) -> Set[str]:
    fonts_filename: Set[str] = set()

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

        path_len = wintypes.UINT()
        local_loader.GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, byref(path_len))

        buffer = create_unicode_buffer(path_len.value + 1)
        local_loader.GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, buffer, len(buffer))

        fonts_filename.add(buffer.value)
    return fonts_filename


def enum_font_families_w(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRIC, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value

    lfFaceName = create_unicode_buffer(enum_data.gdi.LF_FACESIZE)
    enum_data.msvcrt.wcsncpy_s(lfFaceName, enum_data.gdi.LF_FACESIZE, logfont.elfFullName, enum_data.msvcrt.TRUNCATE)
    logfont.elfLogFont.lfFaceName = lfFaceName.value

    hfont = enum_data.gdi.CreateFontIndirectW(byref(logfont.elfLogFont))
    enum_data.gdi.SelectObject(enum_data.dc, hfont)

    error = False
    try:
        font_face = POINTER(IDWriteFontFace)()
        enum_data.gdi_interop.CreateFontFaceFromHdc(enum_data.dc, byref(font_face))
    except COMError:
        error = True
    
    if not error:
        enum_data.fonts_filename.update(get_filepath_from_IDWriteFontFace(font_face))
    enum_data.gdi.DeleteObject(hfont)

    return True


def enum_fonts_w(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRIC, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value

    if not (font_type & enum_data.gdi.RASTER_FONTTYPE):
        enum_data.gdi.EnumFontFamiliesW(enum_data.dc, logfont.elfLogFont.lfFaceName, enum_data.gdi.ENUMFONTFAMEXPROC(enum_font_families_w), lparam)

    return True


class EnumData:
    def __init__(self, gdi: GDI, gdi_interop: POINTER(IDWriteGdiInterop), msvcrt: MSVCRT, fonts_filename: Set[str], dc: wintypes.HDC):
        self.gdi = gdi
        self.gdi_interop = gdi_interop
        self.msvcrt = msvcrt
        self.fonts_filename = fonts_filename
        self.dc = dc


class WindowsFonts(SystemFonts):

    VALID_FONT_FORMATS = [
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_CFF,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_TRUETYPE,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_OPENTYPE_COLLECTION,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_TRUETYPE_COLLECTION,
    ]

    def get_system_fonts_filename() -> Set[str]:
        windows_version = getwindowsversion()

        if WindowsVersionHelpers.is_windows_10_or_greater(windows_version):
            fonts_filename = WindowsFonts._get_fonts_filename_windows_10_or_more()
        elif WindowsVersionHelpers.is_windows_vista_sp2_or_greater(windows_version):
            fonts_filename = WindowsFonts._get_fonts_filename_windows_vista_sp2_or_more()
        else:
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        return fonts_filename

    @staticmethod
    def _get_fonts_filename_windows_10_or_more() -> Set[str]:
        """
        Return an set of all the installed fonts filename.
        """

        dwrite = DirectWrite()
        fonts_filename = set()

        dwrite_factory = POINTER(IDWriteFactory3)()
        dwrite.DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, IDWriteFactory3._iid_, byref(dwrite_factory))

        font_set = POINTER(IDWriteFontSet)()
        dwrite_factory.GetSystemFontSet(byref(font_set))

        for i in range(font_set.GetFontCount()):
            font_face_reference = POINTER(IDWriteFontFaceReference)()
            font_set.GetFontFaceReference(i, byref(font_face_reference))

            locality = font_face_reference.GetLocality()
            if DWRITE_LOCALITY(locality) != DWRITE_LOCALITY.DWRITE_LOCALITY_LOCAL:
                continue

            font_file = POINTER(IDWriteFontFile)()
            font_face_reference.GetFontFile(byref(font_file))

            loader = POINTER(IDWriteFontFileLoader)()
            font_file.GetLoader(byref(loader))

            font_file_reference_key = wintypes.LPCVOID()
            font_file_reference_key_size = wintypes.UINT()
            font_file.GetReferenceKey(byref(font_file_reference_key), byref(font_file_reference_key_size))

            # For a user, even if IDWriteFontFaceReference::GetLocality returned DWRITE_LOCALITY_LOCAL,
            # the QueryInterface always fails for one specific font.
            # I did a bunch of tests with him to try to understand why it fails.
            # Here are my conclusions:
            # First, with IDWriteFontFace3::GetInformationalStrings, we found the family name of the problematic font. It was "Levenim MT".
            # Secondly, WindowsFonts._get_fonts_filename_windows_vista_sp2_or_more doesn't list "Levenim MT",
            # so QueryInterface doesn't raise an exception.
            # Thirdly, EnumFontFamiliesEx didn't enumerate "Levenim MT". Also, TextOut also doesn't display the font.
            # Fourthly, if we search "Levenim MT" with IDWriteFontSet::GetMatchingFonts, the font is not found.
            # Fifthly, the font doesn't show up in "C:\Windows\Fonts".
            # Sixthly, in Word, Aegisub, Paint.NET, libass, and VSFilter the font doesn't show up.
            # Finally, with IDWriteFontFileStream, we have been able to get the file.
            #   So the font should be physically on the hard drive, but we couldn't find it.
            #   If we are able to get the data of the font file, why can't we display the font in any software?
            # This seems to be a DirectWrite bug. To bypass it, if QueryInterface fails, ignore the font.
            # Anyways, the font cannot be displayed, so it doesn't matter.
            try:
                local_loader = loader.QueryInterface(IDWriteLocalFontFileLoader)
            except COMError:
                continue

            path_len = wintypes.UINT()
            local_loader.GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, byref(path_len))

            buffer = create_unicode_buffer(path_len.value + 1)
            local_loader.GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, buffer, len(buffer))

            font_filename = buffer.value
            if isfile(font_filename):
                is_supported_font_type = wintypes.BOOLEAN()
                font_file_type = wintypes.UINT()
                font_face_type = wintypes.UINT()
                number_of_faces = wintypes.UINT()
                font_file.Analyze(byref(is_supported_font_type), byref(font_file_type), byref(font_face_type), byref(number_of_faces))

                if DWRITE_FONT_FILE_TYPE(font_file_type.value) in WindowsFonts.VALID_FONT_FORMATS:
                    fonts_filename.add(buffer.value)

        return fonts_filename

    @staticmethod
    def _get_fonts_filename_windows_vista_sp2_or_more() -> Set[str]:
        """
        Return an set of all the installed fonts filename.
        """
        if WindowsFonts._DWriteCreateFactory is None:
            WindowsFonts._load_DWriteCreateFactory()

        dwrite = DirectWrite()
        fonts_filename = set()

        dwrite_factory = POINTER(IDWriteFactory)()
        dwrite.DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, IDWriteFactory._iid_, byref(dwrite_factory))

        sys_collection = POINTER(IDWriteFontCollection)()
        dwrite_factory.GetSystemFontCollection(byref(sys_collection), False)

        for i in range(sys_collection.GetFontFamilyCount()):
            family = POINTER(IDWriteFontFamily)()
            sys_collection.GetFontFamily(i, byref(family))

            for j in range(family.GetFontCount()):
                try:
                    font = POINTER(IDWriteFont)()
                    family.GetFont(j, byref(font))
                except COMError:
                    # If the file doesn't exist, DirectWrite raise an exception
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

        return fonts_filename

    @staticmethod
    def get_font_family_name(font_file_path: str) -> str:
        windows_version = getwindowsversion()
        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater(windows_version):
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        gdi_plus = GDIPlus()

        token = wintypes.ULONG()
        startup_in = GdiplusStartupInput(1, None, False, False)
        startup_out = GdiplusStartupOutput()
        gdi_plus.GdiplusStartup(byref(token), byref(startup_in), byref(startup_out))

        gdi_font_collection = wintypes.LPVOID()
        gdi_plus.GdipNewPrivateFontCollection(byref(gdi_font_collection))

        #gdi_plus.GdipPrivateAddFontFile(gdi_font_collection, r"C:\Users\moi15moi\Desktop\diwani.ttf")
        #gdi_plus.GdipPrivateAddFontFile(gdi_font_collection, r"C:\Windows\Fonts\SitkaB.ttc")
        gdi_plus.GdipPrivateAddFontFile(gdi_font_collection, font_file_path)

        gdi_family_count = wintypes.INT()
        gdi_plus.GdipGetFontCollectionFamilyCount(gdi_font_collection, byref(gdi_family_count))

        gdi_families = (wintypes.LPVOID * gdi_family_count.value)()
        num_found = wintypes.INT()
        gdi_plus.GdipGetFontCollectionFamilyList(gdi_font_collection, gdi_family_count, gdi_families, byref(num_found))

        total_family_name = ""

        for family in gdi_families:
            family_name = create_unicode_buffer(gdi_plus.LF_FACESIZE)
            gdi_plus.GdipGetFamilyName(family, family_name, gdi_plus.LANG_NEUTRAL)
            total_family_name += f"{family_name.value} & " 
        total_family_name = total_family_name.rstrip(" & ")

        total_family_name += " (FontBase)"

        gdi_plus.GdipDeletePrivateFontCollection(byref(gdi_font_collection))
        gdi_plus.GdiplusShutdown(token)

        return total_family_name

    @staticmethod
    def install_font(font_file_path: str):

        gdi = GDI()
        user32 = User32()

        USER_FONT_REG_PATH = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts"

        family_name = WindowsFonts.get_font_family_name(font_file_path)

        gdi.AddFontResourceW(font_file_path)

        reg_font_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, USER_FONT_REG_PATH)
        winreg.SetValueEx(reg_font_key, family_name, 0, winreg.REG_SZ, font_file_path)
        reg_font_key.Close()

        #user32.SendMessageW(user32.HWND_BROADCAST, user32.WM_FONTCHANGE, 0, 0)
        # https://stackoverflow.com/questions/1951658/sendmessagehwnd-broadcast-hangs
        user32.SendNotifyMessageW(user32.HWND_BROADCAST, user32.WM_FONTCHANGE, 0, 0)
