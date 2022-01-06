from bs4 import BeautifulSoup
from dearpygui.core import *
from dearpygui.simple import *
import requests
import time
import re
import execjs
from requests import utils

# todo 报平安
def hand_timestamp():
    return str(int(time.time() * 1000))


url_login = 'http://ids.njust.edu.cn/authserver/login'
url_zh = 'http://ehall.njust.edu.cn/new/index.html'
url_getdata = 'http://ehall.njust.edu.cn/jsonp/personalRemind/getViewDataDetail.do'
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56',
    'Upgrade-Insecure-Requests': '1'
}
para1 = {
    'service': 'http://ehall.njust.edu.cn/login?service=http://ehall.njust.edu.cn/new/index.html'
}

para_card = {
    'wid': '1d5575da29d04c928c81089db3736f94',
    'mailAccount': '更新日期【clrq】',
    '_': hand_timestamp()
}
para_netyue = {
    'wid': 'b932268f062c4e2aaf601b9d678d2135',
    'mailAccount': '网络认证计费余额',
    '_': hand_timestamp()
}
para_book = {
    'wid': '775ec39aa4ff44f882ad2ae7edcb9957',
    'mailAccount': '在借图书【zs】册，将要到期【yh】册',
    '_': hand_timestamp()
}


class zhlg:
    def __init__(self, username, password, cookie):
        self.islogin = False
        self.s = requests.session()
        self.s.headers = header
        self.info = []
        if cookie is None:
            re1 = self.s.get(url_login, params=para1)
            text = self.hand_text(re1)
            soup = BeautifulSoup(text, 'html.parser')
            data_list = []  # 登录 寻找完毕
            a1 = soup.find('input', id='pwdDefaultEncryptSalt')
            a2 = soup.findAll(name='input')
            data_list.append(self.hand_value(str(a1)))
            for x in a2:
                try:
                    if x['name'] == 'lt':
                        data_list.append(self.hand_value(str(x)))
                        continue
                    if x['name'] == 'execution':
                        data_list.append(self.hand_value(str(x)))
                        break
                except:
                    pass
            fun = self.encode_js()
            data_list[0] = fun.call('myencode', password, data_list[0])
            data2 = {
                'username': username,
                'password': data_list[0],
                'lt': data_list[1],
                'dllt': 'userNamePasswordLogin',
                'execution': data_list[2],
                '_eventId': 'submit',
                'rmShown': '1'
            }
            # 第一个login完毕
            self.s.post(url_login, params=para1, data=data2)
        else:
            self.s.cookies = utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)
        re_card = self.s.get(url_getdata, headers=header, params=para_card)
        if type(re_card.json()) is list:
            self.islogin = True
        else:
            return
        re_netyue = self.s.get(url_getdata, headers=header, params=para_netyue)
        re_book = self.s.get(url_getdata, headers=header, params=para_book)
        self.handle_info(re_card)
        self.handle_info(re_netyue)
        self.handle_info(re_book)

    def hand_text(self, r):
        return r.text.encode('gbk', 'ignore').decode('gbk')

    def hand_value(self, t):
        r = re.findall("value=\".*\"", t)
        if len(r) > 0:
            m = re.findall("value=\".*\"", t)[0]
            m = m.replace("value=", '')
            m = m.replace("\"", '')
            return m
        else:
            return ''

    def encode_js(self):
        f = open('resource\\need.js', 'r', encoding='utf-8')
        ff = f.read()
        f.close()
        return execjs.compile(ff)

    def handle_info(self, result, ):
        json = result.json()
        self.info.append([json[0]["title"], json[0]["subTitle"], json[0]["imptInfo"]])

    def paint(self):
        with tab('tab4', label='智慧理工', parent='bar'):
            add_table('个人信息', ["title", "subTitle", "information"], width=1380, height=450)
            for x in self.info:
                add_row('个人信息', x)
