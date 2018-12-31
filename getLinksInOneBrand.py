from bs4 import BeautifulSoup
import json
import urllib
import re
import pymysql
import getItemInOneProduct

conn = pymysql.connect(host='',user='',password='',db='', use_unicode=True, charset='utf8')

def getProductLinksInBrand(brandName):
    fp = urllib.urlopen('https://store.musinsa.com/app/brand/goods_list/'+brandName)
    source = fp.read()

    soup = BeautifulSoup(source)

    fp.close()

    rawProductLinks = soup.find_all('div', attrs={'class':'list_img'})

    productLinks = []

    for productLink in rawProductLinks[:20]:
        productLinks.append('https://store.musinsa.com'+productLink.find('a')['href'])

    return productLinks

def getAllBrandList():
    curs = conn.cursor()
    sql = 'select name_english from brand'
    curs.execute(sql)
    rows = curs.fetchall()
    brands=[]
    for brand in rows:
        brands.append(brand[0].encode('utf8').replace(' ','').replace('.',''))
    return brands

def getAllRawBrandList():
    curs = conn.cursor()
    sql = 'select name_english from brand'
    curs.execute(sql)
    rows = curs.fetchall()
    brands=[]
    for brand in rows:
        brands.append(brand[0].encode('utf8'))
    return brands

allBrandProductLinkList = []

print '::: crawling start :::'

for b in getAllBrandList():
    allBrandProductLinkList.append(getProductLinksInBrand(b))

print "all product links crawling success"

brand_index = 0
brandName = ''
for brandLinks in allBrandProductLinkList:
    brandName = getAllRawBrandList()[brand_index]
    for link in brandLinks:
        try:
            getItemInOneProduct.mainCrawler(brandName, link)
        except:
            print link
    brand_index = brand_index+1
