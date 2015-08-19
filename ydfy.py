#!/usr/bin/env python3
# coding: utf-8
'''
Youdao Fanyi
Author: Cheng Rui

# Youdao Fanyi Api:
http://fanyi.youdao.com/openapi.do?keyfrom={0}&key={1}&type=data&doctype=json&version=1.1&q={query}

#option 1
keyfrom=wadexing
key=89413557

#option 2
keyfrom=YouDaoCV
key=659600698

#option 3
keyfrom = 'atupal-site'
key = '401682907'
'''
import json, os
from urllib import request as urq
from urllib.parse import quote
from argparse import ArgumentParser

KEYFROM = 'wadexing'
API_KEY = '89413557'
URL = "http://fanyi.youdao.com/openapi.do?keyfrom={0}&key={1}&type=data&doctype=json&version=1.1&q={word}"

def _json(urlopen):
    def wrapper(*args, **kwargs):
        ret = json.loads(urlopen(*args, **kwargs).read().decode('utf-8'))
        return ret
    return wrapper

urlopen_json = _json(urq.urlopen)

def ydfy_history(path=None):
    if not path:
        home = os.environ['HOME']
        path = os.path.join(home, '.ydfy_history')
    else:
        path = os.path.abspath(path)
    return path

def content(fn):
    with open(fn, 'r') as f:
        words = f.read()
    return words

def is_chinese(char):
    if ord(char) >= ord('\u4E00') and ord(char) <= ord('\u9FA5'):
        return True
    else:
        return False

def lookup_word(word):
    word = quote(word)
    url = URL.format(KEYFROM, API_KEY, word=word)
    try:
        result = urlopen_json(url)
    except IOError:
        print("Network is unavailable")
        return None
    return result

def print_web_info(web):
    print("""
    网络释义:
    ==============""")
    for item in web:
        print('   ', item['key'], ':')
        print('     ', '\n      '.join(item['value']))

def print_explains(explains):
    print('    explains:', end='\n    ')
    print('\n    '.join(explains))

def print_translation(translation):
    '''result['translation'], type is list'''
    print('''
    翻译:
    ================''')
    if translation:
        print('    ', end='')
        print('\n    '.join(translation))

def print_basic(basic):
    """result['basic'], {'uk-phonetic': "", 'explains': [], 'us-phonetic': '', 'phonetic': ""}"""
    # meishiyingmibao
    print('''
    基本释义:
    ================''')
    if 'us-phonetic' in basic:
        print('    美式读音: [' + basic['us-phonetic'] + ']', end='    ')
    if 'uk-phonetic' in basic:
        print('\n    英式读音: [' + basic['uk-phonetic'] + ']')
    print_explains(basic['explains'])


def print_result(res, t, b, w, word=None):
    if res['errorCode'] != 0:
        print('errorCode:', res['errorCode'])
        return None
    if t:
        print_translation(res['translation'])
    if b and 'basic' in res:
        print_basic(res['basic'])
    if w and 'web' in res:
        print_web_info(res['web'])
    with open(ydfy_history(), 'a') as yh:
        yh.write(word+'\n')


def translate(word, t = True, b = True, w = True):
    res = lookup_word(word)
    print_result(res, t, b, w, word)

def main():
    parser = ArgumentParser(description="Youdao Console Version")
    parser.add_argument('-t', '--translate',
                        action='store_true',
                        default=False,
                        help="print translate content !")
    parser.add_argument('-b', '--basic',
                        action="store_true",
                        default=False,
                        help="print basic content !")
    parser.add_argument('-w', '--web',
                        action="store_true",
                        default=False,
                        help="print web content !")
    parser.add_argument('-f', '--file',
                        help="translate a file content")
    parser.add_argument('words', nargs='*', help=
                        "words to lookup, or quoted sentences to translate.")

    options = parser.parse_args()
    if options.words:
        word = ' '.join(options.words)
        res = lookup_word(word)
        if not (options.translate or options.basic or options.web):
            options.basic = True
        print_result(res, options.translate, options.basic, options.web, word)
    if options.file:
        word = content(options.file)
        res = lookup_word(word)
        print_result(res, True, options.basic, options.web, word)

    if not any( getattr(options, '__dict__').values() ):
        while True:
            print('有道翻译>>', end=' ')
            try:
                word = input()
                word = word.strip()
                if not word:
                    continue
                if word in ["quit", "exit", 'q']:
                    return 1
            except EOFError:
                print()
                return 1
            res = lookup_word(word)
            if 'basic' in res and res['basic']:
                options.translate = False
                options.basic = True
                options.web = False
            else :
                options.translate = True
                options.basic = False
                options.web = False

            print_result(res, options.translate, options.basic, options.web, word)

if __name__ == '__main__':
    main()
