def assemble_tweet_text(ttl, short_url):
    '''Assemble tweet status'''
    c2del = [('\n', ' '), ('\u2013', '-'), ('  ', ' ')]
    for c in c2del:
        ttl = ttl.replace(*c)
    tweet_text = ttl[0:115]+'... '+short_url # title: 115 characters, bitly: 21, punctuation: 4
    return tweet_text
