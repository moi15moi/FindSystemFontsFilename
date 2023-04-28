# FindSystemFontsFilename
This tool allows you to get the font filename on your system.

It uses some APIs to find the font filename:
- Windows: [DirectWrite API](https://learn.microsoft.com/en-us/windows/win32/directwrite/direct-write-portal)
- macOS: [Core Text API](https://developer.apple.com/documentation/coretext)
- Linux: [Fontconfig API](https://www.freedesktop.org/wiki/Software/fontconfig/)

## Installation
```
pip install FindSystemFontsFilename
```

## How to use it
```python
from find_system_fonts_filename import get_system_fonts_filename

fonts_filename = get_system_fonts_filename()
```
