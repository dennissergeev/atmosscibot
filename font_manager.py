#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Get font for wordcloud."""
from glob import glob
import os
import subprocess as sb

DEFAULT_FONT_PATH = "fonts/Chicle/Chicle-Regular.ttf"
GOOGLEFONT_DOWNLOAD_SCRIPT = "../google-font-download/google-font-download"
ALL_EXTENSIONS = ["woff2", "woff", "eot", "svg", "ttf"]
FONT_EXTENSIONS = ["otf", "ttf"]


def get_font(font_name):
    """Try to download a regular font from Google Fonts or use the default one."""
    curdir = os.path.dirname(os.path.realpath(__file__))
    default = os.path.join(curdir, DEFAULT_FONT_PATH)
    if font_name is None:
        return default
    try:
        script = os.path.join(curdir, GOOGLEFONT_DOWNLOAD_SCRIPT)
        p = sb.run([script, "{}:400".format(font_name)])
        if p.returncode == 0:
            files = []
            for ext in ALL_EXTENSIONS:
                # move font files to a separate directory
                font_dir = os.path.join(curdir, "googlefonts")
                if not os.path.isdir(font_dir):
                    os.mkdir(font_dir)
                for f in glob(
                    os.path.join(
                        os.path.expanduser("~"),
                        "{}_400.*".format(font_name.replace(" ", "_")),
                    )
                ):
                    try:
                        new_name = os.path.join(font_dir, os.path.basename(f))
                        os.rename(f, new_name)
                        if os.path.splitext(new_name)[1][1:] in FONT_EXTENSIONS:
                            files.append(new_name)
                    except Exception as e:
                        _msg = "ERR when moving {f}: {e}"
                        logger.warning(_msg.format(f=f, e=e))
            try:
                # print(files)
                return files[0]
            except IndexError:
                return default
        else:
            return default
    except Exception as e:
        # print(e)
        return default
