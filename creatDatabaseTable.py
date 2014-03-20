#!/usr/bin/env python
#encoding=utf-8

import db
from db import *
import tornado.database
import sys


def installCommentTable():
    NewsDatabase.reconnect()
    NewsDatabase.execute("""CREATE TABLE `commTable`(
            `cid` INT NOT NULL AUTO_INCREMENT, 
            `id` int, 
            `level` int, 
            `tolevel` int, 
            `content` text, 
            `posttime` TIMESTAMP, 
            PRIMARY KEY(cid)) 
    """)

    
def installEmailTable():
    NewsDatabase.reconnect()
    NewsDatabase.execute("""CREATE TABLE `emailTable`(
            `id` INT NOT NULL AUTO_INCREMENT,
            `name` VARCHAR(30),
            `address` VARCHAR(50),
            PRIMARY` KEY(id))
    """)

def installNewsTable():
    NewsDatabase.reconnect()
    NewsDatabase.execute("""CREATE TABLE `newsTable`(
            `id` INT NOT NULL AUTO_INCREMENT,
            `nid` INT NOT NULL,
            `publisher` VARCHAR(100),
            `sha1` VARCHAR(100),
            `date` VARCHAR(100),
            `title` text,
            `source` VARCHAR(100),
            `link` VARCHAR(100),
            `source_link` VARCHAR(100),
            `clean_body` text,
            `body text`,
            PRIMARY KEY(id))
            AUTO_INCREMENT=1000000
    """)

def installUsersTable():
    NewsDatabase.reconnect()
    NewsDatabase.execute("""CREATE TABLE `usersTable`(
            `id` INT NOT NULL AUTO_INCREMENT,
            `email` VARCHAR(64) NOT NULL,
            `name` VARCHAR(32) NOT NULL,
            `password` VARCHAR(64) NOT NULL,
            `last_login` timestamp,
            `admin` TINYINT(1) DEFAULT '0',
            `checked` TINYINT(1) DEFAULT '0',
            `subscribed` TINYINT(1) DEFAULT '0',
            PRIMARY KEY(id),
            UNIQUE KEY `name` (`name`),
            UNIQUE KEY `email` (`email`))
            AUTO_INCREMENT=100000
    """)

def installFllwTable():
    NewsDatabase.reconnect()
    NewsDatabase.execute("""CREATE TABLE `fllwTable`(
            `id` INT NOT NULL AUTO_INCREMENT,
            `pid` VARCHAR(64) NOT NULL,
            `fid` VARCHAR(32) NOT NULL,
            `fllw_time` timestamp,
            `checked` TINYINT(1) DEFAULT '0',
            PRIMARY KEY(id))
    """)

def installCheckTable():
    NewsDatabase.reconnect()
    NewsDatabase.execute("""CREATE TABLE `checkTable`(
            `id` INT NOT NULL AUTO_INCREMENT,
            `email` VARCHAR(64) NOT NULL,
            `code` VARCHAR(64) NOT NULL,
            `check_time` timestamp,
            PRIMARY KEY(id))
    """)

if __name__ == "__main__":
    # db.init_db()
    # models.kv.db_inited = ''
    if '-C' in sys.argv:
        installCommentTable()

    if '-E' in sys.argv:
        installEmailTable()

    if '-N' in sys.argv:
        installNewsTable()

    if '-U' in sys.argv:
        installUsersTable()

    if '-F' in sys.argv:
        installFllwTable()
        
    if '-CHECK' in sys.argv:
        installCheckTable()
