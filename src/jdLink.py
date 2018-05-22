# coding=utf-8
import unittest
from selenium import webdriver
import time
from lxml import etree
from xml.dom.minidom import Document
from selenium.webdriver.common.keys import Keys
import os

dataPath = os.path.abspath('..')
# 工程根目录
file = dataPath + r'\data\jdGood.txt'
urlfile = dataPath + r'\data\jdUrl.txt'


class ShopGoodSearch():

    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def test_search_in_python_org(self, url):
        # flag:True 从京东搜索获取商品，
        # 写入文件时需要对商品所在店铺名进行判断
        # flag:False 从商店"所有商品"页获取商品信息
        # 对获取的所有商品名和商品连接可以直接写入
        driver = self.driver
        with open(file, 'a', encoding='utf-8') as f:
            doc = Document()
            string = "JDgood"
            jdspider = doc.createElement(string)
            doc.appendChild(jdspider)
            time.sleep(3)
            driver.get(url)

            flag = False

            if ("list.jd.com" in url)or("search.jd.com" in url):
                flag = True
                xpath1 = './/div[@class="gl-i-wrap"]/div[4]/a'
                nextpage = './/a[@class="pn-next"]'
                shop = './/div[@class="gl-i-wrap"]/div[7]/span/a'
            else:
                xpath1 = './/div[@class="jGoodsInfo"]/div[1]/a'
                # having './div[jGoodsInfo]/div[jDesc]' and './div[jGoodsInfo]/user_tj_title'
                nextpage = './/a[@class="current"]/following-sibling::a[1]'

            for i in range(20):
                goodnames = [n.text for n in driver.find_elements_by_xpath(xpath1)]
                goodlinks = [l.get_attribute("href") for l in driver.find_elements_by_xpath(xpath1)]

                if flag:
                    shopname = [s.text for s in driver.find_elements_by_xpath(shop)]

                length = len(goodnames)
                for w in range(length):
                    if flag:
                        try:
                            if "官方旗舰店" in shopname[w]:
                                f.write('%s\n' % goodnames[w])
                                f.write('%s\n' % goodlinks[w])
                        except Exception as e:
                            print(e)
                    else:
                        f.write('%s\n' % goodnames[w])
                        f.write('%s\n' % goodlinks[w])

                try:
                    elem = driver.find_element_by_xpath(nextpage)
                    print('the next page:', elem.text)
                    time.sleep(3)
                    elem.click()
                    print('sent Enter to get the next page')
                except Exception as e:
                    print(e)
                    str1 = str(i+1)+"st page has been caught."
                    print(str1)
                    break
                finally:
                    goodnames.clear()
                    goodlinks.clear()
                    if flag:
                        shopname.clear()
                    time.sleep(10)
            print("file write over")
            f.close()
        assert "No results found." not in driver.page_source

    def tearDown(self):
        self.driver.close()

    def writeInfoToXml(self, gNames, gLinks, doc, spider):

        length = len(gNames)

        for i in range(length):
            print(gNames[i])
            print(gLinks[i])

            links = doc.getElementsByTagName("goodLink")
            if gLinks[i] in links:
                print('this good has been caught.Continue.')
                continue

            (name, link) = (gNames[i], gLinks[i])
            docu = doc.createElement("document")
            spider.appendChild(docu)

            gname = doc.createElement('goodName')
            name_text = doc.createTextNode(name)
            gname.appendChild(name_text)
            docu.appendChild(gname)

            glink = doc.createElement('goodLink')
            name_text = doc.createTextNode(link)
            glink.appendChild(name_text)
            docu.appendChild(glink)

    def getShopUrl(self):
        with open(urlfile, encoding='utf-8') as f:
            self.urls = []
            for index, line in enumerate(f):
                self.urls.append(line)
            f.close()


if __name__ == "__main__":
    test = ShopGoodSearch()
    test.getShopUrl()
    test.setUp()
    for url in test.urls:
        print('the shop url:', url)
        test.test_search_in_python_org(url)
    print('over')
    test.tearDown()
