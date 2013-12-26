#!/usr/bin/env python
#encoding=utf-8

import db
from db import *
import models
import tornado.database


def installCommentTable():
    NewsDatabase.reconnect()
    NewsDatabase.execute("""CREATE TABLE `commTable`(
            cid INT NOT NULL AUTO_INCREMENT, 
            id int, 
            level int, 
            tolevel int, 
            content text, 
            posttime TIMESTAMP, 
            PRIMARY KEY(cid)) 
    """)

    
if __name__ == "__main__":
    # db.init_db()
    # models.kv.db_inited = ''
    installCommentTable()
