from .types import CFIndex
from ctypes import c_bool, c_uint32, c_void_p, cdll, util
from enum import IntEnum

__all__ = [
    "CoreText",
    "CTFontFormat",
    "CTFontManagerScope"
]


class CTFontFormat(IntEnum):
    # https://developer.apple.com/documentation/coretext/ctfontformat?language=objc
    kCTFontFormatUnrecognized = 0
    kCTFontFormatOpenTypePostScript = 1
    kCTFontFormatOpenTypeTrueType = 2
    kCTFontFormatTrueType = 3
    kCTFontFormatPostScript = 4
    kCTFontFormatBitmap = 5


class CTFontManagerScope(IntEnum):
    # https://developer.apple.com/documentation/coretext/ctfontmanagerscope?language=objc
    kCTFontManagerScopeNone = 0
    kCTFontManagerScopeProcess = 1
    kCTFontManagerScopePersistent = 2
    kCTFontManagerScopeSession = 3
    kCTFontManagerScopeUser = 2


class CoreText():
    def __init__(self) -> None:
        core_text_library_name = util.find_library("CoreText")
        # Hack for compatibility with macOS greater or equals to 11.0.
        # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L520-L524
        core_text = cdll.LoadLibrary(core_text_library_name)

        self.kCTFontURLAttribute = c_void_p.in_dll(core_text, "kCTFontURLAttribute")
        self.kCTFontFormatAttribute = c_void_p.in_dll(core_text, "kCTFontFormatAttribute")

        # https://developer.apple.com/documentation/coretext/1509907-ctfontcollectioncreatefromavaila?language=objc
        self.CTFontCollectionCreateFromAvailableFonts = core_text.CTFontCollectionCreateFromAvailableFonts
        self.CTFontCollectionCreateFromAvailableFonts.restype = c_void_p
        self.CTFontCollectionCreateFromAvailableFonts.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/coretext/1511091-ctfontcollectioncreatematchingfo?language=objc
        self.CTFontCollectionCreateMatchingFontDescriptors = core_text.CTFontCollectionCreateMatchingFontDescriptors
        self.CTFontCollectionCreateMatchingFontDescriptors.restype = c_void_p
        self.CTFontCollectionCreateMatchingFontDescriptors.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/coretext/1510346-ctfontdescriptorcopyattribute?language=objc
        self.CTFontDescriptorCopyAttribute = core_text.CTFontDescriptorCopyAttribute
        self.CTFontDescriptorCopyAttribute.restype = c_void_p
        self.CTFontDescriptorCopyAttribute.argtypes = [c_void_p, c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1541581-cfurlcopyfilesystempath?language=objc
        self.CFURLCopyFileSystemPath = core_text.CFURLCopyFileSystemPath
        self.CFURLCopyFileSystemPath.restype = c_void_p
        self.CFURLCopyFileSystemPath.argtypes = [c_void_p, CFIndex]

        # https://developer.apple.com/documentation/coretext/1499468-ctfontmanagerregisterfontsforurl?language=objc
        self.CTFontManagerRegisterFontsForURL = core_text.CTFontManagerRegisterFontsForURL
        self.CTFontManagerRegisterFontsForURL.restype = c_bool
        self.CTFontManagerRegisterFontsForURL.argtypes = [c_void_p,  c_uint32, c_void_p]

        # https://developer.apple.com/documentation/coretext/1499496-ctfontmanagerunregisterfontsforu?language=objc
        self.CTFontManagerUnregisterFontsForURL = core_text.CTFontManagerUnregisterFontsForURL
        self.CTFontManagerUnregisterFontsForURL.restype = c_bool
        self.CTFontManagerUnregisterFontsForURL.argtypes = [c_void_p,  c_uint32, c_void_p]
