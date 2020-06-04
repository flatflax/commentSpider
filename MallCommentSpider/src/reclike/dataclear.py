import json,csv,os

def commentClear(comment_file,csv_file):
	with open(comment_file,'r',encoding='utf-8') as f:
		comment = f.read()
		f.close()

	comment_json = json.loads(comment.split('(')[1].split(')')[0])
	comment_dict = dict(comment_json)
	comment_list = comment_dict['result']['comments']
	product_id = comment_dict['result']['productCommentSummary']['SkuId']

	'''
	with open(csv_file,'a',encoding='utf-8') as f_c:
		for i in comment_list:
			c_str = ''
			c_str = str(i['id'])+',"'+i['content'].replace('\n','')+'",'+i['creationTime']+','+i['userClientShow']
			c_str = c_str+','+i['userLevelName']+','+i['nickname']+','+str(i['score'])+'\n'
			f_c.write(c_str)
		f_c.close()
	'''
	header = ['id','product_id','score','creationTime','userLevelName','content']
	data = []
	for i in comment_list:
		d_i = {}
		d_i['id'] = i['id']
		#d_i['product_id'] = product_id
		d_i['product_id'] =i['referenceId']
		d_i['score'] = i['score']
		d_i['creationTime'] = i['creationTime']
		d_i['userLevelName'] = i['userLevelName']
		d_i['content'] = i['content']
		data.append(d_i)

	with open(csv_file,'w',encoding='utf-8',newline='') as f_c:
		writer = csv.DictWriter(f_c, fieldnames=header)
		writer.writeheader()
		writer.writerows(data)
		f_c.close()



def reclikeClear(reclike_file, csv_file):
	with open(reclike_file,'r',encoding='utf-8') as f:
		reclike = f.read()
		f.close()

	reclike_json = json.loads(reclike.split('(')[1].split(')')[0])
	reclike_dict = dict(reclike_json)
	reclike_list = reclike_dict['data']

	product_id = os.path.basename(reclike_file).replace("_reclike.txt","")
	'''
	with open(csv_file,'a',encoding='utf-8') as f_c:
		for i in reclike_list:
			price = '%.2f' % (int(i['jp'])/100)
			r_str = ''
			r_str = str(i['sku'])+',"'+i['t']+'",'+str(price)+','+str(i['c3'])+'\n'
			f_c.write(r_str)
		f_c.close()
	'''
	header = ['product_id','origin_id','c3','product_price','product_name']

	data = [] 
	for i in reclike_list: 
		d_i = {} 
		d_i['product_id'] = i['sku']
		d_i['product_name'] = i['t']
		d_i['c3'] = i['c3']
		d_i['product_price'] = '%.2f' % (int(i['jp'])/100) 
		d_i['origin_id'] = product_id 
		data.append(d_i) 

	with open(csv_file,'w',encoding='utf-8',newline='') as f_c: 
		writer = csv.DictWriter(f_c, fieldnames=header) 
		writer.writeheader() 
		writer.writerows(data) 
		f_c.close() 


if __name__ == '__main__':
	this_path = os.getcwd()

	comment_file = os.path.dirname(os.path.dirname(this_path))+'/data/reclike/5463278_comment.txt'
	comment_csv_file = os.path.dirname(os.path.dirname(this_path))+'/data/reclike/5463278_comment_c_test.csv'

	reclike_file = os.path.dirname(os.path.dirname(this_path))+'/data/reclike/5463278_reclike.txt'
	reclike_csv_file = os.path.dirname(os.path.dirname(this_path))+'/data/reclike/5463278_reclike_c_test.csv'
	
	#commentClear(comment_file, comment_csv_file)
	reclikeClear(reclike_file, reclike_csv_file)