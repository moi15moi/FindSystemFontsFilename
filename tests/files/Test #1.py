from fontTools.ttLib.ttFont import TTFont
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

font = TTFont(os.path.join(dir_path, "Sunshine Tropical.ttf"))

name_record = font["name"].getName(4, 3, 1)
name_record.string = "A" * 30 + "\U0001f60b"

font.save(os.path.join(dir_path, "Test #1.ttf"))
