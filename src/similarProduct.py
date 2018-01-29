import unittest
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class similarProductSearch(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_search_in_python_org(self):

        with open('productName.txt', encoding="utf-8") as reader:   # 获取需要搜索的商品名
            goodnames = []
            for index, line in enumerate(reader):
                goodnames.append(line.replace("\n",""))
            reader.close()

        driver = self.driver
        url = "https://3c.tmall.com/"
        driver.get(url)

        for name in goodnames:
            print(name)
            try:
                similarProductSearch.switchHandle(self, driver)
                element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="mallSearch"]/form/fieldset/div/button'))
                            )   # 搜索框旁边的确认键
                driver.find_element_by_xpath('//*[@id="mq"]').send_keys(name)   # 搜索框输入型号
                time.sleep(10)
                element.send_keys(Keys.ENTER)
                for i in range(50):
                    similarProductSearch.switchHandle(self, driver)
                    try:
                        xpath1 = "//p[@class='productTitle']/a"  # 商品名称（链接）
                        flag = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, xpath1)))
                        print("find flag %s " % flag.text)
                        links = (e for e in
                                 driver.find_elements_by_xpath(xpath1))     # 获得该页所有商品连接所在elements
                        for link in links:
                            similarProductSearch.switchHandle(self, driver)
                            time.sleep(3)
                            try:
                                link.click()
                                similarProductSearch.getInfoTwo(self, driver)   # 点击进入商品页
                            except Exception as e:
                                print('getIntoTwo Error')
                                print(link.get_attribute("href"))
                                print(e)
                                continue
                        print('link click over')

                        if len(driver.window_handles) > 1:  # 判断是否已回到搜索页，否则删除当前页
                            driver.close()
                            similarProductSearch.switchHandle(self, driver)
                            time.sleep(3)

                        try:
                            element = driver.find_element_by_xpath('//*[@class="ui-page-next"]')    # 点击下一页
                            element.send_keys(Keys.ENTER)
                        except Exception as e:
                            print(e)
                            print("%d st page end" % i)
                            break
                        finally:
                            time.sleep(3)
                    except Exception as e:
                        print('search Error')
                        print(e)
                        continue
            finally:
                time.sleep(3)
                similarProductSearch.switchHandle(self, driver)
                driver.find_element_by_xpath('//*[@id="mq"]').clear()   # 删除搜索框中文字
                time.sleep(3)

    def tearDown(self):
        self.driver.close()

# 2017/11/14 更新后没有套装个页
    def getInfoOne(self, driver):   # 进入套装个页，点击各商品获取相关信息
        time.sleep(3)

        similarProductSearch.switchHandle(self, driver)
        for i in range(30):
            goodlinks = (l for l in driver.find_elements_by_xpath('.//h4[@class="proInfo-title"]/a'))
            for good in goodlinks:
                similarProductSearch.switchHandle(self, driver)

                time.sleep(3)
                good.send_keys(Keys.ENTER)
                similarProductSearch.getInfoTwo(self, driver)   # 商品个页def

            try:    # 点击下一页的功能
                similarProductSearch.switchHandle(self, driver)
                time.sleep(3)
                nextPage = driver.find_element_by_xpath('.//a[@class="ui-page-next"]')
                nextPage.click()
            except Exception as e:

                print(e)
                time.sleep(5)
                similarProductSearch.switchHandle(self, driver)
                # driver.close()
                break
            finally:
                time.sleep(3)

    def getInfoTwo(self, driver):   # 进入商品个页，获取商品相关信息
        time.sleep(3)
        similarProductSearch.switchHandle(self, driver)
        goodInfo = []
        time.sleep(10)

        selects = (s for s in driver.find_elements_by_xpath('.//li[@class="tb-selected"]'))
        # 待补全，点击所有li[@class="tb-selected"]，获得所有库存
        for selected in selects:
            selected.click()
            time.sleep(3)
        # 月销量，价格，库存
        tmCount = driver.find_elements_by_xpath('.//span[@class="tm-count"]')
        sell = tmCount[0].text
        goodInfo.append(sell)

        price = driver.find_element_by_xpath('.//span[@class="tm-price"]').text
        goodInfo.append(price)

        try:
            stock = driver.find_element_by_xpath('.//*[@id="J_EmStock"]').text
            goodInfo.append(stock)
        except Exception as e:
            print(e)
            goodInfo.append('')

        # 店铺，商品名
        goodname = driver.find_element_by_xpath('.//div[@class="tb-detail-hd"]').text.replace("\n","")
        shop = driver.find_element_by_xpath('.//div[@class="shop-intro"]//div[@class="name"]/a[1]')
        shopName = shop.text
        shopLink = shop.get_attribute("href")
        goodInfo.append(goodname)
        goodInfo.append(shopName)
        goodInfo.append(shopLink)

        time.sleep(10)
        # 最后写入文本
        with open('similarProduct.txt', 'a', encoding='utf-8') as f:
            for info in goodInfo:
                f.write('%s\n' % info)
            f.close()
        time.sleep(5)
        goodInfo.clear()
        driver.close()

    def switchHandle(self, driver):     # 切换到最新窗口
        handles = driver.window_handles     # 获取当前窗口句柄集合（列表类型）
        driver.switch_to_window(handles[-1])
