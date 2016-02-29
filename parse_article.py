# -*- coding: utf-8 -*-
"""
Retrieve journal article and get text
"""
import bs4
import urllib

def get_text(url):
    """Download XML/PDF doc and parse it"""
    url_split = [s for s in url.split('/') if s]
    if 'discuss' in url:
        # links like http://www.atmos-chem-phys-discuss.net/acp-2016-95/acp-2016-95.xml
        end_url = url_split[-1] + '.xml'
        xml_url = url + '/' + end_url
        find_by = 'abstract'
    else:
        # links like http://www.atmos-chem-phys.net/16/2309/2016/acp-16-2309-2016.xml
        end_url = '-'.join(['acp']+url_split[-3:]) + '.xml'
        xml_url = url + end_url
        find_by = 'body'
        
    with urllib.request.urlopen(xml_url) as req:
        xml_doc = req.read()
        
    soup = bs4.BeautifulSoup(xml_doc, 'lxml-xml')
    text_body = soup.find(find_by).text

    return text_body
