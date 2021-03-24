# from src.lisa.data.scraper import PttScraper
#
#
# scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
#                                       board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
#                                       scrapt_page_num=100,
#                                       executable_path="C:/Users/Lisa/chromedriver_win32/chromedriver.exe")
# articles = scraper.scraper(savepath="dataset/train/images")


from src.lisa.data.scraper import DcardScraper
scraper = DcardScraper.get_scraper(executable_path="C:/Users/Lisa/chromedriver_win32/chromedriver.exe")
articles = scraper.scraper(keyword="試色", savepath="dataset/train/images", limit=300)
