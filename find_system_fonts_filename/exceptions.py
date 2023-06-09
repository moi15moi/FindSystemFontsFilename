class OSNotSupported(Exception):
    "Raised when an OS isn't supported"
    pass


class FontConfigNotFound(Exception):
    "Raised when the Fontconfig API haven't been found"
    pass


class AndroidLibraryNotFound(Exception):
    "Raised when the android library haven't been found"
    pass
