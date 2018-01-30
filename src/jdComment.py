import unittest
import os
import time
import threading
from selenium.webdriver.common.keys import Keys
from selenium import webdriver


class commentSearch:
    def setUp(self, threadname, threadid):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(chrome_options=chrome_options)

        self.test_search_in_python_org(threadname, threadid, driver)

    def test_search_in_python_org(self, threadname, threadid, driver):
        if threadid == 1:
            goodname = names[0:N//2]
            goodlink = links[0:N//2]
        elif threadid == 2:
            goodname = names[N//2+1:N]
            goodlink = links[N//2+1:N]

        length = len(goodname)
        for l in range(length):
            name = goodname[l]
            url = goodlink[l]
            print(threadname, url)

            driver.get(url)
            time.sleep(3)
            elem = driver.find_element_by_xpath(".//*[@id='detail']/div[1]/ul/li[4]")
            if '商品评价' not in elem.text:
                elem = driver.find_element_by_xpath('//*[@id="detail"]/div[1]/ul/li[5]')
            elem.click()
            time.sleep(3)

            driver.find_element_by_xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[4]/a').send_keys(Keys.ENTER)
            time.sleep(2)
            greatid = '//div[@id="comment-3"]'
            commentSearch.commSpider(self, greatid, name, driver, threadname)

            driver.find_element_by_xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[5]/a').send_keys(Keys.ENTER)
            time.sleep(2)
            middleid = '//div[@id="comment-4"]'
            commentSearch.commSpider(self, middleid, name, driver, threadname)

            driver.find_element_by_xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[6]/a').send_keys(Keys.ENTER)
            time.sleep(2)
            badid = '//div[@id="comment-5"]'
            commentSearch.commSpider(self, badid, name, driver, threadname)
        self.driver.close()

    def commSpider(self, idpath, name, driver, threadname):
        with open(comment, 'a', encoding='utf-8') as f:
            for i in range(300):
                string = threadname + ':the ' + str(i+1) + 'th page comment'
                print(string)

                sxpath = idpath + '//div[@class="comment-column J-comment-column"]/div[1]'
                cxpath = idpath + '//p[@class="comment-con"]'
                lxpath = idpath + '//div[@class="user-level"]/span'
                txpath = idpath + '//div[@class="order-info"]/span[last()]'
                stars = [s.get_attribute("class") for s in driver.find_elements_by_xpath(sxpath)]
                comments = [c.text for c in driver.find_elements_by_xpath(cxpath)]
                levels = [l.text for l in driver.find_elements_by_xpath(lxpath)]
                times = [t.text for t in driver.find_elements_by_xpath(txpath)]

                length = len(stars)
                for j in range(length):
                    f.write("%s" % name)
                    f.write("%s\n" % levels[j])
                    f.write("%s\n" % stars[j].replace('comment-star ', ''))
                    f.write("%s\n" % comments[j].replace('\n', ''))
                    f.write("%s\n" % times[j])
                    f.write("\n")

                try:
                    elem = driver.find_element_by_xpath(idpath +
                                                        '//div[@class="com-table-footer"]/div[1]/div[1]/a[@class="ui-pager-next"]')
                    time.sleep(1)
                    elem.send_keys(Keys.ENTER)
                except:
                    break
                    str2 = threadname + str(i+1) + "th page has been caught."
                    print(str2)
                finally:
                    time.sleep(1)
                    stars.clear()
                    comments.clear()
                    levels.clear()
                    times.clear()
            print("file write over")
            f.close()


class myThread(threading.Thread):   # 继承threading.Thread
    def __init__(self, threadid, name):
        threading.Thread.__init__(self)
        self.threadID = threadid
        self.name = name

    def run(self):
        driver = commentSearch()
        driver.setUp(self.name, self.threadID)

dataPath = os.path.abspath('..')    # 工程根目录
link = dataPath + r'\data\jdGood.txt'
comment = dataPath + r'\data\jdComment.txt'
with open(link, encoding='utf-8') as reader:
        names = []
        links = []
        for index, line in enumerate(reader):
            if index % 2 == 0:
                names.append(line)
            else:
                links.append(line)
        reader.close()
print("file load over.")
N = len(names)

thread1 = myThread(1, "Thread-1")
thread2 = myThread(2, "Thread-2")

thread1.start()
thread2.start()
