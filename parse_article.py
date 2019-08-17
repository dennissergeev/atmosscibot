# -*- coding: utf-8 -*-
"""
Retrieve journal article and get text
"""
import bs4
import requests
import urllib
import warnings
from fake_useragent import UserAgent


def text_from_soup(
    url,
    parser,
    find_args,
    check_for_open_access=None,
    between_children=None,
    escape_result=None,
):
    """
    Extract text from html or xml page using beautifulsoup

    Arguments
    ---------
    url: str
        URL pointing to the page
    parser: str
        HTML/XML parser, used by beautifulsoup
    find_args: dict
        Dictionary specifying tag names and attributes
        from which the text is extracted
    check_for_open_access: dict, optional
        Check if the page contains elements that mean
        open access
    between_children: list, optional
        List of dictionaries that describe tags between
        which the main text is
    escape_result: dict, optional
        Omit these elements

    Returns
    -------
    text: str
        Extracted text joined by whitespace
    """
    ua = UserAgent()
    req = requests.get(url, headers={"User-Agent": ua.data_browsers["chrome"][2]})

    if req.status_code == 200:
        # try:
        #     with urllib.request.urlopen(url) as req:
        #         doc = req.read()
        doc = req.content
        soup = bs4.BeautifulSoup(doc, parser)
        if check_for_open_access is not None:
            oa_check = soup.find_all(**check_for_open_access)
            # if len(oa_check) == 0:
            if len(oa_check) > 0:
                result = soup.find_all(**find_args)
            else:
                return ""
        else:
            result = soup.find_all(**find_args)

        if escape_result is not None:
            assert isinstance(escape_result, dict)
            if len(result) == 1:
                # if result consists of only 1 element,
                # loop over its children and append tags to
                # a new list, escaping tags specified by
                # escape_result dictionary
                _res = result[0]
                result = []
                for tag in _res:
                    if isinstance(tag, bs4.element.Tag):
                        if not (
                            escape_result["name"] == tag.name
                            and escape_result["attrs"]["class"] == tag.attrs["class"]
                        ):
                            result.append(tag)
            else:
                # Loop over tags in the list `result` and remove
                # tags specified by escape_result dictionary
                to_remove = []
                for tag in result:
                    found = tag.find_all(**escape_result)
                    if len(found) != 0:
                        to_remove.append(tag)
                [result.remove(i) for i in to_remove]

        if between_children is None:
            return " ".join([i.text for i in result])
        else:
            assert len(between_children) == 2
            for i, child_descr in enumerate(between_children):
                if isinstance(child_descr, dict):
                    child_tag = result[0].find_all(**child_descr)[0]
                    between_children[i] = result[0].contents.index(child_tag)
            children_subset = slice(*between_children)
            text = ""
            for child in result[0].contents[children_subset]:
                try:
                    text += child.text
                except AttributeError:
                    text += child.strip()
                except Exception:
                    pass
            return text
    else:
        # except urllib.request.HTTPError as e:
        # return empty text if url is wrong
        return ""


def extract_text(url, journal, url_ready=False, isdiscuss=False):
    """Download XML/HTML doc and parse it"""
    parsed_link = urllib.parse.urlparse(url)

    between_tags = None
    escape_result = None
    check_for_open_access = None

    if journal.upper() in ["ACP", "AMT", "GMD"]:
        # EGU journals
        if journal.upper() == "ACP":
            # TODO: make this automatic
            netloc = "http://www.atmos-chem-phys{}.net"
        elif journal.upper() == "AMT":
            netloc = "http://www.atmos-meas-tech{}.net"
        elif journal.upper() == "GMD":
            netloc = "http://www.geosci-model-dev{}.net"
        link_path = parsed_link.path
        path_split = [s for s in link_path.split("/") if s]
        if isdiscuss:
            # links like
            # atmos-chem-phys-discuss.net/acp-2016-95/acp-2016-95.xml
            netloc = netloc.format("-discuss")
            # new_path = '{l}/{l}.xml'.format(l=link_path)
            new_url = "{n}/{ll}/{ll}.xml".format(n=netloc, ll=path_split[1])
            find_args = dict(name="abstract")
        else:
            netloc = netloc.format("")
            # links like
            # http://www.atmos-chem-phys.net/16/2309/2016/acp-16-2309-2016.xml
            # new_path = '{}{}.xml'.format(link_path,
            #                              '-'.join([journal.lower()] +
            #                                       path_split))
            _sub_path = "/".join(path_split[1].split("-")[1:])
            new_url = "{}/{}/{}.xml".format(netloc, _sub_path, path_split[1])
            find_args = dict(name="body")
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            # doc_url = parsed_link._replace(path=new_path).geturl()
            doc_url = new_url
        parser = "lxml-xml"

    elif journal.upper() in ["BLM", "AAS", "MAP", "JAC", "TAC", "CC", "APJAS"]:
        # Springer journals
        new_path = "article{}/fulltext.html".format(parsed_link.path)
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link._replace(path=new_path).geturl()
        parser = "lxml-html"
        find_args = dict(attrs={"class": "Para"})

    elif journal.upper() in ["ASL", "JAMES", "JGRA", "QJRMS", "GRL"]:
        # Wiley journals
        new_path = parsed_link.path.replace("/abs", "/full")
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link._replace(path=new_path, query="").geturl()
        parser = "lxml-html"
        # find_args = dict(attrs={'class': 'para'})
        # This is probably better (although excludes abstract):
        # find_args = dict(name='section',
        #                 attrs={'class':
        #                        'article-section article-body-section'})
        # Wiley's website seems to have changed HTML tags, so now the text is
        # within div tags of class "article-section__content"
        find_args = dict(name="div", attrs={"class": "article-section__content"})
        if journal.upper() in ["JGRA", "QJRMS", "GRL"]:
            # # parse only the articles that are open-access
            # # under the Creative Commons license
            # _class_attr = "article-type article-type--cc"
            # check_for_open_access = dict(name='a',
            #                              attrs={'class': _class_attr})
            # New: check for non-open-access,
            # because older open-access papers do not have CC license
            # Check if there is a button to get access
            # NOTE: text_from_soup() is changed accordingly
            # _class_attr = dict(title='Log in to get access')
            # check_for_open_access = dict(name='a',
            #                              attrs=_class_attr)
            #
            # 2018-11-28: Changed again to check for a OA badge,
            # because closed-access accepted issues go through
            check_for_open_access = dict(
                name="div",
                text=lambda x: x in ["Open Access", "Free Access"],
                attrs={"class": "doi-access"},
            )

    elif journal.upper() in ["TA", "TB"]:
        # Tellus A/B
        # Now one of Taylor&Francis journals
        doc_url = parsed_link.geturl()
        parser = "lxml-html"
        # find_args = dict(name='div', attrs={'id': 'articleHTML'})
        # between_tags = [None, dict(name='h1', text='References')]
        find_args = dict(
            name="p",
            attrs={
                "xmlns:mml": "http://www.w3.org/1998/Math/MathML",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xmlns:oasis": "http://docs.oasis-open.org/ns/oasis-exchange/table",  # NOQA
            },
        )
        escape_result = dict(name="span", attrs={"class": "ref-overlay scrollable-ref"})

    elif journal.upper() in ["AM", "IJAS", "JCLI"]:
        # Hindawi journals (by HTML)
        doc_url = parsed_link.geturl()
        parser = "lxml-html"
        find_args = dict(name="div", attrs={"class": "xml-content"})
        escape_result = dict(name="h4", text="References")

    elif journal.upper() in ["BAMS", "EINT"]:
        # American Meteorological Society journals
        new_path = parsed_link.path.replace("/abs", "/full")
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link._replace(path=new_path, query="").geturl()
        # print(doc_url)
        parser = "lxml-html"
        find_args = dict(
            name="p",
            attrs={
                "xmlns:mml": "http://www.w3.org/1998/Math/MathML",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xmlns:ali": "http://www.niso.org/schemas/ali/1.0/",
                "xmlns:oasis": "http://www.niso.org/standards/z39-96/ns/oasis-exchange/table",  # NOQA
            },
        )
        # find_args = dict(name='div',
        #                  attrs={'class':
        #                         'NLM_sec NLM_sec_level_1'})

    elif journal.upper() == "ATMOS":
        # MDPI Atmosphere
        if parsed_link.geturl().endswith("/htm"):
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link.geturl() + "/htm"
        parser = "lxml-html"
        find_args = dict(name="div", attrs={"class": "html-body"})

    elif journal.upper() == "FRONT":
        # Frontiers in Earth Science | Atmospheric Science section
        if parsed_link.geturl().endswith("/full"):
            doc_url = parsed_link.geturl()
        else:
            doc_url = parsed_link.geturl() + "/full"
        parser = "lxml-html"
        find_args = dict(name="div", attrs={"class": "JournalFullText"})
        escape_result = dict(name="div", attrs={"class": ["References"]})

    else:
        warnings.warn("Skip {0} journal: no rule for it".format(journal))
        doc_url = None

    if doc_url is not None:
        text = text_from_soup(
            doc_url,
            parser,
            find_args,
            check_for_open_access,
            between_tags,
            escape_result,
        )
    else:
        text = ""

    return text
