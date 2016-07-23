# -*- coding: utf-8 -*-
"""
Twitter API class
"""
import time
import tweepy


class TwitterApi(object):
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        # Authorise twitter access
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        # Initialise twitter api
        self.twitter_api = tweepy.API(auth)
        # In case of error, try again one more time after n seconds
        self.wait_seconds = 120

    def assemble_tweet_text(self, tweet_text, short_url, text_len=85):
        """Assemble tweet status"""
        c2del = [('\n', ' '),
                 ('  ', ' ')]
        for c in c2del:
            tweet_text = tweet_text.replace(*c)
        if len(tweet_text) > text_len:
            ellipsis = '... '
        else:
            ellipsis = ' '
        # title: <text_len> characters, shortened url: ~21,
        # punctuation: 4, image url (auto-generated by twitter)
        tweet_text = tweet_text[0:text_len] + ellipsis + short_url
        return tweet_text

    def post_tweet(self, tweet_text, short_url, imgname=None):
        """Update status with a wordcloud image"""
        tweet_text = self.assemble_tweet_text(tweet_text, short_url)
        # debug
        # print(tweet_text)
        # print(len(tweet_text))

        if imgname is not None:
            # Tweet text and image
            # print(tweet_text)
            # print(len(tweet_text))
            try:
                self.twitter_api.update_with_media(imgname, status=tweet_text)
            except tweepy.TweepError as e:
                # print('wait...')
                time.wait(self.wait_seconds)
                self.twitter_api.update_with_media(imgname, status=tweet_text)
        else:
            # post tweet without a wordcloud
            self.twitter_api.update_status(tweet_text)
