import datetime
import sys
from twython import Twython

from gettokens import tokens

tweet = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') 

api = Twython(tokens['api_key'],
              tokens['api_secret'],
              tokens['access_token'],
              tokens['access_token_secret'])

api.update_status(status=tweet)

#print("Tweeted: " + tweet)
