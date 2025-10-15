from ctypes import c_char_p, c_int, c_void_p, CDLL, POINTER, Structure, util
from enum import Enum, IntEnum
from ..exceptions import FontConfigNotFound

__all__ = [
    "FontConfig",
    "FC_FONT_FORMAT",
    "FC_RESULT",
    "FcFontSet"
]


class FC_FONT_FORMAT(Enum):
    # https://freetype.org/freetype2/docs/reference/ft2-font_formats.html#ft_get_font_format
    # https://gitlab.freedesktop.org/freetype/freetype/-/blob/0a3836c97d5e84d6721ac0fd2839e8ae1b7be8d9/include/freetype/internal/services/svfntfmt.h#L36
    FT_FONT_FORMAT_TRUETYPE = b"TrueType"
    FT_FONT_FORMAT_TYPE_1 = b"Type 1"
    FT_FONT_FORMAT_BDF = b"BDF"
    FT_FONT_FORMAT_PCF = b"PCF"
    FT_FONT_FORMAT_TYPE_42 = b"Type 42"
    FT_FONT_FORMAT_CID = b"CID Type 1"
    FT_FONT_FORMAT_CFF = b"CFF"
    FT_FONT_FORMAT_PFR = b"PFR"
    FT_FONT_FORMAT_WINFNT = b"Windows FNT"


class FC_RESULT(IntEnum):
    # https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/222d058525506e587a45368f10e45e4b80ca541f/fontconfig/fontconfig.h#L241
    FC_RESULT_MATCH = 0
    FC_RESULT_NO_MATCH = 1
    FC_RESULT_TYPE_MISMATCH = 2
    FC_RESULT_NO_ID = 3
    FC_RESULT_OUT_OF_MEMORY = 4


class FcFontSet(Structure):
    # https://gitlab.freedesktop.org/fontconfig/fontconfig/-/blob/222d058525506e587a45368f10e45e4b80ca541f/fontconfig/fontconfig.h#L278
    _fields_ = [
        ("nfont", c_int),
        ("sfont", c_int),
        ("fonts", POINTER(POINTER(c_void_p))),
    ]


class FontConfig():
    def __init__(self) -> None:

        font_config_library_name = util.find_library("fontconfig")

        if font_config_library_name is None:
            raise FontConfigNotFound("You need to install FontConfig to get the fonts filename")

        font_config = CDLL(font_config_library_name)

        self.FC_FONTFORMAT = FontConfig.string_to_cstring("fontformat")
        self.FC_FILE = FontConfig.string_to_cstring("file")

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcinitloadconfigandfonts.html
        self.FcInitLoadConfigAndFonts = font_config.FcInitLoadConfigAndFonts
        self.FcInitLoadConfigAndFonts.restype = c_void_p
        self.FcInitLoadConfigAndFonts.argtypes = []

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcpatterncreate.html
        self.FcPatternCreate = font_config.FcPatternCreate
        self.FcPatternCreate.restype = c_void_p
        self.FcPatternCreate.argtypes = []

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcobjectsetbuild.html
        self.FcObjectSetBuild = font_config.FcObjectSetBuild
        self.FcObjectSetBuild.restype = c_void_p
        self.FcObjectSetBuild.argtypes = [c_char_p, c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcfontlist.html
        self.FcFontList = font_config.FcFontList
        self.FcFontList.restype = POINTER(FcFontSet)
        self.FcFontList.argtypes = [c_void_p, c_void_p, c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcpatternget-type.html
        self.FcPatternGetString = font_config.FcPatternGetString
        self.FcPatternGetString.restype = FC_RESULT
        self.FcPatternGetString.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_char_p)]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcconfigdestroy.html
        self.FcConfigDestroy = font_config.FcConfigDestroy
        self.FcConfigDestroy.restype = None
        self.FcConfigDestroy.argtypes = [c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcpatterndestroy.html
        self.FcPatternDestroy = font_config.FcPatternDestroy
        self.FcPatternDestroy.restype = None
        self.FcPatternDestroy.argtypes = [c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcobjectsetdestroy.html
        self.FcObjectSetDestroy = font_config.FcObjectSetDestroy
        self.FcObjectSetDestroy.restype = None
        self.FcObjectSetDestroy.argtypes = [c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcfontsetdestroy.html
        self.FcFontSetDestroy = font_config.FcFontSetDestroy
        self.FcFontSetDestroy.restype = None
        self.FcFontSetDestroy.argtypes = [c_void_p]

        # https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-devel/fcconfiggetfontdirs.html
        self.FcConfigGetFontDirs = font_config.FcConfigGetFontDirs
        self.FcConfigGetFontDirs.restype = c_void_p
        self.FcConfigGetFontDirs.argtypes = [c_void_p]

        # Introduced in 2.11.0
        if hasattr(font_config, "FcStrListFirst"):
            # https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-devel/fcstrlistfirst.html
            self.FcStrListFirst = font_config.FcStrListFirst
            self.FcStrListFirst.restype = None
            self.FcStrListFirst.argtypes = [c_void_p]

        # https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-devel/fcstrlistnext.html
        self.FcStrListNext = font_config.FcStrListNext
        self.FcStrListNext.restype = c_char_p
        self.FcStrListNext.argtypes = [c_void_p]

        # https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-devel/fcstrlistdone.html
        self.FcStrListDone = font_config.FcStrListDone
        self.FcStrListDone.restype = None
        self.FcStrListDone.argtypes = [c_void_p]

        # https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-devel/fcconfiggetcurrent.html
        self.FcConfigGetCurrent = font_config.FcConfigGetCurrent
        self.FcConfigGetCurrent.restype = c_void_p
        self.FcConfigGetCurrent.argtypes = []

        # Introduced in 2.11.1
        if hasattr(font_config, "FcDirCacheRescan"):
            # https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-devel/fcdircacherescan.html
            self.FcDirCacheRescan = font_config.FcDirCacheRescan
            self.FcDirCacheRescan.restype = c_void_p
            self.FcDirCacheRescan.argtypes = [c_char_p, c_void_p]

        # https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-devel/fcgetversion.html
        self.FcGetVersion = font_config.FcGetVersion
        self.FcGetVersion.restype = c_int
        self.FcGetVersion.argtypes = []


    @staticmethod
    def string_to_cstring(string: str) -> c_char_p:
        return c_char_p(bytes(ord(c) for c in string))
