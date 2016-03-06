# -*- coding: utf-8 -*-
"""
Bot that creates word clouds from scientific articles and posts them to Twitter
"""
import feedparser as fp
import json
import os
import urllib

from parse_article import get_text
from draw_wordcloud import plot_wc
from twiply import post_tweet

curdir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(curdir,'journal_list.json')) as json_file:
    j_list = json.load(json_file)

for journ in j_list:
    f = fp.parse(journ['rss'])
    
    if journ['short_name'] in ['ACP', 'ACPD']:
        # write ACP and ACPD in the same log file
        logfile = os.path.join(curdir, 'processed_entries_urls_ACP.log')
    else:
        logfile = os.path.join(curdir, 'processed_entries_urls_'+journ['short_name']+'.log')

    for i, entry in enumerate(f.entries):
        if journ['short_name'] == 'ASL' and 'author' in entry:
            # Skip "Issue information"
            if entry.author == '':
                new_entry = False

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
            text = get_text(url, journ['short_name'])
            
            if len(text) > 100:
                imgname = plot_wc(text)
            else:
                imgname = None
            
            post_tweet(url, journ['short_name'], entry.title, imgname) 
            with open(logfile, 'a') as log:
                log.write(url + '\n')
