# -*- coding: utf-8 -*-
"""
Create a word cloud from text
"""
import matplotlib.pyplot as plt
import os
from wordcloud import WordCloud, STOPWORDS

_omit_words = ['et', 'al', 'br', 'sup', 'sub', 'minus', 'plus', 'also', 'will', 'km', 'cm', 'therefore', 'may', 'fig']
dpi = 100
_fig_kw = dict(figsize=(440/dpi, 220/dpi), dpi=dpi)
_output_dir = 'wordcloud_img'

def basic(text):
    wc = WordCloud(stopwords=list(STOPWORDS)+_omit_words)
    arr = wc.generate(text)

    fig = plt.figure(**_fig_kw)
    ax = fig.add_subplot(111)
    ax.imshow(wc)
    ax.axis('off')
    
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    
    if not os.path.isdir(_output_dir):
        os.mkdir(_output_dir)

    imgname = os.path.join(_output_dir,
                           'fig2tweet.png')
    
    fig.savefig(imgname, bbox_inches=extent)
    plt.close(fig)

    return imgname
