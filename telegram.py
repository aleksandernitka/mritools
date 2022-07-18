#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
args = argparse.ArgumentParser(description='Send telegram messages with bot and chat ID.')
args.add_argument('-m', '--message', help='Message to send', required=False, default='Test message')
args = args.parse_args()

def sendtel(msg):

    import requests

    BOT_API = '1964277764:AAFColinXwUeo4NaMQA1beFm5va9jZY9GJQ'
    CHAT_ID = '1228696749'


    r = requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(BOT_API, CHAT_ID, msg))

sendtel(args.message)