from comtypes import COMError, GUID, HRESULT, IUnknown, STDMETHOD
from comtypes.automation import VARIANT
from ctypes import byref, create_unicode_buffer, POINTER, Structure, Union, windll, wintypes
from enum import IntEnum
from pathlib import Path
from sys import getwindowsversion
from typing import Set
from .exceptions import OSNotSupported
from .system_fonts import SystemFonts

# DIRECTWRITE definition

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


# Shell definition

class SHCONTF(IntEnum):
    # https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/ne-shobjidl_core-_shcontf
    SHCONTF_CHECKING_FOR_CHILDREN = 0x10
    SHCONTF_FOLDERS = 0x20
    SHCONTF_NONFOLDERS = 0x40
    SHCONTF_INCLUDEHIDDEN = 0x80
    SHCONTF_INIT_ON_FIRST_NEXT = 0x100
    SHCONTF_NETPRINTERSRCH = 0x200
    SHCONTF_SHAREABLE = 0x400
    SHCONTF_STORAGE = 0x800
    SHCONTF_NAVIGATION_ENUM = 0x1000
    SHCONTF_FASTITEMS = 0x2000
    SHCONTF_FLATLIST = 0x4000
    SHCONTF_ENABLE_ASYNC = 0x8000
    SHCONTF_INCLUDESUPERHIDDEN = 0x10000


class SHITEMID(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/shtypes/ns-shtypes-shitemid
    _fields_ = [
        ("cb", wintypes.USHORT),
        ("abID", wintypes.BYTE),
    ]


class ITEMIDLIST(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/shtypes/ns-shtypes-itemidlist
    _fields_ = [
        ("mkid", SHITEMID),
    ]


class STRRET(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/shtypes/ns-shtypes-strret
    class DUMMYUNIONNAME(Union):
        _fields_ = [
            ("pOleStr", wintypes.LPWSTR),
            ("uOffset", wintypes.UINT),
            ("cStr", wintypes.CHAR * 260),
        ]

    _fields_ = [
        ("uType", wintypes.UINT),
        ('DUMMYUNIONNAME', DUMMYUNIONNAME),
    ]


class PROPERTYKEY(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/wtypes/ns-wtypes-propertykey
    _fields_ = [
        ("fmtid", GUID),
        ("pid", wintypes.DWORD),
    ]


class SHELLDETAILS(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/shtypes/ns-shtypes-shelldetails
    _fields_ = [
        ("fmt", wintypes.INT),
        ("cxChar", wintypes.INT),
        ("str", STRRET),
    ]


# This PROPERTYKEY have obtained with IShellFolder2::MapColumnToSCID with the column 13
PK_FONTS_FILENAMES = PROPERTYKEY()
PK_FONTS_FILENAMES.fmtid = GUID("{4530d076-b598-4a81-8813-9b11286ef6ea}")
PK_FONTS_FILENAMES.pid = 7

FOLDERID_FONTS = GUID("{FD228CB7-AE11-4AE3-864C-16F3910AB8FE}")


class IBindCtx(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/objidl/nn-objidl-ibindctx
    _iid_ = GUID("{0000000e-0000-0000-C000-000000000046}")

    _methods_ = [
        STDMETHOD(None, "RegisterObjectBound"),  # Need to be implemented
        STDMETHOD(None, "RevokeObjectBound"),  # Need to be implemented
        STDMETHOD(None, "ReleaseBoundObjects"),  # Need to be implemented
        STDMETHOD(None, "SetBindOptions"),  # Need to be implemented
        STDMETHOD(None, "GetBindOptions"),  # Need to be implemented
        STDMETHOD(None, "GetRunningObjectTable"),  # Need to be implemented
        STDMETHOD(None, "RegisterObjectParam"),  # Need to be implemented
        STDMETHOD(None, "GetObjectParam"),  # Need to be implemented
        STDMETHOD(None, "EnumObjectParam"),  # Need to be implemented
        STDMETHOD(None, "RevokeObjectParam"),  # Need to be implemented
    ]


class IEnumIDList(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ienumidlist
    _iid_ = GUID("{000214F2-0000-0000-C000-000000000046}")

    _methods_ = [
        STDMETHOD(HRESULT, "Next", [wintypes.ULONG, POINTER(POINTER(ITEMIDLIST)), POINTER(wintypes.ULONG)]),
        STDMETHOD(None, "Skip"),  # Need to be implemented
        STDMETHOD(None, "Reset"),  # Need to be implemented
        STDMETHOD(None, "Clone"),  # Need to be implemented
    ]


class IShellFolder(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ishellfolder
    _iid_ = GUID("{000214E6-0000-0000-C000-000000000046}")

    _methods_ = [
        STDMETHOD(None, "ParseDisplayName"),  # Need to be implemented
        STDMETHOD(HRESULT, "EnumObjects", [wintypes.HWND, wintypes.DWORD, POINTER(POINTER(IEnumIDList))]),
        STDMETHOD(HRESULT, "BindToObject", [POINTER(ITEMIDLIST), POINTER(IBindCtx), POINTER(GUID), POINTER(wintypes.LPCVOID)]),
        STDMETHOD(None, "BindToStorage"),  # Need to be implemented
        STDMETHOD(None, "CompareIDs"),  # Need to be implemented
        STDMETHOD(None, "CreateViewObject"),  # Need to be implemented
        STDMETHOD(None, "GetAttributesOf"),  # Need to be implemented
        STDMETHOD(None, "GetUIObjectOf"),  # Need to be implemented
        STDMETHOD(HRESULT, "GetDisplayNameOf", [POINTER(ITEMIDLIST), wintypes.DWORD, POINTER(STRRET)]),
        STDMETHOD(None, "SetNameOf"),  # Need to be implemented
    ]


class IShellFolder2(IShellFolder):
    # https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ishellfolder2
    _iid_ = GUID("{93F2F68C-1D1B-11d3-A30E-00C04F79ABD1}")

    _methods_ = [
        STDMETHOD(None, "GetDefaultSearchGUID"),  # Need to be implemented
        STDMETHOD(None, "EnumSearches"),  # Need to be implemented
        STDMETHOD(None, "GetDefaultColumn"),  # Need to be implemented
        STDMETHOD(None, "GetDefaultColumnState"),  # Need to be implemented
        STDMETHOD(HRESULT, "GetDetailsEx", [POINTER(ITEMIDLIST), POINTER(PROPERTYKEY), POINTER(VARIANT)]),
        STDMETHOD(HRESULT, "GetDetailsOf", [POINTER(ITEMIDLIST), wintypes.UINT, POINTER(SHELLDETAILS)]),
        STDMETHOD(None, "MapColumnToSCID"),  # Need to be implemented
    ]


class WindowsFonts(SystemFonts):
    _DWriteCreateFactory = None
    _Shell32 = None
    _CoTaskMemFree = None
    _VariantClear = None
    VALID_FONT_FORMATS_DWRITE = [
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_CFF,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_TRUETYPE,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_OPENTYPE_COLLECTION,
        DWRITE_FONT_FILE_TYPE.DWRITE_FONT_FILE_TYPE_TRUETYPE_COLLECTION,
    ]
    VALID_FONT_FORMATS_EXTENSION = ["ttf", "otf", "ttc", "otc"]

    def get_system_fonts_filename() -> Set[str]:
        windows_version = getwindowsversion()

        if WindowsVersionHelpers.is_windows_10_or_greater(windows_version):
            fonts_filename = WindowsFonts._get_fonts_filename_windows_10_or_more()
        elif WindowsVersionHelpers.is_windows_vista_sp2_or_greater(windows_version):
            fonts_filename = WindowsFonts._get_fonts_filename_windows_vista_sp2_or_more()
        elif WindowsVersionHelpers.is_windows_vista_or_greater(windows_version):
            fonts_filename = WindowsFonts._get_fonts_filename_windows_vista_or_more()
        else:
            raise OSNotSupported("FindSystemFontsFilename only works on Windows Vista or more")

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

            is_supported_font_type = wintypes.BOOLEAN()
            font_file_type = wintypes.UINT()
            font_face_type = wintypes.UINT()
            number_of_faces = wintypes.UINT()
            font_file.Analyze(byref(is_supported_font_type), byref(font_file_type), byref(font_face_type), byref(number_of_faces))

            if DWRITE_FONT_FILE_TYPE(font_file_type.value) not in WindowsFonts.VALID_FONT_FORMATS_DWRITE:
                continue

            path_len = wintypes.UINT()
            local_loader.GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, byref(path_len))

            buffer = create_unicode_buffer(path_len.value + 1)
            local_loader.GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, buffer, len(buffer))

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
                font = POINTER(IDWriteFont)()
                family.GetFont(j, byref(font))

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

                    if DWRITE_FONT_FILE_TYPE(font_file_type.value) not in WindowsFonts.VALID_FONT_FORMATS_DWRITE:
                        continue

                    path_len = wintypes.UINT()
                    local_loader.GetFilePathLengthFromKey(font_file_reference_key, font_file_reference_key_size, byref(path_len))

                    buffer = create_unicode_buffer(path_len.value + 1)
                    local_loader.GetFilePathFromKey(font_file_reference_key, font_file_reference_key_size, buffer, len(buffer))

                    fonts_filename.add(buffer.value)

        return fonts_filename


    @staticmethod
    def _get_fonts_filename_windows_vista_or_more() -> Set[str]:
        """
        Return an set of all the installed fonts filename.
        """
        if WindowsFonts._Shell32 is None:
            WindowsFonts._load_Shell32_CoTaskMemFree_VariantClear()

        fonts_filename = set()

        pidl_fonts = POINTER(ITEMIDLIST)()
        WindowsFonts._Shell32.SHGetKnownFolderIDList(FOLDERID_FONTS, 0, None, byref(pidl_fonts))

        font_shell_folder = POINTER(IShellFolder2)()
        WindowsFonts._Shell32.SHBindToObject(None, pidl_fonts, None, IShellFolder2._iid_, byref(font_shell_folder))

        enum_id_list = POINTER(IEnumIDList)()
        font_shell_folder.EnumObjects(None, SHCONTF.SHCONTF_FOLDERS | SHCONTF.SHCONTF_NONFOLDERS | SHCONTF.SHCONTF_INCLUDEHIDDEN | SHCONTF.SHCONTF_FLATLIST, byref(enum_id_list))

        while True:
            shell_item = POINTER(ITEMIDLIST)()
            shell_fetched = wintypes.ULONG()
            
            enum_id_list.Next(1, byref(shell_item), byref(shell_fetched))
        
            if shell_fetched.value != 1:
                break

            variant_font_filename = VARIANT()
            has_child = False
            try:
                font_shell_folder.GetDetailsEx(shell_item, byref(PK_FONTS_FILENAMES), byref(variant_font_filename))
            except COMError:
                has_child = True

            if not has_child:
                # The tuple will always have a length of 1
                font_filename = variant_font_filename.value[0]
                if Path(font_filename).suffix.lstrip(".").strip().lower() in WindowsFonts.VALID_FONT_FORMATS_EXTENSION:
                    fonts_filename.add(font_filename)
                WindowsFonts._VariantClear(variant_font_filename)
            else:
                WindowsFonts._VariantClear(variant_font_filename)

                shell_item_child = POINTER(IShellFolder)()
                font_shell_folder.BindToObject(shell_item, None, IShellFolder._iid_, byref(shell_item_child))

                enum_id_list_child = POINTER(IEnumIDList)()
                shell_item_child.EnumObjects(None, SHCONTF.SHCONTF_FOLDERS | SHCONTF.SHCONTF_NONFOLDERS | SHCONTF.SHCONTF_INCLUDEHIDDEN | SHCONTF.SHCONTF_FLATLIST, byref(enum_id_list_child))

                while True:
                    shell_item_child = POINTER(ITEMIDLIST)()
                    shell_fetched_child = wintypes.ULONG()
                    
                    enum_id_list_child.Next(1, byref(shell_item_child), byref(shell_fetched_child))
                
                    if shell_fetched_child.value != 1:
                        break

                    font_shell_folder.GetDetailsEx(shell_item_child, byref(PK_FONTS_FILENAMES), byref(variant_font_filename))
                    # The tuple will always have a length of 1
                    font_filename = variant_font_filename.value[0]
                    if Path(font_filename).suffix.lstrip(".").strip().lower() in WindowsFonts.VALID_FONT_FORMATS_EXTENSION:
                        fonts_filename.add(font_filename)
                    WindowsFonts._VariantClear(variant_font_filename)
                    WindowsFonts._CoTaskMemFree(shell_item_child)
            WindowsFonts._CoTaskMemFree(shell_item)
        WindowsFonts._CoTaskMemFree(pidl_fonts)

        return fonts_filename


    @staticmethod
    def _load_Shell32_CoTaskMemFree_VariantClear():
        WindowsFonts._Shell32 = windll.Shell32

        # https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderidlist
        WindowsFonts._Shell32.SHGetKnownFolderIDList.restype = HRESULT
        WindowsFonts._Shell32.SHGetKnownFolderIDList.argtypes = [POINTER(GUID), wintypes.DWORD, wintypes.HANDLE, POINTER(POINTER(ITEMIDLIST))]
        
        # https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shbindtoobject
        WindowsFonts._Shell32.SHBindToObject.restype = HRESULT
        WindowsFonts._Shell32.SHBindToObject.argtypes = [POINTER(IShellFolder), POINTER(ITEMIDLIST), POINTER(IBindCtx), GUID, POINTER(wintypes.LPVOID)]
        
        # https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cotaskmemfree
        WindowsFonts._CoTaskMemFree = windll.ole32.CoTaskMemFree
        WindowsFonts._CoTaskMemFree.restype = None
        WindowsFonts._CoTaskMemFree.argtypes = [POINTER(ITEMIDLIST)]

        # https://learn.microsoft.com/en-us/windows/win32/api/oleauto/nf-oleauto-variantclear
        WindowsFonts._VariantClear = windll.oleaut32.VariantClear
        WindowsFonts._VariantClear.restype = HRESULT
        WindowsFonts._VariantClear.argtypes = [POINTER(VARIANT)]


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
    def is_windows_vista_or_greater(windows_version) -> bool:
        # From https://www.lifewire.com/windows-version-numbers-2625171
        return WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 6, 0, 6000)

    @staticmethod
    def is_windows_vista_sp2_or_greater(windows_version) -> bool:
        # From https://www.lifewire.com/windows-version-numbers-2625171
        return WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 6, 0, 6002)

    @staticmethod
    def is_windows_10_or_greater(windows_version) -> bool:
        # From https://www.lifewire.com/windows-version-numbers-2625171
        return WindowsVersionHelpers.is_windows_version_or_greater(windows_version, 10, 0, 10240)
