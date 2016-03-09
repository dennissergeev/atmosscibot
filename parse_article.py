# -*- coding: utf-8 -*-
"""
Retrieve journal article and get text
"""
import bs4
import urllib
import warnings

def text_from_soup(url, parser, find_args):
    try:
        with urllib.request.urlopen(url) as req:
            doc = req.read()
        soup = bs4.BeautifulSoup(doc, parser)
        result = soup.find_all(**find_args)
        return ''.join([i.text for i in result])
    except urllib.request.HTTPError as e:
        # return empty text if url is wrong
        return ''


def get_text(url, journal):
    """Download XML/HTML doc and parse it"""
    parsed_link = urllib.parse.urlparse(url)
    
    if journal.upper() in ['ACP', 'ACPD', 'AMT']:
        # EGU journals
        link_path = parsed_link.path
        path_split = [s for s in link_path.split('/') if s]
        if 'discuss' in url:
            # links like http://www.atmos-chem-phys-discuss.net/acp-2016-95/acp-2016-95.xml
            new_path = link_path + '/' + link_path + '.xml'
            find_args = dict(name='abstract')
        else:
            # links like http://www.atmos-chem-phys.net/16/2309/2016/acp-16-2309-2016.xml
            new_path = link_path + '-'.join([journal.lower()]+path_split) + '.xml'
            find_args = dict(name='body')
            
        doc_url = parsed_link._replace(path=new_path).geturl()            
        parser = 'lxml-xml'
        
    elif journal.upper() in ['BML', 'AAS', 'MAP', 'JAC', 'TAC', 'CC', 'APJAS']:
        # Springer journals
        new_path = 'article'+parsed_link.path+'/fulltext.html'
        doc_url = parsed_link._replace(path=new_path).geturl()      
        parser = 'lxml-html'
        find_args = dict(attrs={'class':'Para'})
            
    elif journal.upper() in ['ASL']:
        # Wiley journals with HTML available
        new_path = parsed_link.path.replace('/resolve','') + \
                   parsed_link.query.replace('%2F','/').replace('DOI=', '/') + \
                   '/full'
        doc_url = parsed_link._replace(path=new_path, query='').geturl()
        parser = 'lxml-html'
        find_args = dict(attrs={'class':'para'})
            
    else:
        warnings.warn('Skip {0} journal: no rule for it'.format(journal))
        doc_url = None
        
    if doc_url is not None:
        text = text_from_soup(doc_url, parser, find_args)
    else:
        text = ''
            
    return text
