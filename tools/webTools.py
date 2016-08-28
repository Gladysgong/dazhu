'''
Created on Mar 12, 2016

@author: yzh
'''
# coding: utf-8

import os
import base64
import re
import HTMLParser
import dazhu.settings as settings
import random
import time

def GetRndStr():   
    rndByte = os.urandom(6)
    b64Str = base64.urlsafe_b64encode(rndByte)
    return b64Str

def GetMap(input):
    return chr(input + 97)
 
def GetTimeCode(input=0):    
    '''
    0 - a
    1 - b
    25 - z
    26 - aa
    '''
    if input == 0:
        input = int(time.time())*100 + random.randint(1, 99)
 
    result = ""
    while True:
        quotient = input // 26
        remainder = input - quotient * 26
        input = quotient
        result = GetMap(remainder) + result
        if quotient < 26:
            if quotient == 0:
                break
            result = GetMap(quotient-1) + result
            break
    return result



def RemoveHttpStr(val):
    return re.sub('<[^>]*>|&[^;]*;', '', val)

def CutStringSafe(strIn, length):
    if length > len(strIn):
        return strIn
    else:
        return strIn[0:length]
    
def getHtmlPics(strHtml):
    class parseLinks(HTMLParser.HTMLParser):
        def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.links = []
            
        def handle_starttag(self, tag, attrs):
            if tag == 'img':        
                for name, value in attrs:       
                    if name == 'src':
                        self.links.append(value)                        
    lParser = parseLinks()
    lParser.feed(strHtml)
    return lParser.links
            

def readFile(filePath):
    data = None
    try:            
        with open(filePath, 'r') as f:  
            return f.read()
    except Exception as error:
        #print(error)
        pass
    return data

def ExtractData(regex, content):
    r = None
    p = re.compile(regex)
    m = p.findall(content)
    if m:
        r = m
    return r

isdebug = settings.DEBUG
def debug(*obj):
    if isdebug:
        print(obj)
