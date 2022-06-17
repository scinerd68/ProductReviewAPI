import json
import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

STAR_RATING_CONVERT = {
    "d7e-4e4dcb d7e-271a22" : 5,
    "d7e-4e4dcb d7e-cd8bf7" : 4,
    "d7e-4e4dcb d7e-f924b9" : 3,
    "d7e-4e4dcb d7e-9ac674" : 2,
    "d7e-4e4dcb d7e-fede87" : 1
    }
CHROME_DRIVER_PATH = "/home/viet/OneDrive/Studying_Materials/Introduction_to_Data_Science/EDA Project/chromedriver_linux64/chromedriver"
REVIEW_COUNTER = 0


def check_reply(review):
    """
    Check if current review is actually a reply to another review. 
    Return True if it is an reply, false otherwise.
    """
    return len(review["class"]) != 1


def scrape_from_review_list(review_list, result, max_review_num):
    """
    Scrape from the given list of reviews and store in result
    """
    global REVIEW_COUNTER
    for cur_review in review_list:
        if check_reply(cur_review):
            continue
        logging.info("Scraping a new customer")
        cur_review_dict = {}

        # customer's name
        name = cur_review.contents[1].strong.text
        logging.info(f"Got customer's name: {name}")

        # review date
        date = cur_review.contents[1].time.text
        logging.info(f"Got date: {date}")

        # review content
        content = cur_review.contents[1].p.text
        logging.info(f"Got review text: {content}")

        # review rating
        class_name = " ".join(cur_review.contents[1].find("div", "d7e-7f502f d7e-7dd432").div["class"])
        rating = STAR_RATING_CONVERT[class_name]
        logging.info(f"Got rating: {rating}")

        # store the features into cur_review_dict
        cur_review_dict["id"] = REVIEW_COUNTER
        cur_review_dict["name"] = name
        cur_review_dict["date"] = date
        cur_review_dict["content"] = content
        cur_review_dict["rating"] = rating

        # add this customer's review to result
        result["reviews"].append(cur_review_dict)
        logging.info(f"Added customer {name}'s review")

        # increment REVIEW_COUNTER
        REVIEW_COUNTER += 1
        
        logging.info("Number of reviews scraped: {}".format(len(result["reviews"])))
        # stop if the number of records exceeds the maxinum number
        if len(result["reviews"]) == max_review_num:
            break


def check_alert(driver):
    """
    Check if there's any alert popping up. If yes then click "No" to make it fuck off
    """

    try:
        logging.info("Checking for alert")
        alert = driver.find_element(By.CLASS_NAME, "d7e-aa34b6.e9f-f95cf0")
        logging.info("Sendo alert detected")
        alert.click()
        logging.info("Sendo alert clicked")
    except:
        logging.info("Alert not found, continuing")


def next_review_page(driver):
    """
    Find the next page button and click it.
    Return True if executed sucessfully, False otherwise
    """
    move_page_buttons = driver.find_elements(By.CLASS_NAME, "d7e-aa34b6.d7e-1b9468.d7e-13f811.d7e-2a1884.d7e-dc4b7b.d7e-d8b43f.d7e-0f6285")

    if move_page_buttons:
        logging.info("Buttons found")
        # the second one is the next page button
        forward_button = move_page_buttons[1]

        # check if forward is clickable
        if forward_button.is_enabled():
            logging.info("Forward button is clickable")

            # srcoll so that the button is visible
            driver.execute_script("arguments[0].scrollIntoView(true);", forward_button)
            driver.execute_script("window.scrollBy(0,-150)")
            logging.info("Finished scrolling to the forward button")

            check_alert(driver)
            forward_button.click()
            logging.info("Next review page clicked")
            return True
        
        logging.info("Button is not clickable. The last page is reached")
        return False
    
    logging.info("Buttons are not present")
    return False


def scrape_sendo(driver, url, max_review_num=20, review_check_num=10, review_wait_time=0.1, verbose=False):
    """
    Scrape users' reviews on Sendo website
    max_review_num: maxinmum number of reviews to scrape
    review_check_num: number of retries to scroll down and wait for the review section to load
    review_wait_time: waiting duration in each try
    verbose: show running info
    """

    if verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

    # get the page
    driver.get(url)
    for check_num in range(1, review_check_num + 1):
        logging.info(f"Check if the reviews are present, try number: {check_num}")
        # check for alert
        check_alert(driver)
        
        # find the review section by scrolling down to 2000 until the review section is found
        try:
            driver.execute_script("window.scrollTo(0,2000)")
            review = WebDriverWait(driver, review_wait_time).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "_39a-71cc39"))) # old value: 39a-673889

            # escape the loop if the element is present
            logging.info("Review section found")
            break 
        
        except:
            pass

    # return None if cant find the reviews
    if not review:
        logging.info("Review section not found")
        return

    else:
        logging.info("Start scraping")

        # create a dictionary to store review information
        result = {
            "product_name": None,
            "total" : None,
            "source" : "sendo",
            "reviews" : []
        }
        
        # wait for cumulative rating to be loaded before cooking soup
        cum = WebDriverWait(driver, review_wait_time).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "_39a-7b5c89")))

        # cook soup
        soup = BeautifulSoup(driver.page_source, features="lxml")

        # get product's name
        product_name = soup.find(class_="d7e-ed528f d7e-7dcda3 d7e-f56b44 d7e-fb1c84 undefined").text
        result["product_name"] = product_name
        logging.info(f"Got product's name: {product_name}")

        # cumulative rating
        total = soup.find(class_="_39a-7b5c89").text
        result["total"] = total
        logging.info(f"Got cumulative rating: {total}")

        # get the reviews
        reviews = soup.find_all(class_="_39a-71cc39")
        scrape_from_review_list(reviews, result, max_review_num)
        # stop if the number of records exceeds the maxinum number
        if len(result["reviews"]) == max_review_num:
            logging.info("Maximum number of reviews reached, stopping scraping")
            logging.info("Finished scraping")
            return result

        # grab the reviews from the other pages
        while next_review_page(driver):
            logging.info("Scraping the new page")
            reviews = soup.find_all(class_="_39a-71cc39")
            scrape_from_review_list(reviews, result, max_review_num)

            # stop if the number of records exceeds the maxinum number
            if len(result["reviews"]) == max_review_num:
                logging.info(f"Maximum number of reviews reached({max_review_num}), stopping scraping")
                break
            # time.sleep(1)

        logging.info("Finished scraping")
        return result


if __name__ == "__main__":
    url = [
        "https://www.sendo.vn/op-lung-iphone-6-plus-24661530.html?source_block_id=feed&source_page_id=home&source_info=desktop2_60_1653209392128_34e4536f-bc6a-4a91-9335-ace33da5bcc1_-1_ishyperhome0_0_57_22_-1", # 1 page
        "https://www.sendo.vn/combo-6-goi-khan-uot-khong-mui-unifresh-vitamin-e-khan-uot-tre-em-80-mienggoi-23796514.html?source_block_id=feed&source_page_id=home&source_info=desktop2_60_1653306028025_17f349b3-3df6-4ea5-9ae7-ae076bbd7e9b_-1_ishyperhome0_0_2_1_-1", # many pages
        "https://www.sendo.vn/op-lung-iphone-6-plus-6s-plus-chong-soc-360-17878754.html?source_block_id=feed&source_page_id=home&source_info=desktop2_60_1653314071212_17f349b3-3df6-4ea5-9ae7-ae076bbd7e9b_-1_ishyperhome0_0_11_22_-1" # 2 pages
    ]
    chrome_options = Options()
    # chrome_options.add_argument("--headless")

    # start a webdriver
    start = time.time()
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
    result = scrape_sendo(driver, url[2], max_review_num=5, verbose=True)
    driver.quit()
    print("Time taken: ", time.time() - start)
    pretty = json.dumps(result, indent=4, ensure_ascii=False)
    print(pretty)
    