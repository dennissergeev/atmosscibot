# coding: utf-8
import bs4
import matplotlib.pyplot as plt
import feedparser as fp
import urllib
from wordcloud import WordCloud, STOPWORDS

rss_feed_url = 'http://www.atmos-chem-phys.net/xml/rss2_0.xml'

f = fp.parse(rss_feed_url)

for i, entry in enumerate(f.entries):
    url = entry.link
    url_split = [s for s in url.split('/') if s]
    if 'discuss' in url:
        # links look like http://www.atmos-chem-phys-discuss.net/acp-2016-95/acp-2016-95.xml
        end_url = url_split[-1] + '.xml'
        xml_url = url + '/' + end_url
        find_by = 'abstract'
    else:
        # links look like http://www.atmos-chem-phys.net/16/2309/2016/acp-16-2309-2016.xml
        end_url = '-'.join(['acp']+url_split[-3:]) + '.xml'
        xml_url = url + end_url
        find_by = 'body'
        
    print(xml_url)
        
    with urllib.request.urlopen(xml_url) as req:
        xml_doc = req.read()
        
    soup = bs4.BeautifulSoup(xml_doc, 'lxml-xml')
    text_body = soup.find(find_by).text
    
    wc = WordCloud(stopwords=list(STOPWORDS)+
                   ['et', 'al', 'br', 'sup', 'sub', 'minus', 'plus']).generate(text_body)
    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis('off')
    
    fig.savefig('wordcloud_images/{imgname}_by_{find_by}.png'.format(imgname=i, find_by=find_by))
