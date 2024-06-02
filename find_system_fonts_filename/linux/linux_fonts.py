from .fontconfig import FontConfig, FC_FONT_FORMAT
from ctypes import byref, c_char_p, c_int, c_void_p, cdll, POINTER, Structure, util
from enum import Enum, IntEnum
from typing import Set
from ..exceptions import FontConfigNotFound
from ..system_fonts import SystemFonts



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

        fonts_filename = set()
        font_config = FontConfig()

        config = font_config.FcInitLoadConfigAndFonts()
        pat = font_config.FcPatternCreate()
        os = font_config.FcObjectSetBuild(font_config.FC_FILE, font_config.FC_FONTFORMAT, 0)
        fs = font_config.FcFontList(config, pat, os)

        for i in range(fs.contents.nfont):
            font = fs.contents.fonts[i]
            file_path_ptr = c_char_p()
            font_format_ptr = c_char_p()

            if (
                font_config.FcPatternGetString(font, font_config.FC_FONTFORMAT, 0, byref(font_format_ptr)) == font_config.FC_RESULT.FC_RESULT_MATCH
                and font_config.FcPatternGetString(font, font_config.FC_FILE, 0, byref(file_path_ptr)) == font_config.FC_RESULT.FC_RESULT_MATCH
            ):
                font_format = FC_FONT_FORMAT(font_format_ptr.value)

                if font_format in LinuxFonts.VALID_FONT_FORMATS:
                    # Decode with utf-8 since FcChar8
                    fonts_filename.add(file_path_ptr.value.decode())

        font_config.FcConfigDestroy(config)
        font_config.FcPatternDestroy(pat)
        font_config.FcObjectSetDestroy(os)
        font_config.FcFontSetDestroy(fs)

        return fonts_filename
