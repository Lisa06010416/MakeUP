import time
import json
import re

from pyramid.config.views import urljoin
from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup

from src.lisa.data.utils import check_os


"""
Scrapt 需要會
1 拿到網頁原始碼 
2. 供有變數 首頁 domain name

"""
from abc import ABC, abstractmethod


class Scraper(ABC):
    @abstractmethod
    def get_webdata(self, web_url, **kwargs):
        pass


class GoogleSearchScrapt():
    def get_webdata(self, web_url, **kwargs):
        from googlesearch import search
        return search(web_url, **kwargs)

class SeleniumScraper(Scraper):
    def __init__(self, chrome):
        self.chrome = chrome

    def get_webdata(self, web_url, **kwargs):
        self.chrome.get(web_url)
        return BeautifulSoup(self.chrome.page_source, 'html.parser')

    @classmethod
    def get_scraper(cls, **kwargs):
        options = kwargs.pop("options", None)
        options = cls._set_chromedriver_options(options)
        chromedriver = cls._get_chromedriver(options)
        return cls(chromedriver, **kwargs)

    @staticmethod
    def _get_chromedriver(options):
        os = check_os()

        chromedriver = None
        if os == "win":
            print("~~")
        elif os == "mac":
            print("QQQ")
            chromedriver = webdriver.Chrome(chrome_options=options)
        else:
            assert False, "The OS must be windows or mac"
        assert chromedriver, "Cannot get chromedriver"

        return chromedriver

    @staticmethod
    def _set_chromedriver_options(options=None):
        if not options:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-notifications")
            options.add_argument("headless")
        return options

    @staticmethod
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


class PttImageScraper(SeleniumScraper):
    def __init__(self,
                 chrome,
                 domain_name,
                 board_url,
                 scrapt_page_num=1):
        super().__init__(chrome)
        self.domain_name = domain_name
        self.board_url = board_url
        self.scrapt_page_num = scrapt_page_num

    def get_ppt_article_list(self, soup):
        article_anchor_info = []
        resultset = soup.find_all("div", class_='title')
        for result in resultset:
            article_anchor = result.find('a')
            info = self.get_attrs_and_text(article_anchor)
            article_anchor_info.append(info[0])
        return article_anchor_info

    def _scrape_imageurl_from_article(self, article):
        # article_url and get soup
        article_url = self.domain_name + article['href']
        soup = self.get_webdata(article_url)

        # parser
        article_and_command = soup.find("div", id="main-container")
        content = article_and_command.find_all("a")
        content_info = self.get_attrs_and_text(content)

        # get image path
        article['image'] = []
        for index, info in enumerate(content_info):
            href = info['href']
            if is_image_path(href):
                article['image'].append(href)

    def _get_change_contens_button(self, soup):
        button_info = soup.find_all("a", class_="btn wide")
        button_info = self.get_attrs_and_text(button_info)
        newest_page = None
        oldest_page = None
        last_page = None
        next_page = None
        print(button_info)
        for button in button_info:
            if "最舊" in button['text']:
                oldest_page = button['href']
            elif "上頁" in button['text']:
                last_page = button['href']
            elif "最新" in button['text']:
                newest_page = button['href']
            elif "下頁" in button['text']:
                next_page = button['href']
        return oldest_page, last_page, newest_page, next_page

    def scraper(self, save_path=None):
        contents_url = self.board_url
        for _ in range(self.scrapt_page_num):
            soup = self.get_webdata(contents_url)
            articles = self.get_ppt_article_list(soup)
            for article in articles:
                # get image path
                if 'href' in article:
                    self._scrape_imageurl_from_article(article)
                # save path
                if 'image' in article:
                    for image in article['image']:
                        download(image, save_path)
                time.sleep(3)

            _, last_page, _, _ = self._get_change_contens_button(soup)
            contents_url = urljoin(self.domain_name, last_page)


class XiaohongshuScraper(SeleniumScraper):
    image_w = 300
    image_h = 300

    def set_imagesize(self, w=300,h=300):
        self.image_w = w
        self.image_h = h

    def scraper(self, web_url):
        soup = self.get_webdata(web_url)
        # get image
        imgefield = soup.find("script", text=lambda text: text and 'imagelist' in text.lower())
        imgefield = str(imgefield).split('"imageList":')[1]
        imgefield = imgefield.split("]")[0]
        imgefield = json.loads(imgefield + "]")
        # resize image
        urls = []
        for image in imgefield:
            url = re.sub("/w/*/", "/w/{}}/".format(self.image_w), image['url'])
            url = re.sub("/h/*/", "/h/{}}/".format(self.image_h), url)
            url = url if 'https' in url else "https:" + url
            urls.append(url)
        return urls

class DcardScrapt():
    pass