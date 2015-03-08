import falcon
import json
from sparkey import HashReader as SHR
import requests
import re

class ResultsView(object):
	product_ids = []

	def __init__(self, db):
		self.db = db
		f = open('product_ids_sample.txt','rb')
		self.product_ids = [line.strip() for line in f.readlines()]

	def on_get(self, req, resp):
		data_str = []

		for pid in self.product_ids:
			data = json.loads(self.db.get(pid))
			data_str.append(json.dumps(data))
		resp.body = '[' + ','.join(data_str) + ']'

class ProductDetailView(object):
	def __init__(self, db):
		self.db = db

	@staticmethod
	def get_images(link):
		try:
			res = requests.get(link).text.encode('utf-8')
			return re.findall(r'(?<=href=\")http://.*normal_large_flex.jpeg', res)
		except:
			return None

	def on_get(self, req, resp, product_id):
		sp_data = self.db.get(product_id)
		if not sp_data:
			raise falcon.HTTPError(falcon.HTTP_404, "Product not found")
		else:
			data = json.loads(sp_data)
			resp_data = {
				"product_id": data["product_id"],
				"designer": data["designer"],
				"product_title": data["product_name"],
				"link": data["product_link"],
				"image_urls": ProductDetailView.get_images(data["product_link"])
				}
			resp.body = json.dumps(resp_data)

db_metadata_short = SHR('/mnt/product_metadata_short.spi', '/mnt/product_metadata_short.spl')
db_metadata_full = SHR('/mnt/product_metadata.spi', '/mnt/product_metadata.spl')

app = falcon.API()
rv = ResultsView(db_metadata_short)
pdv = ProductDetailView(db_metadata_full)
app.add_route('/sommelier', rv)
app.add_route('/product/{product_id}', pdv)
