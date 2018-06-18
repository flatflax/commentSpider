import requests

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

	r = requests.get(url_shop)
	with open("../../data/reclike/shop.txt",'a+',encoding="utf-8") as f:
		f.write(r.text)
		f.close

	
