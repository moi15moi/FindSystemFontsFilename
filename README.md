# FindSystemFontsFilename
This tool allows you to get the font filename on your system. It will collect TrueType (.ttf), OpenType (.otf) and TrueType Collection (.ttf) font format.

It uses some APIs to find the font filename:
- Windows: [DirectWrite API](https://learn.microsoft.com/en-us/windows/win32/directwrite/direct-write-portal)
- macOS: [Core Text API](https://developer.apple.com/documentation/coretext)
- Linux: [Fontconfig API](https://www.freedesktop.org/wiki/Software/fontconfig/)
- Android: [NDK Font API](https://developer.android.com/ndk/reference/group/font)

## Installation
```
pip install FindSystemFontsFilename
```

## How to use it
```python
from find_system_fonts_filename import get_system_fonts_filename, FontConfigNotFound, OSNotSupported

try:
    fonts_filename = get_system_fonts_filename()
except (FontConfigNotFound, OSNotSupported):
    # Deal with the exception
    # OSNotSupported can only happen in Windows, macOS and Android
    #   - Windows Vista SP2 and more are supported
    #   - macOS 10.6 and more are supported
    #   - Android SDK/API 29 and more are supported
    # FontConfigNotFound can only happen on Linux when Fontconfig could't be found.
    pass
```
