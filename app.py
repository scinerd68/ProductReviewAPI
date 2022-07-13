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
import hashlib
import json
from datetime import date, datetime, timedelta
import os

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


@app.route("/api_key",  methods = ['GET', 'POST'])
def api_key():
    if request.method == 'POST':
        device_name = request.form.get('device_name')
        if DeviceModel.find_by_name(device_name=device_name):
            return {'message': f"A device with name {device_name} already exists."}, 400

        new_device = DeviceModel(
            device_name=device_name,
        )
        new_device.save_to_db()
        api_key = new_device.device_key
        return render_template('generate_key.html', key=api_key)
    return render_template('generate_key.html', key=None)


def get_cache_path(type, query, site):
    cache_file_name = str(type)+"__"+str(query)+"__"+str(site)
    cache_file_name = str(int(hashlib.sha1(cache_file_name.encode("utf-8")).hexdigest(), 16) % (10 ** 32))+".json"
    cache_path = os.path.join(os.getcwd(), 'cache', cache_file_name)
    return cache_path


class GetReviewByProductName(Resource):
    @api_required
    def get(self):
        product_name = request.args.get('name')
        site = request.args.get('site')
        max_review = int(request.args.get('maxreview', 5)) # 5 is default max_review
        product_num = int(request.args.get('productnum', 3)) # 3 is default product num

        cache_path = get_cache_path("productname", product_name, site)
        cache_exist = False

        if os.path.exists(cache_path):
            cache = json.load(cache_path)
            date_recorded = datetime.strptime(cache['date'], '%y %m %d')
            if (datetime.combine(date.today(), datetime.min.time()) - date_recorded) < timedelta(days = 15):
                if max_review < cache['maxreview'] and product_num < cache['productnum']:
                    _result = cache['result']
                    if site != 'all':
                        _result = _result[:min(product_num, len(_result))] #in case the number of scrapable products < max product
                        for i in range(len(_result)):
                            _result[i]['reviews'] = _result[i]['reviews'][:min(max_review, len(_result[i]['reviews']))]
                        result = {'query': product_name, 'result': _result}
                    else:
                        result = {'query': product_name, 'result': []}
                        counters = {'sendo':0, 'lazada':0, 'tiki':0}
                        for __result in _result:
                            _site = __result["source"]
                            if counters[_site] < product_num:
                                __result['reviews'] = __result['reviews'][: min(max_review, len(__result['reviews']))]
                                result['result'].append(__result)
                                counters[_site] +=1

                    cache_exist = True

        if not cache_exist:
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
            else:
                results = {}
                results['sendo'] = scrape_sendo(driver=driver, input=product_name, max_review_num=max_review,
                                      product_num=product_num, verbose=True)
                result = results['sendo'].copy()

                results['lazada'] = scrape_lazada_by_product(driver=driver, product_name=product_name, max_page=product_num,
                                                  max_comment_per_page=max_review)
                result.extend(results['lazada'])


                results['tiki'] = scrape_tiki_by_name(driver=driver, input=product_name, product_num=product_num,
                                             max_review_num=max_review)
                result.extend(results['tiki'])

            driver.quit()

            cache = {"date": datetime.strftime(date.today(), '%y %m %d'), "result" : result, 'maxreview': max_review, 'productnum': product_num }
            with open(cache_path, 'w', encoding='utf8') as json_file:
                json.dump(cache, json_file, ensure_ascii=False)

            if site == 'all':
                for site in ['sendo', 'lazada', 'tiki']:
                     cache = {"date": datetime.strftime(date.today(), '%y %m %d'), "result" : results[site], 'maxreview': max_review, 'productnum': product_num }

                     cache_path = get_cache_path("productname", product_name, site)

                     with open(cache_path, 'w', encoding='utf8') as json_file:
                         json.dump(cache, json_file, ensure_ascii=False)

        return result


class GetReviewByURL(Resource):
    @api_required
    def get(self):
        url = request.args.get('url')
        site = request.args.get('site')
        if site not in ['sendo', 'lazada', 'tiki']:
            return f"Argument value '{site}' is not supported", 400

        cache_path = get_cache_path('', url, '')
        cache_exist = False

        max_review = int(request.args.get('maxreview', 5)) # 5 is default max_review

        if os.path.exists(cache_path):
            cache = json.load(cache_path)
            date_recorded = datetime.strptime(cache['date'], '%y %m %d')
            if (datetime.combine(date.today(), datetime.min.time()) - date_recorded) < timedelta(days = 15):
                if max_review < cache['maxreview']:
                    result = cache.copy()
                    result['reviews'] = cache['reviews'][:min(max_review, len(cache['reviews']))] #in case scrapable reviews num < max_review
                    cache_exist = True

        if not cache_exist:
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

            cache = result.copy()
            cache['date'] = datetime.strftime(date.today(), '%y %m %d')
            with open(cache_path, 'w', encoding='utf8') as json_file:
                json.dump(cache, json_file, ensure_ascii=False)

        return result


class AddDevice(Resource):
    def post(self):
        name = request.form["device_name"]

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
