import unittest
from selenium import webdriver
import time
from lxml import etree
from xml.dom.minidom import Document
from selenium.webdriver.common.keys import Keys
import os

dataPath = os.path.abspath('..')    # 工程根目录
file = dataPath + r'\data\jdGood.txt'
urlfile = dataPath + r'\data\jdUrl.txt'


class ShopGoodSearch():

    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def test_search_in_python_org(self, url):
        driver = self.driver
        with open(file, 'a', encoding='utf-8') as f:
            doc = Document()
            string = "JDgood"
            jdspider = doc.createElement(string)
            doc.appendChild(jdspider)
            time.sleep(3)
            driver.get(url)

            for i in range(20):
                xpath1 = './/div[@class="jGoodsInfo"]/div[1]/a'
                # having './div[jGoodsInfo]/div[jDesc]' and './div[jGoodsInfo]/user_tj_title'
                xpath2 = './/div[@class="jDesc"]/a'
                goodNames = [n.text for n in driver.find_elements_by_xpath(xpath1)]
                goodLinks = [l.get_attribute("href") for l in driver.find_elements_by_xpath(xpath1)]

                length = len(goodNames)
                for w in range(length):
                    f.write('%s\n' % goodNames[w])
                    f.write('%s\n' % goodLinks[w])

                try:
                    goodXpath = './/div[@class="jPage"]/a[@class="current"]/following-sibling::a[1]'
                    elem = driver.find_element_by_xpath(goodXpath)
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
                    goodNames.clear()
                    goodLinks.clear()
                    time.sleep(10)

            #f.write(doc.toprettyxml(indent="", encoding='utf-8'))
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