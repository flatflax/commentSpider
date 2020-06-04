import unittest
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import os

dataPath = os.path.abspath('..')    # 工程根目录
link = dataPath + r'\\data\\tmGood.txt'
comment = dataPath + r'\\data\\tmComment.txt'


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
            time.sleep(8)
            elem = driver.find_element_by_xpath('//*[@id="J_TabBar"]/li/a[contains(text(),"评价")]')
            num = elem.find_element_by_xpath('//em[@class="J_ReviewsCount"]')
            print('comment number:%s' % num.text)
            if num.text == '0':
                print('have no comment,continue')
                continue
            elem.send_keys(Keys.ENTER)
            time.sleep(5)

            try:
                commentSearch.commSpider(self, name, driver)
            except Exception as e :
                print(str(e))
                continue

    def tearDown(self):
        self.driver.close()

    def commSpider(self, name, driver):
        with open(comment, 'a', encoding='utf-8') as f:
            for i in range(300):
                # string = 'the ' + str(i) + 'th page comment'
                # print(string)

                cxpath = '//*[@id="J_Reviews"]/div/div[6]/table/tbody//tr/td[1]'
                lxpath = '//*[@id="J_Reviews"]/div/div[6]/table/tbody//tr/td[3]'
                # txpath = '//div[@class="order-info"]/span[last()]'
                com = [c for c in driver.find_elements_by_xpath(cxpath)]
                lev = [l for l in driver.find_elements_by_xpath(lxpath)]
                # times = [t.text for t in driver.find_elements_by_xpath(txpath)]
                comments=[]
                levels=[]

                length = len(com)

                for c in com:
                    try:
                        elem = (c.find_element_by_class_name('tm-rate-fulltxt'))
                        text = elem.text
                    finally:
                        comments.append(text)
                for l in lev:
                    try:
                        elem = (l.find_element_by_class_name('gold-user'))
                        text = elem.text
                    except:
                        text = '普通会员'
                    finally:
                        levels.append(text)
                for j in range(length):
                    f.write("%s" % name)
                    f.write("%s\n" % levels[j])
                    # f.write("%s\n" % stars[j].replace('comment-star ', ''))
                    f.write("%s\n" % comments[j].replace('\n', ''))
                    # f.write("%s\n" % times[j])
                    f.write("\n")

                try:
                    elem = driver.find_element_by_xpath("//div[@class='rate-paginator']//span[last()]/following-sibling::a[1]")
                    time.sleep(5)
                    elem.send_keys(Keys.ENTER)
                except:
                    break
                    str2 = str(i) + "th page has been caught."
                    print(str2)
                finally:
                    time.sleep(5)
                    # stars.clear()
                    comments.clear()
                    levels.clear()
                    # times.clear()
            print("file write over")
            f.close()
