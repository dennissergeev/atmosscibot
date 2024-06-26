#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main body of atmosscibot.

This bot creates word clouds from scientific articles and posts them to Twitter.
"""
# Standard library
from datetime import datetime
import json
from glob import glob
import os
from random import choice, randint
import re
import time

# External packages
import feedparser as fp
import numpy as np
from PIL import Image
from tinydb import TinyDB, where
from wordcloud import WordCloud, STOPWORDS

# Local modules
from font_manager import get_font
from logger import logger
from parse_article import extract_text
from settings import Settings
from shorten_url_api import UrlShortener
from twitter_api import TwitterApi


SUCCESS = 0
NO_TEXT = 1  # mostly because it's not open access


class AtmosSciBot(object):
    """Main class for running atmosscibot."""

    def __init__(self, curdir, settings, twitter_api, url_shortener):
        self.settings = settings
        self.BOT_NAME = self.settings.get_bot_name()
        self.curdir = curdir
        self.browser_exec_dir = self.settings.get_browser_exec_dir()
        self.j_list_path = os.path.join(self.curdir, self.settings.get_journal_list())
        self.db_file = self.settings.get_db_file()

        # Word Cloud settings
        self.minwords = self.settings.get_min_words()
        self.stopwords_dir = self.settings.get_stopwords_dir()
        self.dpi = self.settings.get_dpi()
        self.width = self.settings.get_width()
        self.height = self.settings.get_height()
        self.wordcloud_mask_dir = self.settings.get_wordcloud_mask_dir()
        self.allow_font_change = self.settings.get_font_switch()
        self.font_name = None  # use default font
        self.temp_dir = self.settings.get_temp_dir()
        self.temp_file = self.settings.get_temp_file()
        self.mentions_file = self.settings.get_mentions_file()

        self.no_magic_word_gif = self.settings.get_no_magic_word_gif()

        self.twitter_api = twitter_api
        self.url_shortener = url_shortener

    def check_new_entry(self, url):
        # TODO: check status?
        query_result = self.DB.search(where("url") == url)
        new_entry = len(query_result) == 0
        return new_entry

    def write_entry(self, url, j_short_name, status):
        tstamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        new_entry = dict(
            journal_short_name=j_short_name, url=url, status=status, datetime=tstamp
        )
        self.DB.insert(new_entry)

    def make_title(self, url, journal, title):
        journal_name = journal
        if journal.upper() == "ATMOS":
            title = re.sub(r"Atmosphere, Vol. [0-9]+, Pages [0-9]+: ", "", title)
        return "#{}: {}".format(journal_name, title)

    def make_img_file(self):
        output_dir = os.path.join(self.curdir, self.temp_dir)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        tstamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        self.img_file = os.path.join(output_dir, self.temp_file.format(datetime=tstamp))

    def get_exclude_words(self):
        """list of words to exclude"""
        exclude_words = list(STOPWORDS)
        stopword_files = glob(os.path.join(self.curdir, self.stopwords_dir, "*.txt"))
        for fname in stopword_files:
            with open(fname, "r") as f:
                exclude_words += f.read().split("\n")
        self.exclude_words = set(exclude_words)

    def get_stencil(self):
        """Randomly select a stencil from the specified directory."""
        # Other masks can be extracted from
        # Font-Awesome (http://minimaxir.com/2016/05/wordclouds/)
        imgdir = os.path.join(self.curdir, self.wordcloud_mask_dir)
        imgpath = choice(glob(os.path.join(imgdir, "cloud_*.png")))
        self.stencil = np.array(Image.open(imgpath))

    def generate_wc(self, background_color="#ffffff"):
        """generate wordcloud and save to file"""
        # fig_kw = dict(figsize=(self.width/self.dpi, self.height/self.dpi),
        #               dpi=self.dpi)
        self.get_exclude_words()
        try:
            self.get_stencil()

            # Download font or use the default one
            font_path = get_font(self.font_name)
            if self.allow_font_change:
                logger.info(f"Using {font_path} font")

            wc = WordCloud(
                width=self.width,
                height=self.height,
                font_path=font_path,
                colormap=self.cmap,
                stopwords=self.exclude_words,
                background_color=background_color,
                mode="RGBA",
                mask=self.stencil,
            ).generate(self.text)

            self.make_img_file()
            wc.to_file(self.img_file)
            self.error_in_wordcloud_gen = None

            self.font_name = None  # reset to default

        except Exception as e:
            self.error_in_wordcloud_gen = e

    def parse_request(self, mention):
        regex_font = r"\[font=\s*([\w\s]*)\]"
        contains_j_name = False
        j_short_name = None
        url = None
        font_name = None
        contains_request = (
            "make" in mention.text.lower()
            and "word" in mention.text.lower()
            and "cloud" in mention.text.lower()
        )
        contains_magic_word = "please" in mention.text.lower()
        if self.allow_font_change:
            r = re.search(regex_font, mention.text)
            if r is not None:
                font_name = r.group(1)
        hashtags = [i["text"] for i in mention.entities["hashtags"]]
        if len(hashtags) == 1:
            j_short_name = hashtags[0].upper()
            j_names = [j["short_name"] for j in self.j_list]
            # check if hashtags contain a correct journal short name
            contains_j_name = j_short_name in j_names
            # any(i in j_names for i in hashtags)
        contains_url = len(mention.entities["urls"]) == 1
        if contains_url:
            url = mention.entities["urls"][0]["expanded_url"]
        is_correct = contains_request and contains_j_name and contains_url
        return is_correct, contains_magic_word, url, j_short_name, font_name

    def make_reply(self, user_name, url, err_msg=None):
        if err_msg is None:
            reply = f"@{user_name} here is a word cloud for this article {url}"
        else:
            reply = f"@{user_name} Unfortunately I can't create a word cloud. {err_msg}"
        return reply

    def check_new_mention(self, mention):
        query_res = self.mentions_db.search(where("id_str") == mention.id_str)
        new_mention = False if len(query_res) > 0 else True
        return new_mention

    def save_mention(self, mention):
        tstamp = mention.created_at.strftime("%Y%m%d%H%M%S")
        new_mention = dict(id_str=mention.id_str, datetime=tstamp)
        self.mentions_db.insert(new_mention)

    def get_new_mentions(self, last_mention_id=1):
        """Download the new mentions"""
        mentions = self.twitter_api.twitter_api.mentions_timeline(last_mention_id)
        return mentions

    def handle_mentions(self):
        """
        Handle the mentions of this twitter bot
        to generate wordclouds on demand

        using a database approach might be an overkill, but:
        1) it works
        2) is easily expandable
        """
        self.mentions_db = TinyDB(os.path.join(curdir, self.mentions_file))
        stored_mentions = sorted(self.mentions_db.all(), key=lambda k: k["datetime"])
        if len(stored_mentions) > 0:
            the_most_recent = stored_mentions[-1]["id_str"]
        else:
            the_most_recent = 1
        # get only the latest mentions
        mentions = self.get_new_mentions(the_most_recent)
        for mention in mentions:
            # may be redundant...
            new_mention = self.check_new_mention(mention)
            if new_mention:
                logger.info(
                    f"Handling mention from @{mention.user.screen_name}, with id={mention.id_str}"
                )
                self.save_mention(mention)

                user_name = mention.user.screen_name
                if user_name == self.BOT_NAME:
                    logger.info("Skipping this self mention")
                    continue

                kw = dict(imgname=None, in_reply_to_status_id=mention.id_str)
                (
                    is_correct,
                    please,
                    url,
                    j_short_name,
                    self.font_name,
                ) = self.parse_request(mention)
                short_url = None
                no_error = True
                if not is_correct:
                    err_msg = "Sorry, your request was not correct."
                    reply = self.make_reply(user_name, short_url, err_msg)
                    no_error = False
                if not please:
                    err_msg = "You did't say the magic word!"
                    kw["imgname"] = self.no_magic_word_gif
                    reply = self.make_reply(user_name, short_url, err_msg)
                    no_error = False
                if j_short_name not in [i["short_name"] for i in self.j_list]:
                    err_msg = "Sorry, the requested journal is not on the journal list."
                    reply = self.make_reply(user_name, short_url, err_msg)
                    no_error = False
                if no_error:
                    self.cmap = [
                        i["cmap"]
                        for i in self.j_list
                        if i["short_name"] == j_short_name
                    ][0]
                    # URL must be correct and directly lead to
                    # webpage with text to be parsed
                    # (unlike the ones in RSS feeds)
                    self.text = extract_text(
                        url, self.browser_exec_dir, j_short_name, url_ready=True
                    )
                    if len(self.text.split(" ")) >= self.minwords:
                        self.generate_wc()
                        if self.error_in_wordcloud_gen is None:
                            short_url = self.url_shortener.shorten(url)
                            reply = self.make_reply(user_name, short_url)
                            kw["imgname"] = self.img_file
                        else:
                            # TODO: specify the problem
                            err_msg = "Please check your request or the URL"
                            reply = self.make_reply(user_name, short_url, err_msg)
                    else:
                        err_msg = "Something went wrong or there is not enough text (<100 words)"
                        reply = self.make_reply(user_name, short_url, err_msg)
                self.twitter_api.post_tweet(reply, short_url, **kw)

    def run(self):
        with open(self.j_list_path) as json_file:
            self.j_list = json.load(json_file)

        # self.handle_mentions()

        self.DB = TinyDB(os.path.join(curdir, self.db_file))

        for journ in self.j_list:
            f = fp.parse(journ["rss"])
            j_short_name = journ["short_name"]
            self.cmap = journ["cmap"]
            logger.info(f"({j_short_name}) Parsed RSS of {journ['name']}")

            for i, entry in enumerate(f.entries):
                # Sleep for a few seconds to avoid too many requests errors
                time.sleep(randint(1, 11))
                try:
                    url = entry.link
                except AttributeError:
                    logger.error(f"No `link` attribute in entry={entry}")
                    continue
                if (j_short_name == "ASL") and ("author" in entry):
                    # Skip "Issue information"
                    # TODO: needs improvement...
                    if entry.author == "":
                        new_entry = False
                new_entry = self.check_new_entry(url)

                # if j_short_name in ['ACP', 'AMT', 'GMD']:
                # Check if the article is in the preprint stage
                try:
                    ispp = "Preprint under review" in entry.summary_detail.value
                except AttributeError:
                    ispp = False

                if ispp:
                    # Do not process preprints in EGU journals
                    new_entry = False

                if new_entry:
                    logger.info(f"({j_short_name}) New entry in: {url}")
                    self.text = extract_text(
                        url, self.browser_exec_dir, j_short_name, url_ready=False
                    )

                    if len(self.text) > self.minwords:
                        self.generate_wc()
                        if self.error_in_wordcloud_gen is None:
                            imgname = self.img_file
                            ttl = self.make_title(
                                url,
                                j_short_name,
                                entry.title,
                            )
                            short_url = self.url_shortener.shorten(url)
                            self.twitter_api.post_tweet(ttl, short_url, imgname)
                            self.write_entry(url, j_short_name, status=SUCCESS)
                            # time.sleep(10)
                        else:
                            logger.warning(
                                f"({j_short_name}) Error in word cloud generation:"
                                f" {self.error_in_wordcloud_gen}"
                            )
                    else:
                        imgname = None
                        logger.warning(
                            f"({j_short_name}) Text length {len(self.text)}"
                            f" is less than {self.minwords}"
                        )
                        if len(self.text) == 0:
                            self.write_entry(url, j_short_name, status=NO_TEXT)


if __name__ == "__main__":
    # Get current directory path
    curdir = os.path.dirname(os.path.realpath(__file__))
    # Read settings
    s = Settings(os.path.join(curdir, "settings.ini"))

    twitter_api = TwitterApi(
        s.get_twitter_bearer_token(),
        s.get_twitter_api_key(),
        s.get_twitter_api_secret(),
        s.get_twitter_access_token(),
        s.get_twitter_access_token_secret(),
    )
    url_shortener = UrlShortener(
        api_name=s.get_url_shortener_api(),
        login=s.get_url_shortener_login(),
        api_key=s.get_url_shortener_key(),
    )
    logger.info("Initialised")
    bot = AtmosSciBot(curdir, s, twitter_api, url_shortener)
    logger.info("Run started")
    bot.run()
    logger.info("Run finished")
