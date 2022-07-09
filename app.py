from itertools import product
from flask import Flask, render_template, request
from flask_restful import Resource, Api
from scrape.LazadaScraping import scrape_lazada, scrape_lazada_by_product
from scrape.sendo_scrape import scrape_sendo, scrape_sendo_by_url
from scrape.tiki_scrape import scrape_tiki_by_name, scrape_tiki_by_url
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from db import db
from models.device import DeviceModel
from security import api_required

CHROME_DRIVER_PATH = "D:/chromedriver.exe"

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_ECHO'] = True
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/doc")
def documentation():
    return render_template('documentation.html')


class GetReviewByProductName(Resource):
    @api_required
    def get(self):
        product_name = request.args.get('name')
        site = request.args.get('site')
        max_review = request.args.get('maxreview', 5) # 5 is default max_review
        product_num = request.args.get('productnum', 3) # 3 is default product num

        if site not in ['sendo', 'lazada', 'tiki', 'all']:
            return f"Argument value '{site}' is not supported", 400


        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)

        if site == 'sendo':
            result = scrape_sendo(driver=driver, input=product_name, max_review_num=max_review,
                                  product_num=product_num, verbose=True)
        elif site == 'lazada':
            result = scrape_lazada_by_product(driver=driver, product_name=product_name, max_page=product_num,
                                              max_comment_per_page=max_review)
        elif site == 'tiki':
            result = scrape_tiki_by_name(driver=driver, input=product_name, product_num=product_num,
                                         max_review_num=max_review)

        driver.quit()
        return result


class GetReviewByURL(Resource):
    @api_required
    def get(self):
        url = request.args.get('url')
        site = request.args.get('site')
        max_review = request.args.get('maxreview', 5) # 5 is default max_review

        if site not in ['sendo', 'lazada', 'tiki']:
            return f"Argument value '{site}' is not supported", 400

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")


        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)

        if site == 'sendo':
            result = scrape_sendo_by_url(driver=driver, url=url, max_review_num=5, verbose=True)
        elif site == 'lazada':
            result = scrape_lazada(driver=driver, url=url, max_comment=max_review)
        elif site == 'tiki':
            result = scrape_tiki_by_url(driver=driver, url=url, max_review_num=max_review)

        driver.quit()
        return result


class AddDevice(Resource):
    def get(self):
        name = request.args["device_name"]

        if DeviceModel.find_by_name(device_name = name):
            return {'message': f"A device with name {name} already exists."}, 400

        new_device = DeviceModel(
            device_name=name,
        )
        new_device.save_to_db()

        return  {"api_key": new_device.device_key}, 201

api.add_resource(AddDevice, '/new_api_key')
api.add_resource(GetReviewByURL, '/review/byurl')
api.add_resource(GetReviewByProductName, '/review/byname')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
