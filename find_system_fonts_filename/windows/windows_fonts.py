from .advapi32 import Advapi32, RegistryDataType
from .dwrite import (
    DWrite,
    DWRITE_FACTORY_TYPE,
    DWRITE_FONT_FILE_TYPE,
    DWRITE_FONT_SIMULATIONS,
    DWRITE_INFORMATIONAL_STRING_ID,
    IDWriteFactory,
    IDWriteFont,
    IDWriteFontCollection,
    IDWriteFontCollectionLoader,
    IDWriteFontFace,
    IDWriteFontFile,
    IDWriteFontFileEnumerator,
    IDWriteFontFileLoader,
    IDWriteGdiInterop,
    IDWriteLocalFontFileLoader,
    IDWriteLocalizedStrings
)
from .gdi32 import GDI32, ENUMLOGFONTEXW, TEXTMETRICW
from .kernel32 import Kernel32
from .msvcrt import MSVCRT
from .user32 import User32
from .version_helpers import WindowsVersionHelpers
from comtypes import COMObject
from ctypes import addressof, byref, cast, create_unicode_buffer, POINTER, py_object, sizeof, wintypes
from pathlib import Path
from sys import getwindowsversion
from typing import List, Set
from ..exceptions import NotSupportedFontFile, OSNotSupported, SystemApiError
from ..system_fonts import SystemFonts

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


def enum_fonts_2(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRICW, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value

    # It seems that font_type can be 0. In those case, the font format is .fon
    # We also discard RASTER_FONTTYPE which are bitmap font
    if not (font_type & enum_data.gdi.RASTER_FONTTYPE) and font_type:
        # Replace the lfFaceName with the elfFullName.
        # See why here: https://github.com/libass/libass/issues/744
        lfFaceName = create_unicode_buffer(enum_data.gdi.LF_FACESIZE)
        enum_data.msvcrt.wcsncpy_s(lfFaceName, enum_data.gdi.LF_FACESIZE, logfont.elfFullName, enum_data.msvcrt.TRUNCATE)
        logfont.elfLogFont.lfFaceName = lfFaceName.value

        hfont = enum_data.gdi.CreateFontIndirectW(byref(logfont.elfLogFont))
        enum_data.gdi.SelectObject(enum_data.dc, hfont)

        font_face = POINTER(IDWriteFontFace)()
        enum_data.gdi_interop.CreateFontFaceFromHdc(enum_data.dc, byref(font_face))
        enum_data.fonts_filename.update(get_filepath_from_IDWriteFontFace(font_face))

        enum_data.gdi.DeleteObject(hfont)

    return True


def enum_fonts_1(logfont: ENUMLOGFONTEXW, text_metric: TEXTMETRICW, font_type: wintypes.DWORD, lparam: wintypes.LPARAM):
    enum_data: EnumData = py_object.from_address(lparam).value
    enum_data.gdi.EnumFontFamiliesW(enum_data.dc, logfont.elfLogFont.lfFaceName, enum_data.gdi.ENUMFONTFAMEXPROC(enum_fonts_2), lparam)

    return True


class EnumData:
    def __init__(self, gdi: GDI32, msvcrt: MSVCRT, dc: wintypes.HDC, fonts_filename: Set[str], gdi_interop: POINTER(IDWriteGdiInterop)):
        self.gdi = gdi
        self.msvcrt = msvcrt
        self.dc = dc
        self.fonts_filename = fonts_filename
        self.gdi_interop = gdi_interop


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

        dwrite = DWrite()
        gdi = GDI32()
        msvcrt = MSVCRT()
        fonts_filename = set()

        dwrite_factory = POINTER(IDWriteFactory)()
        dwrite.DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, dwrite_factory._iid_, byref(dwrite_factory))

        gdi_interop = POINTER(IDWriteGdiInterop)()
        dwrite_factory.GetGdiInterop(byref(gdi_interop))

        dc = gdi.CreateCompatibleDC(None)

        enum_data = EnumData(gdi, msvcrt, dc, fonts_filename, gdi_interop)
        object_enum_data = py_object(enum_data)

        # See this link to understand why we do call EnumFontFamiliesW and then a EnumFontFamiliesW
        # and not directly EnumFontFamiliesExW.
        # https://stackoverflow.com/a/62405274/15835974
        enum_data.gdi.EnumFontFamiliesW(enum_data.dc, None, enum_data.gdi.ENUMFONTFAMEXPROC(enum_fonts_1), addressof(object_enum_data))

        gdi.DeleteDC(dc)

        return fonts_filename


    @staticmethod
    def get_registry_font_name(font_filename: Path) -> str:
        dwrite = DWrite()
        kernel32 = Kernel32()
        font_filename_buffer = create_unicode_buffer(str(font_filename))

        dwrite_factory = POINTER(IDWriteFactory)()
        dwrite.DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, IDWriteFactory._iid_, byref(dwrite_factory))

        font_file = POINTER(IDWriteFontFile)()
        dwrite_factory.CreateFontFileReference(font_filename_buffer, None, byref(font_file))

        is_supported_font_type = wintypes.BOOLEAN()
        font_file_type = wintypes.UINT()
        font_face_type = wintypes.UINT()
        number_of_faces = wintypes.UINT()
        font_file.Analyze(byref(is_supported_font_type), byref(font_file_type), byref(font_face_type), byref(number_of_faces))

        if not is_supported_font_type:
            raise NotSupportedFontFile(f"The font file \"{font_filename}\" isn't supported on Windows.")

        font_collection_loader = CustomFontCollectionLoader([font_filename])
        dwrite_factory.RegisterFontCollectionLoader(font_collection_loader)

        custom_collection = POINTER(IDWriteFontCollection)()
        font_loader_key = create_unicode_buffer("find_system_fonts_filename_collection_loader")
        dwrite_factory.CreateCustomFontCollection(font_collection_loader,
                                                    cast(font_loader_key, wintypes.LPVOID),
                                                    sizeof(font_loader_key),
                                                    byref(custom_collection))

        full_names: List[str] = []
        for i in range(number_of_faces.value):
            font_face = POINTER(IDWriteFontFace)()
            dwrite_factory.CreateFontFace(font_face_type.value, 1, byref(font_file), i, DWRITE_FONT_SIMULATIONS.DWRITE_FONT_SIMULATIONS_NONE, byref(font_face))

            """
            Converting a IDWriteFontFace to a IDWriteFont isn't easy.
            We can't use IDWriteGdiInterop and use ConvertFontFaceToLOGFONT and then CreateFontFromLOGFONT,
            because it needs to have the font installed in the system and since we just called AddFontResourceW,
            the font may not be available. See issue #14
            """
            font = POINTER(IDWriteFont)()
            custom_collection.GetFontFromFontFace(font_face, byref(font))

            full_name = POINTER(IDWriteLocalizedStrings)()
            exists = wintypes.BOOL()
            font.GetInformationalStrings(
                DWRITE_INFORMATIONAL_STRING_ID.DWRITE_INFORMATIONAL_STRING_FULL_NAME,
                byref(full_name),
                byref(exists)
            )

            if not exists:
                raise SystemApiError("Could not fetch the font name")

            # Based on https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-idwritelocalizedstrings-findlocalename#remarks
            locale_name = create_unicode_buffer(kernel32.LOCALE_NAME_MAX_LENGTH)
            kernel32.GetUserDefaultLocaleName(locale_name, kernel32.LOCALE_NAME_MAX_LENGTH)

            index = wintypes.UINT()
            exists = wintypes.BOOL()
            full_name.FindLocaleName(locale_name, byref(index), byref(exists))

            if not exists.value:
                full_name.FindLocaleName("en-us", byref(index), byref(exists))

            if not exists.value:
                index = 0

            length = wintypes.UINT()
            full_name.GetStringLength(index, byref(length))

            family_names_buffer = create_unicode_buffer(length.value + 1)
            full_name.GetString(index, family_names_buffer, len(family_names_buffer))

            full_names.append(family_names_buffer.value)

        registry_font_name = " & ".join(full_names) + " (FindSystemFontsFilename)"
        dwrite_factory.UnregisterFontCollectionLoader(font_collection_loader)

        return registry_font_name


    def install_font(font_filename: Path, add_font_to_registry: bool) -> None:
        windows_version = getwindowsversion()

        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater(windows_version):
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        # Font in the registry have been added in 10.0.17083.
        # Source: https://superuser.com/a/1658749/1729132
        is_build_17083_or_greater = WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 10, 0, 17083)

        gdi = GDI32()
        user32 = User32()

        font_filename_buffer = create_unicode_buffer(str(font_filename))

        gdi.AddFontResourceW(font_filename_buffer)
        if add_font_to_registry and is_build_17083_or_greater:
            advapi32 = Advapi32()
            hkey = wintypes.HKEY()
            registry_font_name = WindowsFonts.get_registry_font_name(font_filename)

            advapi32.RegOpenKeyExW(advapi32.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts", 0, advapi32.KEY_SET_VALUE, byref(hkey))
            advapi32.RegSetValueExW(hkey, registry_font_name, 0, RegistryDataType.REG_SZ.value, cast(font_filename_buffer, wintypes.LPBYTE), sizeof(font_filename_buffer))
            advapi32.RegCloseKey(hkey)

        user32.SendNotifyMessageW(user32.HWND_BROADCAST, user32.WM_FONTCHANGE, 0, 0)


    def uninstall_font(font_filename: Path, added_font_to_registry: bool) -> None:
        windows_version = getwindowsversion()

        if not WindowsVersionHelpers.is_windows_vista_sp2_or_greater(windows_version):
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista SP2 or more")

        # Font in the registry have been added in 10.0.17083.
        # Source: https://superuser.com/a/1658749/1729132
        is_build_17083_or_greater = WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 10, 0, 17083)

        gdi = GDI32()
        user32 = User32()

        if added_font_to_registry and is_build_17083_or_greater:
            advapi32 = Advapi32()
            hkey = wintypes.HKEY()
            registry_font_name = WindowsFonts.get_registry_font_name(font_filename)

            advapi32.RegOpenKeyExW(advapi32.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts", 0, advapi32.KEY_SET_VALUE, byref(hkey))
            advapi32.RegDeleteValueW(hkey, registry_font_name)
            advapi32.RegCloseKey(hkey)

        # When a font have been installed multiple time,
        # we need to call RemoveFontResourceW until it fails.
        # Also, when the font have been added to the registry,
        # RemoveFontResourceW fails, but in reality, it actually uninstalled
        # the font, so let's always ignore any error it returns.
        while True:
            try:
                gdi.RemoveFontResourceW(str(font_filename))
            except SystemApiError:
                break

        user32.SendNotifyMessageW(user32.HWND_BROADCAST, user32.WM_FONTCHANGE, 0, 0)


class CustomFontFileEnumerator(COMObject):
    _com_interfaces_ = [IDWriteFontFileEnumerator]

    def __init__(self, dwrite_factory: POINTER(IDWriteFactory), font_files_path: List[Path]):
        super(CustomFontFileEnumerator, self).__init__()
        self.dwrite_factory = dwrite_factory
        self.font_files_path = font_files_path
        self.current_index = -1
        self.current_font_file = None

    def IDWriteFontFileEnumerator_MoveNext(self, this, has_current_file: POINTER(wintypes.BOOL)) -> int:
        self.current_index += 1
        if self.current_index < len(self.font_files_path):
            font_filename_buffer = create_unicode_buffer(str(self.font_files_path[self.current_index]))

            font_file = POINTER(IDWriteFontFile)()
            self.dwrite_factory.CreateFontFileReference(font_filename_buffer, None, byref(font_file))

            self.current_font_file = font_file
            has_current_file.contents.value = True
        else:
            has_current_file.contents.value = False
        return 0 # S_OK

    def IDWriteFontFileEnumerator_GetCurrentFontFile(self, this, font_file: POINTER(POINTER(IDWriteFontFile))) -> int:
        if self.current_font_file:
            font_file[0] = self.current_font_file
            return 0 # S_OK
        return 1 # S_FALSE


class CustomFontCollectionLoader(COMObject):
    _com_interfaces_ = [IDWriteFontCollectionLoader]

    def __init__(self, font_files_path: List[Path]):
        super(CustomFontCollectionLoader, self).__init__()
        self.font_files_path = font_files_path

    def IDWriteFontCollectionLoader_CreateEnumeratorFromKey(
            self,
            this,
            factory: POINTER(IDWriteFactory),
            collection_key: wintypes.LPVOID,
            collection_key_size: wintypes.UINT,
            font_file_enumerator: POINTER(POINTER(IDWriteFontFileEnumerator))
        )-> int:

        enum = CustomFontFileEnumerator(factory, self.font_files_path)
        enumerator_ref = enum.QueryInterface(IDWriteFontFileEnumerator)
        font_file_enumerator[0] = enumerator_ref

        return 0 # S_OK
