#!/usr/bin/env python

import time
import sys
import logging
import os

logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level =
        logging.DEBUG)

while True:
    logging.debug('this is a message')
    time.sleep(1)

