#!/usr/bin/env python
#encoding: utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import tornado.database
import threading
import httplib
import sys
import os
import time
import json

ali_page = "115.28.2.165"

mailto_list=['rightpeter@163.com']

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
        send_smtp.login(mail_user, mail_pass)
        send_smtp.sendmail(me, to_list, msg.as_string())
        send_smtp.close()
        return True
    except (Exception, e):
        print(str(e))
        return False

if __name__=='__main__':
    subject = "test" 
    
    context = "test"
    # context = jsonDic['clean_body']
    if (True == send_mail(['857166634@qq.com'], subject, context)):
        print "success" 
    else:
        print "fail"

    # if (True == send_mail(mailto_list, "subject", "context")):
    #     print "success"
    # else:
    #     print "failed"
