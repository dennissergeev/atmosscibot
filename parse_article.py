# -*- coding: utf-8 -*-
"""Retrieve journal article's HTML/XML and extract the text."""
# Standard library
import os
import logging
import urllib

# External libraries
import bs4
from fake_useragent import UserAgent
import requests


logger = logging.getLogger(__name__)


def get_page_source(url, exec_dir):
    """
    Send an HTTP request to get the HTML/XML page.

    Uses requests first, but if the status code is not 200,
    tries to use run a headless browser session using selenium.


    Arguments
    ---------
    url: str
        URL pointing to the page
    exec_dir: str
        Directory with firefox & geckodriver

    Returns
    -------
    content: str
        Page source.
    """
    ua = UserAgent()
    try:
        req = requests.get(url, headers={"User-Agent": ua.data_browsers["chrome"][2]})
    except requests.exceptions.RequestException as e:
        logger.info(f"Requests exception {e} when processing {url}")
        return ""

    if req.status_code == 200:
        content = req.content
    else:
        try:
            # Try Selenium instead
            logger.info("Using Selenium")
            from selenium import webdriver  # noqa
            from selenium.webdriver.firefox.options import Options  # noqa
            from selenium.webdriver.firefox.service import Service  # noqa

            options = Options()
            options.add_argument("--headless")
            service = Service(os.path.join(exec_dir, "geckodriver"))

            dr = webdriver.Firefox(options=options, service=service)
            dr.get(url)
            content = dr.page_source
            dr.quit()
        except Exception as e:
            logger.info(f"Selenium exception {e} when processing {url}")
            content = ""
    return content


def text_from_soup(
    content,
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
    content: str
        HTML or XML page source.
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
    soup = bs4.BeautifulSoup(content, parser)
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
        if isinstance(escape_result, dict):
            escape_result = [escape_result]
        for esc in escape_result:
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
                            esc["name"] == tag.name
                            and esc["attrs"]["class"] == tag.attrs["class"]
                        ):
                            result.append(tag)
            else:
                # Loop over tags in the list `result` and remove
                # tags specified by escape_result dictionary
                to_remove = []
                for tag in result:
                    found = tag.find_all(**esc)
                    if len(found) != 0:
                        to_remove.append(tag)
                [result.remove(i) for i in to_remove]

    if between_children is None:
        return " ".join([i.text for i in result])
    else:
        assert len(between_children) == 2
        try:
            if len(result) == 0:
                _children = between_children.copy()
                for i, child_descr in enumerate(between_children):
                    if isinstance(child_descr, dict):
                        child_tag = result[0].find_all(**child_descr)[0]
                        _children[i] = result[0].contents.index(child_tag)
                children_subset = slice(*_children)
                text = ""
                for child in result[0].contents[children_subset]:
                    try:
                        text += child.text
                    except AttributeError:
                        text += child.strip()
                    except Exception:
                        pass
            else:
                to_keep = False
                _res = []
                for tag in result:
                    found = tag.find_all(**between_children[0])
                    if (len(found) != 0) or (
                        between_children[0].get("attrs", {}).items()
                        <= tag.attrs.items()
                    ):
                        to_keep = True
                    found = tag.find_all(**between_children[1])
                    if (len(found) != 0) or (
                        between_children[1].get("attrs", {}).items()
                        <= tag.attrs.items()
                    ):
                        to_keep = False
                    if to_keep:
                        _res.append(tag)
                text = " ".join([i.text for i in _res])
        except IndexError:
            text = ""
        return text


def extract_text(url, exec_dir, journal, url_ready=False):
    """
    Download XML/HTML doc and parse it.

    Arguments
    ---------
    url: str
        URL pointing to the page
    exec_dir: str
        Directory with firefox & geckodriver
    journal: str
        Journal short name (see `journal_list.json` for available journals).
    url_ready: bool
        If False, the `url` is modified according to journal rules.

    Returns
    -------
    text: str
        Extracted text.
    """
    parsed_link = urllib.parse.urlparse(url)

    between_children = None
    escape_result = None
    check_for_open_access = None

    if journal.upper() in ["ACP", "AMT", "GMD", "WCD"]:
        # EGU journals
        if url_ready:
            doc_url = parsed_link.geturl()
        else:
            netloc = "http://{}.copernicus.org/articles".format(journal.lower())
            path_split = [s for s in parsed_link.path.split("/") if s]
            _sub_path = "/".join(path_split[1].split("-")[1:])
            doc_url = "{}/{}/{}.xml".format(netloc, _sub_path, path_split[1])
        find_args = dict(name="body")
        parser = "lxml-xml"

    elif journal.upper() in ["BLM", "AAS", "MAP", "JAC", "TAC", "CC", "APJAS"]:
        # Springer journals
        doc_url = parsed_link.geturl()
        # new_path = "article{}/fulltext.html".format(parsed_link.path)
        # if url_ready:
        #     doc_url = parsed_link.geturl()
        # else:
        #     doc_url = parsed_link._replace(path=new_path).geturl()
        parser = "lxml-html"
        # find_args = dict(attrs={"class": "Para"})
        # find_args = dict(
        #     name="div", attrs={"class": "c-article-section__content"}
        # )
        find_args = dict(name="section")
        between_children = [
            dict(name="section", attrs={"data-title": "Abstract"}),
            dict(name="section", attrs={"data-title": "References"}),
        ]

    elif journal.upper() in ["ASL", "JAMES", "JGRA", "QJRMS", "GRL", "METAPPS"]:
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
        # within div or section tags of class "article-section__content"
        find_args = dict(
            name=["div", "section"], attrs={"class": "article-section__content"}
        )
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
                text=lambda x: x in ["Open Access", "Free Access", "Full Access"],
                attrs={"class": "doi-access"},
            )

    elif journal.upper() in ["TA", "TB"]:
        # Tellus A/B
        # Now one of Taylor&Francis journals
        doc_url = parsed_link.geturl()
        parser = "lxml-html"
        # find_args = dict(name='div', attrs={'id': 'articleHTML'})
        # between_children = [None, dict(name='h1', text='References')]
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
        doc_url = parsed_link.geturl()
        parser = "lxml-html"
        find_args = {"name": "div", "attrs": {"id": "articleBody"}}
        between_children = [
            {},
            {"name": "section", "attrs": {"class": ["refSection", "level1"]}},
        ]
        escape_result = [
            {"name": "a"},
            {"name": "ack"},
        ]

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

    elif journal.upper() == "NPJCLIMATSCI":
        doc_url = parsed_link.geturl()
        parser = "lxml-html"
        find_args = dict(name="section")
        escape_result = dict(name="div", attrs={"class": "c-article-equation"})
        between_children = [
            dict(name="section", attrs={"data-title": "Abstract"}),
            dict(name="section", attrs={"data-title": "References"}),
        ]

    else:
        logger.info("Skip {0} journal: no rule for it".format(journal))
        doc_url = None

    if doc_url is not None:
        try:
            doc = get_page_source(url, exec_dir)
            if not doc:
                return ""
            text = text_from_soup(
                doc,
                parser,
                find_args,
                check_for_open_access,
                between_children=between_children,
                escape_result=escape_result,
            )
        except Exception as e:
            err_msg = f"Exception {e} when processing {doc_url} with the following arguments:"
            err_msg += f"\n{parser=}"
            err_msg += f"\n{find_args=}"
            err_msg += f"\n{check_for_open_access=}"
            err_msg += f"\n{between_children=}"
            err_msg += f"\n{escape_result=}"
            logger.debug(err_msg)
            return ""
    else:
        text = ""

    return text
