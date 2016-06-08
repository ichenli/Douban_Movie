#!/usr/bin/env python
# encoding: utf-8

import requests
import re
from bs4 import BeautifulSoup

header = {
        'user-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'en-US,en;q=0.5',
        'Accept-Encoding':'gzip,deflate,br',
        'Connetion':'keep-alive'
        }
login_url = "https://accounts.douban.com/login"
movie_class_url = 'https://movie.douban.com/tag/'
data = {'form_email': '197294332@qq.com', 'form_password': 'chenli197294332'}


class movie_crawler:
    def login(self):
        session = requests.Session()
        session.post(login_url,data = data, headers = header)
        return session

    def get_classlist(self,url,session):
        content =[]
        classlist = []
        content =session.get(url).text
        class_list = re.findall(r"(\/tag\/)([\u4e00-\u9fa5]+)",content)
        for i in range(34) :
            tag = class_list[i][1]
            classlist.append(tag)
        return classlist

    def gettagurl(self,classlist):
        taglist = []
        for i in  range(len(classlist)) :
            tagurl = movie_class_url+classlist[i]
            taglist.append(tagurl)
        return taglist

    def getmovielist(self,url,session):
        movie_list = []
        page = session.get(url)
        content = page.text
        movie_list = re.findall(r'https://movie.douban.com/subject/[0-9]+',content)
        return movie_list

    def getpagenumber(self,url,session):
        page = session.post(url)
        content = page.text
        totalpages = re.findall(r'data-total-page=\"[0-9]*\"',content)
        tatalpage = int(totalpages[0][17:-1])
        return tatalpage

    def getcontent(selg,url,session):
        page = session.post(url)
        content = page.text
        return content
crawler = movie_crawler()
session =crawler.login()
classlist = crawler.get_classlist(movie_class_url,session)
taglist = crawler.gettagurl(classlist)
movielist = []
for item in taglist :
    #pagenumber = crawler.getpagenumber(item,session)
    pagenumber = 1
    for i in range(pagenumber):
        url = item + '?start=' + str(i*20) + '&type=T'
        movie_list = crawler.getmovielist(url,session)
        movielist[-1:-1] = movie_list
    break
totallist = list(set(movielist))
content = crawler.getcontent(totallist[0],session)
soup = BeautifulSoup(content,'lxml')
#title = soup.h1
title = soup.find('span',{"property":"v:itemreviewed"}).string
year = soup.find('span',{"class":"year"}).string[1:-1]
print(year)
