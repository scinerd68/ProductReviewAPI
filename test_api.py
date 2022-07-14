import requests
import json
import pprint

bs_api_key = 'DITF>NGE'
legit_api_key = 'ab837f0cf3f14b9a9fce78265dc45076'

url = "https://www.sendo.vn/op-lung-iphone-6-plus-6s-plus-chong-soc-360-17878754.html?source_block_id=feed&source_page_id=home&source_info=desktop2_60_1653314071212_17f349b3-3df6-4ea5-9ae7-ae076bbd7e9b_-1_ishyperhome0_0_11_22_-1" # 2 pages
result = requests.get("http://localhost:5000/review/byname", params={"api_key":legit_api_key,
                                                                     "name": "tủ lạnh LG",
                                                                     "site": "all",
                                                                     "maxreview": 5,
                                                                     "productnum": 5})

pprint.pprint(result.json())
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(result.json(), f, indent=4, ensure_ascii=False)
