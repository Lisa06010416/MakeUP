from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup
import wget




domain_name = "https://www.ptt.cc/"
home_path = 'https://www.ptt.cc/bbs/MakeUp/index.html'
scrap_page_num = 1

scrapt = PptScraper(domain_name,home_path)
url = 'https://imgur.com/rjArCSJ.jpg'
scrapt.download(url)

# 爬蟲的順序
# 1 參數設定  domain_name home_path
# 2 webdriver 設定
# 3 進到首頁
# 4 拿到全部要爬的頁面
# 5 爬每個頁面
#
# domain_name = "https://www.ptt.cc/"
# home_path = 'https://www.ptt.cc/bbs/MakeUp/index.html'
# scrap_page_num = 1
#
# scrapt = PptScraper(domain_name,home_path )
# page_list = scrapt.get_page_list(scrap_page_num)
# print("page_list {}".format(page_list))
# for url_path in page_list:
#     # ptt makeup 首頁
#     soup = scrapt.get_soup(url_path)
#
#     # 拿到每頁裡的文章資訊
#     article_anchors = scrapt.get_article_list(soup)
#     print("article_anchors {}".format(article_anchors))
#
#     # 每篇文章連結 拿到圖的連結 並存起來
#     for anchor in article_anchors[0:1]:
#         # article_url and get soup
#         article_url = domain_name + anchor['href']
#         soup = scrapt.get_soup(article_url)
#
#         # parser
#         article_and_command = soup.find("div", id="main-container")
#         content = article_and_command.find_all("a")
#         content_info = scrapt.get_attrs_and_text(content)
#
#         # get image path
#         anchor['image'] = []
#         for index,info in enumerate(content_info):
#             href = info['href']
#             if scrapt.is_image(href):
#                 anchor['image'].append(href)
#
#     print(article_anchors)
