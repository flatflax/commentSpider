# -*- coding: UTF-8 -*- 
import threading
import queue,time,json
import random
from garticle_scrapy import GcoresScrap 

class runner(threading.Thread):
	def __init__(self, config):
		threading.Thread.__init__(self)
		self.thread_stop = False
		self.name = config["name"]
		self.q = config["quque"]

	def run(self):
		while not self.thread_stop:
			article_id = self.q.get()
			print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), self.name, ":new queue_id", article_id)

			hfile = '../result/html/article_' + str(article_id) + '.html'
			clear_file = '../result/clear.json'

			scrap_test = GcoresScrap()
			r = scrap_test.articleScrap(article_id, hfile)

			if r == True:
				# get content of the web
				result = scrap_test.articleClear(article_id, hfile)

				# write into file with json
				with open(clear_file, 'a+', encoding='UTF-8') as f:
					# ensure_ascii=False : story will not be writen using unicode
					f.write(json.dumps(result, ensure_ascii=False))
					f.write("\n")
					f.close()

			if r == False:
				result = scrap_test.newResultDict()
				result["exist"] = 1
				result["article_id"] = article_id

				# write into file with json
				with open(clear_file, 'a+', encoding='UTF-8') as f:
					f.write(json.dumps(result, ensure_ascii=False))
					f.write("\n")
					f.close()


	def stop(self):
		self.thread_stop = True

def test():
	thread = []
	q = queue.Queue()
	flag = True

	config = {}
	config["quque"] = q

	# generate a order list, use it to generate a random list
	list_random = random.sample(range(1,50), 49)

	# put into queue
	for i in list_random :
		q.put(i)

	# generate threading
	# setDaemon():Main threading
	for i in range(10):
		config["name"] = "threading"+ str(i)
		t = runner(config)
		t.setDaemon(True)
		thread.append(t)
	for t in thread:
		t.start()

	# stop threading while queue is empty
	while 1:
		if (q.qsize() == 0):
			print("queue is empty,stop threading")
			for t in thread:
				t.stop()
			break
		time.sleep(1)

if __name__ == '__main__':
	test()