import pytest
import sys
from filecmp import cmp
from os.path import dirname, isfile, join, realpath, samefile
from pathlib import Path
from platform import system
from sys import platform
from find_system_fonts_filename import get_system_fonts_filename, install_font, uninstall_font, OSNotSupported


def test_get_system_fonts_filename():
    fonts_filename = get_system_fonts_filename()

    # A system has at least 10 fonts, so the value should be safe
    assert len(fonts_filename) >= 10

    for filename in fonts_filename:
        assert isfile(filename)
        assert isinstance(filename, str)
        assert Path(filename).suffix.lstrip(".").strip().lower() in ["ttf", "otf", "ttc", "otc"]

        with open(filename, "rb") as font_file:
            truetype_signature = b"\x00\x01\x00\x00"
            opentype_signature = b"OTTO"
            collection_signature = b"ttcf"

            signature = font_file.read(4)
            assert signature in [truetype_signature, opentype_signature, collection_signature]

@pytest.mark.skipif(not (system() == "Windows" or platform == "cygwin"), reason="Test runs only on Windows")
def test_install_uninstall_font_windows():

    dir_path = dirname(realpath(__file__))
    filename = Path(join(dir_path, "files", "SuperFunky-lgmWw.ttf"))

    fonts_filename = get_system_fonts_filename()
    assert not any(samefile(filename, f) for f in fonts_filename)

    install_font(filename, True)
    fonts_filename = get_system_fonts_filename()
    assert any(samefile(filename, f) for f in fonts_filename)

    uninstall_font(filename, True)
    fonts_filename = get_system_fonts_filename()
    assert not any(samefile(filename, f) for f in fonts_filename)

    install_font(filename, False)
    fonts_filename = get_system_fonts_filename()
    assert any(samefile(filename, f) for f in fonts_filename)

    uninstall_font(filename, False)
    fonts_filename = get_system_fonts_filename()
    assert not any(samefile(filename, f) for f in fonts_filename)

@pytest.mark.skipif(system() != 'Darwin', reason="Test runs only on Darwin")
def test_install_uninstall_font_darwin():

    dir_path = dirname(realpath(__file__))
    filename = Path(join(dir_path, "files", "SuperFunky-lgmWw.ttf"))

    fonts_filename = get_system_fonts_filename()
    assert not any(samefile(filename, f) for f in fonts_filename)

    install_font(filename)
    fonts_filename = get_system_fonts_filename()
    assert any(samefile(filename, f) for f in fonts_filename)

    uninstall_font(filename)
    fonts_filename = get_system_fonts_filename()
    assert not any(samefile(filename, f) for f in fonts_filename)

@pytest.mark.skipif(not (system() == 'Linux' and not hasattr(sys, "getandroidapilevel")), reason="Test runs only on Linux")
def test_install_uninstall_font_linux():

    # On Linux, the installed font is a copy of the
    # requested font, so we need to compare the actual file,
    # not the file path.
    dir_path = dirname(realpath(__file__))
    filename = Path(join(dir_path, "files", "SuperFunky-lgmWw.ttf"))

    fonts_filename = get_system_fonts_filename()
    assert not any(cmp(filename, f, False) for f in fonts_filename)

    install_font(filename)
    fonts_filename = get_system_fonts_filename()
    assert any(cmp(filename, f, False) for f in fonts_filename)

    uninstall_font(filename)
    fonts_filename = get_system_fonts_filename()
    assert not any(cmp(filename, f, False) for f in fonts_filename)

@pytest.mark.skipif(not (system() == 'Linux' and hasattr(sys, "getandroidapilevel")), reason="Test runs only on Android")
def test_install_uninstall_font_android():
    dir_path = dirname(realpath(__file__))
    filename = Path(join(dir_path, "files", "SuperFunky-lgmWw.ttf"))

    with pytest.raises(OSNotSupported) as exc_info:
        install_font(filename)
    assert str(exc_info.value) == "You cannot install font on android."

    with pytest.raises(OSNotSupported) as exc_info:
        uninstall_font(filename)
    assert str(exc_info.value) == "You cannot uninstall font on android."
