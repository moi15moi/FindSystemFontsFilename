from .types import CFIndex, CFNumberRef, CFStringEncoding
from ctypes import c_bool, c_char_p, c_void_p, cdll, util
from enum import IntEnum

__all__ = [
    "CoreFoundation",
    "CFURLPathStyle",
    "CFStringBuiltInEncodings",
    "CFNumberType",
]


class CFURLPathStyle(IntEnum):
    # https://developer.apple.com/documentation/corefoundation/cfurlpathstyle?language=objc
    kCFURLPOSIXPathStyle = 0
    kCFURLHFSPathStyle = 1
    kCFURLWindowsPathStyle = 2


class CFStringBuiltInEncodings(IntEnum):
    # https://developer.apple.com/documentation/corefoundation/cfstringbuiltinencodings?language=objc
    kCFStringEncodingMacRoman = 0
    kCFStringEncodingWindowsLatin1 = 0x0500
    kCFStringEncodingISOLatin1 = 0x0201
    kCFStringEncodingNextStepLatin = 0x0B01
    kCFStringEncodingASCII = 0x0600
    kCFStringEncodingUnicode = 0x0100
    kCFStringEncodingUTF8 = 0x08000100
    kCFStringEncodingNonLossyASCII = 0x0BFF
    kCFStringEncodingUTF16 = 0x0100
    kCFStringEncodingUTF16BE = 0x10000100
    kCFStringEncodingUTF16LE = 0x14000100
    kCFStringEncodingUTF32 = 0x0c000100
    kCFStringEncodingUTF32BE = 0x18000100
    kCFStringEncodingUTF32LE = 0x1c000100


class CFNumberType(IntEnum):
    # https://developer.apple.com/documentation/corefoundation/cfnumbertype?language=objc
    kCFNumberSInt8Type = 1
    kCFNumberSInt16Type = 2
    kCFNumberSInt32Type = 3
    kCFNumberSInt64Type = 4
    kCFNumberFloat32Type = 5
    kCFNumberFloat64Type = 6
    kCFNumberCharType = 7
    kCFNumberShortType = 8
    kCFNumberIntType = 9
    kCFNumberLongType = 10
    kCFNumberLongLongType = 11
    kCFNumberFloatType = 12
    kCFNumberDoubleType = 13
    kCFNumberCFIndexType = 14
    kCFNumberNSIntegerType = 15
    kCFNumberCGFloatType = 16
    kCFNumberMaxType = 16


class CoreFoundation():
    def __init__(self) -> None:
        core_foundation_library_name = util.find_library("CoreFoundation")
        # Hack for compatibility with macOS greater or equals to 11.0.
        # From: https://github.com/pyglet/pyglet/blob/a44e83a265e7df8ece793de865bcf3690f66adbd/pyglet/libs/darwin/cocoapy/cocoalibs.py#L10-L14
        if core_foundation_library_name is None:
            core_foundation_library_name = "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        core_foundation = cdll.LoadLibrary(core_foundation_library_name)


        # https://developer.apple.com/documentation/corefoundation/1521153-cfrelease
        self.CFRelease = core_foundation.CFRelease
        self.CFRelease.restype = c_void_p
        self.CFRelease.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1388772-cfarraygetcount?language=objc
        self.CFArrayGetCount = core_foundation.CFArrayGetCount
        self.CFArrayGetCount.restype = CFIndex
        self.CFArrayGetCount.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1388767-cfarraygetvalueatindex?language=objc
        self.CFArrayGetValueAtIndex = core_foundation.CFArrayGetValueAtIndex
        self.CFArrayGetValueAtIndex.restype = c_void_p
        self.CFArrayGetValueAtIndex.argtypes = [c_void_p, CFIndex]

        # https://developer.apple.com/documentation/corefoundation/1542853-cfstringgetlength?language=objc
        self.CFStringGetLength = core_foundation.CFStringGetLength
        self.CFStringGetLength.restype = CFIndex
        self.CFStringGetLength.argtypes = [c_void_p]

        # https://developer.apple.com/documentation/corefoundation/1542143-cfstringgetmaximumsizeforencodin?language=objc
        self.CFStringGetMaximumSizeForEncoding = core_foundation.CFStringGetMaximumSizeForEncoding
        self.CFStringGetMaximumSizeForEncoding.restype = CFIndex
        self.CFStringGetMaximumSizeForEncoding.argtypes = [c_void_p, CFStringEncoding]

        # https://developer.apple.com/documentation/corefoundation/1542721-cfstringgetcstring?language=objc
        self.CFStringGetCString = core_foundation.CFStringGetCString
        self.CFStringGetCString.restype = c_bool
        self.CFStringGetCString.argtypes = [c_void_p, c_char_p, CFIndex, CFStringEncoding]

        # https://developer.apple.com/documentation/corefoundation/1543114-cfnumbergetvalue?language=objc
        self.CFNumberGetValue = core_foundation.CFNumberGetValue
        self.CFNumberGetValue.restype = c_bool
        self.CFNumberGetValue.argtypes = [CFNumberRef, CFIndex, c_void_p]
