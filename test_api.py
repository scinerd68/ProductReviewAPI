import requests

bs_api_key = 'DITF>NGE'
legit_api_key = 'ab837f0cf3f14b9a9fce78265dc45076'

url = "https://www.sendo.vn/op-lung-iphone-6-plus-6s-plus-chong-soc-360-17878754.html?source_block_id=feed&source_page_id=home&source_info=desktop2_60_1653314071212_17f349b3-3df6-4ea5-9ae7-ae076bbd7e9b_-1_ishyperhome0_0_11_22_-1" # 2 pages
# url = r'https://www.lazada.vn/products/dien-thoai-apple-iphone-13-pro-max-128gb-i1522497182-s6393590575.html?search=1&spm=a2o4n.searchlistcategory.list.i72.75bf3a1fbXB2jM'
# url = "https://tiki.vn/o-cam-dien-6-phich-cam-3-cong-usb-p21482873.html?spid=104556487"


# #TEST GET NEW API KEY
# device_name = "test"
# result = requests.get("http://localhost:5000/new_api_key", params={"device_name":device_name})
#
# #TEST NO API KEY
# result = requests.get("http://localhost:5000/review", params={"url": url, "site": "lazada"})
#
# #TEST INVALID API KEY
# api_key = 'ASDad'
# result = requests.get("http://localhost:5000/review", params={"api_key":bs_api_key, "url": url, "site": "lazada"})
# # legit_api_key = result.json()['api_key']

#TEST SCRAPING
# result = requests.get("http://localhost:5000/review/byurl", params={"api_key":legit_api_key, "url": url, "site": "lazada"})
result = requests.get("http://localhost:5000/review/byname", params={"api_key":legit_api_key, "name": "tủ lạnh lg", "site": "sendo"})

print(result.json())
