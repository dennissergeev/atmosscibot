# -*- coding: utf-8 -*-
"""
URL shortener class
"""


class UrlShortener(object):
    def __init__(self, api_name="bitly", **keys):
        implemented = ["bitly"]

        if api_name == "bitly":
            import bitly_api

            self.api = bitly_api.Connection(**keys)
        else:
            _msg = "Only one of {0} are allowed"
            raise NotImplementedError(_msg.format(implemented))

    def shorten(self, url):
        """ Shorten url """
        # TODO: generalise the call
        return self.api.shorten(url)["url"]
