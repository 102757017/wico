"""
Themes/Font Definitions
=======================

.. seealso::

   `Material Design spec, The type system <https://material.io/design/typography/the-type-system.html>`_
"""

from kivy.core.text import LabelBase
import os
import sys
from pathlib import Path
import pprint

#  所有基于模块的使用到__file__属性的代码，在源码运行时表示的是当前脚本的绝对路径，但是用pyinstaller打包后就是当前模块的模块名（即文件名xxx.py）
#  因此需要用以下代码来获取exe的绝对路径
if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    p = sys._MEIPASS
else:
    p = str(Path(__file__).parent)

fonts_path = p+os.path.sep


fonts = [
     {
         "name": "Roboto",
         "fn_regular": fonts_path + "DroidSansFallback.ttf",
         "fn_bold": fonts_path + "DroidSansFallback.ttf",
         "fn_italic": fonts_path + "DroidSansFallback.ttf",
         "fn_bolditalic": fonts_path + "DroidSansFallback.ttf",
     },
     {
         "name": "RobotoThin",
         "fn_regular": fonts_path + "DroidSansFallback.ttf",
         "fn_italic": fonts_path + "DroidSansFallback.ttf",
     },
     {
         "name": "RobotoLight",
         "fn_regular": fonts_path + "DroidSansFallback.ttf",
         "fn_italic": fonts_path + "DroidSansFallback.ttf",
     },
     {
         "name": "RobotoMedium",
         "fn_regular": fonts_path + "DroidSansFallback.ttf",
         "fn_italic": fonts_path + "DroidSansFallback.ttf",
     },
     {
         "name": "RobotoBlack",
         "fn_regular": fonts_path + "DroidSansFallback.ttf",
         "fn_italic": fonts_path + "DroidSansFallback.ttf",
     },
     {
         "name": "Icons",
         "fn_regular": fonts_path + "materialdesignicons-webfont.ttf",
     },
 ]

pprint.pprint(fonts)

for font in fonts:
    LabelBase.register(**font)

theme_font_styles = [
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "Subtitle1",
    "Subtitle2",
    "Body1",
    "Body2",
    "Button",
    "Caption",
    "Overline",
    "Icon",
]
"""
.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/font-styles-2.png
"""
