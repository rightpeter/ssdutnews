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

# mail_host = "smtp.163.com"
# mail_user = "rightpeter"
# mail_pass = "15961374343"
# mail_postfix = "163.com"
mail_host = "smtp.163.com"
mail_user = "pedestal_peter"
mail_pass = "15961374343"
mail_postfix = "163.com"

def send_mail(to_list, sub, context):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(context, 'html', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        send_smtp = smtplib.SMTP()
        send_smtp.connect(mail_host)
        print mail_user
        print mail_pass
        send_smtp.login(mail_user, mail_pass)
        send_smtp.sendmail(me, to_list, msg.as_string())
        send_smtp.close()
        print msg
        return True
    except e:
        print(str(e))
        return False

if __name__=="__main__":
    user_addr = raw_input('User Email: ')
    NewsDatabase.execute("""INSERT emailTable(name, address) VALUES(%s, %s)""",
            'test', user_addr)
    subject = '学生周知邮件通知-Pedestal主页君'
    context = 'Pedestal主页君已将您加入测试列表，有任何BUG欢迎反馈' 
    if (True == send_mail([user_addr], subject, context)):
        print "success"
    else:
        print "fail"
