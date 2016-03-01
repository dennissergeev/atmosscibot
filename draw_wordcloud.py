# -*- coding: utf-8 -*-
"""
Create a word cloud from text
"""
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

dpi = 100
fig_kw = dict(figsize=(1024/dpi, 512/dpi), dpi=dpi)
curdir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(curdir,'wordcloud_img')
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
imgname = os.path.join(output_dir,
                       'fig2tweet.png')
logging.basicConfig(filename=os.path.join(curdir,'draw_wordcloud.log'),
                    level=logging.DEBUG, format='%(asctime)s %(message)s')

# words to exclude
exclude_words = list(STOPWORDS)
for fname in ['ten_hundred_most_used_words',
              'technical_words',
              'academ_words',
              'unit_words']:
    with open(os.path.join(curdir,'exclude_words',fname), 'r') as f:
        exclude_words += f.read().split('\n')
exclude_words = set(exclude_words)

def plot_wc(text):
    try:
        arr = np.array(Image.open(os.path.join(curdir, 'mask_ellipse.png')))

        wc = WordCloud(stopwords=exclude_words, background_color=None, mode='RGBA', mask=arr)
        wc.generate(text)

        fig = plt.figure(**fig_kw)
        ax = fig.add_axes([0., 0., 1., 1.])
        ax.imshow(wc)
        ax.axis('off')

        #extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(imgname)
        plt.close(fig)
        return imgname

    except Exception as e:
        logging.error(e)
