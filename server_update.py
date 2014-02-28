#!/usr/bin/env python
#-*- coding: utf-8 -*-

import MySQLdb
import sys
import os
import re
import time
import json
import tornado.web
import tornado.ioloop
# tornado 3.x nolonger have this. use torndb
#import tornado.database
import torndb
import math
import httplib
import json
import pickle
import datetime
import threading
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from db import *
from config import *

reload(sys)
sys.setdefaultencoding('utf-8')

from tornado.options import define, options

# define("port", default=2357, help="run on the given port", type=int)
define("port", default=2358, help="run on the given port", type=int)

NewsDatabase.reconnect()
home_page = "http://210.30.97.149:2358"
local_page = "210.30.97.149"
ali_page = "115.28.2.165"

mail_host = "smtp.163.com"
mail_user = "pedestal_peter"
mail_pass = "15961374343"
mail_postfix = "163.com"

def get_page_data(url):
    try:
        httpClient = httplib.HTTPConnection(ali_page, 8000, timeout=2000)
        httpClient.request('GET', url) 

        response = httpClient.getresponse()
        # print response.status
        response.reason
        raw_news = response.read()
	return raw_news
    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()

def send_mail(to_list, sub, context):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(context, 'html', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(mail_host)
        send_smtp.login(mail_user, mail_pass)
        send_smtp.sendmail(me, to_list, msg.as_string())
        send_smtp.close()
        return True
    except (Exception, e):
        print(str(e))
        return False

def update_news(pre_latest, new_latest): 
    if pre_latest < new_latest:
        NewsDatabase.reconnect()
        users = NewsDatabase.query("""SELECT name, address FROM emailTable""")
        print users

        url = '/id/3843'
        raw_news = get_page_data(url)
        jsonDic = json.loads(raw_news)

        subject = u''.join([
            jsonDic['title'],
            ' - ',
            jsonDic['publisher']])
            
        context = """<a
            href="http://210.30.97.149:2358/tucao/comm/%s">%s</a><br>"""%(new_latest,
                subject) +\
                """<div align="LEFT" style="width:600px;">""" +\
                jsonDic['body'] +\
                "</div>"

           
        return True
    else:
        return False 

class reptile:
    def get_latest(self):
        url = "/latest"
        return json.loads(get_page_data(url))['id']

    def add_news(self, id): 
        url = "/id/%s" % id
        raw_news = get_page_data(url)

        if raw_news:
            json_dic = json.loads(raw_news)

            NewsDatabase.execute("""INSERT newsTable
                (nid,publisher,sha1,date,title,source,
                link,source_link,clean_body,body)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""" \
                ,json_dic['id'],\
                 json_dic['publisher'],\
                 json_dic['sha1'],\
                 json_dic['date'],\
                 json_dic['title'],\
                 json_dic['source'],\
                 json_dic['link'],\
                 json_dic['source_link'],\
                 json_dic['clean_body'],\
                 json_dic['body'])

            #NewsDatabase.execute("""INSERT newsTable
            #    (nid,publisher,sha1,date,title,source,
            #    link,source_link,clean_body,body)
            #    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""" \
            #    ,json_dic['id'],\
            #     MySQLdb.escape_string(json_dic['publisher']),\
            #     MySQLdb.escape_string(json_dic['sha1']),\
            #     MySQLdb.escape_string(json_dic['date']),\
            #     MySQLdb.escape_string(json_dic['title']),\
            #     MySQLdb.escape_string(json_dic['source']),\
            #     MySQLdb.escape_string(json_dic['link']),\
            #     MySQLdb.escape_string(json_dic['source_link']),\
            #     MySQLdb.escape_string(json_dic['clean_body']),\
            #     MySQLdb.escape_string(json_dic['body']))


if __name__ == "__main__":
    url = "/latest"
    NewsDatabase.reconnect()
    while True:
        maxid = NewsDatabase.query("""SELECT MAX(nid) AS mid FROM newsTable""")
        if maxid[0]['mid']:
            maxid = int(maxid[0]['mid'])
        else:
            maxid = 268 
        print datetime.datetime.now(), ':', maxid

        rep = reptile()
        latest = rep.get_latest()

        for i in range(maxid+1,latest+1):
            print datetime.datetime.now(), ':', i
            rep.add_news(i) 
        time.sleep(15)

    #while True:
    #    print 'xixi'
    #    raw_news = get_page_data(url)
    #    jsonDic = json.loads(raw_news)

    #    new_latest = jsonDic['id'] 
    #    try:
    #        f = open('env_dict.pickle', 'rb')
    #        env_dict = pickle.load(f)
    #        f.close()
    #    except:
    #        env_dict = {}
    #        env_dict['latest'] = new_latest-5
    #        f = open('env_dict.pickle', 'wb')
    #        pickle.dump(env_dict, f)
    #        f.close()
    #    pre_latest = env_dict['latest']

    #    if update_news(pre_latest, new_latest):
    #        env_dict['latest'] = new_latest
    #        f = open('env_dict.pickle', 'wb')
    #        pickle.dump(env_dict, f)
    #        print 'update: %s %s' % (pre_latest, new_latest)
    #    else:
    #        print 'nothing'
    #        
    #    time.sleep(15)
