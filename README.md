# FindSystemFontsFilename
[![FindSystemFontsFilename - CI Build Status](https://github.com/moi15moi/FindSystemFontsFilename/workflows/Run%20Tests/badge.svg)](https://github.com/moi15moi/FindSystemFontsFilename/actions/workflows/run_test.yml)
[![FindSystemFontsFilename - Version](https://img.shields.io/pypi/v/findsystemfontsfilename.svg)](https://pypi.org/project/FindSystemFontsFilename)
[![FindSystemFontsFilename - Python Version](https://img.shields.io/pypi/pyversions/findsystemfontsfilename.svg)](https://pypi.org/project/FindSystemFontsFilename)

This tool allows you to get the font filename on your system. It will collect TrueType (.ttf), OpenType (.otf), TrueType Collection (.ttc) and OpenType Collection (.otc) font format.

It uses some APIs to find the font filename:
- Windows (Vista SP2 and more are supported): [DirectWrite API](https://learn.microsoft.com/en-us/windows/win32/directwrite/direct-write-portal) and [GDI API](https://learn.microsoft.com/en-us/windows/win32/gdi/windows-gdi)
- macOS (10.6 and more are supported): [Core Text API](https://developer.apple.com/documentation/coretext)
- Unix: [Fontconfig API](https://www.freedesktop.org/wiki/Software/fontconfig/)
- Android (SDK/API 29 and more are supported): [NDK Font API](https://developer.android.com/ndk/reference/group/font)

## Installation
```
pip install FindSystemFontsFilename
```

## How to use it
```python
from find_system_fonts_filename import get_system_fonts_filename, FindSystemFontsFilenameException

try:
    fonts_filename = get_system_fonts_filename()
except FindSystemFontsFilenameException:
    # Deal with the exception
    pass
```
