# -*- coding: utf-8 -*-
"""
Bot that creates word clouds from scientific articles and posts them to Twitter
"""
import feedparser as fp
import os
import urllib

from parse_article import get_text
from draw_wordcloud import plot_wc
from twiply import post_tweet

rss_feed_urls = dict(ACP='http://www.atmos-chem-phys.net/xml/rss2_0.xml')

for journ in rss_feed_urls:
    rss = rss_feed_urls[journ]
    f = fp.parse(rss)
    
    curdir = os.path.dirname(os.path.realpath(__file__))
    logfile = os.path.join(curdir, 'processed_entries_urls_'+journ+'.log')
    for i, entry in enumerate(f.entries):
        url = entry.link
        try:
            with open(logfile, 'r') as log:
                logged = log.read().split('\n')
            new_entry = True
            for l in logged:
                if url == l:
                    new_entry = False
                    break
        except FileNotFoundError:
            #print('file not found')
            new_entry = True 
    
        if new_entry:
            text = get_text(url)
            
            imgname = plot_wc(text)
            
            post_tweet(url, journ, entry.title, imgname) 
            with open(logfile, 'a') as log:
                log.write(url + '\n')
