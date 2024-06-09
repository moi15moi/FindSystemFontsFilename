from .fontconfig import FontConfig, FC_FONT_FORMAT, FC_RESULT
import os
from pathlib import Path
from shutil import copyfile
from ctypes import byref, c_char_p
from typing import Set
from ..exceptions import FindSystemFontsFilenameException, OSNotSupported
from ..system_fonts import SystemFonts

__all__ = ["LinuxFonts"]


class LinuxFonts(SystemFonts):
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
                font_config.FcPatternGetString(font, font_config.FC_FONTFORMAT, 0, byref(font_format_ptr)) == FC_RESULT.FC_RESULT_MATCH
                and font_config.FcPatternGetString(font, font_config.FC_FILE, 0, byref(file_path_ptr)) == FC_RESULT.FC_RESULT_MATCH
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


    def install_font(font_filename: Path, windows_flags: bool) -> None:
        font_config = FontConfig()
        version = font_config.FcGetVersion()

        # We need 2.11.1 for FcDirCacheRescan
        if version < 21101:
            raise OSNotSupported("To install a font, you need to have at least the version 2.11.1 of fontconfig.")

        config = font_config.FcConfigGetCurrent()
        font_dirs = font_config.FcConfigGetFontDirs(config)
        font_config.FcStrListFirst(font_dirs)

        # We suppose that FcStrListNext always return the same Dirs
        dirs_encoded = font_config.FcStrListNext(font_dirs)
        if not dirs_encoded:
            raise FindSystemFontsFilenameException(f"Couldn't get the font directory.")
        dirs_decoded = dirs_encoded.decode("utf-8")

        font_config.FcStrListDone(font_dirs)

        copyfile(font_filename, os.path.join(dirs_decoded, font_filename.name))
        font_config.FcDirCacheRescan(dirs_encoded, config)
        font_config.FcConfigDestroy(config)


    def uninstall_font(font_filename: Path, windows_flags: bool) -> None:
        font_config = FontConfig()
        version = font_config.FcGetVersion()

        # We need 2.11.1 for FcDirCacheRescan
        if version < 21101:
            raise OSNotSupported("To install a font, you need to have at least the version 2.11.1 of fontconfig.")

        config = font_config.FcConfigGetCurrent()
        font_dirs = font_config.FcConfigGetFontDirs(config)
        font_config.FcStrListFirst(font_dirs)

        # We suppose that FcStrListNext always return the same Dirs
        dirs_encoded = font_config.FcStrListNext(font_dirs)
        if not dirs_encoded:
            raise FindSystemFontsFilenameException(f"Couldn't get the font directory.")
        dirs_decoded = dirs_encoded.decode("utf-8")

        font_config.FcStrListDone(font_dirs)

        file_path = os.path.join(dirs_decoded, font_filename.name)

        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            raise FindSystemFontsFilenameException(f"Couldn't get delete the font {font_filename}.")

        font_config.FcDirCacheRescan(dirs_encoded, config)
        font_config.FcConfigDestroy(config)
