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
