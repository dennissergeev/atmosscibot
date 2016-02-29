# -*- coding: utf-8 -*-
"""
Bot that creates word clouds from scientific articles and posts them to Twitter
"""
import feedparser as fp
import urllib

from parse_article import get_text
from draw_wordcloud import basic
from twiply import post_tweet

rss_feed_url = 'http://www.atmos-chem-phys.net/xml/rss2_0.xml'

f = fp.parse(rss_feed_url)

for i, entry in enumerate(f.entries):
    url = entry.link
    try:
        with open('links.log', 'r') as log:
            if not url in log.read():
                # Continue
                new_entry = True
            else:
                new_entry = False
    except FileNotFoundError:
        new_entry = True 

    if new_entry:
        text = get_text(url)
        
        imgname = basic(text)
        
        post_tweet(url, entry.title, imgname) 
        with open('links.log', 'a') as log:
            log.write(url + '\n')
