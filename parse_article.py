# -*- coding: utf-8 -*-
"""
Retrieve journal article and get text
"""
import bs4
import urllib
import warnings

def prepare_soup(url, parser):
    try:
        with urllib.request.urlopen(url) as req:
            doc = req.read()
        return bs4.BeautifulSoup(doc, parser)
    except urllib.request.HTTPError as e:
        pass


def get_text(url, journal):
    """Download XML/HTML doc and parse it"""
    parsed_link = urllib.parse.urlparse(url)
    text = ''
    
    if journal.upper() in ['ACP', 'ACPD']:
        # EGU journals
        link_path = parsed_link.path
        path_split = [s for s in link_path.split('/') if s]
        if 'discuss' in url:
            # links like http://www.atmos-chem-phys-discuss.net/acp-2016-95/acp-2016-95.xml
            new_path = link_path + '/' + link_path + '.xml'
            find_by = 'abstract'
        else:
            # links like http://www.atmos-chem-phys.net/16/2309/2016/acp-16-2309-2016.xml
            new_path = link_path + '-'.join(['acp']+path_split) + '.xml'
            find_by = 'body'
        doc_url = parsed_link._replace(path=new_path).geturl()            
        soup = prepare_soup(doc_url, 'lxml-xml')
        if soup is not None:
            text = soup.find(find_by).text
        
    elif journal.upper() in ['BML', 'AAS', 'MAP', 'JAC', 'TAC']:
        # Springer journals
        new_path = 'article'+parsed_link.path+'/fulltext.html'
        doc_url = parsed_link._replace(path=new_path).geturl()      

        soup = prepare_soup(doc_url, 'lxml-html')
        if soup is not None:
            text = soup.find(find_by).text
            
    elif journal.upper() in ['ASL']:
        # Wiley journals with HTML available
        new_path = parsed_link.path.replace('/resolve','') + \
                   parsed_link.query.replace('%2F','/').replace('DOI=', '/') + \
                   '/full'
        doc_url = parsed_link._replace(path=new_path, query='').geturl()
        soup = prepare_soup(doc_url, 'lxml-html')
        if soup is not None:
            text = soup.find(find_by).text
            
    else:
        warnings.warn('Skip {} journal: no rule for it'.format(journal))
            
    return text