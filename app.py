from flask import Flask, render_template, request
from flask_restful import Resource, Api
from scrape.LazadaScraping import scrape_lazada
from scrape.sendo_scrape import scrape_sendo
from scrape.tiki_scrape import scrape_tiki
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask_sqlalchemy import SQLAlchemy

import functools
import uuid


CHROME_DRIVER_PATH = "D:/chromedriver.exe"

app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = True
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devices.sqlite3'
db = SQLAlchemy(app)
api = Api(app)


'''
################################################################################
############################### DB MODELS ######################################
################################################################################
'''
class DeviceModel(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(80))
    device_key = db.Column(db.String(80))


    def __init__(self, device_name, device_key=None):
        self.device_name = device_name
        self.device_key = device_key or uuid.uuid4().hex

    def json(self):
        return {
            'device_name': self.device_name,
            'device_key': self.device_key,
        }

    @classmethod
    def find_by_name(cls, device_name):
        return cls.query.filter_by(device_name=device_name).first()

    @classmethod
    def find_by_device_key(cls, device_key):
        return cls.query.filter_by(device_key=device_key).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

'''
################################################################################
############################### SECURITY #######################################
################################################################################
'''

def is_valid(api_key):
    device = DeviceModel.find_by_device_key(device_key = api_key)
    if device:
        return True

def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):

        if "api_key" in request.args:
            api_key = request.args["api_key"]
        else:
            return {"message": "Please provide an API key"}, 400
        # Check if API key is correct and valid
        if request.method == "GET" and is_valid(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator

'''
################################################################################
######################## ROUTES & ENDPOINTS ####################################
################################################################################
'''
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
    db.create_all()
    app.run(debug=True)
