from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
import json

def scrape_lazada(driver, url, max_comment_page = 4, sleep_time_unit = 0.2):

    driver.get(url)
    result = {'product_name':'','avg_rating':0,'source':'lazada','reviews':[]}
    review_count = 0
    
    #click out pop up
    time.sleep(sleep_time_unit*2)
    ac = ActionChains(driver)
    ac.move_by_offset(1, 1).click().perform()

    #scrape from at most 'max_comment_page' number of review pages
    x = 0
    while x < max_comment_page:
        time.sleep(sleep_time_unit)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(sleep_time_unit*2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        result['product_name'] = driver.find_element(By.CSS_SELECTOR, "[class='pdp-mod-product-badge-title']").text
        result['avg_rating'] = driver.find_element(By.CSS_SELECTOR, "[class='score-average']").text
        product_reviews = driver.find_elements(By.CSS_SELECTOR,"[class='item']")

        # Get product review
        for product in product_reviews:
            review = {}
            details = product.find_element(By.CSS_SELECTOR, "[class='middle']")
            details= details.find_elements(By.TAG_NAME,'span')
            review['id']=review_count
            review_count +=1
            review['name'] = details[0].text[3:]
            review['status'] = details[1].text
            review['date'] = product.find_element(By.CSS_SELECTOR, "[class='title right']").text
            review['rating'] = len(product.find_elements(By.CSS_SELECTOR, "[src='//laz-img-cdn.alicdn.com/tfs/TB19ZvEgfDH8KJjy1XcXXcpdXXa-64-64.png']"))
            review['review'] = product.find_element(By.CSS_SELECTOR, "[class='content']").text
            if review != "" or review.strip():
                # print(review, "\n")
                result['reviews'].append(review)

        #Check for next button to click. If no button found, exit loop.
        if len(driver.find_elements(By.CSS_SELECTOR,"button.next-pagination-item.next[disabled]")) > 0:
            break
        else:
            button_next = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button.next-pagination-item.next")))
            driver.execute_script("arguments[0].click();", button_next)
            time.sleep(sleep_time_unit*2)

        x += 1

    return result

if __name__ == '__main__':

    driver = webdriver.Chrome()
    #driver = webdriver.Edge()
    url = r'https://www.lazada.vn/products/dien-thoai-apple-iphone-13-pro-max-128gb-i1522497182-s6393590575.html?search=1&spm=a2o4n.searchlistcategory.list.i72.75bf3a1fbXB2jM'
    test = scrape_lazada(driver, url, 4)
    driver.close()
    test_result = json.dumps(test, indent=4, ensure_ascii=False)
    print(test_result)
