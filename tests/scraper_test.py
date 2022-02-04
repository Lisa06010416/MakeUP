import os
import shutil
import time
import pytest
from bs4 import BeautifulSoup

from makeup.data.scraper import RequestScraper, SeleniumScraper, PttScraper, XiaohongshuScraper, DcardScraper, Article
from makeup.utils.envchecker import get_chrome_driver
from makeup.script import setup_mitmdump_server, close_mitmdump_server

# in mac need abs path
chromedriver_path = os.path.abspath("chromedriver")

test_web_url = "https://www.google.com.tw/"
test_img_url = "https://drive.google.com/u/1/uc?id=1Y_6wLpMBscr1Kkw13xDr5kKgkrEyXvE2&export=download"
test_xiaohongshu_url = "https://www.xiaohongshu.com/discovery/item/5ff15da0000000000101ef28?source=question"

get_chrome_driver()


def get_soup_from_file(path):
    with open(path, 'r') as f:
        file = f.read()
    return BeautifulSoup(file, 'html.parser')


class TestRequestScraper:
    def setup(self):
        self.test_web_url = test_web_url
        self.test_img_url = test_img_url

    def test_request_scraper(self):
        scraper = RequestScraper()
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

    def test_download_from_url(self):
        savepath = "testdata/image/"
        if os.path.isdir(savepath):
            shutil.rmtree(savepath)
        scraper = RequestScraper()
        scraper.download_from_url(self.test_img_url, savepath)
        assert os.path.isdir(savepath), "Didn't creat dir!"
        assert len(os.listdir()) != 1, "download from url error!"

    def test_download_images_from_list(self):
        savepath = "testdata/image/"
        if os.path.isdir(savepath):
            shutil.rmtree(savepath)
        scraper = RequestScraper()
        scraper.download_from_urllist([self.test_img_url]*3, savepath)
        assert os.path.isdir(savepath), "Didn't creat dir!"
        assert len(os.listdir()) != 3, "download from url error!"

    def teardown(self):
        if os.path.isdir("testdata/image/"):
            shutil.rmtree("testdata/image/")


class TestSeleniumScraper:
    def setup(self):
        self.test_web_url = test_web_url
        self.test_img_url = test_img_url

    def test_get_webdata(self):
        scraper = SeleniumScraper(executable_path=chromedriver_path)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

    def test_get_webdata_with_proxy(self):
        setup_mitmdump_server()
        time.sleep(3)
        scraper = SeleniumScraper(executable_path=chromedriver_path, use_proxy=True)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup
        close_mitmdump_server()


class TestPttScraper:
    def setup(self):
        self.test_web_url = test_web_url
        self.test_img_url = test_img_url
        self.ptt_board_soup = get_soup_from_file("testdata/ptt_board_page")

    def test_get_scraper(self):
        # test get scraper
        scraper = PttScraper(domain_name="https://www.ptt.cc/",
                             board_url="https://www.ptt.cc/bbs/MakeUp/")
        assert isinstance(scraper, RequestScraper)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

    def test_get_scraper_change_base(self):
        print(chromedriver_path)
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/",
                                         executable_path=chromedriver_path,
                                         base=SeleniumScraper)  # 換過了該class就會指定為SeleniumScraper
        assert isinstance(scraper, SeleniumScraper)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

    def test_get_articles(self):
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/",
                                         base=RequestScraper)

        # 用keyword search
        article_generator = scraper.get_articles(keyword="粉餅")
        assert next(article_generator)
        with pytest.raises(StopIteration):
            next(article_generator)

        # 指定目錄的url
        article_generator = scraper.get_articles(url="https://www.ptt.cc/bbs/MakeUp/index3723.html")
        assert next(article_generator)
        with pytest.raises(StopIteration):
            next(article_generator)

    def test_get_article_detail(self):
        article = Article(url='/bbs/MakeUp/M.1616415945.A.11C.html')
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/",
                                         base=RequestScraper)
        scraper.get_article_detail(article)
        assert len(article.images) == 12

    def test_download_images(self):
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/",
                                         base=RequestScraper)
        scraper.download_images(savepath="testdata/image/", search_page_num=1)


class TestXiaohongshuScraper:
    def setup(self):
        self.test_web_url = test_xiaohongshu_url
        setup_mitmdump_server()
        time.sleep(3)

    def test_set_imagesize(self):
        scraper = XiaohongshuScraper(executable_path=chromedriver_path,
                                     use_proxy=True)
        scraper.set_imagesize(100, 50)
        assert scraper.image_h == 50
        assert scraper.image_w == 100

    def test_scraper(self):  # error
        scraper = XiaohongshuScraper(executable_path=chromedriver_path,
                                     use_proxy=True)
        urls = scraper.download_images(self.test_web_url)
        print(urls)
        pass

    def teardown(self):
        close_mitmdump_server()



class TestDcardScraper:
    def setup(self):
        self.test_web_url = test_web_url
        self.dcard_article_soup = get_soup_from_file("testdata/dcard_article")

    def test_get_img_urlpath(self):
        scraper = DcardScraper.get_scraper(executable_path=chromedriver_path)
        url = scraper.get_img_urlpath(self.dcard_article_soup)
        assert len(url) == 150

    def test_download_images(self):
        scraper = DcardScraper.get_scraper(executable_path=chromedriver_path)
        scraper.download_images(keyword="口紅", savepath="testdata/image/", limit=1)
        assert os.listdir("testdata/image/")

    def test_get_articles(self):
        scraper = DcardScraper.get_scraper(executable_path=chromedriver_path)
        articles = scraper.get_articles("口紅", limit=2)
        assert len(articles)==2

    def test_get_article_detail(self):
        scraper = DcardScraper.get_scraper(executable_path=chromedriver_path)
        article = Article(url="238038505")
        scraper.get_article_detail(article)
        assert article.title
        assert article.text

    def teardown(self):
        if os.path.isdir("testdata/image/"):
            shutil.rmtree("testdata/image/")
