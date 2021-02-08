from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup
import time
import bs4

domain_name = "https://www.ptt.cc/"
options = webdriver.ChromeOptions()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
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


# 第一頁
soup = BeautifulSoup(chrome.page_source, 'html.parser')
article_anchors = get_ppt_article_list(soup)
print(article_anchors)


# 每篇文章連結 拿到圖的連結 並存起來
for anchor in article_anchors[0:1]:
    # article_url and get soup
    article_url = domain_name + anchor['href']
    chrome.get(article_url)
    soup = BeautifulSoup(chrome.page_source, 'html.parser')

    # parser
    article_and_command = soup.find("div", id="main-container")
    content = article_and_command.find_all("a")
    content_info = get_attrs_and_text(content)

    # get image path
    anchor['image'] = []
    for index,info in enumerate(content_info):
        href = info['href']
        if is_image(href):
            anchor['image'].append(href)

print(article_anchors[0])
