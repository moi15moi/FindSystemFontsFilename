from pathlib import Path
from .android import Android
from contextlib import contextmanager
from os import close, devnull, dup, dup2, O_WRONLY, open
from sys import stderr, stdout
from typing import Set
from ..exceptions import OSNotSupported
from ..system_fonts import SystemFonts

__all__ = ["AndroidFonts"]


class AndroidFonts(SystemFonts):

    def get_system_fonts_filename() -> Set[str]:
        android = Android()
        fonts_filename = set()

        # Redirect the stderr_and_stdout to null since we don't care about android logs
        # There is __android_log_set_minimum_priority to set the log level, but even if I set it to 8 (which correspond to ANDROID_LOG_SILENT),
        #   it was still logging: https://developer.android.com/ndk/reference/group/logging#__android_log_set_minimum_priority
        with AndroidFonts._silence_stderr_and_stdout():
            font_iterator = android.ASystemFontIterator_open()

            while True:
                font = android.ASystemFontIterator_next(font_iterator)

                if font is None:
                    break

                font_filename = android.AFont_getFontFilePath(font).decode("utf-8")
                fonts_filename.add(font_filename)

                android.AFont_close(font)
            android.ASystemFontIterator_close(font_iterator)

        return fonts_filename


    def install_font(font_filename: Path, windows_flags: bool) -> None:
        raise OSNotSupported("You cannot install font on android.")


    def uninstall_font(font_filename: Path, windows_flags: bool) -> None:
        raise OSNotSupported("You cannot uninstall font on android.")


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
