from ctypes import POINTER, c_ubyte, Structure, windll, WINFUNCTYPE, wintypes
from enum import IntEnum

__all__ = [
    "LOGFONTW",
    "TEXTMETRIC",
    "GDI",
]

class Pitch(IntEnum):
    # https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wmf/22dbe377-aec4-4669-88e6-b8fdd9351d76
    DEFAULT_PITCH           = 0
    FIXED_PITCH             = 1
    VARIABLE_PITCH          = 2


class Family(IntEnum):
    # https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wmf/9a632766-1f1c-4e2b-b1a4-f5b1a45f99ad
    FF_DONTCARE = 0 << 4
    FF_ROMAN = 1 << 4
    FF_SWISS = 2 << 4
    FF_MODERN = 3 << 4
    FF_SCRIPT = 4 << 4
    FF_DECORATIVE = 5 << 4


class CharacterSet(IntEnum):
    # https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wmf/0d0b32ac-a836-4bd2-a112-b6000a1b4fc9
    ANSI_CHARSET = 0x00000000
    DEFAULT_CHARSET = 0x00000001
    SYMBOL_CHARSET = 0x00000002
    MAC_CHARSET = 0x0000004D
    SHIFTJIS_CHARSET = 0x00000080
    HANGUL_CHARSET = 0x00000081
    JOHAB_CHARSET = 0x00000082
    GB2312_CHARSET = 0x00000086
    CHINESEBIG5_CHARSET = 0x00000088
    GREEK_CHARSET = 0x000000A1
    TURKISH_CHARSET = 0x000000A2
    VIETNAMESE_CHARSET = 0x000000A3
    HEBREW_CHARSET = 0x000000B1
    ARABIC_CHARSET = 0x000000B2
    BALTIC_CHARSET = 0x000000BA
    RUSSIAN_CHARSET = 0x000000CC
    THAI_CHARSET = 0x000000DE
    EASTEUROPE_CHARSET = 0x000000EE
    OEM_CHARSET = 0x000000FF
    FEOEM_CHARSET = 254 # From https://github.com/tongzx/nt5src/blob/daad8a087a4e75422ec96b7911f1df4669989611/Source/XPSP1/NT/windows/core/ntgdi/fondrv/tt/ttfd/fdfon.c#L6718


class LOGFONTW(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-logfontw
    _fields_ = [
        ("lfHeight", wintypes.LONG),
        ("lfWidth", wintypes.LONG),
        ("lfEscapement", wintypes.LONG),
        ("lfOrientation", wintypes.LONG),
        ("lfWeight", wintypes.LONG),
        ("lfItalic", c_ubyte), # Cannot use c_ubyteS on old version of python, see https://github.com/python/cpython/issues/60580
        ("lfUnderline", c_ubyte),
        ("lfStrikeOut", c_ubyte),
        ("lfCharSet", c_ubyte),
        ("lfOutPrecision", c_ubyte),
        ("lfClipPrecision", c_ubyte),
        ("lfQuality", c_ubyte),
        ("lfPitchAndFamily", c_ubyte),
        ("lfFaceName", wintypes.WCHAR * 32),
    ]

    def __str__(self) -> str:
        attributes = []
        for field_name, _ in self._fields_:
            value = getattr(self, field_name)
            if field_name == "lfCharSet":
                value = CharacterSet(value).name
            elif field_name == "lfPitchAndFamily":
                family = value & 0b11110000
                pitch = value & 0b00001111
                value = f"{Pitch(pitch).name}|{Family(family).name}"
            elif field_name == "lfItalic":
                value = bool(value)

            attributes.append(f"{field_name}: {value}")
        return "\n".join(attributes)


class TEXTMETRIC(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-textmetricw
    _fields_ = [
        ('tmHeight', wintypes.LONG),
        ('tmAscent', wintypes.LONG),
        ('tmDescent', wintypes.LONG),
        ('tmInternalLeading', wintypes.LONG),
        ('tmExternalLeading', wintypes.LONG),
        ('tmAveCharWidth', wintypes.LONG),
        ('tmMaxCharWidth', wintypes.LONG),
        ('tmWeight', wintypes.LONG),
        ('tmOverhang', wintypes.LONG),
        ('tmDigitizedAspectX', wintypes.LONG),
        ('tmDigitizedAspectY', wintypes.LONG),
        ('tmFirstChar', wintypes.WCHAR),
        ('tmLastChar', wintypes.WCHAR),
        ('tmDefaultChar', wintypes.WCHAR),
        ('tmBreakChar', wintypes.WCHAR),
        ('tmItalic', c_ubyte),
        ('tmUnderlined', c_ubyte),
        ('tmStruckOut', c_ubyte),
        ('tmPitchAndFamily', c_ubyte),
        ('tmCharSet', c_ubyte)
    ]


class ENUMLOGFONTEXW(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-enumlogfontexw
    _fields_ = [
        ("elfLogFont", LOGFONTW),
        ("elfFullName", wintypes.WCHAR * 64),
        ("elfStyle", wintypes.WCHAR * 32),
        ("elfScript", wintypes.WCHAR * 32),
    ]


class GDI:
    def __init__(self) -> None:
        gdi = windll.gdi32

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createcompatibledc
        self.CreateCompatibleDC = gdi.CreateCompatibleDC
        self.CreateCompatibleDC.restype = wintypes.HDC
        self.CreateCompatibleDC.argtypes = [wintypes.HDC]
        self.CreateCompatibleDC.errcheck = self.errcheck_is_result_0_or_null

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-deletedc
        self.DeleteDC = gdi.DeleteDC
        self.DeleteDC.restype = wintypes.BOOL
        self.DeleteDC.argtypes = [wintypes.HDC]
        self.DeleteDC.errcheck = self.errcheck_is_result_0_or_null

        # https://learn.microsoft.com/en-us/previous-versions/dd162618(v=vs.85)
        self.ENUMFONTFAMEXPROC = WINFUNCTYPE(
            wintypes.INT,
            ENUMLOGFONTEXW,
            TEXTMETRIC,
            wintypes.DWORD,
            wintypes.LPARAM,
        )

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-enumfontfamiliesw
        self.EnumFontFamiliesW = gdi.EnumFontFamiliesW
        self.EnumFontFamiliesW.restype = wintypes.INT
        self.EnumFontFamiliesW.argtypes = [wintypes.HDC, wintypes.LPCWSTR, self.ENUMFONTFAMEXPROC, wintypes.LPARAM]

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-enumfontfamiliesexw
        self.EnumFontFamiliesExW = gdi.EnumFontFamiliesExW
        self.EnumFontFamiliesExW.restype = wintypes.INT
        self.EnumFontFamiliesExW.argtypes = [wintypes.HDC, POINTER(LOGFONTW), self.ENUMFONTFAMEXPROC, wintypes.LPARAM, wintypes.DWORD]

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-enumfontsw
        self.EnumFontsW = gdi.EnumFontsW
        self.EnumFontsW.restype = wintypes.INT
        self.EnumFontsW.argtypes = [wintypes.HDC, wintypes.LPCWSTR, self.ENUMFONTFAMEXPROC, wintypes.LPARAM]

        self.RASTER_FONTTYPE = 0x0001
        self.DEVICE_FONTTYPE = 0x0002
        self.TRUETYPE_FONTTYPE = 0x0004

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfontindirectw
        self.CreateFontIndirectW = gdi.CreateFontIndirectW
        self.CreateFontIndirectW.restype = wintypes.HFONT
        self.CreateFontIndirectW.argtypes = [POINTER(LOGFONTW)]
        self.CreateFontIndirectW.errcheck = self.errcheck_is_result_0_or_null

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-selectobject
        self.SelectObject = gdi.SelectObject
        self.SelectObject.restype = wintypes.HGDIOBJ
        self.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
        self.SelectObject.errcheck = self.is_SelectObject_failed

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-deleteobject
        self.DeleteObject = gdi.DeleteObject
        self.DeleteObject.restype = wintypes.BOOL
        self.DeleteObject.argtypes = [wintypes.HGDIOBJ]
        self.DeleteObject.errcheck = self.errcheck_is_result_0_or_null

        self.LF_FACESIZE = 32

    @staticmethod
    def errcheck_is_result_0_or_null(result, func, args):
        if not result:
            raise OSError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

    @staticmethod
    def is_SelectObject_failed(result, func, args):
        HGDI_ERROR = wintypes.HGDIOBJ(0xFFFFFFFF)
        if result == None or result == HGDI_ERROR:
            raise OSError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result