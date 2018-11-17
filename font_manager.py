#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Get font for wordcloud."""
from glob import glob
import os
import subprocess as sb

DEFAULT_FONT_PATH = 'fonts/Chicle/Chicle-Regular.ttf'
GOOGLEFONT_DOWNLOAD_SCRIPT = '../oogle-font-download/google-font-download'
FONT_EXTENSIONS = ['.ttf', '.otf']


def get_font(font_name):
    """Try to download a regular font from Google Fonts or use the default one."""
    curdir = os.path.dirname(os.path.realpath(__file__))
    if font_name is None:
        return DEFAULT_FONT_PATH
    try:
        p = sb.run([GOOGLEFONT_DOWNLOAD_SCRIPT, '{}:400'.format(font_name)])
        if p.returncode == 0:
            files = []
            for ext in FONT_EXTENSIONS:
                files += [*glob('name*{ext}'.format(name=font_name.replace(' ', '_'),
                                                    ext=ext))]
            try:
                font_path = os.path.join(curdir, files[0])
                return font_path
            except IndexError:
                return DEFAULT_FONT_PATH
        else:
            return DEFAULT_FONT_PATH
    except Exception:
        return DEFAULT_FONT_PATH
