import requests

url = "https://www.sendo.vn/op-lung-iphone-6-plus-6s-plus-chong-soc-360-17878754.html?source_block_id=feed&source_page_id=home&source_info=desktop2_60_1653314071212_17f349b3-3df6-4ea5-9ae7-ae076bbd7e9b_-1_ishyperhome0_0_11_22_-1" # 2 pages
result = requests.put("http://localhost:5000/review", data={"url": url})
print(result.json())