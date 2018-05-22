import os,datetime
import jdLink,jdComment


dataPath = os.path.abspath('..')    # 工程根目录


def getLink():
    test = jdLink.ShopGoodSearch()
    test.getShopUrl()
    test.setUp()
    for url in test.urls:
        print('the shop url:', url)
        test.test_search_in_python_org(url)
    print('over')
    test.tearDown()

def getComment(comment):
    link = dataPath + r'\data\jdGood.txt'
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

    thread1 = jdComment.myThread(1, "Thread-1", N, names, links, comment)
    thread2 = jdComment.myThread(2, "Thread-2", N, names, links, comment)

    thread1.start()
    thread2.start()

if __name__ == "__main__":
    nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    nowTime1 = datetime.datetime.now()
    comment = dataPath + r'\data\jdComment_'+str(nowTime) + '.txt'
    str = input("%s\nInput 1 to get goods link from 'jdUrl.txt',then get good comments\n"
                "Input 2 to get goods comment from 'jdGood.txt'\n" % nowTime1)
    if str == '1':
        getLink()
        print("Get good links over")
        print("Continue to get good comments?")
        nowTime2 = datetime.datetime.now()
        print("Use Time:", nowTime2-nowTime1)
        getComment(comment)
        print("Get good comments over")
        nowTime2 = datetime.datetime.now()
        print("Use Time:", nowTime2-nowTime1)
    elif str == '2':
        getComment(comment)
        print("Get good comments over")
        nowTime2 = datetime.datetime.now()
        print("Use Time:", nowTime2-nowTime1)
