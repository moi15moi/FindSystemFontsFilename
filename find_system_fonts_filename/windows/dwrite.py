from .gdi32 import LOGFONTW
from comtypes import GUID, HRESULT, IUnknown, STDMETHOD
from ctypes import POINTER, windll, wintypes
from enum import IntEnum, IntFlag

__all__ = [
    "DWrite",
    "DWRITE_FACTORY_TYPE",
    "DWRITE_FONT_FILE_TYPE",
    "DWRITE_FONT_SIMULATIONS",
    "DWRITE_INFORMATIONAL_STRING_ID",
    "DWRITE_LOCALITY",
    "IDWriteFactory",
    "IDWriteFactory1",
    "IDWriteFactory2",
    "IDWriteFactory3",
    "IDWriteFont",
    "IDWriteFontCollection",
    "IDWriteFontCollection1",
    "IDWriteFontCollectionLoader",
    "IDWriteFontFace",
    "IDWriteFontFaceReference",
    "IDWriteFontFamily",
    "IDWriteFontFile",
    "IDWriteFontFileEnumerator",
    "IDWriteFontFileLoader",
    "IDWriteFontList",
    "IDWriteFontSet",
    "IDWriteFontSetBuilder",
    "IDWriteGdiInterop",
    "IDWriteLocalFontFileLoader",
    "IDWriteLocalizedStrings"
]


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


class DWRITE_INFORMATIONAL_STRING_ID(IntEnum):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/ne-dwrite-dwrite_informational_string_id
    DWRITE_INFORMATIONAL_STRING_NONE = 0
    DWRITE_INFORMATIONAL_STRING_COPYRIGHT_NOTICE = 1
    DWRITE_INFORMATIONAL_STRING_VERSION_STRINGS = 2
    DWRITE_INFORMATIONAL_STRING_TRADEMARK = 3
    DWRITE_INFORMATIONAL_STRING_MANUFACTURER = 4
    DWRITE_INFORMATIONAL_STRING_DESIGNER = 5
    DWRITE_INFORMATIONAL_STRING_DESIGNER_URL = 6
    DWRITE_INFORMATIONAL_STRING_DESCRIPTION = 7
    DWRITE_INFORMATIONAL_STRING_FONT_VENDOR_URL = 8
    DWRITE_INFORMATIONAL_STRING_LICENSE_DESCRIPTION = 9
    DWRITE_INFORMATIONAL_STRING_LICENSE_INFO_URL = 10
    DWRITE_INFORMATIONAL_STRING_WIN32_FAMILY_NAMES = 11
    DWRITE_INFORMATIONAL_STRING_WIN32_SUBFAMILY_NAMES = 12
    DWRITE_INFORMATIONAL_STRING_TYPOGRAPHIC_FAMILY_NAMES = 13
    DWRITE_INFORMATIONAL_STRING_TYPOGRAPHIC_SUBFAMILY_NAMES = 14
    DWRITE_INFORMATIONAL_STRING_SAMPLE_TEXT = 15
    DWRITE_INFORMATIONAL_STRING_FULL_NAME = 16
    DWRITE_INFORMATIONAL_STRING_POSTSCRIPT_NAME = 17
    DWRITE_INFORMATIONAL_STRING_POSTSCRIPT_CID_NAME = 18
    DWRITE_INFORMATIONAL_STRING_WEIGHT_STRETCH_STYLE_FAMILY_NAME = 19
    DWRITE_INFORMATIONAL_STRING_DESIGN_SCRIPT_LANGUAGE_TAG = 20
    DWRITE_INFORMATIONAL_STRING_SUPPORTED_SCRIPT_LANGUAGE_TAG = 21
    DWRITE_INFORMATIONAL_STRING_PREFERRED_FAMILY_NAMES = DWRITE_INFORMATIONAL_STRING_TYPOGRAPHIC_FAMILY_NAMES
    DWRITE_INFORMATIONAL_STRING_PREFERRED_SUBFAMILY_NAMES = DWRITE_INFORMATIONAL_STRING_TYPOGRAPHIC_SUBFAMILY_NAMES
    DWRITE_INFORMATIONAL_STRING_WWS_FAMILY_NAME = DWRITE_INFORMATIONAL_STRING_WEIGHT_STRETCH_STYLE_FAMILY_NAME


class DWRITE_FONT_SIMULATIONS(IntFlag):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/ne-dwrite-dwrite_font_simulations
    DWRITE_FONT_SIMULATIONS_NONE = 0x0000
    DWRITE_FONT_SIMULATIONS_BOLD = 0x0001
    DWRITE_FONT_SIMULATIONS_OBLIQUE = 0x0002


class IDWriteFontFileLoader(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontfileloader
    _iid_ = GUID("{727cad4e-d6af-4c9e-8a08-d695b11caa49}")
    _methods_ = [
        STDMETHOD(None, "CreateStreamFromKey"),  # Need to be implemented
    ]


class IDWriteLocalFontFileLoader(IDWriteFontFileLoader):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritelocalfontfileloader
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


class IDWriteLocalizedStrings(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritelocalizedstrings
    _iid_ = GUID("{08256209-099a-4b34-b86d-c22b110e7771}")
    _methods_ = [
        STDMETHOD(wintypes.UINT, "GetCount"),
        STDMETHOD(HRESULT, "FindLocaleName", [POINTER(wintypes.WCHAR), POINTER(wintypes.UINT), POINTER(wintypes.BOOL)]),
        STDMETHOD(HRESULT, "GetLocaleNameLength", [wintypes.UINT, POINTER(wintypes.UINT)]),
        STDMETHOD(HRESULT, "GetLocaleName", [wintypes.UINT, POINTER(wintypes.WCHAR), wintypes.UINT]),
        STDMETHOD(HRESULT, "GetStringLength", [wintypes.UINT, POINTER(wintypes.UINT)]),
        STDMETHOD(HRESULT, "GetString", [wintypes.UINT, POINTER(wintypes.WCHAR), wintypes.UINT]),
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
        STDMETHOD(HRESULT, "GetInformationalStrings", [wintypes.UINT, POINTER(POINTER(IDWriteLocalizedStrings)), POINTER(wintypes.BOOL)]),
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
        STDMETHOD(HRESULT, "GetFontFromFontFace", [POINTER(IDWriteFontFace), POINTER(POINTER(IDWriteFont))]),
    ]


class IDWriteGdiInterop(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritegdiinterop
    _iid_ = GUID("{1edd9491-9853-4299-898f-6432983b6f3a}")
    _methods_ = [
        STDMETHOD(HRESULT, "CreateFontFromLOGFONT1", [POINTER(LOGFONTW), POINTER(POINTER(IDWriteFont))]),
        STDMETHOD(None, "ConvertFontToLOGFONT"),  # Need to be implemented
        STDMETHOD(None, "ConvertFontFaceToLOGFONT"),  # Need to be implemented
        STDMETHOD(HRESULT, "CreateFontFaceFromHdc", [wintypes.HDC, POINTER(POINTER(IDWriteFontFace))]),
        STDMETHOD(None, "CreateBitmapRenderTarget"),  # Need to be implemented
    ]


class IDWriteFontFileEnumerator(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontfileenumerator
    _iid_ = GUID("{72755049-5ff7-435d-8348-4be97cfa6c7c}")
    _methods_ = [
        STDMETHOD(HRESULT, "MoveNext", [POINTER(wintypes.BOOL)]),
        STDMETHOD(HRESULT, "GetCurrentFontFile", [POINTER(POINTER(IDWriteFontFile))]),
    ]


class IDWriteFontCollectionLoader(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefontcollectionloader
    _iid_ = GUID("{cca920e4-52f0-492b-bfa8-29c72ee0a468}")


class IDWriteFactory(IUnknown):
    # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nn-dwrite-idwritefactory
    _iid_ = GUID("{b859ee5a-d838-4b5b-a2e8-1adc7d93db48}")
    _methods_ = [
        STDMETHOD(HRESULT, "GetSystemFontCollection", [POINTER(POINTER(IDWriteFontCollection)), wintypes.BOOLEAN]),
        STDMETHOD(HRESULT, "CreateCustomFontCollection", [POINTER(IDWriteFontCollectionLoader), wintypes.LPVOID, wintypes.UINT, POINTER(POINTER(IDWriteFontCollection))]),
        STDMETHOD(HRESULT, "RegisterFontCollectionLoader", [POINTER(IDWriteFontCollectionLoader)]),
        STDMETHOD(HRESULT, "UnregisterFontCollectionLoader", [POINTER(IDWriteFontCollectionLoader)]),
        STDMETHOD(HRESULT, "CreateFontFileReference", [POINTER(wintypes.WCHAR), POINTER(wintypes.FILETIME), POINTER(POINTER(IDWriteFontFile))]),
        STDMETHOD(HRESULT, "CreateCustomFontFileReference", [wintypes.LPVOID, wintypes.UINT, POINTER(IDWriteFontFileLoader), POINTER(POINTER(IDWriteFontFile))]),
        STDMETHOD(HRESULT, "CreateFontFace", [wintypes.UINT, wintypes.UINT, POINTER(POINTER(IDWriteFontFile)), wintypes.UINT, wintypes.UINT, POINTER(POINTER(IDWriteFontFace))]),
        STDMETHOD(None, "CreateRenderingParams"),  # Need to be implemented
        STDMETHOD(None, "CreateMonitorRenderingParams"),  # Need to be implemented
        STDMETHOD(None, "CreateCustomRenderingParams"),  # Need to be implemented
        STDMETHOD(HRESULT, "RegisterFontFileLoader", [POINTER(IDWriteFontFileLoader)]),
        STDMETHOD(HRESULT, "UnregisterFontFileLoader", [POINTER(IDWriteFontFileLoader)]),
        STDMETHOD(None, "CreateTextFormat"),  # Need to be implemented
        STDMETHOD(None, "CreateTypography"),  # Need to be implemented
        STDMETHOD(HRESULT, "GetGdiInterop", [POINTER(POINTER(IDWriteGdiInterop))]),
        STDMETHOD(None, "CreateTextLayout"),  # Need to be implemented
        STDMETHOD(None, "CreateGdiCompatibleTextLayout"),  # Need to be implemented
        STDMETHOD(None, "CreateEllipsisTrimmingSign"),  # Need to be implemented
        STDMETHOD(None, "CreateTextAnalyzer"),  # Need to be implemented
        STDMETHOD(None, "CreateNumberSubstitution"),  # Need to be implemented
        STDMETHOD(None, "CreateGlyphRunAnalysis"),  # Need to be implemented
    ]

IDWriteFontCollectionLoader._methods_ = [
    STDMETHOD(HRESULT, "CreateEnumeratorFromKey", [POINTER(IDWriteFactory), wintypes.LPVOID, wintypes.UINT, POINTER(POINTER(IDWriteFontFileEnumerator))]),
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


class DWrite:
    def __init__(self) -> None:
        dwrite = windll.dwrite

        # https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-dwritecreatefactory
        self.DWriteCreateFactory = dwrite.DWriteCreateFactory
        self.DWriteCreateFactory.restype = HRESULT
        self.DWriteCreateFactory.argtypes = [wintypes.UINT, GUID, POINTER(POINTER(IUnknown))]
