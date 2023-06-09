from contextlib import contextmanager
from ctypes import c_char_p, c_void_p, cdll, util
from os import close, devnull, dup, dup2, O_WRONLY, open
from sys import stderr, stdout
from typing import Set
from .exceptions import AndroidLibraryNotFound, OSNotSupported
from .system_fonts import SystemFonts


class AndroidFonts(SystemFonts):
    _android = None

    def get_system_fonts_filename() -> Set[str]:
        if AndroidFonts._android is None:
             AndroidFonts._load_android_library()

        fonts_filename = set()

        # Redirect the stderr_and_stdout to null since we don't care about android logs
        # There is __android_log_set_minimum_priority to set the log level, but even if I set it to 8 (which correspond to ANDROID_LOG_SILENT),
        #   it was still logging: https://developer.android.com/ndk/reference/group/logging#__android_log_set_minimum_priority
        with AndroidFonts._silence_stderr_and_stdout():
            font_iterator = AndroidFonts._android.ASystemFontIterator_open()

            while True:
                font = AndroidFonts._android.ASystemFontIterator_next(font_iterator)

                if font is None:
                    break

                font_filename = AndroidFonts._android.AFont_getFontFilePath(font).decode("utf-8")
                fonts_filename.add(font_filename)

                AndroidFonts._android.AFont_close(font)
            AndroidFonts._android.ASystemFontIterator_close(font_iterator)

        return fonts_filename

    @staticmethod
    def _load_android_library():
        android_library_name = util.find_library("android")

        if android_library_name is None:
            raise AndroidLibraryNotFound("You need to have the libandroid library. It is only available since the SDK/API level 29.")

        AndroidFonts._android = cdll.LoadLibrary(android_library_name)

        # The android device need to be at least on the level 29.
        # The function android_get_device_api_level is only available since the level 29, so we can't use it. See: https://developer.android.com/ndk/reference/group/apilevels#android_get_device_api_level
        # So, we try and see if the function are available
        try:
            # https://developer.android.com/ndk/reference/group/font#asystemfontiterator_open
            AndroidFonts._android.ASystemFontIterator_open.restype = c_void_p
            AndroidFonts._android.ASystemFontIterator_open.argtypes = []
        except AttributeError:
            raise OSNotSupported("FindSystemFontsFilename only works on Android API level 29 or more.")

        # https://developer.android.com/ndk/reference/group/font#asystemfontiterator_next
        AndroidFonts._android.ASystemFontIterator_next.restype = c_void_p
        AndroidFonts._android.ASystemFontIterator_next.argtypes = [c_void_p]

        # https://developer.android.com/ndk/reference/group/font#asystemfontiterator_close
        AndroidFonts._android.ASystemFontIterator_close.restype = None
        AndroidFonts._android.ASystemFontIterator_close.argtypes = [c_void_p]

        # https://developer.android.com/ndk/reference/group/font#afont_getfontfilepath
        AndroidFonts._android.AFont_getFontFilePath.restype = c_char_p
        AndroidFonts._android.AFont_getFontFilePath.argtypes = [c_void_p]

        # https://developer.android.com/ndk/reference/group/font#afont_close
        AndroidFonts._android.AFont_close.restype = None
        AndroidFonts._android.AFont_close.argtypes = [c_void_p]

    @contextmanager
    def _silence_stderr_and_stdout():
        # From: https://stackoverflow.com/a/75037627/15835974
        stderr_fd = stderr.fileno()
        orig_stderr_fd = dup(stderr_fd)

        stdout_fd = stdout.fileno()
        orig_stdout_fd = dup(stdout_fd)

        null_fd = open(devnull, O_WRONLY)
        dup2(null_fd, stderr_fd)
        dup2(null_fd, stdout_fd)
        try:
            yield
        finally:
            dup2(orig_stderr_fd, stderr_fd)
            dup2(orig_stdout_fd, stdout_fd)
            close(orig_stderr_fd)
            close(orig_stdout_fd)
            close(null_fd)
