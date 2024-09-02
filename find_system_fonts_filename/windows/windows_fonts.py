from ctypes import addressof, byref, cast, create_unicode_buffer, POINTER, py_object, sizeof
from pathlib import Path
from sys import platform
from typing import List, Set
from win32more import Byte, FAILED, UInt32, VoidPtr, WinError
from win32more.Windows.Win32.Foundation import BOOL, LPARAM
from win32more.Windows.Win32.Globalization import GetUserDefaultLocaleName
from win32more.Windows.Win32.Graphics.DirectWrite import (
    DWRITE_FACTORY_TYPE_ISOLATED,
    DWRITE_FONT_FACE_TYPE,
    DWRITE_FONT_FILE_TYPE,
    DWRITE_FONT_FILE_TYPE_CFF,
    DWRITE_FONT_FILE_TYPE_OPENTYPE_COLLECTION,
    DWRITE_FONT_FILE_TYPE_TRUETYPE,
    DWRITE_FONT_FILE_TYPE_TRUETYPE_COLLECTION,
    DWRITE_FONT_SIMULATIONS_NONE,
    DWRITE_INFORMATIONAL_STRING_FULL_NAME,
    DWriteCreateFactory,
    IDWriteFactory,
    IDWriteFontFace,
    IDWriteFontFace3,
    IDWriteFontFile,
    IDWriteFontFileLoader,
    IDWriteGdiInterop,
    IDWriteLocalFontFileLoader,
    IDWriteLocalizedStrings,
)
from win32more.Windows.Win32.Graphics.Gdi import (
    AddFontResourceW,
    CreateCompatibleDC,
    CreateFontIndirectW,
    DeleteDC,
    DeleteObject,
    ENUMLOGFONTEXW,
    EnumFontFamiliesW,
    FONTENUMPROCW,
    GDI_ERROR,
    HDC,
    HGDIOBJ,
    LF_FACESIZE,
    LOGFONTW,
    RASTER_FONTTYPE,
    RemoveFontResourceW,
    SelectObject,
    TEXTMETRICW,
)
from win32more.Windows.Win32.System.SystemServices import LOCALE_NAME_MAX_LENGTH
from win32more.Windows.Win32.System.Registry import (
    HKEY,
    HKEY_CURRENT_USER,
    KEY_SET_VALUE,
    REG_SZ,
    RegCloseKey,
    RegDeleteValueW,
    RegOpenKeyExW,
    RegSetValueExW,
)
from win32more.Windows.Win32.UI.WindowsAndMessaging import (
    HWND_BROADCAST,
    SendNotifyMessageW,
    WM_FONTCHANGE,
)
from .cygwin import Cygwin
from .version_helpers import WindowsVersionHelpers
from ..exceptions import NotSupportedFontFile, OSNotSupported, SystemApiError
from ..system_fonts import SystemFonts

__all__ = ["WindowsFonts"]


def get_filepath_from_IDWriteFontFace(font_face: IDWriteFontFace) -> Set[str]:
    fonts_filename: Set[str] = set()

    file_count = UInt32()
    hr = font_face.GetFiles(byref(file_count), None)
    if FAILED(hr):
        raise WinError(hr)

    font_files = (IDWriteFontFile * file_count.value)()
    hr = font_face.GetFiles(byref(file_count), font_files)
    if FAILED(hr):
        raise WinError(hr)

    for font_file in font_files:
            font_file._own = True

            font_file_reference_key = VoidPtr()
            font_file_reference_key_size = UInt32()
            hr = font_file.GetReferenceKey(byref(font_file_reference_key), byref(font_file_reference_key_size))
            if FAILED(hr):
                raise WinError(hr)

            loader = IDWriteFontFileLoader(own=True)
            hr = font_file.GetLoader(byref(loader))
            if FAILED(hr):
                raise WinError(hr)

            local_loader = IDWriteLocalFontFileLoader(own=True)
            hr = loader.QueryInterface(local_loader._iid_, byref(local_loader))
            if FAILED(hr):
                raise WinError(hr)

            is_supported_font_type = BOOL()
            font_file_type = DWRITE_FONT_FILE_TYPE()
            font_face_type = DWRITE_FONT_FACE_TYPE()
            number_of_faces = UInt32()
            hr = font_file.Analyze(byref(is_supported_font_type), byref(font_file_type), byref(font_face_type), byref(number_of_faces))
            if FAILED(hr):
                raise WinError(hr)

            if font_file_type.value not in WindowsFonts.VALID_FONT_FORMATS:
                continue

            path_len = UInt32()
            hr = local_loader.GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, byref(path_len))
            if FAILED(hr):
                raise WinError(hr)

            buffer = create_unicode_buffer(path_len.value + 1)
            hr = local_loader.GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, buffer, len(buffer))
            if FAILED(hr):
                raise WinError(hr)

            fonts_filename.add(buffer.value)

    return fonts_filename


def enum_fonts_2(logfont: POINTER(LOGFONTW), text_metric: POINTER(TEXTMETRICW), font_type: UInt32, lparam: LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value

    # It seems that font_type can be 0. In those case, the font format is .fon
    # We also discard RASTER_FONTTYPE which are bitmap font
    if not (font_type & RASTER_FONTTYPE) and font_type:
        # Replace the lfFaceName with the elfFullName.
        # See why here: https://github.com/libass/libass/issues/744
        enum_logfont = cast(logfont, POINTER(ENUMLOGFONTEXW))
        enum_logfont.contents.elfLogFont.lfFaceName = enum_logfont.contents.elfFullName[:LF_FACESIZE - 1]

        hfont = CreateFontIndirectW(byref(enum_logfont.contents.elfLogFont))
        if not hfont:
            raise SystemApiError(f"CreateFontIndirectW fails. The result is {hfont} which is invalid")

        result = SelectObject(enum_data.dc, hfont)
        if result == None or result == HGDIOBJ(GDI_ERROR):
            raise SystemApiError(f"SelectObject fails. The result is {result} which is invalid")

        font_face = IDWriteFontFace(own=True)
        enum_data.gdi_interop.CreateFontFaceFromHdc(enum_data.dc, byref(font_face))
        enum_data.fonts_filename.update(get_filepath_from_IDWriteFontFace(font_face))

        DeleteObject(hfont)

    return True

def enum_fonts_1(logfont: POINTER(LOGFONTW), text_metric: POINTER(TEXTMETRICW), font_type: UInt32, lparam: LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value
    EnumFontFamiliesW(enum_data.dc, logfont.contents.lfFaceName, FONTENUMPROCW(enum_fonts_2), lparam)

    return True


class EnumData:
    def __init__(self, dc: HDC, fonts_filename: Set[str], gdi_interop: IDWriteGdiInterop):
        self.dc = dc
        self.fonts_filename = fonts_filename
        self.gdi_interop = gdi_interop


class WindowsFonts(SystemFonts):
    VALID_FONT_FORMATS = [
        DWRITE_FONT_FILE_TYPE_CFF,
        DWRITE_FONT_FILE_TYPE_TRUETYPE,
        DWRITE_FONT_FILE_TYPE_OPENTYPE_COLLECTION,
        DWRITE_FONT_FILE_TYPE_TRUETYPE_COLLECTION,
    ]

    def get_system_fonts_filename() -> Set[str]:

        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater():
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        fonts_filename = set()

        dwrite_factory = IDWriteFactory(own=True)
        DWriteCreateFactory(DWRITE_FACTORY_TYPE_ISOLATED, dwrite_factory._iid_, byref(dwrite_factory))

        gdi_interop = IDWriteGdiInterop(own=True)
        dwrite_factory.GetGdiInterop(byref(gdi_interop))

        dc = CreateCompatibleDC(0)

        enum_data = EnumData(dc, fonts_filename, gdi_interop)
        object_enum_data = py_object(enum_data)

        # See this link to understand why we do call EnumFontFamiliesW and then a EnumFontFamiliesW
        # and not directly EnumFontFamiliesExW.
        # https://stackoverflow.com/a/62405274/15835974
        EnumFontFamiliesW(enum_data.dc, None, FONTENUMPROCW(enum_fonts_1), addressof(object_enum_data))

        DeleteDC(dc)

        return fonts_filename


    @staticmethod
    def get_registry_font_name(font_filename: Path) -> str:
        if platform == "cygwin":
            font_filename_buffer = create_unicode_buffer(Cygwin().posix_path_to_win32_path(font_filename))
        else:
            font_filename_buffer = create_unicode_buffer(str(font_filename))

        dwrite_factory = IDWriteFactory(own=True)
        DWriteCreateFactory(DWRITE_FACTORY_TYPE_ISOLATED, dwrite_factory._iid_, byref(dwrite_factory))

        font_file = IDWriteFontFile(own=True)
        hr = dwrite_factory.CreateFontFileReference(font_filename_buffer, None, byref(font_file))
        if FAILED(hr):
            raise WinError(hr)

        is_supported_font_type = BOOL()
        font_file_type = DWRITE_FONT_FILE_TYPE()
        font_face_type = DWRITE_FONT_FACE_TYPE()
        number_of_faces = UInt32()
        font_file.Analyze(byref(is_supported_font_type), byref(font_file_type), byref(font_face_type), byref(number_of_faces))

        if not is_supported_font_type:
            raise NotSupportedFontFile(f"The font file \"{font_filename}\" isn't supported on Windows.")

        full_names: List[str] = []
        for i in range(number_of_faces.value):
            font_face = IDWriteFontFace(own=True)
            dwrite_factory.CreateFontFace(font_face_type.value, 1, byref(font_file), i, DWRITE_FONT_SIMULATIONS_NONE, byref(font_face))

            font_face_3 = IDWriteFontFace3(own=True)
            hr = font_face.QueryInterface(font_face_3._iid_, byref(font_face_3))

            full_name = IDWriteLocalizedStrings(own=True)
            exists = BOOL()
            font_face_3.GetInformationalStrings(
                DWRITE_INFORMATIONAL_STRING_FULL_NAME,
                byref(full_name),
                byref(exists)
            )

            if not exists:
                raise SystemApiError("Could not fetch the font name")

            # Based on https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-idwritelocalizedstrings-findlocalename#remarks
            locale_name = create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
            GetUserDefaultLocaleName(locale_name, LOCALE_NAME_MAX_LENGTH)

            index = UInt32()
            exists = BOOL()
            full_name.FindLocaleName(locale_name, byref(index), byref(exists))

            if not exists.value:
                full_name.FindLocaleName("en-us", byref(index), byref(exists))

            if not exists.value:
                index = 0

            length = UInt32()
            full_name.GetStringLength(index, byref(length))

            family_names_buffer = create_unicode_buffer(length.value + 1)
            full_name.GetString(index, family_names_buffer, len(family_names_buffer))

            full_names.append(family_names_buffer.value)

        registry_font_name = " & ".join(full_names) + " (FindSystemFontsFilename)"

        return registry_font_name


    def install_font(font_filename: Path, add_font_to_registry: bool) -> None:

        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater():
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        # Font in the registry have been added in 10.0.17083.
        # Source: https://superuser.com/a/1658749/1729132
        is_build_17083_or_greater = WindowsVersionHelpers.is_windows_version_or_greater_build(10, 0, 17083)

        if platform == "cygwin":
            font_filename_buffer = create_unicode_buffer(Cygwin().posix_path_to_win32_path(font_filename))
        else:
            font_filename_buffer = create_unicode_buffer(str(font_filename))

        result = AddFontResourceW(font_filename_buffer)
        if not result:
            raise SystemApiError(f"AddFontResourceW fails. The result is {result} which is invalid")

        if add_font_to_registry and is_build_17083_or_greater:
            hkey = HKEY()
            registry_font_name = WindowsFonts.get_registry_font_name(font_filename)

            RegOpenKeyExW(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts", 0, KEY_SET_VALUE, byref(hkey))
            RegSetValueExW(hkey, registry_font_name, 0, REG_SZ, cast(font_filename_buffer, POINTER(Byte)), sizeof(font_filename_buffer))
            RegCloseKey(hkey)

        SendNotifyMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)


    def uninstall_font(font_filename: Path, added_font_to_registry: bool) -> None:

        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater():
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        # Font in the registry have been added in 10.0.17083.
        # Source: https://superuser.com/a/1658749/1729132
        is_build_17083_or_greater = WindowsVersionHelpers.is_windows_version_or_greater_build(10, 0, 17083)

        if added_font_to_registry and is_build_17083_or_greater:
            hkey = HKEY()
            registry_font_name = WindowsFonts.get_registry_font_name(font_filename)

            RegOpenKeyExW(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts", 0, KEY_SET_VALUE, byref(hkey))
            RegDeleteValueW(hkey, registry_font_name)
            RegCloseKey(hkey)

        if platform == "cygwin":
            font_filename_buffer = create_unicode_buffer(Cygwin().posix_path_to_win32_path(font_filename))
        else:
            font_filename_buffer = create_unicode_buffer(str(font_filename))

        # When a font have been installed multiple time,
        # we need to call RemoveFontResourceW until it fails.
        # Also, when the font have been added to the registry,
        # RemoveFontResourceW fails, but in reality, it actually uninstalled
        # the font, so let's always ignore any error it returns.
        while True:
            result = RemoveFontResourceW(font_filename_buffer)
            if not result:
                break

        SendNotifyMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)