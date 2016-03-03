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
    if len(ttl) > 80:
         ellipsis = '... '
    else:
         ellipsis = ''
    # title: 80 characters, bitly: 21, punctuation: 4 + image
    tweet_text = ttl[0:80] + ellipsis + short_url
    return tweet_text

def post_tweet(url, journal, title, imgname=None):
    tw_api, bicon = init_api()
    short_url = bicon.shorten(url)['url']
    
    tweet_text = assemble_tweet_text(title, short_url)
    # debug
    #print(tweet_text)
    #print(len(tweet_text))

    if imgname is not None:
        # Tweet text and image
        #print(tweet_text)
        #print(len(tweet_text))
        try:
            tw_api.update_with_media(imgname, status=tweet_text)
        except tweepy.TweepError as e:
            #print('wait...')
            time.wait(300) # wait for 5 min and try again
            tw_api.update_with_media(imgname, status=tweet_text)
    else:
        tw_api.update_status(tweet_text)
