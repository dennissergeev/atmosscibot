# -*- coding: utf-8 -*-
"""atmosscibot settings interface."""
import configparser


class Settings(object):
    """Read configs from a file and store them in a dictionary."""

    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.config = configparser.ConfigParser()
        self.config.read(self.settings_file)

        self.TWITTER = "twitter"
        self.URLSHORT = "urlshort"
        self.CONFIGS = "configs"

    def get_twitter_api_key(self):
        return self.config[self.TWITTER]["api_key"]

    def get_twitter_api_secret(self):
        return self.config[self.TWITTER]["api_secret"]

    def get_twitter_access_token(self):
        return self.config[self.TWITTER]["access_token"]

    def get_twitter_access_token_secret(self):
        return self.config[self.TWITTER]["access_token_secret"]

    def get_url_shortener_api(self):
        return self.config[self.URLSHORT]["api_name"]

    def get_url_shortener_login(self):
        return self.config[self.URLSHORT]["api_login"]

    def get_url_shortener_key(self):
        return self.config[self.URLSHORT]["api_key"]

    def get_stopwords_dir(self):
        return self.config[self.CONFIGS]["stopwords_dir"]

    def get_wordcloud_mask_dir(self):
        return self.config[self.CONFIGS]["wordcloud_mask_dir"]

    # def get_font_path(self):
    #     return self.config[self.CONFIGS].get('font_path')
    def get_font_switch(self):
        return self.config[self.CONFIGS]["allow_font_change"]

    def get_width(self):
        return int(self.config[self.CONFIGS]["width"])

    def get_height(self):
        return int(self.config[self.CONFIGS]["height"])

    def get_dpi(self):
        return int(self.config[self.CONFIGS]["dpi"])

    def get_min_words(self):
        return int(self.config[self.CONFIGS]["min_words"])

    def get_log_dirname(self):
        return self.config[self.CONFIGS]["log_dirname"]

    def get_log_filename(self):
        return self.config[self.CONFIGS]["log_filename"]

    def get_db_file(self):
        return self.config[self.CONFIGS]["db_file"]

    def get_journal_list(self):
        return self.config[self.CONFIGS]["journal_list"]

    def get_temp_dir(self):
        return self.config[self.CONFIGS]["temp_dir"]

    def get_temp_file(self):
        return self.config[self.CONFIGS]["temp_file"]

    def get_mentions_file(self):
        return self.config[self.CONFIGS]["mentions_file"]

    def get_bot_name(self):
        return self.config[self.CONFIGS]["botname"]
