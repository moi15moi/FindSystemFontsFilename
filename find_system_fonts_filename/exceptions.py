__all__ = [
    "FindSystemFontsFilenameException",
    "OSNotSupported",
    "FontConfigNotFound",
    "AndroidLibraryNotFound",
    "NotSupportedFontFile",
    "SystemApiError"
]


class FindSystemFontsFilenameException(Exception):
    "Basic exception for this package"
    pass


class OSNotSupported(FindSystemFontsFilenameException):
    "Raised when an OS isn't supported"
    pass


class FontConfigNotFound(FindSystemFontsFilenameException):
    "Raised when the Fontconfig API haven't been found"
    pass


class AndroidLibraryNotFound(FindSystemFontsFilenameException):
    "Raised when the android library haven't been found"
    pass

class NotSupportedFontFile(FindSystemFontsFilenameException):
    "Raised when the user try to install a font, but it isn't supported by the OS"
    pass

class SystemApiError(FindSystemFontsFilenameException):
    "Raised when the system API returned an unexpected error."
    pass
