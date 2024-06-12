# -*- coding: utf-8 -*-
"""atmosscibot URL shortener interface."""
# Local modules
from logger import logger

IMPLEMENTED = ["bitly"]


class UrlShortener(object):
    def __init__(self, api_name="bitly", **keys):
        if api_name == "bitly":
            import bitly_api

            self.api = bitly_api.Connection(**keys)
        else:
            raise NotImplementedError(f"Only one of {IMPLEMENTED} are allowed")

    def shorten(self, url):
        """Shorten url."""
        # TODO: generalise the call
        try:
            short = self.api.shorten(url)["url"]
        except Exception as e:
            logger.info(f"Encountered {e} for {url=}")
            logger.info(f"Proceeding with the original URL (len={len(url)})")
            short = url
        return short
