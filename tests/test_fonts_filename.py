import os
from pathlib import Path
from platform import system

import pytest
from find_system_fonts_filename import get_system_fonts_filename, install_font, uninstall_font
from os.path import isfile


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

@pytest.mark.skipif(system() != 'Windows', reason="Test runs only on Windows")
def test_install_uninstall_font_windows():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = Path(os.path.join(dir_path, "SuperFunky-lgmWw.ttf"))

    fonts_filename = get_system_fonts_filename()
    assert not any(os.path.samefile(filename, f) for f in fonts_filename)

    install_font(filename, True)
    fonts_filename = get_system_fonts_filename()
    assert any(os.path.samefile(filename, f) for f in fonts_filename)

    uninstall_font(filename, True)
    assert not any(os.path.samefile(filename, f) for f in fonts_filename)

    install_font(filename, False)
    fonts_filename = get_system_fonts_filename()
    assert any(os.path.samefile(filename, f) for f in fonts_filename)

    uninstall_font(filename, False)
    assert not any(os.path.samefile(filename, f) for f in fonts_filename)

@pytest.mark.skipif(system() == 'Windows', reason="Test runs on any platform except Windows")
def test_install_uninstall_font_not_windows():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = Path(os.path.join(dir_path, "SuperFunky-lgmWw.ttf"))

    fonts_filename = get_system_fonts_filename()
    assert not any(os.path.samefile(filename, f) for f in fonts_filename)

    install_font(filename)
    fonts_filename = get_system_fonts_filename()
    assert any(os.path.samefile(filename, f) for f in fonts_filename)

    uninstall_font(filename)
    assert not any(os.path.samefile(filename, f) for f in fonts_filename)
