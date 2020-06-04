import unittest
from selenium import webdriver
import time
import os
from xml.dom.minidom import Document
from selenium.webdriver.common.keys import Keys

dataPath = os.path.abspath('..')    # 工程根目录
url = 'https://sony.tmall.com/category.htm?spm=a1z10.1-b-s.w15786047-15102841353.2.7ea96638smYOEt&search=y'     # 官方旗舰店


class PythonOrgSearch(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_search_in_python_org(self):
        driver = self.driver
        file = dataPath + r'\\data\\tmGood.txt'
        with open(file, 'a', encoding='utf-8') as f:
            doc = Document()
            string = "JDgood"
            jdspider = doc.createElement(string)
            doc.appendChild(jdspider)
            time.sleep(3)
            driver.get(url)

            for i in range(20):     # 写死抓20页的商品
                # 用xpath抓商品名称和商品连接
                xpath1 = "//div[@class='J_TItems']//div[@class='pagination']/preceding" \
                         "-sibling::div//dd[@class='detail']/a"
                xpath2 = "//div[@class='J_TItems']//div[@class='pagination']/preceding-si" \
                         "bling::div//dd[@class='detail']/a"
                goodname = [n.text for n in driver.find_elements_by_xpath(xpath1)]
                goodlink = [l.get_attribute("href") for l in driver.find_elements_by_xpath(xpath2)]

                length = len(goodname)
                for w in range(length):
                    f.write('%s\n' % goodname[w])
                    f.write('%s\n' % goodlink[w])

                try:    # 尝试抓取下一页组件并点击，末页无法点击则输出抓取多少页并关闭
                    elem = driver.find_element_by_xpath(
                        "//div[@class='J_TItems']//div[@class='pagination']"
                        "//a[@class='page-cur']/following-sibling::a[1]")
                    print(elem.text)
                    time.sleep(5)
                    elem.send_keys(Keys.ENTER)
                except:
                    str1 = str(i+1) + "st page has been caught."
                    print(str1)
                    break
                finally:
                    goodname.clear()
                    goodlink.clear()
                    time.sleep(5)

            # f.write(doc.toprettyxml(indent="", encoding='utf-8'))
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
