from src.lisa.data.data_crawler import PttScraper


scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                      board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                      scrapt_page_num=1,
                                      executable_path="C:/Users/Lisa/chromedriver_win32/chromedriver.exe")
articles = scraper.scraper()
print(articles)
scraper.download_images_from_listofdicts(articles[0:2], savepath="dataset/train/images")


from src.lisa.data.data_crawler import DcardScrapt
scraper = DcardScrapt.get_scraper(executable_path="C:/Users/Lisa/chromedriver_win32/chromedriver.exe")
articles = scraper.scraper("試色")
print(articles)
scraper.download_images_from_listofdicts(articles[0:2], savepath="dataset/train/images")

