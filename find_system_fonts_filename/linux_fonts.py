from ctypes import byref, c_char_p, c_int, c_void_p, cdll, POINTER, Structure, util
from enum import Enum, IntEnum
from typing import Set
from .exceptions import FontConfigNotFound
from .system_fonts import SystemFonts


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


def string_to_cstring(string: str) -> c_char_p:
    return c_char_p(bytes(ord(c) for c in string))


FC_FONTFORMAT = string_to_cstring("fontformat")
FC_FILE = string_to_cstring("file")


class LinuxFonts(SystemFonts):
    _font_config = None
    VALID_FONT_FORMATS = [
        FC_FONT_FORMAT.FT_FONT_FORMAT_TRUETYPE,
        FC_FONT_FORMAT.FT_FONT_FORMAT_CFF,
    ]

    def get_system_fonts_filename() -> Set[str]:
        """
        Inspired by: https://stackoverflow.com/questions/10542832/how-to-use-fontconfig-to-get-font-list-c-c/14634033#14634033

        Return an list of all the font installed.
        """
        if LinuxFonts._font_config is None:
            LinuxFonts._load_font_config_library()

        fonts_filename = set()

        config = LinuxFonts._font_config.FcInitLoadConfigAndFonts()
        pat = LinuxFonts._font_config.FcPatternCreate()
        os = LinuxFonts._font_config.FcObjectSetBuild(FC_FILE, FC_FONTFORMAT, 0)
        fs = LinuxFonts._font_config.FcFontList(config, pat, os)

        for i in range(fs.contents.nfont):
            font = fs.contents.fonts[i]
            file_path_ptr = c_char_p()
            font_format_ptr = c_char_p()

            if (
                LinuxFonts._font_config.FcPatternGetString(font, FC_FONTFORMAT, 0, byref(font_format_ptr)) == FC_RESULT.FC_RESULT_MATCH
                and LinuxFonts._font_config.FcPatternGetString(font, FC_FILE, 0, byref(file_path_ptr)) == FC_RESULT.FC_RESULT_MATCH
            ):
                font_format = FC_FONT_FORMAT(font_format_ptr.value)

                if font_format in LinuxFonts.VALID_FONT_FORMATS:
                    # Decode with utf-8 since FcChar8
                    fonts_filename.add(file_path_ptr.value.decode())

        LinuxFonts._font_config.FcConfigDestroy(config)
        LinuxFonts._font_config.FcPatternDestroy(pat)
        LinuxFonts._font_config.FcObjectSetDestroy(os)
        LinuxFonts._font_config.FcFontSetDestroy(fs)

        return fonts_filename

    @staticmethod
    def _load_font_config_library():
        font_config_library_name = util.find_library("fontconfig")

        if font_config_library_name is None:
            raise FontConfigNotFound("You need to install FontConfig to get the fonts filename")

        LinuxFonts._font_config = cdll.LoadLibrary(font_config_library_name)

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcinitloadconfigandfonts.html
        LinuxFonts._font_config.FcInitLoadConfigAndFonts.restype = c_void_p
        LinuxFonts._font_config.FcInitLoadConfigAndFonts.argtypes = []

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcpatterncreate.html
        LinuxFonts._font_config.FcPatternCreate.restype = c_void_p
        LinuxFonts._font_config.FcPatternCreate.argtypes = []

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcobjectsetbuild.html
        LinuxFonts._font_config.FcObjectSetBuild.restype = c_void_p
        LinuxFonts._font_config.FcObjectSetBuild.argtypes = [c_char_p, c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcfontlist.html
        LinuxFonts._font_config.FcFontList.restype = POINTER(FcFontSet)
        LinuxFonts._font_config.FcFontList.argtypes = [c_void_p, c_void_p, c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcpatternget-type.html
        LinuxFonts._font_config.FcPatternGetString.restype = FC_RESULT
        LinuxFonts._font_config.FcPatternGetString.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_char_p)]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcconfigdestroy.html
        LinuxFonts._font_config.FcConfigDestroy.restype = None
        LinuxFonts._font_config.FcConfigDestroy.argtypes = [c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcpatterndestroy.html
        LinuxFonts._font_config.FcPatternDestroy.restype = None
        LinuxFonts._font_config.FcPatternDestroy.argtypes = [c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcobjectsetdestroy.html
        LinuxFonts._font_config.FcObjectSetDestroy.restype = None
        LinuxFonts._font_config.FcObjectSetDestroy.argtypes = [c_void_p]

        # https://www.freedesktop.org/software/fontconfig/fontconfig-devel/fcfontsetdestroy.html
        LinuxFonts._font_config.FcFontSetDestroy.restype = None
        LinuxFonts._font_config.FcFontSetDestroy.argtypes = [c_void_p]