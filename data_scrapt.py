from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup

# class BasicScrapt:
#     def __init__(self, chrome):
#     def

domain_name = "https://www.ptt.cc/"
options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
options.add_argument("headless")
chrome = webdriver.Chrome('./chromedriver', chrome_options=options)
chrome.get('https://www.ptt.cc/bbs/MakeUp/index.html')


def get_attrs_and_text(resultset):
    all_info = []
    if isinstance(resultset, Sequence):
        for r in resultset:
            attrs = {} if not r else r.attrs
            text = {} if not r else r.text
            attrs['text'] = text
            all_info.append(attrs)
    else:
        attrs = {} if not resultset else resultset.attrs
        text = None if not resultset else resultset.text
        attrs['text'] = text
        all_info.append(attrs)
    return all_info


def get_ppt_article_list(soup):
    article_anchor_info = []
    resultset = soup.find_all("div", class_='title')
    for result in resultset:
        article_anchor = result.find('a')
        info = get_attrs_and_text(article_anchor)
        article_anchor_info.append(info[0])
    return article_anchor_info


def is_image(imagepath):
    if isinstance(imagepath, str):
        if imagepath.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
            return True
        else:
            return False
