#!/usr/bi/env python
#-*- coding: utf-8 -*-

import sys
import os
import re
import time
import json
import tornado.web
import tornado.ioloop
import tornado.database
import math
import httplib
import json
import pickle
import datetime
from db import *

reload(sys)
sys.setdefaultencoding('gb2312')

from tornado.options import define, options

define("port", default=2358, help="run on the given port", type=int)

NewsDatabase.reconnect()
home_page = "http://210.30.97.149:2358"
ali_page = "115.28.2.165"
tmp_page = "210.30.97.149"


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/tucao', TucaoHandler),
            (r'/tucao/(\d+)$', TucaoHandler),
            (r'/tucao/comm', TucaoCommHandler),
            (r'/tucao/comm/(\d+)$', TucaoCommHandler),
        ]
        settings = dict(
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello")

    def post(self):
        # self.set_header("Content-Type", "application/json")
        raw_body = str(self.request.body)
        print raw_body
        jsonDic = json.loads(raw_body)
        print jsonDic 
        print jsonDic['id']
        self.write("success")

class TucaoHandler(tornado.web.RequestHandler):
    def get(self, nnid):
        NewsDatabase.reconnect()
        nid = int(nnid)
        comm = NewsDatabase.query("""SELECT * FROM commTable WHERE id=%r ORDER
                BY level DESC""", nid)
        print comm
        reply = json.dumps(comm, cls=CJsonEncoder)
        print reply
        self.write(reply)

    def post(self):
        print ("In post")
        NewsDatabase.reconnect()
        raw_body = str(self.request.body)
        print raw_body

        jsonDic = json.loads(raw_body)
        print jsonDic
        
        nid = int(jsonDic['id'])
        LEVEL = NewsDatabase.query("""SELECT COUNT(*) AS level FROM commTable WHERE id=%r""", nid)
        level = int(LEVEL[0]['level'])
        print level

        level += 1
        tolevel = 0
        content = jsonDic['content']
        print content
            
        NewsDatabase.execute(u"""INSERT commTable(id, level, tolevel,
                    content) VALUES(%r, %r, %r, %s)""", nid, level, tolevel,
                    content)

        print ("Insert comm")
        self.write("success")

class TucaoCommHandler(tornado.web.RequestHandler):
    def get(self, nnid):
        NewsDatabase.reconnect()
        nid = int(nnid)
        url = "/id/%d" % nid
        print ali_page
        print url
        try:
            httpClient = httplib.HTTPConnection(tmp_page, 8000, timeout=30)
            httpClient.request('GET', url) 

            response = httpClient.getresponse()
            # print response.status
            response.reason
            raw_news = response.read()
        except Exception, e:
            print e
        finally:
            if httpClient:
                httpClient.close()

        jsonDic = json.loads(raw_news)
        # print jsonDic['clean_body'] 
        
        comm = NewsDatabase.query("""SELECT * FROM commTable WHERE id=%r ORDER
                BY level DESC""", nid)
        # print comm
        self.render('TucaoComm.html', title=jsonDic['title'],\
                body=jsonDic['clean_body'], publisher=jsonDic['publisher'],\
                date=jsonDic['date'], commList=comm, nid=nid)

    def post(self):
        print ("In post")
        NewsDatabase.reconnect()

        raw_body = str(self.request.body)
        print raw_body

        nid = int(self.get_argument('id'))
        LEVEL = NewsDatabase.query("""SELECT COUNT(*) AS level FROM commTable WHERE id=%r""", nid)
        level = int(LEVEL[0]['level'])
        # print level

        level += 1
        tolevel = 0
        content = self.get_argument('content')
        # print content
            
        NewsDatabase.execute(u"""INSERT commTable(id, level, tolevel,
                    content) VALUES(%r, %r, %r, %s)""", nid, level, tolevel,
                    content)

        print ("Insert comm")
        self.redirect("/tucao/comm/%d" % nid)

def TestTucao():
        NewsDatabase.reconnect()
        nid = 1111 
        comm = NewsDatabase.query("""SELECT * FROM commTable WHERE id=%r ORDER
                BY level DESC""", nid)
        print comm
        reply = json.dumps(comm, cls=CJsonEncoder)
        print reply

        level = NewsDatabase.query("""SELECT COUNT(*) AS level FROM commTable WHERE id=%r""", nid)
        print level[0]['level']


def main():
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
