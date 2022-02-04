import torch
from makeup import PttScraper

from makeup.data.scraper import RequestScraper
from makeup.model.model_utils import ImageInferenceDataset
from torch.utils.data import DataLoader
from makeup.data.utils import read_img_from_url


def search_content_by_target_makeup_product(target_product):
    ptt_scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/",
                                         base=RequestScraper)
    ptt_article_generator = ptt_scraper.get_articles(keyword=f"{target_product}")

    articles = next(ptt_article_generator)

    for article in articles:
        ptt_scraper.get_article_detail(article)
    return articles


def classify_img_in_article(article, model=None):
    image_urls = article.images
    input_img = []
    for url in image_urls:
        input_img.append(read_img_from_url(url, transfer_to_tensor=True))
    inputs = ImageInferenceDataset(input_img)

    outputs = []
    dataloader = DataLoader(dataset=inputs, batch_size=4)
    for data in dataloader:
        if str(model.device) == "cpu":
            data = data.cpu()
        else:
            data = data.cuda()
        output = model(data)
        outputs.extend(torch.argmax(output.logits, dim=1).cpu().tolist())
    return outputs


