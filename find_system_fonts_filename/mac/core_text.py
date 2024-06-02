from .types import CFIndex
from ctypes import c_void_p, cdll, util
from enum import IntEnum

__all__ = [
    "CoreText",
    "CTFontFormat"
]


class CTFontFormat(IntEnum):
    # https://developer.apple.com/documentation/coretext/ctfontformat?language=objc
    kCTFontFormatUnrecognized = 0
    kCTFontFormatOpenTypePostScript = 1
    kCTFontFormatOpenTypeTrueType = 2
    kCTFontFormatTrueType = 3
    kCTFontFormatPostScript = 4
    kCTFontFormatBitmap = 5


class CoreText():
    def __init__(self) -> None:
        core_text_library_name = util.find_library("CoreText")
        # Hack for compatibility with macOS greater or equals to 11.0.
        # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L520-L524
        if core_text_library_name is None:
            core_text_library_name = "/System/Library/Frameworks/CoreText.framework/CoreText"
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
