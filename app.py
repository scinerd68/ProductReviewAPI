from flask import Flask, render_template, request
from flask_restful import Resource, Api
from scrape.sendo_scrape import scrape_sendo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = "D:/chromedriver.exe"

app = Flask(__name__)
api = Api(app)

@app.route("/")
def home():
    return render_template('index.html')

class GetReview(Resource):
    def put(self):
        # TODO: sendo has global start variable in scrape function causing bug
        # TODO: Switch to GET request and parse request.args
        url = request.form['url']
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
        result = scrape_sendo(driver=driver, url=url, max_review_num=5, verbose=True)
        driver.quit()
        return url

api.add_resource(GetReview, '/review')

if __name__ == '__main__':
    app.run(debug=True)