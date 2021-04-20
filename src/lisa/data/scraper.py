import time
import json
import re
import wget
import os
import requests

from urllib.parse import urljoin
from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup

from src.lisa.data.utils import is_image_path, create_dir
from src.lisa.utils.logmanager import get_logger
from abc import ABC, abstractmethod


logger = get_logger(__name__)


class Scraper(ABC):
    @abstractmethod
    def get_webdata(self, web_url, **kwargs):
        pass

    @staticmethod
    def download_from_url(url, savepath=None):
        create_dir(savepath)
        filename = wget.detect_filename(url)
        if not os.path.isfile(os.path.join(savepath,filename)):
            try:
                wget.download(url, out=savepath)
                logger.info("Download file {} success".format(url))
            except:
                logger.info("Download file {} fail".format(url))

    def download_images_from_list(self, url_list, savepath):
        for image_url in url_list:
            self.download_from_url(image_url, savepath)


class GoogleSearchScraper(Scraper):
    def get_webdata(self, web_url, **kwargs):
        from googlesearch import search
        return search(web_url, **kwargs)


class RequestScraper(Scraper):
    def __init__(self, **kwargs):
        pass

    def get_webdata(self, web_url, **kwargs):
        resp = requests.get(web_url)
        return BeautifulSoup(resp.content, 'html.parser')


class SeleniumScraper(Scraper):
    def __init__(self, options=None, executable_path=None, **kwargs):
        chromedriver = self._get_chromedriver(options, executable_path, **kwargs)
        self.chrome = chromedriver

    def get_webdata(self, web_url, **kwargs):
        self.chrome.get(web_url)
        self.chrome.implicitly_wait(5)
        try:  # 您的連線不是私人連線
            go_button = self.chrome.find_element_by_id("details-button")
            go_button.click()
            go_button = self.chrome.find_element_by_id("proceed-link")
            go_button.click()
        except:
            pass
        time.sleep(5)  # !!
        return BeautifulSoup(self.chrome.page_source, 'html.parser')

    @staticmethod
    def _get_chromedriver(options=None, executable_path=None, **kwargs):
        from fake_useragent import UserAgent
        if not options:
            # https://intoli.com/blog/making-chrome-headless-undetectable/
            options = webdriver.ChromeOptions()
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-automation'])

            #!! 沒開時自動開（？ 如何部署（？
            if kwargs.get("use_proxy"):
                # run_proxy_server("inject_js/inject.py") # cross env
                options.add_argument('--proxy-server=http://' + "localhost:8080")

            # 更換user agent
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')

            options.add_argument("--disable-notifications")
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--no-sandbox')

            options.add_argument("headless")

        chromedriver = webdriver.Chrome(executable_path=executable_path,
                                        chrome_options=options)
        assert chromedriver, "Cannot get chromedriver"

        chromedriver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })

        return chromedriver


class PttScraper(RequestScraper):
    def __init__(self,
                 domain_name="https://",
                 board_url="https://",
                 **kwargs):
        super().__init__(**kwargs)
        self.domain_name = domain_name
        self.board_url = board_url

    @classmethod
    def get_scraper(cls, **kwargs):
        # 指定新的父類別 => 給子類別用的
        base = kwargs.pop("base", None)
        if base:
            cls.__bases__ = (base,)
        return cls(**kwargs)

    def get_ppt_article_list(self, soup):
        article_anchor_info = []
        resultset = soup.find_all("div", class_='title')
        for result in resultset:
            article_anchor = result.find('a')
            info = self.get_attrs_and_text(article_anchor)
            article_anchor_info.append(info[0])
        return article_anchor_info

    def _get_imageurl_from_article(self, article):
        # article_url and get soup
        article_url = self.domain_name + article['href']
        soup = self.get_webdata(article_url)

        # parser
        article_and_command = soup.find("div", id="main-container")
        content = article_and_command.find_all("a")
        content_info = self.get_attrs_and_text(content)

        # get image path
        article['images'] = []
        for index, info in enumerate(content_info):
            href = info['href']
            if is_image_path(href):
                article['images'].append(href)

    def _get_change_contens_button(self, soup):
        button_info = soup.find_all("a", class_="btn wide")
        button_info = self.get_attrs_and_text(button_info)
        newest_page = None
        oldest_page = None
        last_page = None
        next_page = None
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

    def scraper_image(self, savepath, search_page_num=1, keyword=None, search_by_keyword=False):
        """
        還未加入keyword search
        """
        if search_by_keyword:
            contents_url = 'https://www.ptt.cc/bbs/movie/search?'
        else:
            contents_url = self.board_url
        articles = None
        for _ in range(search_page_num):
            soup = self.get_webdata(contents_url)
            articles = self.get_ppt_article_list(soup)
            for article in articles:
                # get image path
                if 'href' in article:
                    self._get_imageurl_from_article(article)
                    if 'images' in article:
                        self.download_images_from_list(article['images'], savepath)
                time.sleep(1)
            _, last_page, _, _ = self._get_change_contens_button(soup)
            contents_url = urljoin(self.domain_name, last_page)
        return articles


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


class XiaohongshuScraper(SeleniumScraper):
    """
    一定要用SeleniumScraper
    小紅書目前是給一個小紅書貼文的網址，爬該網址裡面的圖
    小紅書的web沒有search的功能
    """
    image_w = 300
    image_h = 300

    def set_imagesize(self, w=300,h=300):
        self.image_w = w
        self.image_h = h

    def scraper(self, web_url):
        soup = self.get_webdata(web_url)
        # get image
        result = soup.find_all("i", style=lambda style: style and "background-image" in style)
        # resize image
        urls = []
        for image in result:
            url = image.get("style")
            url = url.split('background-image:url(')[1]
            url = url.split(');')[0]
            url = url if 'https' in url else "https:" + url
            urls.append(url)
        print(urls)
        return urls


class DcardScraper(SeleniumScraper):
    """
    python 在繼承時
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_urlpath(self, soup):
        urls = []
        for i in str(soup).split('"'):
            if is_image_path(i):
                urls.append(i)
        return urls

    @classmethod
    def get_scraper(cls, **kwargs):
        # 指定新的父類別 => 給子類別用的
        base = kwargs.pop("base", None)
        if base:
            cls.__bases__ = (base,)
        return cls(**kwargs)

    def scraper(self, keyword, savepath, limit=3, search_by="keyword"):
        search_path = ""
        if search_by == "keyword":
            search_path = "https://www.dcard.tw/service/api/v2/search/posts?limit={}&query={}".format(limit,keyword)
        elif search_by == "keyword":
            search_path = "{}".format(keyword)
        soup = self.get_webdata(search_path)

        articles = json.loads(soup.text)
        for article in articles:
            article_id = article['id']
            article_url = "https://www.dcard.tw/service/api/v2/posts/{}".format(article_id)
            soup = self.get_webdata(article_url)
            url = self.get_urlpath(soup)
            article['images'] = url
            self.download_images_from_list(article['images'], savepath)
        return articles
