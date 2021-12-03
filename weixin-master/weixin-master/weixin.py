# coding: utf-8
import hashlib
import web
import time
import os
import urllib2,urllib
import json
import re
import string
import lxml
from lxml import etree
import pylibmc
import random
import weather
import joke
import trans

'''
小黄鸡功能
'''
def xiaohuangji(ask):
    ask = ask.encode('utf-8')
    enask = urllib2.quote(ask)
    baseurl = r'http://www.simsimi.com/func/req?msg='
    url = baseurl + enask + '&lc=ch&ft=0.0'
    resp = urllib2.urlopen(url)
    reson = json.loads(resp.read())
    return reson

class WeixinInterface:
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)
    
    def GET(self):
        data=web.input()
        signature = data.signature
        timestamp = data.timestamp
        nonce = data.nonce
        echostr = data.echostr
        #自己的token
        token = "kaiyao"
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
        
    def POST(self):
        #从获取的xml构造xml dom树
        str_xml = web.data()	#获取post来的数据
        xml = etree.fromstring(str_xml)	#进行XML解析
        #提取信息
        #content = xml.find("Content").text
        msgtype = xml.find("MsgType").text
        fromUser = xml.find("FromUserName").text
        toUser = xml.find("ToUserName").text
        mc = pylibmc.Client() #初始化一个memcache实例用来保存用户的操作
        if msgtype == "event":
            mscontent = xml.find("Event").text
            if mscontent == "subscribe":
                replyText = u'欢迎关注kaiyao机器人！\n------------------------输入help获取操作指南'
                return self.render.reply_text(fromUser,toUser,int(time.time()),replyText)
            if mscontent == "unsubscribe":
                replyText = u'欢迎您以后再来！！'
                return self.render.reply_text(fromUser,toUser,int(time.time()),replyText)
        
        if msgtype == 'text':
            content = xml.find("Content").text
            if content.lower() == 'bye':
                mc.delete(fromUser+'_xhj')
                return self.render.reply_text(fromUser,toUser,int(time.time()),u'从小黄鸡模式中跳出\n------------------------ \n输入help获取操作指南')
            if content.lower() == 'xhj':
                mc.set(fromUser+'_xhj','xhj')
                return self.render.reply_text(fromUser,toUser,int(time.time()),u'进入小黄鸡模式，聊天吧\n输入bye跳出小黄鸡模式')
            
            #读取memcache中的缓存数据
            mcxhj = mc.get(fromUser+'_xhj')
            
            if mcxhj == 'xhj':
                res = xiaohuangji(content)
                reply_text = res['response']
                if u'微信' in reply_text:
                    reply_text = u"小黄鸡脑袋出问题了，请换个问题吧~"
                return self.render.reply_text(fromUser,toUser,int(time.time()),reply_text)
            
            if content.lower() == 'joke':
                joke_info = joke.getjoke()
                return self.render.reply_text(fromUser,toUser,int(time.time()),joke_info)
            
            if content == 'help':
                replyText = u'''------------------------\n直接输入中英文返回其对应英中翻译\n------------------------\n输入xhj进入小黄鸡模式\n------------------------\n输入'weather+地名'进行天气查询\n------------------------\n输入joke获取一段笑话\n------------------------\n其余功能开发中......'''
                return self.render.reply_text(fromUser,toUser,int(time.time()),replyText)
            if content.startswith('weather'):
                city = content[8:]
                city = city.encode('utf-8')
                weather_info = weather.getweather(city)
                return self.render.reply_text(fromUser,toUser,int(time.time()),weather_info)
            elif type(content).__name__ == "unicode":
                content = content.encode('utf-8')
            Nword = trans.youdao(content)
            return self.render.reply_text(fromUser,toUser,int(time.time()),Nword)
