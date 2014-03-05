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
import tornado.database
#import torndb
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

home_page = "http://210.30.97.149:2358"
local_page = "210.30.97.149"
ali_page = "115.28.2.165"

class myTools:
    @classmethod
    def get_json(self, domain, url):
        try:
            httpClient = httplib.HTTPConnection(domain, 8000, timeout=2000)
            httpClient.request('GET', url) 

            response = httpClient.getresponse()
            # print response.status
            response.reason
            return response.read()
        except Exception, e:
            print e
        finally:
            if httpClient:
                httpClient.close()
        #return raw_news

    @classmethod
    def get_latest_news_id(self):
        maxid = NewsDatabase.query("""SELECT MAX(id) AS mid FROM newsTable""")
        if maxid[0]['mid']:
            maxid = int(maxid[0]['mid'])
        else:
            maxid = 0 
        return maxid       

    @classmethod
    def get_latest_news_nid(self):
        maxnid = NewsDatabase.query("""SELECT MAX(nid) AS mnid FROM newsTable""")
        if maxnid[0]['mnid']:
            maxnid = int(maxnid[0]['mnid'])
        else:
            maxnid = 0
        return maxnid

    @classmethod
    def get_total_news_num(self):
        total = NewsDatabase.query("""SELECT COUNT(id) AS total FROM newsTable""")
        total = int(total[0]['total'])
        return total

    @classmethod
    def get_a_news(self, nid):
        NewsDatabase.reconnect()
        news = NewsDatabase.query("""SELECT * FROM newsTable WHERE id=%s""",
                nid)
        if len(news):
            return news[0]
        else:
            return {} 


    @classmethod
    def send_mail(self, to_list, sub, context):
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

    @classmethod
    def add_news(self, id): 
        url = "/id/%s" % id
        raw_news = self.get_json(ali_page, url)

        if raw_news:
            json_dic = json.loads(raw_news)

            print datetime.datetime.now(), ':', id, 'insert'
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
            return True
        else:
            print datetime.datetime.now(), ':', id, 'nothing'
            #NewsDatabase.execute("""INSERT newsTable(nid) VALUES(%s)""", 9999)
            return False


    @classmethod
    def isInBlackList(self, httprequest):
        ip = httprequest.request.remote_ip.decode('utf-8')
        print "-----------------------------one request-----------------------------"
        print "method: %s" % httprequest.request.method
        print "uri: %s" % httprequest.request.uri
        print "remote_ip: %s" % httprequest.request.remote_ip
        print "body: %s" % httprequest.request.body
        print "time: %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print "-----------------------------one request-----------------------------"
        # print blacklist
        # print blacklist[0]
        # print ip
        # print (ip in blacklist)
        if ( ip in env_dict['blacklist'] ):
            print "In black list"
            return True
        else:
            return False

