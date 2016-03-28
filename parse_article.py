# -*- coding: utf-8 -*-
"""
Retrieve journal article and get text
"""
import bs4
import urllib
import warnings

def text_from_soup(url, parser, find_args, between_children=None, leave_result=None): 
    try: 
        with urllib.request.urlopen(url) as req: 
            doc = req.read() 
        soup = bs4.BeautifulSoup(doc, parser) 
        result = soup.find_all(**find_args)
        
        if leave_result in not None:
            assert isinstance(leave_result, dict)
            to_remove = []
            for tag in result:
                headers = i.find_all(**leave_result)
                if len(headers) == 0:
                    to_remove.append(i)
            [result.remove(i) for i in to_remove]
    
        if between_children is None:
            return ''.join([i.text for i in result])
        else:
            assert len(between_children) == 2
            for i, child_descr in enumerate(between_children):
                if isinstance(child_descr, dict):
                    child_tag = result[0].find_all(**child_descr)[0]
                    between_children[i] = result[0].contents.index(child_tag)
            children_subset = slice(*between_children)
            text = ''
            for child in result[0].contents[children_subset]:
                try:
                    text += child.text
                except AttributeError:
                    text += child.strip()
                except:
                    pass
            return text

    except urllib.request.HTTPError as e: 
        # return empty text if url is wrong 
        return ''


def extract_text(url, journal):
    """Download XML/HTML doc and parse it"""
    parsed_link = urllib.parse.urlparse(url)
    
    if journal.upper() in ['ACP', 'AMT']:
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
        between_tags = None
        
    elif journal.upper() in ['BML', 'AAS', 'MAP', 'JAC', 'TAC', 'CC', 'APJAS']:
        # Springer journals
        new_path = 'article'+parsed_link.path+'/fulltext.html'
        doc_url = parsed_link._replace(path=new_path).geturl()      
        parser = 'lxml-html'
        find_args = dict(attrs={'class':'Para'})
        between_tags = None
            
    elif journal.upper() in ['ASL']:
        # Wiley journals with HTML available
        new_path = parsed_link.path.replace('/resolve','') + \
                   parsed_link.query.replace('%2F','/').replace('DOI=', '/') + \
                   '/full'
        doc_url = parsed_link._replace(path=new_path, query='').geturl()
        parser = 'lxml-html'
        find_args = dict(attrs={'class':'para'})
        between_tags = None

    elif journal.upper() in ['TA', 'TB']:
        # Tellus A/B
        doc_url = parsed_link.geturl()
        parser = 'lxml-html'
        find_args = dict(name='div', attrs={'id':'articleHTML'})
        between_tags = [None, dict(name='h1', text='References')]
        
    elif journal.upper() in ['AM', 'IJAS', 'JCLI']:
        # Hindawi journals (by HTML)
        doc_url = parsed_link.geturl()
        parser = 'lxml-html'
        find_args = dict(name='div', attrs={'class':'xml-content'})
        between_tags = None
        leave_result = dict(name='h4', text='Abstract')
        
    else:
        warnings.warn('Skip {0} journal: no rule for it'.format(journal))
        doc_url = None
        
    if doc_url is not None:
        text = text_from_soup(doc_url, parser, find_args, between_tags)
    else:
        text = ''
            
    return text