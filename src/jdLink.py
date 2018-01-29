import unittest
from selenium import webdriver
import time
from lxml import etree
from xml.dom.minidom import Document
from selenium.webdriver.common.keys import Keys
import os

dataPath = os.path.abspath('..')    # 工程根目录
file = dataPath + r'\data\jdGood.txt'


class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_search_in_python_org(self):
        driver = self.driver
        with open(file, 'a', encoding='utf-8') as f:
            doc = Document()
            string = "JDgood"
            jdspider = doc.createElement(string)
            doc.appendChild(jdspider)
            url = 'https://sony.jd.com/view_search-395323-0-5-1-24-1.html'
            time.sleep(3)
            driver.get(url)

            for i in range(20):
                xpath1 = './/div[@class="jDesc"]/a'
                xpath2 = './/div[@class="jDesc"]/a'
                goodNames = [n.text for n in driver.find_elements_by_xpath(xpath1)]
                goodLinks = [l.get_attribute("href") for l in driver.find_elements_by_xpath(xpath2)]

                length = len(goodNames)
                for w in range(length):
                    f.write('%s\n' % goodNames[w])
                    f.write('%s\n' % goodLinks[w])

                try:
                    elem = driver.find_element_by_xpath('.//div[@class="jPage"]/a[@class="current"]/following-sibling::a[1]')
                    print(elem.text)
                    time.sleep(10)
                    elem.send_keys(Keys.ENTER)
                except:
                    str1 = str(i)+"st page has been caught."
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


if __name__ == "__main__":
    unittest.main()