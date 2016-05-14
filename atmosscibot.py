# -*- coding: utf-8 -*-
"""
Bot that creates word clouds from scientific articles and posts them to Twitter
"""
from datetime import datetime
from glob import glob
import feedparser as fp
import json
import logging
import numpy as np
import os
from PIL import Image
import time
from tinydb import TinyDB, where
from wordcloud import WordCloud, STOPWORDS
import urllib

from parse_article import extract_text
from settings import Settings
from shorten_url_api import UrlShortener
from twitter_api import TwitterApi

class AtmosSciBot(object):
    def __init__(self, curdir, settings, twitter_api, url_shortener, logger):
        self.curdir = curdir
        self.logger =  logger
        self.j_list_path = os.path.join(self.curdir, settings.get_journal_list())
        self.db_file = settings.get_db_file()
        
        # Word Cloud settings
        self.minwords = settings.get_min_words()
        self.stopwords_dir = settings.get_stopwords_dir()
        self.dpi = settings.get_dpi()
        self.width = settings.get_width()
        self.height = settings.get_height()
        self.wordcloud_mask = settings.get_wordcloud_mask()
        self.temp_dir = settings.get_temp_dir()
        self.temp_file = settings.get_temp_file()
        
        self.twitter_api = twitter_api
        self.url_shortener = url_shortener
        
    def check_new_entry(self, url):
        query_result = self.DB.search(where('url')==url)
        new_entry = False if len(query_result)>0 else True
        return new_entry
    
    def write_entry(self, url, j_short_name):
        new_entry = dict(journal_short_name=j_short_name, url=url, datetime=datetime.utcnow().strftime('%Y%m%d%H%M%S'))
        self.DB.insert(new_entry)
            
    def make_title(self, url, journal, title):
        if 'discuss' in url:
            # EGU discussion journals
            journal_name = journal+'D'
        else:
            journal_name = journal
        return journal_name + ': ' + title    
        
    def make_img_file(self):
        output_dir = os.path.join(self.curdir, self.temp_dir)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        self.img_file = os.path.join(output_dir, self.temp_file)
    
    def get_exclude_words(self):
        """ list of words to exclude """
        exclude_words = list(STOPWORDS)
        stopword_files = glob(os.path.join(self.curdir, 
                                           self.stopwords_dir,
                                           '*.txt'))
        for fname in stopword_files:
            with open(fname, 'r') as f:
                exclude_words += f.read().split('\n')
        self.exclude_words = set(exclude_words)

    def generate_wc(self, background_color='#ffffff'):
        """generate wordcloud and save to file"""       
        #fig_kw = dict(figsize=(self.width/self.dpi, self.height/self.dpi),
        #              dpi=self.dpi)
        self.get_exclude_words()
        try:
            arr = np.array(Image.open(os.path.join(self.curdir, self.wordcloud_mask)))
            # Other masks can be extracted from Font-Awesome (http://minimaxir.com/2016/05/wordclouds/)

            wc = WordCloud(width=self.width, height=self.height, \
                           stopwords=self.exclude_words, \
                           background_color=background_color, mode='RGBA', \
                           mask=arr).generate(self.text)
            
            self.make_img_file()
            wc.to_file(self.img_file)
            self.error_in_wordcloud_gen = None

        except Exception as e:
            self.error_in_wordcloud_gen = e

    def run(self):

        self.DB = TinyDB(os.path.join(curdir, self.db_file))
        
        with open(self.j_list_path) as json_file:
            j_list = json.load(json_file)

        for journ in j_list:
            f = fp.parse(journ['rss'])
            j_short_name = journ['short_name']
            self.logger.info('({jshort}) Parsed RSS of {jname}'.format(jname=journ['name'], jshort=j_short_name))
            
            for i, entry in enumerate(f.entries):
                url = entry.link
                if j_short_name == 'ASL' and 'author' in entry:
                    # Skip "Issue information"
                    # TODO: needs improvement...
                    if entry.author == '':
                        new_entry = False

                new_entry = self.check_new_entry(url)

                if new_entry:
                    self.logger.info('({jshort}) New entry in: {url}'.format(jshort=j_short_name, url=entry.url))
                    self.text = extract_text(url, j_short_name)

                    if len(self.text) > self.minwords:
                        imgname = self.generate_wc()
                        if self.error_in_wordcloud_gen is None:
                            imgname = self.img_file
                        else:
                            self.logger.warning('({jshort}) Wordcloud generation ERR: {e}'.format(jshort=j_short_name,
                                                                                              e=self.error_in_wordcloud_gen))
                    else:
                        imgname = None
                        self.logger.warning('({jshort}) Text length {textlen} is less than {minlen}'.format(jshort=j_short_name,
                                                                                                        textlen=len(self.text),
                                                                                                        minlen=(self.minwords)))
                        
                    ttl = self.make_title(url, j_short_name, entry.title)
                    
                    short_url = self.url_shortener.shorten(url)
                    
                    self.twitter_api.post_tweet(ttl, short_url, imgname)
                    
                    self.write_entry(url, j_short_name)


if __name__ == '__main__':
    # Get current directory path
    curdir = os.path.dirname(os.path.realpath(__file__))
    # Read settings
    s = Settings(os.path.join(curdir, 'settings.ini'))
    #
    # Set up logging
    #
    log_dir = os.path.join(curdir, s.get_log_dirname())
    if not os.path.isdir(log_dir): os.mkdir(log_dir)
    log_file = os.path.join(log_dir,
                            s.get_log_filename().format(datetime=datetime.utcnow().strftime('%Y%m%d')))

    # create logger
    logger = logging.getLogger('atmosscibot_main')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s') #, datefmt='%Y%m%d %H:%M:%S')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    
    twitter_api = TwitterApi(s.get_twitter_api_key(), s.get_twitter_api_secret(), 
                             s.get_twitter_access_token(), s.get_twitter_access_token_secret())
    url_shortener = UrlShortener(api_name=s.get_url_shortener_api(), \
                                 login=s.get_url_shortener_login(), \
                                 api_key=s.get_url_shortener_key())
    logger.info('Initialised')
    bot = AtmosSciBot(curdir, s, twitter_api, url_shortener, logger)
    logger.info('Run started')
    bot.run()
    logger.info('Run finished')
