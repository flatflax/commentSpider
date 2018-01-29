import unittest
from selenium import webdriver
import time
from xml.dom.minidom import Document
import xml.dom.minidom
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import etree
import os

dataPath = os.path.abspath('..')    # 工程根目录
link = dataPath + r'\data\jdGood.txt'
comment = dataPath + r'\data\jdComment.txt'


class commentSearch(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_search_in_python_org(self):
        driver = self.driver
        with open(link, encoding='utf-8') as reader:
            names = []
            links = []
            for index, line in enumerate(reader):
                if index % 2 == 0:
                    names.append(line)
                else:
                    links.append(line)
            reader.close()
        length = len(names)
        for l in range(length):
            name = names[l]
            url = links[l]
            print(url)

            driver.get(url)
            time.sleep(3)
            elem = driver.find_element_by_xpath(".//*[@id='detail']/div[1]/ul/li[4]")
            if '商品评价' not in elem.text:
                elem = driver.find_element_by_xpath('//*[@id="detail"]/div[1]/ul/li[5]')
            elem.click()
            time.sleep(3)

            driver.find_element_by_xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[4]/a').send_keys(Keys.ENTER)
            time.sleep(5)
            greatid = '//div[@id="comment-3"]'
            commentSearch.commSpider(self, greatid, name, driver)

            driver.find_element_by_xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[5]/a').send_keys(Keys.ENTER)
            time.sleep(5)
            middleid = '//div[@id="comment-4"]'
            commentSearch.commSpider(self, middleid, name, driver)

            driver.find_element_by_xpath('//*[@id="comment"]/div[2]/div[2]/div[1]/ul/li[6]/a').send_keys(Keys.ENTER)
            time.sleep(5)
            badid = '//div[@id="comment-5"]'
            commentSearch.commSpider(self, badid, name, driver)



    def tearDown(self):
        self.driver.close()

    def commSpider(self, idpath, name, driver):
        with open(comment, 'a', encoding='utf-8') as f:
            for i in range(300):
                string = 'the ' + str(i) + 'th page comment'
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
                    time.sleep(5)
                    elem.send_keys(Keys.ENTER)
                except:
                    break
                    str2 = str(i) + "th page has been caught."
                    print(str2)
                finally:
                    time.sleep(5)
                    stars.clear()
                    comments.clear()
                    levels.clear()
                    times.clear()
            print("file write over")
            f.close()
