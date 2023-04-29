class OSNotSupported(Exception):
    "Raised when an OS isn't supported"
    pass


class FontConfigNotFound(Exception):
    "Raised when a Fontconfig API haven't been found"
    pass