# coding=utf-8

import requests, logging, re, math
from bs4 import BeautifulSoup
import threading
from queue import Queue

from src import tools, account_info
from src.database import Database

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s-%(levelname)s-%(message)s")
logging.disable(logging.DEBUG)

# pool = Pool(database="employer_database.db")

sheetDict = {}


class Zhaopin(object):
    """
        智联招聘
    """

    def __init__(self, city, position, salaryStr):
        """
            初始化
            :param city: 城市，如西安
            :param position: 职位名称包含的字符串，如包含"测试"二字的职位
            :param salaryStr:月薪,如"10001,15000"
        """
        self.city = city
        self.position = position
        self.salaryStr = salaryStr
        self.maximizeNumEachPage = 90  # 智联招聘每页最多记录数

        self.data = [['序号', '职位名称', '工资', '公司名称', '地址', '职位链接', "职位描述"]]  # sheet中的数据

        # 搜索url（url中industry=10100代表IT通信|电子|互联网)）
        self.search_url = (
            "https://fe-api.zhaopin.com/c/i/sou?"
            "pageSize=90&"
            "cityId={}&"
            "industry=10100&"
            "salary={}&"
            "workExperience=-1&"
            "education=-1&"
            "companyType=-1&"
            "employmentType=-1&"
            "jobWelfareTag=-1&"
            "kw={}&{}").format(self.city, self.salaryStr, self.position, account_info.account_info_zhilian)

        logging.info("url:{}".format(self.search_url))

    def formatProcess(self, text):
        """
            对职位描述进行格式处理
            :param text: 职位描述
            :return: 格式处理后对职位描述
        """
        jobDesc = re.sub(r"([；;。]*)(\d[.、])", r'\1\n\2', text)  # 处理条例
        jobDesc = re.sub(r"[：:]", r"：\n", jobDesc)  # 处理条例类别
        jobDesc = re.sub(r"。(\D{4,10}[:：])", r"。\n\1", jobDesc)  # 处理中间的分类，分类前加回车
        jobDesc = re.sub(r"\n{3,}", '\n', jobDesc)  # 3个及3个以上回车 替换成 两个回车
        jobDesc = re.sub(r"\n展开\n*", '', jobDesc)  # 去掉末尾的'展开'二字
        jobDesc = re.sub(r"^\n*职位描述\n*", "", jobDesc)  # 去掉开头对"职位描述"及前后空格
        return jobDesc

    def getJobDesc(self, url):
        """
            获取职位描述
            :param url: 职位的url
            :return: 返回职位描述
        """
        r = requests.get(url)
        try:
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            jobDesc = soup.find('div', {"class:", "responsibility pos-common"})
            jobDesc = jobDesc.get_text()
            jobDesc = self.formatProcess(jobDesc)  # 得到格式处理后的职位描述
            return jobDesc
        except Exception as e:
            print(e)

    def processPageData(self, start, end):
        """
            处理页面数据（一页的）:把一页的数据的相关字段存进列表（该列表的数据最后写进excel的sheetdata中。）
            :param start: 记录开始的index
            :param end: 记录结束的index，不包含该index
            :return: None
        """
        for i in range(start, end):
            position_name = self.search_result_json['data']['results'][i]['jobName']
            self.count += 1  # 处理的记录数

            if self.position in position_name:
                self.effective += 1  # 有效的记录数
                company_name = self.search_result_json['data']['results'][i]['company']['name']
                salary = self.search_result_json['data']['results'][i]['salary']
                city = self.search_result_json['data']['results'][i]['city']['display']
                url = self.search_result_json['data']['results'][i]['positionURL']  # 职位url
                jobDesc = self.getJobDesc(url)  # 职位描述
                self.data.append(
                    [self.effective, position_name, salary, company_name, city, url, jobDesc])  # 找到一个符合条件的就添加到数据列表

                # print("第{}/{}个职位的名称为:{},薪资为:{},公司为:{},地址为:{}".format(self.effective,
                #     self.count, position_name,salary, company_name, city))

    def searchRequests(self, url):
        """
            搜索请求
            :return: 搜索结果的json、当前页的记录数
        """
        try:
            search_result = requests.get(url)  # 职位搜索结果
            search_result.raise_for_status()
            search_result_json = search_result.json()  # 职位搜索结果的json：字典格式
            currentPageRecords = len(search_result_json['data']['results'])  # 当前页的记录数：列表长度
            return search_result_json, currentPageRecords
        except Exception as e:
            print(e)
            exit(1)

    def searchPosition(self):
        """
            职位搜索
            :return: 爬取的职位信息形成的列表,如[[记录1各字段形成的列表], [], []...]
        """
        self.search_result_json, self.currentPageRecords = self.searchRequests(self.search_url)  # 进行搜索请求
        self.numbers = self.search_result_json['data']['numFound']  # 搜索到的职位数量
        self.count = 0  # 已处理记录数量
        self.effective = 0  # 已处理的有效记录数（职位名称中包含提供的信息）
        self.pageNums = self.numbers / self.maximizeNumEachPage  # 全部记录的分页数
        self.modNums = self.numbers % self.maximizeNumEachPage  # 最后一页的记录数量
        self.currentPageRecords = len(self.search_result_json['data']['results'])  # 当前页的记录数量
        logging.info("总共搜索到{}条记录，分为{}页, 最后还剩下{}条记录（取模）.".format(self.numbers, self.pageNums, self.modNums))
        print("一共搜索到{}条职位".format(self.numbers))

        # 根据页数循环处理搜索到的职位记录
        for i in range(math.ceil(self.pageNums)):
            if self.currentPageRecords > 0:
                self.processPageData(0, self.currentPageRecords)  # 处理当前页数据
            else:
                print("当前页没有职位，网站限制最多获取12页。")
                break
            logging.info("当前已处理{}页，共获取了{}条记录，符合条件的有{}条".format(i + 1, self.count, self.effective))
            if self.count < self.numbers:
                next_url = self.search_url + '&start={}'.format(90 * (i + 1))  # 相当于点击"下一页"按钮的请求url
                self.search_result_json, self.currentPageRecords = self.searchRequests(next_url)
            else:
                print("所有职位已处理完成！")
        print("一共处理了{}/{}个职位(标题包含'{}')".format(self.effective, self.count, self.position))

        return self.data


class Liepin(object):
    def __init__(self, city, position, salaryStr):
        """
            初始化
            :param city: 如北京
            :param position: 测试职位，如测试
            :param salaryStr: 年薪，如20$30表示年薪20万至30万
        """
        self.workQueue = Queue()
        self.cityIdDict = {'北京': '010', '西安': '270020', '成都': '280020', '深圳': '050090', '重庆': '040', '广州': '050020'}
        self.city = city
        self.position = position
        self.salaryStr = salaryStr
        self.threadName = "猎聘_{}_{}".format(self.position, self.city)

        # self.data = [['序号', '职位名称', '工资', '公司名称', '地址', '职位链接', "职位描述"]]  # sheet中的数据
        self.data = [['序号', '职位名称', '职位id', '职位地区', '公司名称', '公司Id', '公司地区', '地址', 'location']]

        self.search_url = ("https://www.liepin.com/zhaopin/?"
                           "industries=&"
                           "dqs={}&"
                           "salary={}&"
                           "key={}&"
                           "jobKind=&pubTime=&compkind=&compscale=&industryType=&"
                           "searchType=1&clean_condition=&isAnalysis=&init=1&sortFlag=15&"
                           "flushckid=0&fromSearchBtn=1&{}"
                           ).format(self.cityIdDict[self.city], self.salaryStr, self.position)
        logging.info("url:{}".format(self.search_url))

    def formatProcess(self, text):
        """
            对职位描述进行格式化
            :param text: 职位描述
            :return: 格式化后的职位描述
        """
        pass

    def extractSalary(self, soup):
        """
            从某个职位的源码中提取工资并返回工资
            :param soup:职位源码文本生成的bs对象
        """
        try:
            text = soup.select("div.job-main")[0].get_text()  # 提取包含工资元素的大元素,并获取大元素中的text文本
            salary = re.search(r"\d+-\d+万", text).group()  # 利用正则表达式提取工资
            return salary
        except:
            return None

    def extractInfo(self, soup, str_p):
        """
            从职位的源码中提取与pattern匹配的信息，返回如公司名称、地址等信息
            soup: 职位源码文本生成的bs对象
            str: 要匹配的模版
        """
        try:
            pattern = re.compile(r"var \$CONFIG")
            scriptTxt = soup.find("script", type="text/javascript", text=pattern).get_text()  # 获取职位信息的script脚本中的文本
            pointText = re.search(str_p, scriptTxt).group(2)  # 要提取的目标文本，如公司名称、地址等。
            # logging.info("提取的目标属性值为：{}".format(pointText))
            return pointText
        except:
            return None

    def processCompany(self, companyUrl):
        """
        处理公司信息，获取公司名称，公司地址（data-point, data-address,) 总招聘岗位数，各招聘岗位url
        """
        companyId = re.match(r'^[a-z]*://[a-z.]*/[a-z]*/([0-9]*)', companyUrl).group(1)

        # 搜索数据库中是否存在该id，如果存在则不进行下面的爬取操作
        database = Database()
        conn = database.get_connect()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(1) from company_info where companyId={}".format(companyId))
            value = cursor.fetchall()
            if value[0][0] == 1:
                logging.info("该公司在数据库中存在，跳过")
                return 0
        del database

        logging.info("thread:{} 开始处理第{}个公司: {}".format(self.threadName, self.companyCount + 1, companyId))
        positionText = self.searchRequests(companyUrl)  # 公司url请求，获取返回的text网页数据
        soup = BeautifulSoup(positionText, "html.parser")
        jobCount = soup.select("h2.job-title small")[0].text
        jobCount = int(re.search(r'[0-9]+', jobCount).group(0))
        if jobCount > 0:
            self.companyCount += 1
            self.effective += 1
            """
            如果该公司招聘职位 > 0，爬取公司信息，爬取各招聘url
            """
            pageCount = 15  # 每页职位计数
            maxPage = 20  # 每个公司最大爬取职位数

            jobTotalPage = int(int(jobCount) / pageCount)
            jobTotalPage = jobTotalPage if jobTotalPage < maxPage else maxPage
            nowPage = 0
            # 该公司招聘职位 > 0, 爬取公司信息
            companyInfo = soup.select("ul.new-compintro li")[0]  # 公司信息
            companyAddress = companyInfo['data-address']
            companyName = companyInfo['data-name']
            companyCity = companyInfo['data-city']
            companyLocation = companyInfo['data-point']
            logging.info(
                "thread:{} 公司名:{}, 总页数:{}, 总职位数:{}".format(self.threadName, companyName, jobTotalPage, jobCount))

            database = Database()
            conn = database.get_connect()
            with conn:
                cursor = conn.cursor()
                cursor.execute("INSERT or IGNORE INTO company_info"
                               "(companyId,companyName,companyDistrict,companyAddress,"
                               "companyLocation,companyHireNum,website)"
                               "values(?,?,?,?,?,?,?)",
                               [companyId, companyName, companyCity, companyAddress, companyLocation, jobCount, "猎聘"])

            while (nowPage < jobTotalPage):
                self.processPositionFromCompanyPage(companyUrl, nowPage)
                nowPage = nowPage + 1

    def processPositionFromCompanyPage(self, companyUrl, nowPage):
        requestUrl = companyUrl + "pn" + str(nowPage)
        positionText = self.searchRequests(requestUrl)  # 公司url请求，获取返回的text网页数据
        soup = BeautifulSoup(positionText, "html.parser")
        positionItems = soup.select('div.job-info')
        # logging.info("当前页为{}, 找到{}个职位信息".format(nowPage, len(positionItems)))
        for item in positionItems:
            positionUrl = item.find('a')['href']
            positionUrl = re.match(r'^[a-z]*://[a-z.]*/[a-z]*/[0-9]*[a-z.]*', positionUrl).group(0)
            new_item = {"type": "position", "url": positionUrl}
            self.workQueue.put(new_item)

    def processPosition(self, positionUrl):
        """
            处理每一个职位信息，把每一个职位信息写入data列表中。调用formatProcess进行格式化
        """
        positionId = re.match(r'^[a-z]*://[a-z.]*/[a-z]*/([0-9]*)', positionUrl).group(1)  # 获取职位id

        # 搜索数据库中是否存在该id，如果存在则不进行下面的爬取操作
        database = Database()
        conn = database.get_connect()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(1) from job_info where positionId={}".format(positionId))
            value = cursor.fetchall()
            if value[0][0] == 1:
                return 0
        del database

        logging.info("thread:{} 开始处理第{}个职位".format(self.threadName, self.positionCount + 1))
        positionText = self.searchRequests(positionUrl)  # 职位url请求，获取返回的text网页数据

        soup = BeautifulSoup(positionText, "html.parser")
        positionTitle = soup.find("h1").get_text()  # 职位标题
        positionDistrict = soup.select("p.basic-infor span a")[0].text
        self.positionCount += 1
        self.effective += 1

        # 获取职位信息，获取公司信息
        salary = soup.select("div.job-title-left p")[0].text
        minSalary, maxSalary, bonusSalary = '', '', ''
        if salary != '' or '面议' not in salary:
            minSalary = re.match(r'(\d*)\w?-?(\d*)\w?\S?(\d*\S?)', salary).group(1)
            maxSalary = re.match(r'(\d*)\w?-?(\d*)\w?\S?(\d*\S?)', salary).group(2)
            bonusSalary = re.match(r'(\d*)\w?-?(\d*)\w?\S?(\d*\S?)', salary).group(3)

        companyInfo = soup.select("div.smallmap")[0]
        companyName = companyInfo.find("input", attrs={"id": "company-name"})['value']
        companyDistrict = companyInfo.find("input", attrs={"id": "com-dq"})['value']
        companyAddress = companyInfo.find("input", attrs={"id": "company-address"})['value']
        companyLocation = companyInfo.find("input", attrs={"id": "location"})['value']

        companyUrl = soup.select("div.company-logo a")[0]['href']
        companyId = re.search(r'[0-9]+', companyUrl).group(0)

        database = Database()
        conn = database.get_connect()
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO job_info"
                           "(positionId, positionTitle, positionDistrict, minPositionSalary, "
                           "maxPositionSalary, bonusPositionSalary, companyName, companyId, "
                           "companyDistrict, companyAddress, companyLocation, website) "
                           "values (?,?,?,?,?,?,?,?,?,?,?,?);",
                           [positionId, positionTitle, positionDistrict, minSalary, maxSalary, bonusSalary, companyName,
                            companyId, companyDistrict, companyAddress, companyLocation, '猎聘'])

        # logging.info(
        #     "序号：{} 职位名称:{} 公司名称:{} Id:{} 地区:{} 地址:{} location:{}".format(self.effective, positionTitle,
        #                                                                        companyName,
        #                                                                        companyId, positionDistrict,
        #                                                                        companyAddress,
        #                                                                        companyLocation))

    def processPageData(self, pageData):
        """
            处理每一页的数据：在当前页循环调用processPosition进行处理
            :pageData: 网页text
        """
        logging.info("thread:{} 开始处理第{}页的招聘数据......".format(self.threadName, self.page + 1))
        soup = BeautifulSoup(pageData, 'html.parser')
        # positionElems = soup.select('ul.sojob-list li div div.job-info h3[title] a[target="_blank"]')   # 查找所有的职位<a>元素:查找当前页的所有招聘记录
        # positionElems = soup.select('div.job-info h3[title] a')
        companyElems = soup.select('div.company-info p.company-name a')
        # logging.debug("当前页找到{}条招聘数据:{}".format(len(positionElems), positionElems))
        logging.info("thread:{} 当前页找到{}条招聘公司:{}".format(self.threadName, len(companyElems), companyElems))

        # # 循环处理每个职位
        # for i in positionElems:
        #     positionUrl = i.attrs['href']
        #     logging.info("职位url:{}".format(positionUrl))
        #     flag = re.match(r'^\w*://[a-z.]*/\w*/\d*', positionUrl)
        #     if flag is not None:
        #         self.processPosition(positionUrl)
        #     else:
        #         logging.info("猎头招聘 职位url invalid")
        #         continue

        # 循环处理每个公司
        for i in companyElems:
            if 'href' in i.attrs:
                companyUrl = i.attrs['href']  # 获取职位的链接
            else:
                # 猎头信息，跳过
                continue

            # logging.info("公司url:{}".format(companyUrl))
            flag = re.match(r'^\w*://[a-z.]*/\w*/\d*', companyUrl)
            if flag is not None:
                new_item = {"type": "company", "url": companyUrl}
                self.workQueue.put(new_item)
            # self.processCompany(companyUrl)   # 处理单个职位

    def searchRequests(self, url):
        """
            发起查询请求
            :param url: 猎聘网搜索职位的url
            :return: 返回搜索到的text
        """
        try:
            r = requests.get(url)
        except:
            r = requests.get("https://www.liepin.com" + url)
        finally:
            # with open("text.html", 'w') as f:
            #     f.write(r.text)
            return r.text

    def hasNextPage(self, text):
        """
            判断是否有下一页，有则返回下一页的url，无则返回False
            :text: 网页text
        """
        soup = BeautifulSoup(text, "html.parser")
        # with open("text.html", "w") as f:               # 记录页面text，用来排查错误
        #     f.write(text)
        nextPageElem = soup.find("a", text="下一页")  # 查找class为disabled的<a>元素，即下一页按钮禁用时
        if "class" in nextPageElem.attrs.keys():
            logging.info(
                "thread:{} 已是最后一页。 共爬取公司{}个，职位{}个".format(self.threadName, self.companyCount, self.positionCount))
            return False, None
        else:
            nextPageUrl = nextPageElem.attrs['href']
            nextPageUrl = "https://www.liepin.com" + nextPageUrl
            logging.info("thread:{} [下一页]元素为{}：".format(self.threadName, nextPageElem))
            logging.info("thread:{} [下一页]元素的url：{}".format(self.threadName, nextPageUrl))
            return True, nextPageUrl

    def processItem(self):
        from time import sleep
        while not self.workQueue.empty() or self.searchEndFlag:
            if self.workQueue.empty():
                logging.info('队列暂时为空，等待2s')
                sleep(2)
                continue
            item = self.workQueue.get()
            try:
                if item['type'] == 'position':
                    logging.info("thread:{} 从队列获得职位item".format(self.threadName))
                    self.processPosition(item['url'])
                    continue
                if item['type'] == 'company':
                    logging.info('thread:{} 从队列获得公司item'.format(self.threadName))
                    self.processCompany(item['url'])
                    continue
                if item['type'] == 'search':
                    pass
            except Exception as e:
                logging.error(e)
                if 'url' in item:
                    logging.error(item['url'])
                continue

    def searchPosition(self):
        """
           职位搜索:搜索每一个search_url, 对返回结果进行逐条处理，然后请求下一页再处理页面数据，直到没有下一页。调用processPageData处理每一页数据
           :return: 爬取的职位信息形成的列表,如[[记录1各字段形成的列表], [], []...]
        """
        self.page = 0  # 已处理的页数
        self.companyCount = 0  # 已处理的记录数
        self.positionCount = 0  # 已处理的记录数
        self.effective = 0  # 已处理的有效的记录数:提供的关键字在记录标题中存在时则有效
        self.searchEndFlag = False  # 搜索页面已到达最后一页
        logging.info("thread:{} 开始职位搜索......".format(self.threadName))

        self.search_result_text = self.searchRequests(self.search_url)  # 职位搜索请求返回的text
        logging.debug("{} 搜索到的页面text：{}".format(self.threadName, self.search_result_text))

        self.processPageData(self.search_result_text)  # 处理搜索到的页面数据
        self.processItem()

        # 如果有下一页，则继续搜索下一页、处理搜索的数据，直到末页。
        ok, url = self.hasNextPage(self.search_result_text)
        while ok:
            self.page += 1
            self.search_result_text = self.searchRequests(url)
            self.processPageData(self.search_result_text)
            self.processItem()
            ok, url = self.hasNextPage(self.search_result_text)
        self.searchEndFlag = True

        logging.info("thread:{} 搜索到的职位有：{}".format(self.threadName, self.data))
        return self.data


def salaryRangeProcess(salaryRange, salaryDict):
    """
        对输入的月薪进行正确判断、并处理选择多档薪酬的情况
        :param salaryRange: 月薪范围, 如"1 2"
        :return:对应的月薪或年薪范围列表，如["10001,15000", "15001,2000"]或["10$15", "15$20"]，用来构建请求的url。
    """
    salary = []

    if salaryRange == "":
        print("不指定月薪,将按照不指定月薪进行查询！")
        salary = ['']
    else:
        try:
            salaryRange = salaryRange.split()  # 根据空格，拆分成列表
            # 循环，判断选择是否正确，不正确则按照不指定月薪进行查询, 正确则返回月薪范围列表
            for i in salaryRange:
                if i not in ['1', '2', '3']:
                    print("指定的月薪范围不在提供范围内，将按照不指定月薪进行查询！")
                    salary = ['']
                    break
                else:
                    salary.append(salaryDict[i])
        except Exception as e:
            print(e)

    return salary


def crawling(className, city, position, i):
    """
        爬取各招聘网站的数据
        :param className: 类名如Zhaopin、Liepin
        :param sheetName: 写入excel的sheet名
        :param city: 城市，如西安
        :param position: 职位如测试
        :param i: 薪资选择如20$30 或15001,25000
    """
    className(city, position, i).searchPosition()


def main(city, position):
    """
        主函数
    """
    print("**********欢迎使用招聘信息爬取软件**********")
    threads = []

    database = Database()
    database.create_table('job_info')
    database.create_table('company_info')

    # 智联招聘
    getZL = input("是否获取智联招聘上的信息Y/N:")
    if getZL.upper() == 'Y':
        salaryDict = {"1": "8001,10000", "2": "10001,15000", "3": "15001,25000"}  # 薪资范围
        salaryRange = input("请进行月薪范围选择(1:8K-10K 2:10K-15K 3:15K-25K, 选择多项时以空格分隔)：")
        salary = salaryRangeProcess(salaryRange, salaryDict)        # 月薪，如["10001,15000", "15001,2000"]
        logging.info("选择的月薪为：{}".format(salary))
        for i in salary:
            threadName = "智联招聘_{}_{}_{}".format(city, position, i)
            logging.info(threadName)
            t = threading.Thread(target=crawling, args=[Zhaopin, city, position, i])
            threads.append(t)

    # 猎聘
    getLP = input("是否获取猎聘网上的信息Y/N：")
    if getLP.upper() == "Y":
        # salaryLPDict = {"1": "10$15", "2": "15$20", "3": "20$30"}       # 猎聘薪资范围
        # salaryLPRange = input("请进行年薪范围选择（1：10-15万 2：15-20万 3：20-30万，选择多项时以空格分隔）：")
        # salaryLP = salaryRangeProcess(salaryLPRange, salaryLPDict)      # 选择的年薪，格式如["10$15", "15$20"]
        salaryLP = ['']
        logging.info("选择的年薪为：{}".format(salaryLP))
        for i in salaryLP:
            for p in position:
                threadName = "猎聘网_{}_{}_{}".format(city, position, i)
                logging.info(threadName)
                t = threading.Thread(target=crawling, args=[Liepin, city, p, i])
                threads.append(t)

    # 启动多线程
    for i in threads:
        i.start()

    for i in threads:
        i.join()

def export_database_data(table_name):
    database = Database()
    database.export_database_data(table_name)


if __name__ == "__main__":
    city = '广州'
    position = ['测试', '制药', '外贸', '电商', '美容', '政府'] + ['专员', '成本', 'IT', '招商', '设计', '质量', '采购', '数据', '日化', '食品']
    main(city, position)
    # export_database_data('job_info')
    # export_database_data('company_info')
