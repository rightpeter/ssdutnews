#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import re
import time
import json
import tornado.web
import tornado.ioloop
import tornado.httpclient
# tornado 3.x nolonger have this. use torndb
#import tornado.database
import torndb
import math
import httplib
import json
import pickle
import datetime
import threading
from config import *
from db import *
from myTools import *
import uimodules

reload(sys)
sys.setdefaultencoding('utf-8')

from tornado.options import define, options

# define("port", default=80, help="run on the given port", type=int)
define("port", default=2357, help="run on the given port", type=int)

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
        #self.max_comm = 5000
        handlers = [
            (r'/', MainHandler),
            # API -----------------
            (r'/api', APIHandler),
            (r'/api/follow', FllwHandler),
            (r'/api/subscribed', SbscHandler),
            (r'/api/check', CheckHandler),
            (r'/api/cgpasswd', ChangePasswdHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/signup', SignupHandler),
            (r'/id/(\d+)$', NewsHandler),
            (r'/renrencallback', RenrenCallBackHandler),
            (r'/renrengettoken', RenrenGetTokenHandler),
            
            (r'/404', Error404Handler),
            (r'/index', TucaoIndexHandler),
            (r'/about', AboutHandler),
            #(r'/tucao', TucaoHandler),
            #(r'/tucao/(\d+)$', TucaoHandler),
            (r'/news', TucaoCommHandler),
            (r'/news/(\d+)$', TucaoCommHandler),
            (r'/home/(\d+)$', HomeHandler),
            #(r'/blacklist', BlackListHandler),
        ]
        settings = { 
                "template_path": os.path.join(os.path.dirname(__file__), "templates"),
                "static_path": os.path.join(os.path.dirname(__file__), "static"),
                "ui_modules": uimodules,
                "cookie_secret": "#De1rFq@oyW^!kc3MI@74LY*^TPG6J8fkiG@xidDBF",
                "login_url": "/login",
                "xsrf_cookies": True,
        }
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("name")

class MainHandler(BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        slides = [{}, {}, {}]
        slides[0]['image'] = "pedestal.jpg"
        slides[0]['name'] = "周知吐槽"
        slides[0]['descript'] = "尽情地为自己呐喊"
        slides[0]['href'] = "/about"
        slides[0]['button'] = "关于我们"

        slides[1]['image'] = "tucao_slide.jpg"
        slides[1]['name'] = "周知吐槽"
        slides[1]['descript'] = "尽情地为自己呐喊"
        slides[1]['href'] = "/index"
        slides[1]['button'] = "开始吐槽"

        slides[2]['image'] = "pedestal_welcome.jpg"
        slides[2]['name'] = "这只是一个大标题"
        slides[2]['descript'] = "用来测试轮播插件这个复杂的东西"
        slides[2]['href'] = "/signup"
        slides[2]['button'] = "加入我们"
       
        user = myTools.get_current_user(self)
        self.set_cookie("url", self.request.uri)
        url = self.request.uri
        self.render("index.html", slides=slides, user=user, url=url)
        
class APIHandler(BaseHandler):
    def get(self):
        jsonDict = {}
        api_type = self.get_argument('type')
        value = self.get_argument('value')
        call_back = self.get_argument('callback')
        jsonDict['value'] = value
        if api_type == 'EMAIL':
            jsonDict['type'] = "EMAIL"
            if myTools.is_email_exist(value):
                jsonDict['status'] = "UNIQUE"
            else:
                jsonDict['status'] = "REPEATED"

        if api_type == 'NAME':
            jsonDict['type'] = "NAME"
            if myTools.is_name_exist(value): 
                jsonDict['status'] = "UNIQUE"
            else:
                jsonDict['status'] = "REPEATED"

        encoded_json = json.dumps(jsonDict)
        call_back_json = '%s(%s)' % (call_back, encoded_json)
        self.write(call_back_json)

class Error404Handler(BaseHandler):
    def get(self):
        user = myTools.get_current_user(self)
        url = self.request.uri
        self.render('404.html', user=user, url=url)

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, home_id):
        home_name = myTools.get_name_by_id(home_id)
        user = myTools.get_current_user(self)
        url = self.request.uri
        self.set_cookie('url', url)
        self.render('home.html', home_name=home_name, user=user, url=url)

class AboutHandler(BaseHandler):
    def get(self):
        user = myTools.get_current_user(self) 
        url = self.request.uri
        self.set_cookie('url', url)
        self.render('about.html', user=user, url=url)

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        if ( myTools.is_a_attack(self) ):
            return 
       
        self.set_header("Content-Type", "text/plain")

        email = self.get_argument('email')
        password = self.get_argument('password')

        if myTools.login(email, password):
            name = myTools.get_name_by_email(email)
            if myTools.is_user_checked(email):
                self.set_secure_cookie('name', name)
                url = self.get_cookie('url')
                self.redirect(url)
            else:
                self.set_secure_cookie('guest', name)
                self.redirect('/signup')
        else:
            self.write("Login Failed!")
            
class LogoutHandler(BaseHandler):
    def get(self):
        url = self.get_cookie('url')
        self.clear_cookie('name')
        self.clear_cookie('guest')
        self.redirect(url)

class SignupHandler(BaseHandler):
    def get(self):
        user = myTools.get_current_user(self)
        #if self.get_secure_cookie('guest'):
        #    user['name'] = self.get_secure_cookie('guest')
        #    user['id'] = myTools.get_id_by_name(user['name'])
        #    guest = self.get_secure_cookie('guest')
        #elif self.get_current_user():
        #    user['name'] = self.get_current_user()
        #    user['id'] = myTools.get_id_by_name(user['name'])
        self.render('signup.html', user=user, url='/')

    def post(self):
        if ( myTools.is_a_attack(self) ):
            return 
      
        user = {}
        user['email'] = self.get_argument('email')
        user['name'] = self.get_argument('name')
        user['password'] = self.get_argument('password')
        re_password = self.get_argument('repassword')
        try:
            if self.get_argument('is_subscribed'):
                user['subscribed'] = 1
        except:
            user['subscribed'] = 0

        if user['password'] == re_password:
            if myTools.is_email_exist(user['email']) and myTools.is_name_exist(user['name']):
                if myTools.insert_a_user(user):
                    myTools.send_check_email(user['email'])
                    if myTools.login(user['email'], user['password']):
                        self.set_secure_cookie('guest', user['name'])
                        self.redirect('/signup')
        self.write('Signup Failed!')

class FllwHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        pid = int(self.get_argument('pid'))
        fname = self.get_current_user()
        if myTools.follow(pid, fname):
            self.write("Succeed Following!")
        else:
            self.write("Followed Error!")
        
class SbscHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        subscribed = int(self.get_argument('subscribed'))
        name = self.get_current_user()
        if myTools.subscribe(name, subscribed):
            self.write("Succeed Subscribing!")
        else:
            self.write("Subscribed Error!")

class CheckHandler(BaseHandler):
    def get(self):
        try:
            code = self.get_argument('code')
            email = self.get_argument('email') 
            name = myTools.get_name_by_email(email)
            if myTools.check_email(email, code):
                self.set_secure_cookie('name', name)
                self.redirect('/signup')
            else:
                self.write('Checked Failed!')
        except: 
            name = self.get_argument('name')
            email = myTools.get_email_by_name(name)
            myTools.send_check_email(email)


class ChangePasswdHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = self.get_current_user()
        email = myTools.get_email_by_name(name)
        passwd = self.get_argument('passwd')
        new_passwd = self.get_argument('new_passwd')
        re_new_passwd = self.get_argument('re_new_passwd')
        
        if myTools.change_passwd(email, passwd, new_passwd, re_new_passwd):
            self.write('Passwd Changed!')
        else:
            self.write('Changing Passwd Fail!')

    @tornado.web.authenticated
    def get(self):
        name = self.get_current_user()
        email = myTools.get_email_by_name(name)
        passwd = self.get_argument('passwd')
        new_passwd = self.get_argument('new_passwd')
        re_new_passwd = self.get_argument('re_new_passwd')
        
        if myTools.change_passwd(email, passwd, new_passwd, re_new_passwd):
            self.write('Passwd Changed!')
        else:
            self.write('Changing Passwd Fail!')

class RenrenCallBackHandler(BaseHandler):
    def get(self):
        code = self.get_argument('code')
        print code 
        url = "https://graph.renren.com/oauth/token" +\
                    "?grant_type=authorization_code" + \
                    "&client_id=a5cd69597ccf4b369057f919928cbfce"+\
                    "&redirect_uri=http://tucao.pedestal.cn/renrencallback"+\
                    "&client_secret=ce6f56e203524cfc9c3bb61523009b6e"+\
                    "&code=" + code
        #print url
        http_client = tornado.httpclient.HTTPClient()
        response = http_client.fetch(url)
        print response.body
        jsonDic = json.loads(response.body)
        print jsonDic['access_token']
        http_client.close()

class RenrenGetTokenHandler(BaseHandler):
    def get(self):
        token = self.get_argument('code')
        print token

class NewsHandler(BaseHandler):
    def get(self, nnid):
        nid = int(nnid)
        news = myTools.get_a_news(nid)
        news['id'] = news['nid']
        news.pop('nid')
        news_json = json.dumps(news)
        self.write(news_json)

class TucaoIndexHandler(BaseHandler):
    def get(self):
        try:
            page = int(self.get_argument('page'))
        except:
            page = 1 

        page_size = 20
        latest_id = myTools.get_latest_news_id()
        oldest_id = myTools.get_oldest_news_id()

        total_pages = (myTools.get_total_news_num()-1) / page_size + 1
        if page>total_pages or page<1:
            page = 1
        max_id = latest_id - (page-1)*page_size
        if page == total_pages:
            min_id = myTools.get_oldest_news_id()
        else:
            min_id = max_id - page_size + 1
        newsList = myTools.get_news_list(min_id, max_id)
        visible_pages = 10

        user = myTools.get_current_user(self)
        self.set_cookie("url", self.request.uri)
        url = self.request.uri
        self.render("tucao_index.html", newsList=newsList, total_pages=total_pages, current_page=page,
                visible_pages=visible_pages, user=user, url=url)

class TucaoHandler(BaseHandler):
    def get(self, nnid):
        if ( myTools.is_a_attack(self) ):
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
        if ( myTools.is_a_attack(self) ):
            return 

        print ("In post")
        NewsDatabase.reconnect()

        remote_ip = self.request.remote_ip
        if ( restrict.has_key(remote_ip) ):
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
        
        print self.request
        raw_body = str(self.request.body)
        # print raw_body

        jsonDic = json.loads(raw_body)
        # print jsonDic
        
        nid = int(jsonDic['id'])
        content = jsonDic['content']
       
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
            
        if (content == 'water'):
                NewsDatabase.execute(u"""INSERT blackList(ip) VALUES(%s)""", remote_ip) 
                blacklist.append(remote_ip)
                print blacklist
                myTools.is_a_attack(self)

        NewsDatabase.execute(u"""INSERT commTable(id, level, tolevel,
                    content) VALUES(%r, %r, %r, %s)""", nid, level, tolevel,
                    content)

        restrict[remote_ip][1] += 1
        print ("Insert comm")
        print restrict[remote_ip][1]
        
        self.write("success")

class TucaoCommHandler(BaseHandler):
    def get(self, nnid):
        NewsDatabase.reconnect()
        nid = int(nnid)

        news = myTools.get_a_news(nid)
        
        news['body'] = news['body'].replace('href="/Attachments/file', 'href="http://ssdut.dlut.edu.cn/Attachments/file')
        comm = NewsDatabase.query("""SELECT * FROM commTable WHERE id=%r ORDER
                BY level DESC, tolevel""", nid)
        latest = myTools.get_latest_news_id()
        total = myTools.get_total_news_num()
        # print comm

        user = myTools.get_current_user(self)
        self.set_cookie("url", self.request.uri)
        url = self.request.uri
        self.render('TucaoComm.html', title=news['title'],\
                body=news['body'], publisher=news['publisher'],\
                date=news['date'], clean_body=news['clean_body'],\
                commList=comm, nid=nid, latest=latest, total=total, 
                user=user, url=url)

    def post(self):
        if ( myTools.is_a_attack(self) ):
            self.redirect("/blacklist")
            return 

        print ("In post")
        NewsDatabase.reconnect()

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
            
        if (content == 'water'):
                NewsDatabase.execute(u"""INSERT blackList(ip) VALUES(%s)""", remote_ip) 
                ENV_DIC['blacklist'].append(remote_ip)
                myTools.is_a_attack(self)

        NewsDatabase.execute(u"""INSERT commTable(id, level, tolevel,
                    content) VALUES(%r, %r, %r, %s)""", nid, level, tolevel,
                    content)

        myTools.post_once(self)
        self.redirect("/news/%d" % nid)

class BlackListHandler(BaseHandler):
    def get(self):
        self.write("U are in blacklist!<br>联系人人网“学生周知”")

def main():
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

def init():
    ENV_DICT['latest'] = myTools.get_latest_news_id()
    ENV_DICT['total'] = myTools.get_total_news_num()
    print ENV_DICT['total']

    BLACKLIST = NewsDatabase.query("""SELECT * FROM blackList""")
    ENV_DICT['blacklist'] = []
    ENV_DICT['restrict'] = {}
    for blackdict in BLACKLIST:
        ENV_DICT['blacklist'].append(blackdict['ip'])
    print ENV_DICT['blacklist']


if __name__ == "__main__":
    init()
    main()


