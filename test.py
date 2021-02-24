from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup
import wget
import os
import time
from urllib.parse import urljoin, urlsplit

def check_os():
    import platform
    if platform.system().lower() == "windows":
        return "win"
    elif platform.system().lower() == "darwin":
        return "mac"


def is_image_path(imagepath):
    if isinstance(imagepath, str):
        if imagepath.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
            return True
        else:
            return False


def create_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)

# class Download():
#     @staticmethod
#     def get_filename_from_url(url):
#         url.split
#     @staticmethod
def download_file(url, save_path):
    if not os.path.isdir(save_path):
        create_dir(save_path)
    filename = wget.detect_filename(url)
    if not os.path.isfile(os.path.join(save_path,filename)):
        wget.download(url, out=save_path)


class BasicScraper:
    def __init__(self, chrome):
        self.chrome = chrome

    @classmethod
    def get_chromedriver(cls, **kwargs):
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

    def get_attrs_and_text(self, resultset):
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


class PttImageScraper(BasicScraper):
    def __init__(self, chrome, domain_name, board_url, scrapt_page_num=1):
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
        self.chrome.get(article_url)
        soup = BeautifulSoup(self.chrome.page_source, 'html.parser')

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
            self.chrome.get(contents_url)
            soup = BeautifulSoup(self.chrome.page_source, 'html.parser')

            articles = self.get_ppt_article_list(soup)
            for article in articles:
                # get image path
                if 'href' in article:
                    self._scrape_imageurl_from_article(article)
                # save path
                if 'image' in article:
                    for image in article['image']:
                        download_file(image, save_path)
                time.sleep(3)

            _, last_page, _, _ = self._get_change_contens_button(soup)
            contents_url = urljoin(self.domain_name,last_page)
            print(articles)


scraper = PttImageScraper.get_chromedriver(domain_name="https://www.ptt.cc/",
                                           board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                           scrapt_page_num=30)
scraper.scraper(save_path="dataset/train/images")
