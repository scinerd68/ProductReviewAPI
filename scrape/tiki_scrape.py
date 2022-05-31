import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import codecs

# TODAY = date.today()
CHROME_DRIVER_PATH = "D:/chromedriver.exe"


def scrape_tiki(driver, url, json_file, review_wait_time=10):
    RATING_DICT = {
        "Rất không hài lòng": 1,
        "Không hài lòng": 2,
        "Bình thường": 3,
        "Hài lòng": 4,
        "Cực kì hài lòng": 5
    }
    BUY_STATUS_DICT = {
        "Đã mua hàng": True
    }
    results = []

    # get the page
    driver.get(url)

    driver.execute_script("window.scrollTo(0,3000)")

    review = WebDriverWait(driver, review_wait_time).until(
        EC.presence_of_element_located((By.CLASS_NAME, "review-comment__content")))

    assert review is not None

    # cook soup
    soup = BeautifulSoup(driver.page_source, features="lxml")
    reviews = soup.find_all("div", class_="review-comment__content")

    product_name = soup.find_all("h1", class_="title")[0].text

    if reviews:
        review_id = 0
        next_page_button = next_review_page(driver)
        while next_page_button:
            soup = BeautifulSoup(driver.page_source, features="lxml")
            reviews = soup.findAll("div", class_="review-comment__content")
            texts = soup.find_all(class_="review-comment__content")
            ratings = soup.find_all(class_="review-comment__title")
            buy_statuses = soup.find_all(class_="review-comment__seller-name")
            dates = soup.find_all(class_="review-comment__created-date")
            buyer_names = soup.find_all(class_="review-comment__user-name")

            for text, rating, buy_status, date, buyer_name in zip(texts, ratings, buy_statuses, dates, buyer_names):
                review_dict = {
                    "id": review_id,
                    "review": text.text,
                    "rating": RATING_DICT[rating.text],
                    "buy_status": BUY_STATUS_DICT.get(buy_status.text, False),
                    "review_date": extract_comment_date(date.text),
                    "buyer_name": buyer_name.text.strip()
                }
                review_id += 1
                results.append(review_dict)
                print(review_dict)
            try:
                next_page_button.click()
                next_page_button = next_review_page(driver)
            except:
                print("No button :(")
                break
    results = remove_dup(results)
    results = {
        "product_name": product_name,
        "source": "tiki",
        "reviews": results
    }
    # with codecs.open(json_file, 'w', encoding="utf-8") as f:
    #     json.dump(results, f, ensure_ascii=False)
    print(results)
    return results


def extract_comment_date(text):
    comment_date = [int(word) for word in text.split() if word.isnumeric()]
    return comment_date[0]


def next_review_page(driver):
    move_page_button = driver.find_element(By.CLASS_NAME, "btn.next")
    # print(move_page_button)
    driver.execute_script("arguments[0].scrollIntoView(true);", move_page_button)
    return move_page_button
    # move_page_button.click()


def remove_dup(L):
    res = []
    for i in L:
        if i not in res:
            res.append(i)
    return res
#
# def subtract_month(current_month, time):
#


if __name__ == "__main__":
    # url = "https://tiki.vn/may-xay-sinh-to-va-lam-sua-hat-da-nang-tefal-bl967b66-1300w-luoi-dao-voi-cong-nghe-powelix-hang-chinh-hang-p79561024.html?spid=79561025"
    # url = "https://tiki.vn/o-dien-da-nang-chong-giat-3-cong-usb-va-9-o-cam-icart-p35876754.html?spid=59452050"
    url = "https://tiki.vn/o-cam-dien-6-phich-cam-3-cong-usb-p21482873.html?spid=104556487"

    chrome_options = Options()
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
    scrape_tiki(driver, url, "./abc.json")

    pass