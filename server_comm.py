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
import threading
from db import *

reload(sys)
sys.setdefaultencoding('gb2312')

from tornado.options import define, options

define("port", default=2357, help="run on the given port", type=int)
# define("port", default=2358, help="run on the given port", type=int)

NewsDatabase.reconnect()
home_page = "http://210.30.97.149:2358"
ali_page = "115.28.2.165"
tmp_page = "210.30.97.149"

restrict = {}

BLACKLIST = NewsDatabase.query("""SELECT * FROM blackList""")
blacklist = []
for blackdict in BLACKLIST:
    blacklist.append(blackdict['ip'])
print blacklist
       
def isInBlackList(self):
    ip = self.request.remote_ip.decode('utf-8')
    print "-----------------------------one request-----------------------------"
    print "method: %s" % self.request.method
    print "uri: %s" % self.request.uri
    print "remote_ip: %s" % self.request.remote_ip
    print "body: %s" % self.request.body
    print "-----------------------------one request-----------------------------"
    # print blacklist
    # print blacklist[0]
    # print ip
    # print (ip in blacklist)
    if ( ip in blacklist ):
        print "In black list"
        self.redirect('/blacklist')
        return True
    else:
        return False

class Memoize:
    """
    'Memoizes' a function, caching its return values for each input.
    If `expires` is specified, values are recalculated after `expires` seconds.
    If `background` is specified, values are recalculated in a separate thread.
    
        >>> calls = 0
        >>> def howmanytimeshaveibeencalled():
        ...     global calls
        ...     calls += 1
        ...     return calls
        >>> fastcalls = memoize(howmanytimeshaveibeencalled)
        >>> howmanytimeshaveibeencalled()
        1
        >>> howmanytimeshaveibeencalled()
        2
        >>> fastcalls()
        3
        >>> fastcalls()
        3
        >>> import time
        >>> fastcalls = memoize(howmanytimeshaveibeencalled, .1, background=False)
        >>> fastcalls()
        4
        >>> fastcalls()
        4
        >>> time.sleep(.2)
        >>> fastcalls()
        5
        >>> def slowfunc():
        ...     time.sleep(.1)
        ...     return howmanytimeshaveibeencalled()
        >>> fastcalls = memoize(slowfunc, .2, background=True)
        >>> fastcalls()
        6
        >>> timelimit(.05)(fastcalls)()
        6
        >>> time.sleep(.2)
        >>> timelimit(.05)(fastcalls)()
        6
        >>> timelimit(.05)(fastcalls)()
        6
        >>> time.sleep(.2)
        >>> timelimit(.05)(fastcalls)()
        7
        >>> fastcalls = memoize(slowfunc, None, background=True)
        >>> threading.Thread(target=fastcalls).start()
        >>> time.sleep(.01)
        >>> fastcalls()
        9
    """
    def __init__(self, func, expires=None, background=True): 
        self.func = func
        self.cache = {}
        self.expires = expires
        self.background = background
        self.running = {}
    
    def __call__(self, *args, **keywords):
        key = (args, tuple(keywords.items()))
        if not self.running.get(key):
            self.running[key] = threading.Lock()
        def update(block=False):
            if self.running[key].acquire(block):
                try:
                    self.cache[key] = (self.func(*args, **keywords), time.time())
                finally:
                    self.running[key].release()
        
        if key not in self.cache: 
            update(block=True)
        elif self.expires and (time.time() - self.cache[key][1]) > self.expires:
            if self.background:
                threading.Thread(target=update).start()
            else:
                update()
        return self.cache[key][0]

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
        self.max_comm = 5000
        handlers = [
            (r'/', MainHandler),
            (r'/tucao', TucaoHandler),
            (r'/tucao/(\d+)$', TucaoHandler),
            (r'/tucao/comm', TucaoCommHandler),
            (r'/tucao/comm/(\d+)$', TucaoCommHandler),
            (r'/blacklist', BlackListHandler),
        ]
        settings = dict(
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if ( iInBlackList(self) ):
            return 
        self.write("hello")

    def post(self):
        if ( isInBlackList(self) ):
            return 
        # self.set_header("Content-Type", "application/json")
        raw_body = str(self.request.body)
        # print raw_body
        jsonDic = json.loads(raw_body)
        # print jsonDic 
        print jsonDic['id']
        self.write("success")

class TucaoHandler(tornado.web.RequestHandler):
    def get(self, nnid):
        if ( isInBlackList(self) ):
            return 
        NewsDatabase.reconnect()
        nid = int(nnid)
        comm = NewsDatabase.query("""SELECT * FROM commTable WHERE id=%r ORDER
                BY level DESC, tolevel""", nid)
        # print comm
        reply = json.dumps(comm, cls=CJsonEncoder)
        # print reply
        self.write(reply)

    def post(self):
        if ( isInBlackList(self) ):
            return 
        print ("In post")
        NewsDatabase.reconnect()

        remote_ip = self.request.remote_ip
        if ( restrict.has_key( remote_ip ) ):
            if ( time.time() - restrict[remote_ip][0] < 5 ):
                self.write("less than 5 second")
                print restrict[remote_ip][0]
                print time.time()
                print "less than 5 second"
                return
            if ( restrict[remote_ip][1] > 1000 ):
                self.write("too much")
                NewsDatabase.execute(u"""INSERT blackList(ip) VALUES(%s)""", remote_ip) 
                blacklist.append(remote_ip)
                print blacklist
                print restrict[remote_ip][1]
                print "too much"
                return 
        else:
            restrict[remote_ip] = [time.time(), 0]
        
        raw_body = str(self.request.body)
        # print raw_body

        jsonDic = json.loads(raw_body)
        # print jsonDic
        
        nid = int(jsonDic['id'])
        LEVEL = NewsDatabase.query("""SELECT COUNT(*) AS level FROM commTable WHERE id=%r""", nid)
        level = int(LEVEL[0]['level'])
        # print level

        level += 1
        tolevel = 0
        content = jsonDic['content']
        print content
            
        NewsDatabase.execute(u"""INSERT commTable(id, level, tolevel,
                    content) VALUES(%r, %r, %r, %s)""", nid, level, tolevel,
                    content)

        restrict[remote_ip][1] += 1
        print ("Insert comm")
        print restrict[remote_ip][1]
        
        self.write("success")

def get_page_data(nid):
    url = "/id/%d" % nid
    try:
        httpClient = httplib.HTTPConnection(ali_page, 8000, timeout=30)
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

get_page_data_cache = Memoize(get_page_data)

class TucaoCommHandler(tornado.web.RequestHandler):
    def get(self, nnid):
        if ( isInBlackList(self) ):
            return 
        NewsDatabase.reconnect()
        nid = int(nnid)

        raw_news = get_page_data_cache(nid)
        jsonDic = json.loads(raw_news)
        # print jsonDic['clean_body'] 
        
        comm = NewsDatabase.query("""SELECT * FROM commTable WHERE id=%r ORDER
                BY level DESC, tolevel""", nid)
        # print comm
        self.render('TucaoComm.html', title=jsonDic['title'],\
                body=jsonDic['body'], publisher=jsonDic['publisher'],\
                date=jsonDic['date'], commList=comm, nid=nid)

    def post(self):
        if ( isInBlackList(self) ):
            return 
        self.application.max_comm -=1
        if self.application.max_comm <= 0:
            return
        print ("In post")
        NewsDatabase.reconnect()

        remote_ip = self.request.remote_ip
        if ( restrict.has_key( remote_ip ) ):
            if ( time.time() - restrict[remote_ip][0] < 5 ):
                self.write("less than 5 second")
                print restrict[remote_ip][0]
                print time.time()
                print "less than 5 second"
                return
            if ( restrict[remote_ip][1] > 1000 ):
                self.write("too much")
                NewsDatabase.execute(u"""INSERT blackList(ip) VALUES(%s)""", remote_ip) 
                blacklist.append(remote_ip)
                print blacklist
                print restrict[remote_ip][1]
                print "too much"
                return 
        else:
            restrict[remote_ip] = [time.time(), 0]
        raw_body = str(self.request.body)
        print self.request.remote_ip
        print raw_body

        nid = int(self.get_argument('id'))
        content = self.get_argument('content')
        r = r"^@(\d+):([\s\S]+)$"
        LEVEL = re.findall(r, content)
        if LEVEL:
            level = int(LEVEL[0][0])
            TOLEVEL = NewsDatabase.query("""SELECT COUNT(*) AS tolevel FROM commTable WHERE id=%r AND level=%r""", nid, level) 
            if ( int(TOLEVEL[0]['tolevel']) == 0 ):
                print "no such level"
                self.write("no such level")
                return 
            else:
                tolevel = int(TOLEVEL[0]['tolevel']) + 1
                content = LEVEL[0][1]
        else:
            tolevel = 1
            LEVEL = NewsDatabase.query("""SELECT COUNT(DISTINCT(level)) AS level FROM commTable WHERE id=%r""", nid)
            level = int(LEVEL[0]['level']) + 1

        # print content
            
        NewsDatabase.execute(u"""INSERT commTable(id, level, tolevel,
                    content) VALUES(%r, %r, %r, %s)""", nid, level, tolevel,
                    content)

        restrict[remote_ip][1] += 1
        print ("Insert comm")
        print restrict[remote_ip][1]
        self.redirect("/tucao/comm/%d" % nid)

class BlackListHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("U are in blacklist!<br>联系人人网“学生周知”")

def main():
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

