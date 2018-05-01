# -*- coding: UTF-8 -*- 
from __future__ import unicode_literals
import requests,os,time,json
from bs4 import BeautifulSoup


class GcoresScrap():
	def articleScrap(self, aid, afile):
		url = 'https://www.g-cores.com/articles/' + str(aid)
		r = requests.get(url)
		print("Scraping...Article_id:", aid ,"Status_code:", r.status_code)

		if r.status_code == 200:
			with open(afile, 'w+', encoding='UTF-8') as f:
				f.write(r.text)
				f.close()
				r.close()
			return True

		r.close()
		return False

	# 
	def articleClear(self, aid, afile):
		r = open(afile, 'r', encoding='UTF-8').read()
		soup = BeautifulSoup(r, "lxml")

		result = self.newResultDict()

		result["article_id"] = aid

		# get title of article
		for t in soup.find_all("h1", class_="story_title"):
			if "story_title" not in str(t):
				continue
			result["title"] = t.getText().replace(" ","").replace("\n","")
		# get the post time
		for t in soup.find_all("p", class_="story_info"):
			if "story_info" not in str(t):
				continue
			result["time"] = t.getText()
		# get user_id of article
		for u in soup.find_all("a", class_="story_user"):
			if "story_user" not in str(u):
				continue
			result["user"] = BeautifulSoup(str(u),"lxml").a["href"].replace("/users/","")
		# get the label of the article
		for l in soup.find_all("div", class_="story_consoles"):
			if "story_consoles" not in str(l):
				continue
			for la in l.find_all("a"):
				if len(la) == 0:
					continue
				result["label"].append(la.getText())
		# get num of pics
		for p in soup.find_all("div", class_="story_elem story_elem-image "):
			if "story_elem story_elem-image" not in str(p):
				continue
			result["pics"][0] = result["pics"][0] + 1
		for p in soup.find_all("div", class_="story_elem story_elem-image story_elem-protectHidden"):
			if "story_elem-protectHidden" not in str(p):
				continue
			result["pics"][1] = result["pics"][1] + 1
		for p in soup.find_all("div", class_="swiper-slide"):
			if "swiper-slide" not in str(p):
				continue
			result["pics"][2] = result["pics"][2] + 1
		# get likes
		for l in soup.find_all("strong", id="j_original_likesNum"):
			if "j_original_likesNum" not in str(l):
				continue
			result["likes"] = l.getText()
		# get comments
		for c in soup.find_all("span", class_="j_commentsNum"):
			if "j_commentsNum" not in str(c):
				continue
			if len(c.getText()) > 0:
				result["comments"] = c.getText()
		# get the hole story
		# include the story_elem-protectHidden and not hidden elem
		for s in soup.find_all("div", class_="story_elem-text"):
			if "story_elem story_elem-text " not in str(s):
				continue
			for s_text in s.find_all("p"):
				result["story"] = result["story"] + s_text.getText().replace(" ","").replace("\n", "")

		return result


	def newResultDict(self):
		result = {}

		result["exist"] = 0
		result["title"] = ""
		result["user"] = ""
		result["story"] = ""
		result["now"] = str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		result["label"] = []
		result["pics"] = [0,0,0]
		result["likes"] = 0
		result["comments"] = 0
		result["timeInfo"] = ""
		result["article_id"] = 0

		return result


if __name__ == "__main__":
	article_id = 85463
	user_id = 0

	hfile = '../result/html/article_' + str(article_id) + '.html'
	# clear_file = 'clear_' + str(article_id) + '.txt'
	clear_file = '../result/clear.json'

	scrap_test = GcoresScrap()
	
	# scrap article website
	r = scrap_test.articleScrap(article_id, hfile)

	# only use to test the clear def:
	# r = True


	# if article is exist: get the content and write into result. result["exist"]=0
	# if article is not exist -> r==False : write result["exist"]=1
	if r == True:
		# get content of the web
		result = scrap_test.articleClear(article_id, hfile)

		# write into file with json
		with open(clear_file, 'a+', encoding='UTF-8') as f:
			# ensure_ascii=False : story will not be writen using unicode
			f.write(json.dumps(result, ensure_ascii=False))
			f.write("\n")
			f.close()

		# write into mangoDB
		# document.insert(result)
	if r == False:
		result = scrap_test.newResultDict()
		result["exist"] = 1
		result["article_id"] = article_id

		# write into file with json
		with open(clear_file, 'a+', encoding='UTF-8') as f:
			f.write(json.dumps(result, ensure_ascii=False))
			f.write("\n")
			f.close()
		# write into mongoDB
		# document.insert(result)
	
