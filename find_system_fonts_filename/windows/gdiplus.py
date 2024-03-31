from .gdi import LOGFONTW
from ctypes import c_uint16, POINTER, Structure, windll, wintypes
from enum import IntEnum

__all__ = [
    "FontStyle",
    "GdiplusStartupInput",
    "GdiplusStartupOutput",
    "GPSTATUS",
    "GDIPlus",
]

class FontStyle(IntEnum):
    # https://learn.microsoft.com/en-us/windows/win32/api/gdiplusenums/ne-gdiplusenums-fontstyle
    FontStyleRegular = 0
    FontStyleBold = 1
    FontStyleItalic = 2
    FontStyleBoldItalic = 3
    FontStyleUnderline = 4
    FontStyleStrikeout = 8


class GdiplusStartupInput(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/gdiplusinit/ns-gdiplusinit-gdiplusstartupinput
    _fields_ = [
        ('GdiplusVersion', wintypes.UINT),
        ('DebugEventCallback', wintypes.LPVOID),
        ('SuppressBackgroundThread', wintypes.BOOL),
        ('SuppressExternalCodecs', wintypes.BOOL)
    ]


class GdiplusStartupOutput(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/gdiplusinit/ns-gdiplusinit-gdiplusstartupoutput
    _fields = [
        ('NotificationHookProc', wintypes.LPVOID),
        ('NotificationUnhookProc', wintypes.LPVOID)
    ]


class GPSTATUS(IntEnum):
    # https://learn.microsoft.com/en-us/windows/win32/api/Gdiplustypes/ne-gdiplustypes-status
    Ok = 0
    GenericError = 1
    InvalidParameter = 2
    OutOfMemory = 3
    ObjectBusy = 4
    InsufficientBuffer = 5
    NotImplemented = 6
    Win32Error = 7
    WrongState = 8
    Aborted = 9
    FileNotFound = 10
    ValueOverflow = 11
    AccessDenied = 12
    UnknownImageFormat = 13
    FontFamilyNotFound = 14
    FontStyleNotFound = 15
    NotTrueTypeFont = 16
    UnsupportedGdiplusVersion = 17
    GdiplusNotInitialized = 18
    PropertyNotFound = 19
    PropertyNotSupported = 20
    ProfileNotFound = 21


class GDIPlus:
    def __init__(self):
        gdiplus = windll.gdiplus

        # https://learn.microsoft.com/en-us/windows/win32/api/gdiplusinit/nf-gdiplusinit-gdiplusstartup
        self.GdiplusStartup = gdiplus.GdiplusStartup
        self.GdiplusStartup.restype = wintypes.UINT
        self.GdiplusStartup.argtypes = [wintypes.LPVOID, wintypes.LPVOID, wintypes.LPVOID]
        self.GdiplusStartup.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/api/gdiplusinit/nf-gdiplusinit-gdiplusshutdown
        self.GdiplusShutdown = gdiplus.GdiplusShutdown
        self.GdiplusShutdown.restype = None
        self.GdiplusShutdown.argtypes = [POINTER(wintypes.ULONG)]

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipNewInstalledFontCollection = gdiplus.GdipNewInstalledFontCollection
        self.GdipNewInstalledFontCollection.restype = wintypes.UINT
        self.GdipNewInstalledFontCollection.argtypes = [wintypes.LPVOID]
        self.GdipNewInstalledFontCollection.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipNewPrivateFontCollection = gdiplus.GdipNewPrivateFontCollection
        self.GdipNewPrivateFontCollection.restype = wintypes.UINT
        self.GdipNewPrivateFontCollection.argtypes = [wintypes.LPVOID]
        self.GdipNewPrivateFontCollection.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipDeletePrivateFontCollection = gdiplus.GdipDeletePrivateFontCollection
        self.GdipDeletePrivateFontCollection.restype = wintypes.UINT
        self.GdipDeletePrivateFontCollection.argtypes = [wintypes.LPVOID]
        self.GdipDeletePrivateFontCollection.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipPrivateAddFontFile = gdiplus.GdipPrivateAddFontFile
        self.GdipPrivateAddFontFile.restype = wintypes.UINT
        self.GdipPrivateAddFontFile.argtypes = [wintypes.LPVOID, POINTER(wintypes.WCHAR)]
        self.GdipPrivateAddFontFile.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipGetFontCollectionFamilyCount = gdiplus.GdipGetFontCollectionFamilyCount
        self.GdipGetFontCollectionFamilyCount.restype = wintypes.UINT
        self.GdipGetFontCollectionFamilyCount.argtypes = [wintypes.LPVOID, POINTER(wintypes.INT)]
        self.GdipGetFontCollectionFamilyCount.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipGetFontCollectionFamilyList = gdiplus.GdipGetFontCollectionFamilyList
        self.GdipGetFontCollectionFamilyList.restype = wintypes.UINT
        self.GdipGetFontCollectionFamilyList.argtypes = [wintypes.LPVOID, wintypes.INT, wintypes.LPVOID, POINTER(wintypes.INT)]
        self.GdipGetFontCollectionFamilyList.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipCreateFont = gdiplus.GdipCreateFont
        self.GdipCreateFont.restype = wintypes.UINT
        self.GdipCreateFont.argtypes = [wintypes.LPVOID, wintypes.FLOAT, wintypes.INT, wintypes.UINT, wintypes.LPVOID]
        self.GdipCreateFont.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipDeleteFont = gdiplus.GdipDeleteFont
        self.GdipDeleteFont.restype = wintypes.UINT
        self.GdipDeleteFont.argtypes = [wintypes.LPVOID]
        self.GdipDeleteFont.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipGetLogFontW = gdiplus.GdipGetLogFontW
        self.GdipGetLogFontW.restype = wintypes.UINT
        self.GdipGetLogFontW.argtypes = [wintypes.LPVOID, wintypes.LPVOID, POINTER(LOGFONTW)]
        self.GdipGetLogFontW.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-font-flat
        self.GdipGetFontStyle = gdiplus.GdipGetFontStyle
        self.GdipGetFontStyle.restype = wintypes.UINT
        self.GdipGetFontStyle.argtypes = [wintypes.LPVOID, POINTER(wintypes.INT)]
        self.GdipGetFontStyle.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-US/windows/win32/gdiplus/-gdiplus-fontfamily-flat
        self.GdipGetEmHeight = gdiplus.GdipGetEmHeight
        self.GdipGetEmHeight.restype = wintypes.UINT
        self.GdipGetEmHeight.argtypes = [wintypes.LPVOID, wintypes.INT, POINTER(c_uint16)]
        self.GdipGetEmHeight.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-US/windows/win32/gdiplus/-gdiplus-fontfamily-flat
        self.GdipGetFamilyName = gdiplus.GdipGetFamilyName
        self.GdipGetFamilyName.restype = wintypes.UINT
        self.GdipGetFamilyName.argtypes = [wintypes.LPVOID, POINTER(wintypes.WCHAR), wintypes.WORD]
        self.GdipGetFamilyName.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-US/windows/win32/gdiplus/-gdiplus-fontfamily-flat
        self.GdipIsStyleAvailable = gdiplus.GdipIsStyleAvailable
        self.GdipIsStyleAvailable.restype = wintypes.UINT
        self.GdipIsStyleAvailable.argtypes = [wintypes.LPVOID, wintypes.INT, POINTER(wintypes.BOOL)]
        self.GdipIsStyleAvailable.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-US/windows/win32/gdiplus/-gdiplus-fontfamily-flat
        self.GdipDeleteFontFamily = gdiplus.GdipDeleteFontFamily
        self.GdipDeleteFontFamily.restype = wintypes.UINT
        self.GdipDeleteFontFamily.argtypes = [wintypes.LPVOID]
        self.GdipDeleteFontFamily.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-graphics-flat
        self.GdipCreateFromHDC = gdiplus.GdipCreateFromHDC
        self.GdipCreateFromHDC.restype = wintypes.UINT
        self.GdipCreateFromHDC.argtypes = [wintypes.HDC, wintypes.LPVOID]
        self.GdipCreateFromHDC.errcheck = GDIPlus.gpstatus_errcheck

        # https://learn.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-graphics-flat
        self.GdipDeleteGraphics = gdiplus.GdipDeleteGraphics
        self.GdipDeleteGraphics.restype = wintypes.UINT
        self.GdipDeleteGraphics.argtypes = [wintypes.LPVOID]
        self.GdipDeleteGraphics.errcheck = GDIPlus.gpstatus_errcheck

        self.LF_FACESIZE = 32
        self.LANG_NEUTRAL = 0
        self.UnitPoint = 3 # https://learn.microsoft.com/en-us/windows/win32/api/gdiplusenums/ne-gdiplusenums-unit


    @staticmethod
    def gpstatus_errcheck(result, func, args):
        if result != GPSTATUS.Ok:
            raise OSError(f"{func.__name__} fails. It reported the error {GPSTATUS(result).name}")
        return result
