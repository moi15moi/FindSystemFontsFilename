from ctypes import c_int32, c_void_p, cdll, create_unicode_buffer
from pathlib import Path
from sysconfig import get_platform

__all__ = ["Cygwin"]


class Cygwin():
    def __init__(self) -> None:
        # Detect when it is msys: https://www.msys2.org/docs/python/
        cygwin = cdll.LoadLibrary("msys-2.0.dll" if get_platform().startswith("mingw") else "cygwin1.dll")
    
        # https://cygwin.com/cygwin-api/func-cygwin-conv-path.html
        self._cygwin_conv_path = cygwin.cygwin_conv_path
        self._cygwin_conv_path.restype = c_int32
        self._cygwin_conv_path.argtypes = [c_int32, c_void_p, c_void_p, c_int32]

        self._CCP_POSIX_TO_WIN_W = 1

    def posix_path_to_win32_path(self, path: Path) -> str:
        """
        Parameters:
            path: A path.
        Returns:
            A string that represent the path in the win32 form.
            Ex: /cygdrive/c/Users -> C:\\Users.
        """
        posix_path_buffer = str(path).encode("utf-8")
        size = self._cygwin_conv_path(self._CCP_POSIX_TO_WIN_W, posix_path_buffer, None, 0)
        win_path_buffer = create_unicode_buffer(size + 1)
        self._cygwin_conv_path(self._CCP_POSIX_TO_WIN_W, posix_path_buffer, win_path_buffer, size + 1)
        return win_path_buffer.value

