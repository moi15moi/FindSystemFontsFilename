from ctypes import c_char_p, c_void_p, cdll, util
from ..exceptions import AndroidLibraryNotFound, OSNotSupported

__all__ = ["Android"]


class Android():
    def __init__(self) -> None:

        android_library_name = util.find_library("android")

        if android_library_name is None:
            raise AndroidLibraryNotFound("You need to have the libandroid library. It is only available since the SDK/API level 29.")

        android = cdll.LoadLibrary(android_library_name)

        try:
            # https://developer.android.com/ndk/reference/group/font#asystemfontiterator_open
            self.ASystemFontIterator_open = android.ASystemFontIterator_open
            self.ASystemFontIterator_open.restype = c_void_p
            self.ASystemFontIterator_open.argtypes = []
        except AttributeError:
            raise OSNotSupported("FindSystemFontsFilename only works on Android API level 29 or more.")

        # https://developer.android.com/ndk/reference/group/font#asystemfontiterator_next
        self.ASystemFontIterator_next = android.ASystemFontIterator_next
        self.ASystemFontIterator_next.restype = c_void_p
        self.ASystemFontIterator_next.argtypes = [c_void_p]

        # https://developer.android.com/ndk/reference/group/font#asystemfontiterator_close
        self.ASystemFontIterator_close = android.ASystemFontIterator_close
        self.ASystemFontIterator_close.restype = None
        self.ASystemFontIterator_close.argtypes = [c_void_p]

        # https://developer.android.com/ndk/reference/group/font#afont_getfontfilepath
        self.AFont_getFontFilePath = android.AFont_getFontFilePath
        self.AFont_getFontFilePath.restype = c_char_p
        self.AFont_getFontFilePath.argtypes = [c_void_p]

        # https://developer.android.com/ndk/reference/group/font#afont_close
        self.AFont_close = android.AFont_close
        self.AFont_close.restype = None
        self.AFont_close.argtypes = [c_void_p]
