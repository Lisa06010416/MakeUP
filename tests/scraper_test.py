import os
import shutil
from bs4 import BeautifulSoup

from makeup.data.scraper import RequestScraper, SeleniumScraper, PttScraper, XiaohongshuScraper, DcardScraper
from makeup.utils.envchecker import get_chrom_driver
from makeup.cmdline.script import setup_mitmdump_server

# in mac need abs path
chromedriver_path = os.path.abspath("chromedriver")

test_web_url = "https://www.google.com.tw/"
test_img_url = "https://drive.google.com/u/1/uc?id=1Y_6wLpMBscr1Kkw13xDr5kKgkrEyXvE2&export=download"
test_xiaohongshu_url = "https://www.xiaohongshu.com/discovery/item/5ff15da0000000000101ef28?source=question"

get_chrom_driver()

# open mitmdump_server # !! close!?
setup_mitmdump_server()


def get_soup_from_file(path):
    with open(path, 'r') as f:f
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
        scraper.download_images_from_list([self.test_img_url]*3, savepath)
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
        scraper = SeleniumScraper(executable_path=chromedriver_path, use_proxy=True)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup


class TestPttScraper:
    def setup(self):
        self.test_web_url = test_web_url
        self.test_img_url = test_img_url
        self.ptt_board_soup = get_soup_from_file("testdata/ptt_board_page")

    def test_get_scraper(self):
        # test get scraper
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         base=RequestScraper)
        assert scraper
        assert isinstance(scraper, RequestScraper)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

    def test_get_scraper_change_base(self):
        # change  father class
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         executable_path=chromedriver_path,
                                         base=SeleniumScraper)  # 換過了該class就會指定為SeleniumScraper
        assert scraper
        assert isinstance(scraper, SeleniumScraper)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

    def test_get_ppt_article_list(self):
        # load test data
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         base=RequestScraper)

        article_list = scraper.get_ppt_article_list(self.ptt_board_soup)
        assert article_list
        assert len(article_list)==23

    def test_get_change_content_button(self):
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         base=RequestScraper)
        oldest_page, last_page, newest_page, next_page = scraper._get_change_contens_button(self.ptt_board_soup)
        assert oldest_page=="/bbs/MakeUp/index1.html"
        assert last_page == "/bbs/MakeUp/index3626.html"
        assert newest_page == "/bbs/MakeUp/index.html"
        assert not next_page

    def test_get_imageurl_from_article(self):
        article = {'href': '/bbs/MakeUp/M.1616415945.A.11C.html', 'text': '[心得] Addiction新品/夏季限定 (靠櫃產品心得)'}
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         base=RequestScraper)
        scraper._get_imageurl_from_article(article)
        assert "images" in article
        assert len(article["images"]) == 12

    def test_scraper_image(self):
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         base=RequestScraper)
        articles = scraper.scraper_image(savepath="testdata/image/")
        assert articles


class TestXiaohongshuScraper:
    def setup(self):
        self.test_web_url = test_xiaohongshu_url

    def test_set_imagesize(self):
        scraper = XiaohongshuScraper(executable_path=chromedriver_path,
                                     use_proxy=True)
        scraper.set_imagesize(100, 50)
        assert scraper.image_h == 50
        assert scraper.image_w == 100

    def test_scraper(self):  # error
        scraper = XiaohongshuScraper(executable_path=chromedriver_path,
                                     use_proxy=True)
        urls = scraper.scraper(self.test_web_url)
        print(urls)
        pass


class TestDcardScraper:
    def setup(self):
        self.test_web_url = test_web_url
        self.dcard_article_soup = get_soup_from_file("testdata/dcard_article")

    def test_get_urlpath(self):
        scraper = DcardScraper.get_scraper(executable_path=chromedriver_path)
        url = scraper.get_urlpath(self.dcard_article_soup)
        assert url
        assert len(url) == 176

    def test_scraper(self):
        scraper = DcardScraper.get_scraper(executable_path=chromedriver_path)
        articles = scraper.scraper(keyword="口紅", savepath="testdata/image/", limit=1)
        assert articles

    def teardown(self):
        if os.path.isdir("testdata/image/"):
            shutil.rmtree("testdata/image/")
