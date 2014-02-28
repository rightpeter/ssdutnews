#!/usr/bin/env python
#-*- coding: utf-8 -*-

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
sys.setdefaultencoding('gb2312')

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

        url = '/id/%s' % new_latest
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

        for i in range(pre_latest+1, new_latest):
            url = '/id/%s' % i
            tmp_news = get_page_data(url)
            tmpJsonDic = json.loads(tmp_news)

            tmpTitle = u''.join([
                tmpJsonDic['title'],
                ' - ',
                tmpJsonDic['publisher']])

            context += u"""您可能错过了：<a href="http://210.30.97.149:2358/tucao/comm/%s">%s</a><br>
                """ % (i, tmpTitle)
           
        for user in users:
            print user['name'], ':', user['address']
            if (True == send_mail([user['address']], subject, context)):
                print "success to ", user['name']
            else:
                print "fail to ", user['name']
        return True
    else:
        return False 

if __name__ == "__main__":
    url = "/latest"
    while True:
        print 'xixi'
        raw_news = get_page_data(url)
        jsonDic = json.loads(raw_news)

        new_latest = jsonDic['id'] 
        try:
            f = open('env_dict.pickle', 'rb')
            env_dict = pickle.load(f)
            f.close()
        except:
            env_dict = {}
            env_dict['latest'] = new_latest-5
            f = open('env_dict.pickle', 'wb')
            pickle.dump(env_dict, f)
            f.close()
        pre_latest = env_dict['latest']

        if update_news(pre_latest, new_latest):
            env_dict['latest'] = new_latest
            f = open('env_dict.pickle', 'wb')
            pickle.dump(env_dict, f)
            print 'update: %s %s' % (pre_latest, new_latest)
        else:
            print 'nothing'
            
        time.sleep(15)
