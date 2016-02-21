import os

curdir = os.path.dirname(os.path.realpath(__file__))
tokens = dict()
with open(os.path.join(curdir,'tokens')) as f:
    for l in f.readlines():
        key, val = l.rstrip('\n').split(' ')
        tokens[key.lower()] = val
