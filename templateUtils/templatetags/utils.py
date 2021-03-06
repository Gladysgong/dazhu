# coding: utf-8
'''
Created on Mar 21, 2016

@author: yzh
'''

import tools
from django import template
register = template.Library()
import urllib
@register.filter
def removeHtml(value,length):
    value = value.replace("<br/>","#br/#")\
    .replace("\r\n","\n")\
    .replace("\n","#br/#")\
    .replace("</p>","#br/#")\
    .replace("&nbsp;",'#nbsp;')
    value = tools.webTools.RemoveHttpStr(value)
    value = tools.webTools.CutStringSafe(value,int(length))
    value = value.replace("#br/#","<br/>").replace("#nbsp;","&nbsp;")
    while True:
        if '<br/><br/>' in value:
            value = value.replace('<br/><br/>','<br/>')
        else:
            break
    return value

@register.filter
def quote(value):
    try:
        return urllib.quote(value.encode('utf-8'))
    except:
        tools.webTools.debug("quote fail",value)
        return ""

@register.filter
def cutSafe(value, length):
    data = tools.webTools.CutStringSafe(value, int(length))
    # tools.webTools.debug("cutSafe", data)
    return data

@register.filter
def removeTags(value, tags):
    tags = tags.split(",")
    data = tools.webTools.RemoveSpecHtmlTag(value, tags)
    # tools.webTools.debug("cutSafe", data)
    return data

@register.filter
def getPic(value):
    picList = tools.webTools.getHtmlPics(value)
    if len(picList) == 0:
        return "/static/images/img1.jpg"
    else:
        for item in picList:
            if "/fileTypeImages/" not in item:
                return item
        return "/static/images/img1.jpg"


class GetUserNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        try:
            user = context['user']
            tools.webTools.debug("user is ", user.get_full_name())
            return user.get_full_name()
        except Exception as error:
            tools.webTools.debug("error is ")
            tools.webTools.debug(error)
            return u""

def GetUser(parser, token):
    return GetUserNode()
register.tag('get_user', GetUser)


class GetUserEmailNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        try:
            user = context['user']
            tools.webTools.debug("user is ",user.get_full_name())
            return user.email
        except Exception as error:
            tools.webTools.debug("error is ")
            tools.webTools.debug(error)
            return u""

def get_user_email(parser, token):
    return GetUserEmailNode()

register.tag('get_user_email', get_user_email)


class GetTitleNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        try:
            title = context['title']
            return title
        except Exception as error:
            tools.webTools.debug("error is ",error)
            return u""

def GetTitle(parser, token):
    return GetTitleNode()

register.tag('get_title', GetTitle)


class GetDespNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        try:
            desp = context['description']
            desp = tools.webTools.RemoveHttpStr(desp)
            desp = tools.webTools.CutStringSafe(desp,150)
            return desp
        except Exception as error:
            return u"这是大猪和大兔子的个人网站，用来做笔记。大猪是一个程序员。喜欢python，go，c#和大兔子。"

def get_description(parser, token):
    return GetDespNode()

register.tag('get_description', get_description)

import datetime
def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

register.simple_tag(get_time)

from msg.models import get_msg
def get_msg_count():
    return len(get_msg())
register.simple_tag(get_msg_count)
