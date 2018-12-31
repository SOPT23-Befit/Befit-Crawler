# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json
import urllib
import re
from datetime import datetime
import random
import pymysql
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def getProductDetailInfo(productLink):
    fp = urllib.urlopen(productLink)
    source = fp.read()

    soup = BeautifulSoup(source)

    fp.close()

    productTitle = soup.find('span', attrs={'class':'product_title'}).find_all('span')[0].text

    productPrice = soup.find('span', attrs={'class':'product_article_price'}).text

    productPrice = ''.join(productPrice.encode('utf8').split())

    productCategory = soup.find('p', attrs={'class':'item_categories'}).find_all('a')[-1].text.encode('utf8')

    if productCategory == '기타':
        etc = soup.find('p', attrs={'class':'item_categories'}).find_all('a')[-2:][0].text.encode('utf8')
        productCategory = productCategory+etc

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

    productJsonData = {
        "productTitle" : productTitle,
        "productImgLink" : productImgLink,
        "productPrice" : productPrice,
        "productCategory" : productCategory,
        "productLikeCount" : productLikeCount,
        "productMeasureInfos" : productMeasureInfos,
        "productResistDate" : productResistDate.strftime('%Y-%m-%d')
    }

    return productJsonData


def getBrandId(brandName):
    conn = pymysql.connect(host='befit.ctecxm1v508y.ap-northeast-2.rds.amazonaws.com',user='Befit',password='dbalsgus',db='testDB', use_unicode=True, charset='utf8')
    curs = conn.cursor()
    sql = 'select idx from brand where name_english=%s'
    curs.execute(sql, brandName)
    rows = curs.fetchall()

    return rows[0][0]

def getProductCategory(productCategory):
    productCategoryStr = ''

    if productCategory in '롱 패딩/롱 헤비 아우터 쇼트 헤비 아우터 패딩 베스트':
        productCategoryStr = 'Outer'
    elif productCategory in '블루종/MA-1	레더/라이더스 재킷	트러커 재킷	수트/블레이저 재킷	나일론/코치/아노락 재킷	스타디움 재킷	사파리/헌팅 재킷 기타아우터':
        productCategoryStr = 'Jacket'
    elif productCategory in '환절기 코트	겨울 싱글 코트 겨울 기타 코트':
        productCategoryStr = 'Coat'
    elif productCategory in '베스트':
        productCategoryStr = 'Vest'
    elif productCategory in '니트/스웨터/카디건':
        productCategoryStr = 'Knits'
    elif productCategory in '셔츠/블라우스':
        productCategoryStr = 'Shirts'
    elif productCategory in '후드 스웨트셔츠/후드 집업':
        productCategoryStr = 'Hoody'
    elif productCategory in '맨투맨/스웨트셔츠	기타상의':
        productCategoryStr = 'Sweat Shirts'
    elif productCategory in '반팔 티셔츠	긴팔 티셔츠	피케/카라 티셔츠':
        productCategoryStr = 'T-Shirts'
    elif productCategory in '원피스 점프수트':
        productCategoryStr = 'Onepiece'
    elif productCategory in '데님 팬츠':
        productCategoryStr = 'Jeans'
    elif productCategory in '코튼 팬츠	트레이닝/조거 팬츠	기타하의':
        productCategoryStr = 'Pants'
    elif productCategory in '수트 팬츠/슬랙스':
        productCategoryStr = 'Slacks'
    elif productCategory in '쇼트 팬츠':
        productCategoryStr = 'Short-Pants'
    elif productCategory in '스커트':
        productCategoryStr = 'Skirts'
    elif productCategory in '레깅스':
        productCategoryStr = 'Leggings'

    return productCategoryStr


def mainCrawler(brand, link):
    conn = pymysql.connect(host='befit.ctecxm1v508y.ap-northeast-2.rds.amazonaws.com',user='Befit',password='dbalsgus',db='testDB', use_unicode=True, charset='utf8')
    curs = conn.cursor()

    rawProductData = getProductDetailInfo(link)

    brandIdx = getBrandId(brand)
    productTitle = json.dumps(rawProductData["productTitle"], ensure_ascii=False).replace('"','')
    productImgLink = json.dumps(rawProductData["productImgLink"], ensure_ascii=False).replace('"','')
    productPrice = json.dumps(rawProductData["productPrice"], ensure_ascii=False).replace('"','')
    productCategory = json.dumps(rawProductData["productCategory"], ensure_ascii=False).replace('"','')
    productCategory = getProductCategory(productCategory)
    productLikeCount = json.dumps(rawProductData["productLikeCount"], ensure_ascii=False).replace('"','')
    productResistDate = json.dumps(rawProductData["productResistDate"], ensure_ascii=False).replace('"','')
    productMeasureInfos = json.dumps(rawProductData["productMeasureInfos"], ensure_ascii=False)

    try:
        sql = '''INSERT INTO productTest (name, price, image_url, product_category, brand_idx, date, link, measure, like_score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) '''
        curs.execute(sql, (productTitle, productPrice, productImgLink, productCategory, brandIdx, productResistDate,"",productMeasureInfos, productLikeCount))

        conn.commit()
        print 'DB SAVE SUCCESS'
    except:
        conn.rollback()
        print 'DB SAVE FAIL'

    conn.close()

# mainCrawler('BORN CHAMPS','https://store.musinsa.com/app/product/detail/879172/0')
