from comtypes import COMError, GUID, HRESULT, IUnknown, STDMETHOD
from ctypes import byref, create_unicode_buffer, POINTER, windll, wintypes
from enum import IntEnum
from os.path import isfile
from sys import getwindowsversion
from typing import Set
from .exceptions import OSNotSupported
from .system_fonts import SystemFonts


class DWRITE_FACTORY_TYPE(IntEnum):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/ne-dwrite-dwrite_factory_type
    DWRITE_FACTORY_TYPE_SHARED = 0
    DWRITE_FACTORY_TYPE_ISOLATED = 1


class DWRITE_FONT_FILE_TYPE(IntEnum):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/ne-dwrite-dwrite_font_file_type
    DWRITE_FONT_FILE_TYPE_UNKNOWN = 0
    DWRITE_FONT_FILE_TYPE_CFF = 1
    DWRITE_FONT_FILE_TYPE_TRUETYPE = 2
    DWRITE_FONT_FILE_TYPE_OPENTYPE_COLLECTION = 3
    DWRITE_FONT_FILE_TYPE_TYPE1_PFM = 4
    DWRITE_FONT_FILE_TYPE_TYPE1_PFB = 5
    DWRITE_FONT_FILE_TYPE_VECTOR = 6
    DWRITE_FONT_FILE_TYPE_BITMAP = 7
    DWRITE_FONT_FILE_TYPE_TRUETYPE_COLLECTION = DWRITE_FONT_FILE_TYPE_OPENTYPE_COLLECTION


class DWRITE_LOCALITY(IntEnum):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite_3/ne-dwrite_3-dwrite_locality
    DWRITE_LOCALITY_REMOTE = 0
    DWRITE_LOCALITY_PARTIAL = 1
    DWRITE_LOCALITY_LOCAL = 2


class IDWriteFontFileLoader(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontfileloader
    _iid_ = GUID("{727cad4e-d6af-4c9e-8a08-d695b11caa49}")
    _methods_ = [
        STDMETHOD(None, "CreateStreamFromKey"),  # Need to be implemented
    ]


class IDWriteLocalFontFileLoader(IDWriteFontFileLoader):
    # https://learn.microsoft.com/en-us/windows/win32/directwrite/idwritelocalfontfileloader
    _iid_ = GUID("{b2d9f3ec-c9fe-4a11-a2ec-d86208f7c0a2}")
    _methods_ = [
        STDMETHOD(HRESULT, "GetFilePathLengthFromKey", [wintypes.LPCVOID, wintypes.UINT, POINTER(wintypes.UINT)]),
        STDMETHOD(HRESULT, "GetFilePathFromKey", [wintypes.LPCVOID, wintypes.UINT, POINTER(wintypes.WCHAR), wintypes.UINT]),
        STDMETHOD(None, "GetLastWriteTimeFromKey"),  # Need to be implemented
    ]


class IDWriteFontFile(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontfile
    _iid_ = GUID("{739d886a-cef5-47dc-8769-1a8b41bebbb0}")
    _methods_ = [
        STDMETHOD(HRESULT, "GetReferenceKey", [POINTER(wintypes.LPCVOID), POINTER(wintypes.UINT)]),
        STDMETHOD(HRESULT, "GetLoader", [POINTER(POINTER(IDWriteFontFileLoader))]),
        STDMETHOD(HRESULT, "Analyze", [POINTER(wintypes.BOOLEAN), POINTER(wintypes.UINT), POINTER(wintypes.UINT), POINTER(wintypes.UINT)]),
    ]


class IDWriteFontFaceReference(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite_3/nn-dwrite_3-idwritefontfacereference
    _iid_ = GUID("{5E7FA7CA-DDE3-424C-89F0-9FCD6FED58CD}")
    _methods_ = [
        STDMETHOD(None, "CreateFontFace"),  # Need to be implemented
        STDMETHOD(None, "CreateFontFaceWithSimulations"),  # Need to be implemented
        STDMETHOD(None, "Equals"),  # Need to be implemented
        STDMETHOD(None, "GetFontFaceIndex"),  # Need to be implemented
        STDMETHOD(None, "GetSimulations"),  # Need to be implemented
        STDMETHOD(HRESULT, "GetFontFile", [POINTER(POINTER(IDWriteFontFile))]),
        STDMETHOD(None, "GetLocalFileSize"),  # Need to be implemented
        STDMETHOD(None, "GetFileSize"),  # Need to be implemented
        STDMETHOD(None, "GetFileTime"),  # Need to be implemented
        STDMETHOD(wintypes.UINT, "GetLocality"),
        STDMETHOD(None, "EnqueueFontDownloadRequest"),  # Need to be implemented
        STDMETHOD(None, "EnqueueCharacterDownloadRequest"),  # Need to be implemented
        STDMETHOD(None, "EnqueueGlyphDownloadRequest"),  # Need to be implemented
        STDMETHOD(None, "EnqueueFileFragmentDownloadRequest"),  # Need to be implemented
    ]


class IDWriteFontSet(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite_3/nn-dwrite_3-idwritefontset
    _iid_ = GUID("{53585141-D9F8-4095-8321-D73CF6BD116B}")
    _methods_ = [
        STDMETHOD(wintypes.UINT, "GetFontCount"),
        STDMETHOD(HRESULT, "GetFontFaceReference", [wintypes.UINT, POINTER(POINTER(IDWriteFontFaceReference))]),
        STDMETHOD(None, "FindFontFaceReference"),  # Need to be implemented
        STDMETHOD(None, "FindFontFace"),  # Need to be implemented
        STDMETHOD(None, "GetPropertyValues"),  # Need to be implemented
        STDMETHOD(None, "GetPropertyValues"),  # Need to be implemented
        STDMETHOD(None, "GetPropertyValues"),  # Need to be implemented
        STDMETHOD(None, "GetPropertyOccurrenceCount"),  # Need to be implemented
        STDMETHOD(None, "GetMatchingFonts"),  # Need to be implemented
        STDMETHOD(None, "GetMatchingFonts"),  # Need to be implemented
    ]


class IDWriteFontFace(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontface
    _iid_ = GUID("{5f49804d-7024-4d43-bfa9-d25984f53849}")
    _methods_ = [
        STDMETHOD(None, "GetType"),  # Need to be implemented
        STDMETHOD(HRESULT, "GetFiles", [POINTER(wintypes.UINT), POINTER(POINTER(IDWriteFontFile))]),
        STDMETHOD(None, "GetIndex"),  # Need to be implemented
        STDMETHOD(None, "GetSimulations"),  # Need to be implemented
        STDMETHOD(None, "IsSymbolFont"),  # Need to be implemented
        STDMETHOD(None, "GetMetrics"),  # Need to be implemented
        STDMETHOD(None, "GetGlyphCount"),  # Need to be implemented
        STDMETHOD(None, "GetDesignGlyphMetrics"),  # Need to be implemented
        STDMETHOD(None, "GetGlyphIndices"),  # Need to be implemented
        STDMETHOD(None, "TryGetFontTable"),  # Need to be implemented
        STDMETHOD(None, "ReleaseFontTable"),  # Need to be implemented
        STDMETHOD(None, "GetGlyphRunOutline"),  # Need to be implemented
        STDMETHOD(None, "GetRecommendedRenderingMode"),  # Need to be implemented
        STDMETHOD(None, "GetGdiCompatibleMetrics"),  # Need to be implemented
        STDMETHOD(None, "GetGdiCompatibleGlyphMetrics"),  # Need to be implemented
    ]


class IDWriteFont(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefont
    _iid_ = GUID("{acd16696-8c14-4f5d-877e-fe3fc1d32737}")
    _methods_ = [
        STDMETHOD(None, "GetFontFamily"),  # Need to be implemented
        STDMETHOD(None, "GetWeight"),  # Need to be implemented
        STDMETHOD(None, "GetStretch"),  # Need to be implemented
        STDMETHOD(None, "GetStyle"),  # Need to be implemented
        STDMETHOD(None, "IsSymbolFont"),  # Need to be implemented
        STDMETHOD(None, "GetFaceNames"),  # Need to be implemented
        STDMETHOD(None, "GetInformationalStrings"),  # Need to be implemented
        STDMETHOD(None, "GetSimulations"),  # Need to be implemented
        STDMETHOD(None, "GetMetrics"),  # Need to be implemented
        STDMETHOD(None, "HasCharacter"),  # Need to be implemented
        STDMETHOD(HRESULT, "CreateFontFace", [POINTER(POINTER(IDWriteFontFace))]),
    ]


class IDWriteFontList(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontlist
    _iid_ = GUID("{1a0d8438-1d97-4ec1-aef9-a2fb86ed6acb}")
    _methods_ = [
        STDMETHOD(None, "GetFontCollection"),  # Need to be implemented
        STDMETHOD(wintypes.UINT, "GetFontCount"),
        STDMETHOD(HRESULT, "GetFont", [wintypes.UINT, POINTER(POINTER(IDWriteFont))]),
    ]


class IDWriteFontFamily(IDWriteFontList):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontfamily
    _iid_ = GUID("{da20d8ef-812a-4c43-9802-62ec4abd7add}")
    _methods_ = [
        STDMETHOD(None, "GetFamilyNames"),  # Need to be implemented
        STDMETHOD(None, "GetFirstMatchingFont"),  # Need to be implemented
        STDMETHOD(None, "GetMatchingFonts"),  # Need to be implemented
    ]


class IDWriteFontCollection(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontcollection
    _iid_ = GUID("{a84cee02-3eea-4eee-a827-87c1a02a0fcc}")
    _methods_ = [
        STDMETHOD(wintypes.UINT, "GetFontFamilyCount"),
        STDMETHOD(HRESULT, "GetFontFamily", [wintypes.UINT, POINTER(POINTER(IDWriteFontFamily))]),
        STDMETHOD(None, "FindFamilyName"),  # Need to be implemented
        STDMETHOD(None, "GetFontFromFontFace"),  # Need to be implemented
    ]


class IDWriteFactory(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefactory
    _iid_ = GUID("{b859ee5a-d838-4b5b-a2e8-1adc7d93db48}")
    _methods_ = [
        STDMETHOD(HRESULT, "GetSystemFontCollection", [POINTER(POINTER(IDWriteFontCollection)), wintypes.BOOLEAN]),
        STDMETHOD(None, "CreateCustomFontCollection"),  # Need to be implemented
        STDMETHOD(None, "RegisterFontCollectionLoader"),  # Need to be implemented
        STDMETHOD(None, "UnregisterFontCollectionLoader"),  # Need to be implemented
        STDMETHOD(None, "CreateFontFileReference"),  # Need to be implemented
        STDMETHOD(None, "CreateCustomFontFileReference"),  # Need to be implemented
        STDMETHOD(None, "CreateFontFace"),  # Need to be implemented
        STDMETHOD(None, "CreateRenderingParams"),  # Need to be implemented
        STDMETHOD(None, "CreateMonitorRenderingParams"),  # Need to be implemented
        STDMETHOD(None, "CreateCustomRenderingParams"),  # Need to be implemented
        STDMETHOD(None, "RegisterFontFileLoader"),  # Need to be implemented
        STDMETHOD(None, "UnregisterFontFileLoader"),  # Need to be implemented
        STDMETHOD(None, "CreateTextFormat"),  # Need to be implemented
        STDMETHOD(None, "CreateTypography"),  # Need to be implemented
        STDMETHOD(None, "GetGdiInterop"),  # Need to be implemented
        STDMETHOD(None, "CreateTextLayout"),  # Need to be implemented
        STDMETHOD(None, "CreateGdiCompatibleTextLayout"),  # Need to be implemented
        STDMETHOD(None, "CreateEllipsisTrimmingSign"),  # Need to be implemented
        STDMETHOD(None, "CreateTextAnalyzer"),  # Need to be implemented
        STDMETHOD(None, "CreateNumberSubstitution"),  # Need to be implemented
        STDMETHOD(None, "CreateGlyphRunAnalysis"),  # Need to be implemented
    ]


class IDWriteFactory1(IDWriteFactory):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite_1/nn-dwrite_1-idwritefactory1
    _iid_ = GUID("{30572f99-dac6-41db-a16e-0486307e606a}")
    _methods_ = [
        STDMETHOD(None, "GetEudcFontCollection"),  # Need to be implemented
        STDMETHOD(None, "CreateCustomRenderingParams1"),  # Need to be implemented
    ]


class IDWriteFactory2(IDWriteFactory1):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite_2/nn-dwrite_2-idwritefactory2
    _iid_ = GUID("{0439fc60-ca44-4994-8dee-3a9af7b732ec}")
    _methods_ = [
        STDMETHOD(None, "GetSystemFontFallback"),  # Need to be implemented
        STDMETHOD(None, "CreateFontFallbackBuilder"),  # Need to be implemented
        STDMETHOD(None, "TranslateColorGlyphRun"),  # Need to be implemented
        STDMETHOD(None, "CreateCustomRenderingParams2"),  # Need to be implemented
        STDMETHOD(None, "CreateGlyphRunAnalysis"),  # Need to be implemented
    ]


class IDWriteFactory3(IDWriteFactory2):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite_3/nn-dwrite_3-idwritefactory3
    _iid_ = GUID("{9A1B41C3-D3BB-466A-87FC-FE67556A3B65}")
    _methods_ = [
        STDMETHOD(None, "CreateGlyphRunAnalysis"),  # Need to be implemented
        STDMETHOD(None, "CreateCustomRenderingParams3"),  # Need to be implemented
        STDMETHOD(None, "CreateFontFaceReference"),  # Need to be implemented
        STDMETHOD(None, "CreateFontFaceReference"),  # Need to be implemented
        STDMETHOD(HRESULT, "GetSystemFontSet", [POINTER(POINTER(IDWriteFontSet))]),
        STDMETHOD(None, "CreateFontSetBuilder"),  # Need to be implemented
        STDMETHOD(None, "CreateFontCollectionFromFontSet"),  # Need to be implemented
        STDMETHOD(None, "GetSystemFontCollection3"),  # Need to be implemented
        STDMETHOD(None, "GetFontDownloadQueue"),  # Need to be implemented
    ]


class WindowsFonts(SystemFonts):
    _DWriteCreateFactory = None
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
        if WindowsFonts._DWriteCreateFactory is None:
            WindowsFonts._load_DWriteCreateFactory()

        fonts_filename = set()

        dwrite_factory = POINTER(IDWriteFactory3)()
        WindowsFonts._DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, IDWriteFactory3._iid_, byref(dwrite_factory))

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

            local_loader = loader.QueryInterface(IDWriteLocalFontFileLoader)

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

        fonts_filename = set()

        dwrite_factory = POINTER(IDWriteFactory)()
        WindowsFonts._DWriteCreateFactory(DWRITE_FACTORY_TYPE.DWRITE_FACTORY_TYPE_ISOLATED, IDWriteFactory._iid_, byref(dwrite_factory))

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
    def _load_DWriteCreateFactory():
        WindowsFonts._DWriteCreateFactory = windll.dwrite.DWriteCreateFactory
        WindowsFonts._DWriteCreateFactory.restype = HRESULT
        WindowsFonts._DWriteCreateFactory.argtypes = [wintypes.UINT, GUID, POINTER(POINTER(IUnknown))]


class WindowsVersionHelpers:
    @staticmethod
    def is_windows_version_or_greater(windows_version, major: int, minor: int, build: int) -> bool:
        """
        Parameters:
            windows_version: An object from getwindowsversion.
            major (int): The minimum major OS version number.
            minor (int): The minimum minor OS version number.
            build (int): The minimum build version number.
        Returns:
            True if the specified version matches or if it is greater than the version of the current Windows OS. Otherwise, False.
        """

        if windows_version.major > major:
            return True
        elif windows_version.major == major and windows_version.minor > minor:
            return True
        else:
            return (
                windows_version.major == major
                and windows_version.minor == minor
                and windows_version.build >= build
            )

    @staticmethod
    def is_windows_vista_sp2_or_greater(windows_version) -> bool:
        # From https://www.lifewire.com/windows-version-numbers-2625171
        return WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 6, 0, 6002)

    @staticmethod
    def is_windows_10_or_greater(windows_version) -> bool:
        # From https://www.lifewire.com/windows-version-numbers-2625171
        return WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 10, 0, 10240)
