from bs4 import BeautifulSoup
import json
import urllib
import re
from datetime import datetime
import random

def getProductDetailInfo(brandName, productLink):
    fp = urllib.urlopen(productLink)
    source = fp.read()

    soup = BeautifulSoup(source)

    fp.close()

    productTitle = soup.find('span', attrs={'class':'product_title'}).find_all('span')[0].text

    productPrice = soup.find('span', attrs={'class':'product_article_price'}).text

    productPrice = ''.join(productPrice.encode('utf8').split())

    productLikeCount = soup.find('span', attrs={'class':'prd_like_cnt'})
    if soup.find('span', attrs={'class':'prd_like_cnt'}) is None:
        productLikeCount = 0
    else:
        productLikeCount = soup.find('span', attrs={'class':'prd_like_cnt'}).text

    productImgLink = 'https:'+soup.find('div', attrs={'class':'product-img'}).find('img')['src']

    year = 2018
    month = random.choice(range(11, 13))
    day = random.choice(range(1, 31))
    productResistDate = datetime(year, month, day)

    table = soup.find('table', attrs={'class':'table_th_grey'})
    theadDatas = table.thead.find_all('tr')[0].find_all('th')

    measureCategory = []


    for theadData in theadDatas[1:]:
        measureCategory.append(''.join(theadData.text.encode('utf8').split()))

    tbodyDatas = table.tbody.find_all('tr')

    productMeasureInfos = {}
    for tbodyData in tbodyDatas[:len(tbodyDatas)]:
        productSize = tbodyData.find_all('th')
        measureDatas = tbodyData.find_all('td')
        if len(measureDatas)<2:
            continue

        i = 0

        for measureData in measureDatas:
            if i == 0 :
                productMeasureInfo = {
                measureCategory[i] : measureData.string
                }
            else:
                productMeasureInfo[measureCategory[i]] = measureData.string
            if i==(len(measureDatas)-1) :
                productMeasureInfos[productSize[0].string] = productMeasureInfo

            i=i+1

    print productMeasureInfos

    productJsonData = {
        "brandName" : brandName,
        "productTitle" : productTitle,
        "productImgLink" : productImgLink,
        "productPrice" : productPrice,
        "productLikeCount" : productLikeCount,
        "productMeasureInfos" : productMeasureInfos,
        "productResistDate" : productResistDate.strftime('%Y-%m-%d')
    }

    # print test
    #
    # with open('test.json', 'a') as make_file:
    #     json.dump(test, make_file, ensure_ascii=False, indent=4)

    return productJsonData

print getProductDetailInfo('test','https://store.musinsa.com/app/product/detail/263106/0')
