#!/usr/bin/env python
# encoding: utf8

import requests
import re
import time
import pymysql
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
        print(content)
        print(url)
        class_list = re.findall(r"(\/tag\/)([\u4e00-\u9fa5]+)",content)
        print(len(class_list))
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

    def getcontent(selg,item,session):
        infor = []
        id = int(item[33:])
        page = session.post(item)
        content = page.text
        soup = BeautifulSoup(content,'lxml')
        title = soup.find('span',{"property":"v:itemreviewed"}).string
        year = soup.find('span',{"class":"year"}).string[1:-1]
        movieclass = soup.findAll('span',property="v:genre")
        score = soup.find('strong',{"property":"v:average"}).string
        try:
            comments = soup.find('span',property="v:votes").string
        except Exception:
            comments = ''
            pass
        try:
            time = soup.find('span',{"property":"v:runtime"}).string
        except Exception:
            time = 0
            pass
        classes = ''
        for item in movieclass :
            classes = item.string+" " + classes

        try:
            summary = soup.find('span',property="v:summary")
            p = re.compile(r'<.+>')
            q = re.compile(r'\n|\u3000')
            summary = p.sub('',str(summary))
            summary = q.sub('',summary)
            summary = summary.replace(' ','').strip().strip('\n')
        except Exception:
            summary = ' '
            pass
        infor.append(id)
        infor.append(title)
        infor.append(year)
        infor.append(classes)
        infor.append(time)
        infor.append(score)
        infor.append(comments)
        infor.append(summary)
        #print(infor)
        return infor

    def sqlconnect(self):
        conn=pymysql.connect(host='localhost',user='root',passwd='chenli',\
                db='mysql',port=3306,charset='utf8')
        cur = conn.cursor()
        try :
            cur.execute('drop database douban_movie')
        finally :
            pass
        cur.execute("create database douban_movie ")
        print('create database')
        cur.execute('use douban_movie')
        cur.execute('create table movie(id INT,\
                                        name VARCHAR(60),\
                                        year VARCHAR(5),\
                                        classes VARCHAR(30),\
                                        time VARCHAR(9),\
                                        score VARCHAR(4),\
                                        comments VARCHAR(8),\
                                        summary VARCHAR(1000)\
                                        )CHARACTER SET utf8 COLLATE utf8_general_ci')
        print('create table')
        returnlist = [cur,conn]
        return returnlist

    def sqlinsert(self,returnlist,infor):
        print(returnlist)
        print(infor)
        cur = returnlist[0]
        conn = returnlist[1]
        cur.execute("insert into douban_movie.movie values(%s,%s,%s,%s,%s,%s,%s,%s)",(infor[0],\
                                                                         str(infor[1]),\
                                                                         str(infor[2]),\
                                                                         str(infor[3]),\
                                                                         str(infor[4]),\
                                                                         str(infor[5]),\
                                                                         str(infor[6]),\
                                                                         str(infor[7])))
        print('d')
        cur.execute("select * from douban_movie.movie")
        for item in cur:
           print(item)
        conn.commit()
        cur.close()
        conn.close()

crawler = movie_crawler()
print('开始……')
session =crawler.login()
print('登录成功')
classlist = crawler.get_classlist(movie_class_url,session)
print('获取电影类型')
taglist = crawler.gettagurl(classlist)
print('获取标签')
movielist = []
print('获取电影链接')
for item in taglist :
    pagenumber = crawler.getpagenumber(item,session)
    #pagenumber = 1
    for i in range(pagenumber):
        url = item + '?start=' + str(i*20) + '&type=T'
        movie_list = crawler.getmovielist(url,session)
        movielist.extend(movie_list)
        if pagenumber%10==0 :
            time.sleep(60)
        print(i)
    #break
totallist = list(set(movielist))
print('连接数库')
returnlist = crawler.sqlconnect()
print('开始爬取')
for item in totallist :
    if len(totallist)%20==0 :
        time.sleep(60)
    infor = crawler.getcontent(item,session)
    try:
        crawler.sqlinsert(returnlist,infor)
    finally :
        pass
    print(infor[2]+'完成')
    #break
#crawler.sqlconnect(infor)
