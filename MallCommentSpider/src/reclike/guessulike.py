import requests,random,time,os,json,csv
import logging

this_path = os.getcwd()

def goodOfShop(shop_id,logger):
	'''
	按页数，使用ajax爬取商店中的所有商品
	# user-agent未补充
	'''
	logger.info(u'%d Start scrap.'%shop_id)

	referer = 'https://shop.m.jd.com/search/search?shopId='+str(shop_id)
	user_agent = ''
	cookie = 'abtest=20180606163256259_90; mobilev=html5; USER_FLAG_CHECK=fb71c4a65bb75927a7d0e7082f44575d; subAbTest=20180606163256907_66; intlIpLbsCountryIp=114.141.164.19; intlIpLbsCountrySite=jd; mhome=1; autoOpenApp_downCloseDate_auto=1529458839786_1000; retina=0; cid=9; webp=0; __wga=1529458832708.1529458796385.1529032447237.1528878175274.4.3; __jdv=122270672%7Cdirect%7C-%7Cnone%7C-%7C1528878175282; sc_width=1366; visitkey=5543893774947423; shshshfp=b7c3d339a5684184e59f781780614744; shshshfpa=28917231-4459-b46c-7823-c3b18c2bc2ab-1528878176; shshshfpb=2f3dbf14f82ae45b7928ef1cb623e19145b363905613e97729220d4611; warehistory="5451938,1815521,5463278,"; sid=b8e98a6dd94ba7eadbc13ae881e06402; wxa_level=1; PPRD_P=LOGID.1529458832720.641200659; wq_area=2_78_0%7C3; shshshsID=f7eb6f86675a3ba8904b7dc240737a82_4_1529458833986; wq_logid=1529458830.1467750961'
	content_type = 'application/x-www-form-urlencoded; charset=UTF-8'
	headers = {'Referer':referer,'Cookie':cookie,'Content-Type':content_type}
	

	r = str(random.randint(0,9999999999999)).zfill(13)
	url = 'https://shop.m.jd.com/search/searchWareAjax.json?r='+str(r)
	
	#page = 1
	#d = 'shopId='+str(shop_id)+'&searchPage='+str(page)+'&keyword=&searchSort=0&shopCategoryId=&clickSku=&skus=&jdDeliver=0&pageFrom='
	for page in range(1,10):
		d = {	'shopId':shop_id,
				'searchPage':page,
				'keyword':'',
				'searchSort':0,
				'shopCategoryId':'',
				'clickSku':'',
				'skus':'',
				'jdDeliver':0,
				'pageFrom':''	}

		r = requests.post(url, headers=headers, data=d)
		r.encoding = 'utf-8'

		logger.info(u'Shop:%d Page:%d Scrap over.'%(shop_id,page))
		
		'''
		file = str(shop_id)+'_good.txt'
		with open(file,'wb') as f:
			f.write(r.content)
			f.close()

		logger.info(u'Shop:%d Page:%d Write over.'%(shop_id,page))
		'''
		clearGoodOfShop(shop_id=shop_id,good_json=r.content,page=page,flag=2)
		logger.info(u'Shop:%d Page:%d Clear over.'%(shop_id,page))

def clearGoodOfShop(shop_id,page,flag,good_file='',good_json=''):
	'''
	清洗爬取的店铺商品信息，写入csv
	flag=1:从文件读取;2:从json读取
	'''
	csv_file = os.path.dirname(os.path.dirname(this_path))+'/data/reclike/goodOfShop.csv'

	if flag==1:
		with open(good_file,'r',encoding='utf-8') as f:
			good_json = f.read()
			f.close()
		open_flag = 'w'
	if flag==2:
		good_json = json.loads(good_json.decode('utf-8'))
		open_flag = 'a'

	good_dict = dict(good_json)
	good_list = good_dict['results']['wareInfo']

	# csv header
	header = ['product_id','shop_id','product_price','product_name']

	data = []
	for i in good_list:
		d_i = {} 
		d_i['product_id'] = i['wareId']
		d_i['product_name'] = i['wname']
		d_i['product_price'] = i['jdPrice']
		d_i['shop_id'] = shop_id 
		data.append(d_i)

	with open(csv_file,open_flag,encoding='utf-8',newline='') as f_c: 
		writer = csv.DictWriter(f_c, fieldnames=header)
		if page == 1:
			writer.writeheader() 
		writer.writerows(data)
		f_c.close() 


def createLogger():
	'''
	新建logger
	path:../Logs/yyyymmddhhmm.log
	formatter:time - file - level - messages
	'''
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
	log_path = os.path.dirname(os.path.dirname(os.getcwd())) + '/logs/'
	log_name = log_path + rq + '.log'
	logfile = log_name

	fh = logging.FileHandler(logfile, mode='w')
	fh.setLevel(logging.DEBUG)

	formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
	fh.setFormatter(formatter)
	logger.addHandler(fh)

	return logger

if __name__ == '__main__':
	'''
	url_origin:商品在手机京东的页面
	url_shop:get,返回店铺信息，店铺cateId cateName
	url_comment:get,返回评论信息，page=page,pagesize=in
	url_reclike:get,猜你喜欢
	venderId:店铺ID
	productId:产品ID
	page:评论页面(1-1000?)
	c1-c3:category c3为最小品类？
	'''
	product_id = 5463278
	vender_id = 1000000921
	page = 1
	c1=652
	c2=828
	c3=842
	url_origin = 'https://item.m.jd.com/product/'+str(product_id)+'.html'
	url_shop = 'https://wq.jd.com/mshop/BatchGetShopInfoByVenderId?callback=getVenderInfoCBA&venderIds='+str(vender_id)+'&t=0.22312032341506904'
	url_comment = 'https://wq.jd.com/commodity/comment/getcommentlist?sorttype=5&sceneval=2&sku='+str(product_id)+'&page='+str(page)+'&pagesize=10&score=0&callback=skuJDEvalA&t=0.49016319767375993'
	url_reclike = 'https://wqcoss.jd.com/mcoss/reclike/getrecinfo?recpos=6159&pc=30&sku='+str(product_id)+'&c1='+str(c1)+'&c2='+str(c2)+'&c3='+str(c3)+'&callback=cb902007A&t=0.3817717299637191'
	'''
	r = requests.get(url_shop)
	with open("shop.txt",'a+',encoding="utf-8") as f:
		f.write(r.text)
		f.close
	'''
	logger = createLogger()
	goodOfShop(vender_id,logger)
