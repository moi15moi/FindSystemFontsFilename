from pathlib import Path
from find_system_fonts_filename import get_system_fonts_filename
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
