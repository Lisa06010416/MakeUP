from src.lisa.data.data_crawler import PttImageScraper

scraper = PttImageScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                           board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                           scrapt_page_num=30)
scraper.scraper(save_path="dataset/train/images")
