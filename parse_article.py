# -*- coding: utf-8 -*-
"""
Retrieve journal article and get text
"""
import bs4
import requests
import urllib
import warnings


def text_from_soup(url, parser, find_args,
                   check_for_open_access=None,
                   between_children=None, escape_result=None):

    req = requests.get(url)

    if req.status_code == 200:
        # try:
        #     with urllib.request.urlopen(url) as req:
        #         doc = req.read()
        doc = req.content
        soup = bs4.BeautifulSoup(doc, parser)
        if check_for_open_access is not None:
            oa_check = soup.find_all(**check_for_open_access)
            if len(oa_check) > 0:
                result = soup.find_all(**find_args)
            else:
                return ''
        else:
            result = soup.find_all(**find_args)

        if escape_result is not None:
            assert isinstance(escape_result, dict)
            to_remove = []
            for tag in result:
                found = tag.find_all(**escape_result)
                if len(found) != 0:
                    to_remove.append(tag)
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
    else:
        # except urllib.request.HTTPError as e:
        # return empty text if url is wrong
        return ''


def extract_text(url, journal, url_ready=False):
    """Download XML/HTML doc and parse it"""
    parsed_link = urllib.parse.urlparse(url)

    between_tags = None
    escape_result = None
    check_for_open_access = None

    if journal.upper() in ['ACP', 'AMT']:
        # EGU journals
        link_path = parsed_link.path
        path_split = [s for s in link_path.split('/') if s]
        if 'discuss' in url:
            # links like
            # http://www.atmos-chem-phys-discuss.net/acp-2016-95/acp-2016-95.xml
            new_path = '{l}/{l}.xml'.format(l=link_path)
            find_args = dict(name='abstract')
        else:
            # links like
            # http://www.atmos-chem-phys.net/16/2309/2016/acp-16-2309-2016.xml
            new_path = '{}{}.xml'.format(link_path,
                                         '-'.join([journal.lower()] +
                                                  path_split))
            find_args = dict(name='body')
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link._replace(path=new_path).geturl()
        parser = 'lxml-xml'

    elif journal.upper() in ['BML', 'AAS', 'MAP', 'JAC', 'TAC', 'CC', 'APJAS']:
        # Springer journals
        new_path = 'article{}/fulltext.html'.format(parsed_link.path)
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link._replace(path=new_path).geturl()
        parser = 'lxml-html'
        find_args = dict(attrs={'class': 'Para'})

    elif journal.upper() in ['ASL', 'JAMES', 'JGRA']:
        # Wiley journals
        new_path = '{}{}/full'.format(parsed_link.path.replace('/resolve', ''),
                                      parsed_link.query.
                                      replace('%2F', '/').replace('DOI=', '/'))
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link._replace(path=new_path, query='').geturl()
        parser = 'lxml-html'
        # find_args = dict(attrs={'class': 'para'})
        # This is probably better (although excludes abstract):
        find_args = dict(name='section',
                         attrs={'class':
                                'article-section article-body-section'})
        if journal.upper() in ['JGRA']:
            _class_attr = "article-type article-type--open-access"
            check_for_open_access = dict(name='span',
                                         attrs={'class': _class_attr})

    elif journal.upper() in ['TA', 'TB']:
        # Tellus A/B
        doc_url = parsed_link.geturl()
        parser = 'lxml-html'
        find_args = dict(name='div', attrs={'id': 'articleHTML'})
        between_tags = [None, dict(name='h1', text='References')]

    elif journal.upper() in ['AM', 'IJAS', 'JCLI']:
        # Hindawi journals (by HTML)
        doc_url = parsed_link.geturl()
        parser = 'lxml-html'
        find_args = dict(name='div', attrs={'class': 'xml-content'})
        escape_result = dict(name='h4', text='References')

    elif journal.upper() in ['BAMS']:
        # American Meteorological Society journals
        new_path = parsed_link.path.replace('abs', 'full')
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link._replace(path=new_path, query='').geturl()
        parser = 'lxml-html'
        find_args = dict(name='p',
                         attrs={'xmlns:mml':
                                'http://www.w3.org/1998/Math/MathML',
                                'xmlns:xsi':
                                'http://www.w3.org/2001/XMLSchema-instance'})

    else:
        warnings.warn('Skip {0} journal: no rule for it'.format(journal))
        doc_url = None

    if doc_url is not None:
        text = text_from_soup(doc_url, parser, find_args,
                              check_for_open_access,
                              between_tags, escape_result)
    else:
        text = ''

    return text
