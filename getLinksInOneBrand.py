from bs4 import BeautifulSoup
import json
import urllib
import re


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


print getProductLinksInBrand('lambast')
