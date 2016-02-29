# -*- coding: utf-8 -*-
"""
Initialise Twitter and Bitly API, update status
"""
import bitly_api
import tweepy

def init_api():
    from gettokens import tokens
    # Authorise twitter access
    auth = tweepy.OAuthHandler(tokens['api_key'], tokens['api_secret'])
    auth.set_access_token(tokens['access_token'], tokens['access_token_secret'])
    # Initialise twitter api
    api = tweepy.API(auth)
    # Initialise bitly api
    bicon = bitly_api.Connection(login=tokens['bitly_api_login'], api_key=tokens['bitly_api_key'])
    return api, bicon

def assemble_tweet_text(ttl, short_url):
    """Assemble tweet status"""
    c2del = [('\n', ' '),
             ('\u2013', '-'),
             ('  ', ' ')]
    for c in c2del:
        ttl = ttl.replace(*c)
    tweet_text = ttl[0:80]+'... '+short_url # title: 115 characters, bitly: 21, punctuation: 4
    return tweet_text

def post_tweet(url, title, imgname):
    tw_api, bicon = init_api()
    short_url = bicon.shorten(url)['url']
    
    tweet_text = assemble_tweet_text(title, short_url)
    # debug
    #print(tweet_text)
    #print(len(tweet_text))

    # Tweet text and image
    tw_api.update_with_media(imgname, status=tweet_text)