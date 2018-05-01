# -*- coding: UTF-8 -*- 
from __future__ import unicode_literals
import sys,os

import jieba,json
import jieba.analyse
jieba.load_userdict("../dict/userdict.txt")
jieba.analyse.set_stop_words("../dict/stop_words.txt")

if __name__ == '__main__':
	# get extract_tags with read file and write file
	clear = '../result/clear.json'
	result = '../result/result.json'


	r = {}
	all_r = []

	with open(clear, 'r' , encoding='UTF-8') as f:
		for line in f:
			r = json.loads(line)
			result = {}
			result["story"] = r["story"].encode('utf-8')
			result["article_id"] = r["article_id"]
			all_r.append(result)
		f.close()

	for s in all_r:
		s["x"]=[]
		s["w"]=[]
		for l in jieba.analyse.extract_tags(s["story"], withWeight=True):
			s["w"].append(l[0])
			s["x"].append(l[1])

	with open('../result/analysis-result.json', 'a+', encoding='UTF-8') as f:
		for r in all_r:
			new_r = {}
			new_r["article_id"] = r["article_id"]
			new_r["words"] = r["w"]
			new_r["percents"] = r["x"]
			f.write(json.dumps(new_r, ensure_ascii=False))
			f.write('\n')
		f.close()


	# get extract_tags with mongoDB
	

