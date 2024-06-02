from .advapi32 import Advapi32, RegistryDataType
from .dwrite import (
    DWrite,
    DWRITE_FACTORY_TYPE,
    DWRITE_FONT_FILE_TYPE,
    DWRITE_FONT_SIMULATIONS,
    DWRITE_INFORMATIONAL_STRING_ID,
    DWRITE_LOCALITY,
    IDWriteFactory,
    IDWriteFactory3,
    IDWriteFont,
    IDWriteFontCollection,
    IDWriteFontCollectionLoader,
    IDWriteFontFace,
    IDWriteFontFaceReference,
    IDWriteFontFamily,
    IDWriteFontFile,
    IDWriteFontFileEnumerator,
    IDWriteFontFileLoader,
    IDWriteFontSet,
    IDWriteLocalFontFileLoader,
    IDWriteLocalizedStrings
)
from .gdi32 import GDI32
from .kernel32 import Kernel32
from .user32 import User32
from .version_helpers import WindowsVersionHelpers
from comtypes import COMError, COMObject
from ctypes import byref, cast, create_unicode_buffer, POINTER, sizeof, wintypes
from os.path import isfile
from pathlib import Path
from sys import getwindowsversion
from typing import List, Set
from ..exceptions import NotSupportedFontFile, OSNotSupported
from ..system_fonts import SystemFonts

__all__ = ["WindowsFonts"]


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
        dwrite = DWrite()
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
        dwrite = DWrite()
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
                raise ValueError("Could not fetch the font name")

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

        gdi = GDI32()
        user32 = User32()

        if not font_filename.is_file():
            raise FileNotFoundError(f"The file \"{font_filename}\" doesn't exist")

        font_filename_buffer = create_unicode_buffer(str(font_filename))

        gdi.AddFontResourceW(font_filename_buffer)
        if add_font_to_registry:
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

        gdi = GDI32()
        user32 = User32()

        if added_font_to_registry:
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
            except OSError:
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
            self.current_font_file.AddRef()
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
        enumerator_ref.AddRef()
        font_file_enumerator[0] = enumerator_ref

        return 0 # S_OK
