import requests
from utils import selectUserAgent,selectProxy
from lxml import etree
from collections import deque
from random import randint
from time import sleep
import csv

urlList = deque([])
url = "https://www.mouser.cn/c/semiconductors/memory-ics/memory-controllers/"
urlList.append(url)

class SpiderCaller:
    #主要对网页进行请求，并且筛选数据
    def __init__(self,url,headers = {'User-Agent':selectUserAgent()},proxies = {'https':''}):
        self.url = url
        self.headers = headers
        self.proxies = proxies
        self.response = requests.get(self.url,headers = headers,proxies = proxies,timeout = 10) 
        self.tree = etree.HTML(self.response.content)

    def request(self):
        return self.response
    
    def locateTheData(self,xpathStr):
        return self.tree.xpath(xpathStr)

class Downnloader:
    #将数据保存
    def __init__(self,fileName):
        self.fileName = fileName

    def saveAsCsvHeader(self,headers):
        with open(self.fileName,'a',encoding = "utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)


    def saveAsCsvData(self,data):
        with open(self.fileName,'a',encoding = "utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(data)

#创建下载对象
csvDownload = Downnloader('partsdata.csv')
firstPage = True
while(len(urlList)):
    proxies = selectProxy()
    spider = SpiderCaller(urlList.popleft(),proxies = proxies)
    if firstPage:
       #得到csv文件的header 
       xpathHeader = "//thead[@class='tblHeader']/tr/th/span"
       thead = spider.locateTheData(xpathHeader)
       if len(thead)<1:
           print('无了')
           print(proxies)
           with open('logWule.html','w',encoding='utf-8') as f:
               f.write(spider.request().text)
               break
       headers = [thead[i].text for i in range(2,len(thead)) if (i!=8 and i!=9)]
       headers[5] = headers[5].strip()
       csvDownload.saveAsCsvHeader(headers) #保存header
       firstPage = False

    #得到数据,并存入数组
    xpathData = "//table[@id='SearchResultsGrid_grid']/tbody/tr" 
    tbody = spider.locateTheData(xpathData)
    data = []
    for tr in tbody:
        tr = tr.xpath("td")
        tr = [tr[i] for i in range(2,len(tr)-1) if (i!=8)]
        row = []
        for i in range(len(tr)):
            if i==0:
                id = tr[i].xpath("div/a/text()")
                row += id
            elif i==1:
                manufacture = tr[i].xpath("a/text()")
                row += manufacture
            elif i==2:
                type = tr[i].xpath("span/text()")
                row += type
            elif i==3:
                datasheet = tr[i].xpath("div/a")
                if not len(datasheet):
                    datasheet = ''
                else:
                    datasheet = datasheet[0].get("href")
                row.append(datasheet)
            elif i==4:
                storage = tr[i].xpath("span[@class='available-amount']/text()")
                row += storage
            elif i==5:
                price = tr[i].xpath("table//td/span/text()")
                if not len(price):
                    row.append('')
                else:
                    row.append(price[0])
            elif i==6:
                Rohs = tr[i].xpath("div/a")
                if not len(Rohs):
                    Rohs = ''
                else:
                    Rohs ='https://www.mouser.cn' + Rohs[0].get("href")
                row.append(Rohs)
            else:
                paramater = tr[i].xpath("span/text()")
                if not len(paramater):
                    paramater = ['']
                row += paramater  
        data.append(row)
    csvDownload.saveAsCsvData(data)         #保存data
    print('datasaved')

    #获取下一页的url
    xpathNextPage = "//table//ul[@class='pagination']//a[@id = 'lnkPager_lnkNext']"
    nextUrl = spider.locateTheData(xpathNextPage)
    if len(nextUrl):
        url = nextUrl[0].get("href")
        print(url)
        urlList.append(url)
        #sleep(randint(10,30))
    else:
        urlList.clear()