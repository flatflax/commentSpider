# -*- coding: UTF-8 -*- 
import threading
import queue,time
import random

class runner(threading.Thread):
	def __init__(self, config):
		threading.Thread.__init__(self)
		self.thread_stop = False
		self.name = config["name"]
		self.q = config["quque"]

	def run(self):
		while not self.thread_stop:
			print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), self.name, ":new queue_id", self.q.get())
			t = random.uniform(0,2)
			time.sleep(t)

	def stop(self):
		self.thread_stop = True

def test():
	thread = []
	q = queue.Queue()
	flag = True

	config = {}
	config["quque"] = q

	# generate a order list, use it to generate a random list
	list_random = random.sample(range(1,1000), 100)

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