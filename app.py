from flask import Flask, render_template, request
from flask_restful import Resource, Api
from scrape.LazadaScraping import scrape_lazada
from scrape.sendo_scrape import scrape_sendo
from scrape.tiki_scrape import scrape_tiki
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
db.init_app(app)


@app.route("/")
def home():
    return render_template('index.html')

class GetReview(Resource):
    # def put(self):
    #     # TODO: Switch to GET request and parse request.args
    #     url = request.form['url']
    #     chrome_options = Options()
    #     chrome_options.add_argument("--headless")
    #     driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
    #     result = scrape_sendo(driver=driver, url=url, max_review_num=5, verbose=True)
    #     driver.quit()
    #     return result
    @api_required
    def get(self):
        url = request.args['url']
        site = request.args['site']

        if site not in ['sendo', 'lazada', 'tiki']:
            return f"Argument value '{site}' is not supported", 400

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)

        if site == 'sendo':
            result = scrape_sendo(driver=driver, url=url, max_review_num=5, verbose=True)
        elif site == 'lazada':
            result = scrape_lazada(driver, url, 4)
        elif site == 'tiki':
            result = scrape_tiki(driver, url)

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
api.add_resource(GetReview, '/review')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
