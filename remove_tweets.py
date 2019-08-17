# -*- coding: utf-8 -*-
import os
import sys
from settings import Settings
from twitter_api import TwitterApi

curdir = os.path.dirname(os.path.realpath(__file__))
s = Settings(os.path.join(curdir, "settings.ini"))
twitter_api = TwitterApi(
    s.get_twitter_api_key(),
    s.get_twitter_api_secret(),
    s.get_twitter_access_token(),
    s.get_twitter_access_token_secret(),
)

n = int(sys.argv[1])
timeline = twitter_api.twitter_api.user_timeline(count=n)
for t in timeline:
    twitter_api.twitter_api.destroy_status(t.id)
print("{0} tweets removed.".format(n))
