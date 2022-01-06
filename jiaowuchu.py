from bs4 import BeautifulSoup
from PIL import Image
from dearpygui.core import *
from dearpygui.simple import *
import os
import pytesseract
import requests
import json
import time
import threading
import re

from requests import utils

# from main import mesbox
from math import sin, cos, radians

pic_fpath = "resource\\picf.png"
url_1 = 'http://202.119.81.113:8080'
url_2 = "http://202.119.81.113:8080/Logon.do?method=logon"
url_3 = "http://202.119.81.112:9080"
heard1 = {

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75 '
}
heard2 = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'http://202.119.81.113:8080',
    'Referer': 'http://202.119.81.113:8080/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54 '
}


def sel_title(x):
    return x.split("title")[1]


def sel_href(x):
    x1 = re.findall(pattern="href=\".*\"", string=str(x))[0]
    x2 = re.findall(pattern="\".*\"", string=str(x1))[0]
    x3 = str(x2).replace("\"", '')
    return x3


def replace_luoma(t: str, type: int):
    if type == 0:
        return t.replace('Ⅵ', '6').replace('V', '5').replace('Ⅳ', '4').replace('Ⅲ', '3').replace('Ⅱ', '2').replace('Ⅰ'
                                                                                                                   ,
                                                                                                                   '1').replace(
            '<br />', ' ').replace('<font color=red>', '').replace('</font>', '')
    if type == 1:
        return t.replace('Ⅳ', '四工').replace('Ⅲ', '三工').replace('II', '二工').replace('I', '一工')
    if type == 2:
        p = re.compile('<br />(.+)')
        pp = p.findall(t)
        if pp:
            return pp[0]
        else:
            return t


class jwc:
    username = None
    keywords = None
    keys = None
    list = {}
    s = None
    rr = None
    islogin = False

    def __init__(self, username, keywords, cookie):
        self.username = username
        self.keywords = keywords
        self.s = requests.session()
        self.ck = None
        if cookie is None:
            for i in range(0, 10):
                r = self.s.get(url_1 + '/verifycode.servlet', headers=heard1)
                f = open(pic_fpath, 'wb')
                f.write(r.content)
                f.close()
                cookie1 = self.s.cookies
                self.keys = jwc.read_text(pic_fpath)
                rr = self.s.post(url=url_2, headers=heard2, data={
                    'USERNAME': self.username,
                    'PASSWORD': self.keywords,
                    'useDogCode': '',
                    'RANDOMCODE': self.keys
                })
                if '学生个人中心' in rr.text.split('title')[1]:
                    set_main_window_size(900, 1200)
                    # delete_item('loginwin', children_only=True)
                    for x in get_item_children('loginwin'):
                        if x != 'menu_bar':
                            delete_item(x)
                    set_window_pos('loginwin', 0, 0)
                    add_tab_bar('bar', parent='loginwin')
                    end()
                    self.rr = rr
                    self.findhref()
                    self.islogin = True
                    if cookie1 != self.s.cookies:
                        self.ck = self.s.cookies.get_dict()
                    break
                else:
                    time.sleep(2)
                    print('正在尝试登录')
        else:
            self.s.cookies = utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)
            rr = self.s.get('http://202.119.81.112:9080/njlgdx/framework/main.jsp', headers=heard2)
            if '学生个人中心' in rr.text.split('title')[1]:
                set_main_window_size(900, 1200)
                delete_item('loginwin', children_only=True)
                set_window_pos('loginwin', 0, 0)
                add_tab_bar('bar', parent='loginwin')
                self.rr = rr
                self.findhref()
                self.islogin = True

    @staticmethod
    def read_text(path) -> object:
        # 验证码图片转字符串
        im = Image.open(path)
        imgry = im.convert('L')
        # 二值化，采用阈值分割算法，threshold为分割点
        threshold = 127
        table = []
        for j in range(256):
            if j < threshold:
                table.append(0)
            else:
                table.append(1)
        out = imgry.point(table, '1')
        # 去除边框
        w, h = out.size
        width = 2
        pixdata = out.load()
        for x in range(width):
            for y in range(0, h):
                pixdata[x, y] = 255
        for x in range(w - width, w):
            for y in range(0, h):
                pixdata[x, y] = 255
        for x in range(0, w):
            for y in range(0, width):
                pixdata[x, y] = 255
        for x in range(0, w):
            for y in range(h - width, h):
                pixdata[x, y] = 255
        # 识别文本
        text = pytesseract.image_to_string(out, lang="eng", config='--psm 6')
        text = re.sub('[\W_]+', '', text)  # 删除其他多余字符
        text = text.replace('i', '1')
        return text

    def findhref(self):
        soup = BeautifulSoup(self.rr.text, 'html.parser')
        soup.find()
        list1 = soup.find(class_='wap')
        list2 = list1.find_all('a')
        for x in list2:
            x3 = sel_href(x)
            self.list[x.get_text().replace("\n", '')] = url_3 + x3

    def findhref_btn(self, rr, name):
        soup = BeautifulSoup(rr.text, 'html.parser')
        list1 = soup.find_all('input', class_='button')
        x1 = re.findall("onclick=\".*\(\)", str(list1))[0]
        x1 = str(x1).replace("onclick=", '')
        x1 = x1.replace("()", '')
        x2 = soup.findAll('script')
        x3 = str(x2[len(x2) - 1])
        x4 = str(re.findall('action = .*\"', x3)[0])
        x4 = x4.replace('action = ', '').replace('\"', '')
        return url_3 + x4

    def paint(self):
        r = self.s.get(url=self.list['选课中心'], headers=heard1)
        r = r.text
        l = re.findall('tmpKc\[3] = \"(.*?)\";', r)
        add_menu('选课类别', parent='menu_bar')
        for x in l:
            add_menu_item(x, callback=lambda a, b: paint(b, self), callback_data=x)
        end()


class kc:

    def __init__(self, s, url, name):
        self.yxkc = []
        self.xkkc = []
        self.kc_name = []
        self.xk_memory = []
        self.num_xk = None
        self.num_yx = None
        self.kc_name = ['课程名', '老师', '时间', '编号', '学分', '代号', '学时', '周次', '地点']
        self.s = s
        self.rr = s.get(url=url, headers=heard1)
        self.url = ''
        t = self.rr.text
        list1 = t.split("var tmpKc = Array();")

        if len(list1) != 1:
            i = 1
            for x in list1:
                if i == 1:
                    i = i + 1
                    continue
                else:
                    i = i + 1
                if name in x:
                    list2 = re.findall('.*;', x)
                    for j in range(6, 9):
                        y = re.findall("\".*\"", list2[j])[0]
                        z = str(y).replace('\"', '')
                        self.xk_memory.append(z)
            a = re.findall("link_str.*;", t)[0]
            b = re.findall('\'.*\'', str(a))[0]
            c = str(b).split("\"")
            url = url_3
            j = 0
            for x in c:
                if x[0] != '+':
                    url = url + x.replace('\'', '') + self.xk_memory[j]
                    j = j + 1
                    if j == len(self.xk_memory):
                        break
                pass
            self.url = url
            self.sel_kc()
        else:
            json_path = 'resource\\yxkc.json'
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.yxkc = json.load(f)['data']
                    self.xkkc = None
            else:
                self.yxkc = None
                self.xkkc = None

    def sel_kc(self):
        self.xkkc.clear()
        self.yxkc.clear()
        t = self.s.get(url=self.url, headers=heard1).text
        self.num_xk = len(re.findall("xkkcData\[\d*]", t))
        self.num_yx = len(re.findall("yxkcData\[\d*]", t))
        p = re.compile('function initData\(\){(.+)}\r\n//页面初始加载数据', re.S)
        n = p.findall(t)[0]
        list_xk = re.compile("var tmpKc = Array\(\);(.+?)xkkcData", re.S)
        list_yx = re.compile("var tmpKc = Array\(\);(.+?)yxkcData", re.S)
        xk_final = list_xk.findall(n)
        yx_final = list_yx.findall(n, pos=n.find('xkkcData[{:d}]'.format(self.num_xk - 1)))

        indes1 = (1, 7, 9, 11, 4, 12, 15, 8, 10, 21, 22)  # 课程名 老师 时间 编号 学分 代号 学时 周次 地点 数字周次 数字时间
        indes2 = (1, 10, 6, 0, 4, 22, 8, 5, 9)  # 课程名 老师 时间 编号 学分 代号 学时 周次 地点
        for x in xk_final:
            one = []
            for i in range(0, len(indes1)):
                p = re.compile('tmpKc\[{:d}\].?=.?\"(.+)\"'.format(indes1[i]))
                result = p.findall(x)
                if result:
                    if i == 8:
                        one.append(replace_luoma(result[0], 1))
                    else:
                        if i == 7:
                            one.append(replace_luoma(result[0], 2))
                        else:
                            one.append(replace_luoma(result[0], 0))
                else:
                    one.append('None')
            self.xkkc.append(one)
        for x in yx_final:
            one = []
            for i in range(0, len(indes2)):
                p = re.compile('tmpKc\[{:d}\].?=.?\"(.+)\"'.format(indes2[i]))
                result = p.findall(x)
                if result:
                    if i == 8:
                        one.append(replace_luoma(result[0], 1))
                    else:
                        if i == 7:
                            one.append(replace_luoma(result[0], 2))
                        else:
                            one.append(replace_luoma(result[0], 0))
                else:
                    one.append('None')
            self.yxkc.append(one)
        with open('resource\\yxkc.json', 'w', encoding='utf-8') as f:
            json.dump({'data': self.yxkc}, f)

    def find_index_xk_id(self, classid):
        for i in range(0, len(self.xkkc)):
            if classid == self.xkkc[i][3]:
                return i

    def find_index_xk_teacher(self, name) -> list:
        kc_list = []
        for i in range(0, len(self.xkkc)):
            if name in self.xkkc[i][1]:
                kc_list.append(i)
        return kc_list

    def find_index_yx(self, classname: str):
        for i in range(self.num_xk, len(self.num_yx)):
            if classname in self.yxkc[i][0]:
                return i

    def xk(self, index):
        url = "http://202.119.81.112:9080/njlgdx/xk/processXk"
        pars = {
            'jx0502id': self.xk_memory[1],
            'jx0404id': self.xkkc[index][3],
            'jx0502zbid': self.xk_memory[0],
            'xf': self.xkkc[index][4],
            'kch': self.xkkc[index][5],
            'zxs': self.xkkc[index][6],
            'kcsx': '1',
            'szkcfl': '',
            'kkzcmx': self.xkkc[index][9],
            'kcsjmx': self.xkkc[index][10]
        }
        re = self.s.post(url=url, headers=heard1, data=pars)
        text = re.json()
        print(text)
        add_text(text['msgContent'] + ':' + self.xkkc[index][0] + ' ' + self.xkkc[index][1] + ' ' + self.xkkc[index][2],
                 parent='tab3')
        a = self.xkkc[index][0]
        b = self.xkkc[index][1]
        c = self.xkkc[index][2]
        self.sel_kc()
        self.paint()
        add_text(re.text + ':' + a + ' ' + b + ' ' + c, parent='tab3')

    def tx(self, index):
        url = "http://202.119.81.112:9080/njlgdx/xk/processTx"
        pars = {"jx0502id": self.xk_memory[1],
                "jx0404id": self.xkkc[index][3],
                "jx0502zbid": self.xk_memory[0]
                }
        re = self.s.post(url=url, headers=heard1, data=pars)
        print(re.text)
        a = self.yxkc[index][0]
        b = self.yxkc[index][1]
        c = self.yxkc[index][2]
        self.sel_kc()
        self.paint()
        add_text(re.text["msgContent"] + ':' + a + ' ' + b + ' ' + c, parent='tab3')

    def thread_fun(self, type, text, set_time):
        while True:
            if int(time.time()) == set_time:
                if type == 1:
                    self.xk(text)
                break
            else:
                time.sleep(1000)
        pass

    def xk_item(self, sender, data):
        for x in get_table_selections(sender):
            print(x[0], x[1])
            if x[1] == 6:
                self.xk(x[0])

    def tx_item(self, sender, data):
        for x in get_table_selections(sender):
            print(x[0], x[1])
            if x[1] == 6:
                self.tx(x[0])

    # 绘图
    def paint(self):
        children = get_item_children('tab3')
        if children is not None:
            for x in children:
                delete_item(x)
        else:
            print('tab3无子类')
        with tab('tab3', label='选课', parent='bar'):  # 课程名 老师 时间 编号 学分 代号 学时 周次 地点 0 1 2 8 7 4
            add_input_text('first', default_value='20210823', label='本学期第一周第一天', )
            add_input_text('pre', default_value='30', label='提前提醒时间')
            add_button('printIcs', label='课表生成日历', callback=self.printfIcs,
                       callback_data=[get_value('first'), get_value('pre')])
            add_input_int('timer', label='设置定时选课时间(几分钟后)')
            add_input_int('kc_type', label='输入课程信息类别（1课程名-教师名 2课程号）')
            add_input_text('kc_inp', label='输入课程信息内容')
            add_button('xkTimer', label='定时选课',
                       callback=lambda a, b: threading.Thread(target=self.thread_fun, args=(
                           b['type'], b['content'], int(time.time()) + b['timer'])
                                                              , daemon=True, name='xkTimer').start(),
                       callback_data={'type': get_value('kc_type'),
                                      'content': get_value('kc_inp'),
                                      'time': get_value('timer')})
            if self.xkkc is not None and len(self.xkkc) > 0:
                add_text('选课表')
                add_table('选课表_table', ['课程名', '老师', '时间', '地点', '周次', '学分', '选课按钮'], width=1380, height=450,
                          callback=self.xk_item)
                for x in self.xkkc:
                    add_row('选课表_table', [x[0], x[1], x[2], x[8], x[7], x[4], '选课'])
            if self.yxkc is not None:
                add_text('课表')
                add_table('课表_table', ['课程名', '老师', '时间', '地点', '周次', '学分', '退选按钮'], width=1380, height=450,
                          callback=self.tx_item)
                for x in self.yxkc:
                    add_row('课表_table', [x[0], x[1], x[2], x[8], x[7], x[4], '退选'])

    # 写入日历文件
    def write_rili(self):
        self.rili = []
        for i in range(0, len(self.yxkc)):
            weeks = 0
            isGuoQing = False
            a1 = self.yxkc[i][7].split(',')
            a2 = self.yxkc[i][7].split('-')
            if len(a1) > 1:
                if len(a2) > 1:
                    l = a1[0].split('-')
                    s = l[0]
                    e = l[1]
                    l = a1[1].split('-')
                    ss = l[0]
                    ee = l[1]
                    isGuoQing = True
                elif int(a1[0]) % 2 == 0:
                    weeks = 2
                    s = a1[0]
                    e = a1[len(a1) - 1]
                else:
                    weeks = 1
                    s = a1[0]
                    e = a1[len(a1) - 1]
            elif len(a2) == 1:
                s = a2[0]
                e = a2[0]
            else:
                s = a2[0]
                e = a2[1]

            t = self.yxkc[i][2]
            p = re.compile(r'(.*?)\((.*?)\)')
            result = re.findall(p, t)

            for x in result:
                a = str(x[0]).strip()
                b = str(x[1]).strip()
                if a == "星期一":
                    weekday = 1
                elif a == "星期二":
                    weekday = 2
                elif a == "星期三":
                    weekday = 3
                elif a == "星期四":
                    weekday = 4
                elif a == "星期五":
                    weekday = 5
                elif a == "星期六":
                    weekday = 6
                else:
                    weekday = 7

                self.w(i, s, e, weeks, weekday, b)
                if isGuoQing:
                    self.w(i, ss, ee, weeks, weekday, b)

    def w(self, i, s, e, weeks, weekday, classtime):
        d = {}
        d["ClassName"] = self.yxkc[i][0]
        d["StartWeek"] = int(s)
        d["EndWeek"] = int(e)
        d["WeekStatus"] = int(weeks)
        d["Weekday"] = int(weekday)
        d["ClassTimeId"] = classtime
        d["Classroom"] = self.yxkc[i][8]
        d["isClassSerialEnabled"] = self.yxkc[i][3]
        d["isClassTeacherEnabled"] = self.yxkc[i][1]
        self.rili.append(d)

    # 生成日历文件

    def printfIcs(self, sender, data):
        self.write_rili()
        from print_tool import GenerateCal
        process = GenerateCal(self.rili)
        process.set_attribute([get_value('first'), get_value('pre')])
        process.main_process()
        # mesbox("成功", "生成.ics文件成功", -1)


class cj:
    rr = None
    url = "http://202.119.81.112:9080/njlgdx/kscj/cjcx_list"
    list_cj = []
    plot_x = -1

    def __init__(self, s: object):
        self.s = s
        self.sumxf = []
        self.list_n = []  # 用于计算的成绩序号
        self.zb_cha = [0]  # 理论占比-实际占比
        self.rr = self.s.get(url=self.url, headers=heard1)
        soup = BeautifulSoup(replace_luoma(self.rr.text, 0), 'html.parser')
        list1 = soup.find('table', class_='Nsb_r_list Nsb_table')
        list2 = list1.find_all('tr')
        for x in list2:
            one = []
            if x.find('td') == None:
                for y in x.find_all('th'):
                    one.append(y.get_text())
            else:
                for y in x.find_all('td'):
                    one.append(y.get_text())
            self.list_cj.append(one)

    def tojd(self, m):
        try:
            n = float(m)
            if n in range(90, 101):
                return 4.0
            if n in range(85, 90):
                return 3.7
            if n in range(82, 85):
                return 3.3
            if n in range(78, 82):
                return 3.0
            if n in range(75, 78):
                return 2.7
            if n in range(72, 75):
                return 2.3
            if n in range(68, 72):
                return 2.0
            if n in range(64, 68):
                return 1.5
            if n in range(60, 64):
                return 1.0
            else:
                return 0.0
        except:
            if m == '优秀':
                return 4.0
            if m == '良好':
                return 3.0
            if m == '中等':
                return 2.0
            if m == '及格':
                return 1.0
            else:
                return 0.0

    def tofs(self, m):
        try:
            return float(m)
        except:
            if m == '优秀':
                return 90
            if m == '良好':
                return 80
            if m == '及格':
                return 60

    def toavg(self, list1):
        fs = []
        jd = []
        xq = []
        fs.append(0.0)
        jd.append(0.0)
        self.sumxf.clear()
        self.sumxf.append(0.0)  # 学期总学分
        xq.append(int(self.list_cj[list1[0]][0]))
        for i in list1:
            if self.list_cj[i][1] != self.list_cj[xq[len(xq) - 1]][1]:
                try:
                    xq.append(int(self.list_cj[i][0]))
                    fs.append(0.0)
                    jd.append(0.0)
                    self.sumxf.append(0.0)
                    fs[len(xq) - 1] = fs[len(xq) - 1] + self.tofs(self.list_cj[i][4]) * float(self.list_cj[i][6])
                    jd[len(xq) - 1] = jd[len(xq) - 1] + self.tojd(self.list_cj[i][4]) * float(self.list_cj[i][6])
                    self.sumxf[len(xq) - 1] = self.sumxf[len(xq) - 1] + float(self.list_cj[i][6])
                except:
                    print(self.list_cj[i])
            else:
                fs[len(xq) - 1] = fs[len(xq) - 1] + self.tofs(self.list_cj[i][4]) * float(self.list_cj[i][6])
                jd[len(xq) - 1] = jd[len(xq) - 1] + self.tojd(self.list_cj[i][4]) * float(self.list_cj[i][6])
                self.sumxf[len(xq) - 1] = self.sumxf[len(xq) - 1] + float(self.list_cj[i][6])
        for i in range(0, len(xq)):
            fs[i] = round(fs[i] / self.sumxf[i], 2)
            jd[i] = round(jd[i] / self.sumxf[i], 2)
        set_value(' - > 已选学分', str(self.sumxf).replace('[', '').replace(']', ''))
        return {'jf': fs, 'jj': jd, 'xq': xq}

    def analyze(self, xq):
        j = 0
        xq.append(100000)
        sum = 0
        self.zb = []
        for i in range(1, len(self.list_cj)):
            try:
                if i >= xq[j + 1]:
                    j += 1
                m1 = self.tofs(self.list_cj[i][4]) * float(self.list_cj[i][6]) / self.sumxf[j]
                m2 = 100 * float(self.list_cj[i][6]) / self.sumxf[j]
                self.zb_cha.append(m2 - m1)
                sum += m2 - m1
            except IndexError as e:
                print(e)
        a = 0
        for x in self.zb_cha:
            a += x / sum * 360
            self.zb.append(a)

    def onall(self, sender, data):
        if not get_value('必修'):
            re = self.toavg(self.list_n[1])
        else:
            re = self.toavg(self.list_n[0])
        set_value('1', value=re["jf"])
        set_value('2', value=re["jj"])
        set_value('jf', str(re["jf"]).replace('[', '').replace(']', ''))
        set_value('jj', str(re["jj"]).replace('[', '').replace(']', ''))

    def select_item(self, sender, data):
        self.list_n[1].clear()
        self.list_n[1] = [x for x in range(1, len(self.list_cj))]
        j = False
        for x in range(len(get_table_data(sender))):
            set_table_item(sender, x, 10, str(True))
        for x in get_table_selections(sender):
            if x[1] == 10:
                j = True
                set_table_item(sender, x[0], x[1], str(False))
                self.list_n[1].remove(int(get_table_item(sender, x[0], 0)))
        if len(get_table_selections(sender)) == 0:
            j = True
        if j:
            self.onall(None, None)

    def main_callback(self, sender, data):
        x = get_plot_mouse_pos()[0]
        # if self.plot_x == x:
        #     return
        # if x > len(self.list_cj) or x < 0:
        #     try:
        #         set_item_tip('plot1', '')
        #     except Exception as e:
        #         print(e)
        #     return
        # x = int(x)
        # self.plot_x = x
        # try:
        #     set_item_tip('plot1', self.list_cj[x][3])
        # except Exception as e:
        #     print(e)

    def draw_l(self, l, p1, r):
        i = 1
        for a in l:
            if a == 0:
                continue
            a = radians(-a)
            y = p1[0] + r * sin(a)
            x = p1[1] + r * cos(a)
            p2 = [x, y]
            draw_line('D', p1, p2, color=[255, 255, 0, 255], thickness=1)
            draw_text('D', [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2], self.list_cj[i][3], size=20)
            i += 1

    # 生成excel文件

    def printfXlsx(self, sender, data):
        url_kb = url_3 + '/njlgdx/xskb/xskb_list.do'
        r = self.s.get(url=url_kb, headers=heard2)
        soup = BeautifulSoup(r.text, 'html.parser')
        from print_tool import CreateExcel
        CreateExcel(soup=soup)

    def paint(self):
        # 序号 开学学期 课程编号 课程名称 成绩 成绩标识 学分 总学时 考核方式 课程属性 课程性质 是否选中
        # 0    1      2       3      4   5 （删除）      6   7     8       9      10      11
        with tab('tab2', label="考试成绩", parent='bar'):
            add_button('printXlsx', label='课表生成excel', callback=self.printfXlsx)
            self.list_n.append([])
            self.list_n.append([x for x in range(1, len(self.list_cj))])
            re1 = self.toavg(self.list_n[1])
            self.analyze(re1['xq'])  # 分析成绩占比
            data_fs = []
            for x in re1['xq']:
                table_name = "{} 成绩查询".format(x)
                if len(self.list_cj) < x:
                    continue
                add_text(self.list_cj[x][1])
                add_table(table_name, self.list_cj[0], callback=self.select_item)
                endi = len(self.list_cj)
                for i in range(x, len(self.list_cj)):
                    if self.list_cj[i][1] != self.list_cj[x][1]:
                        endi = i
                        break
                    add_row(table_name, self.list_cj[i])
                    data_fs.append(self.tofs(self.list_cj[i][4]))
                    if self.list_cj[i][9] == '必修':
                        self.list_n[0].append(i)
                add_column(table_name, '是否选中', [str(True) for y in range(endi - x)])
                delete_column(table_name, 5)
            add_label_text(' - > 已选学分', default_value=str(self.sumxf).replace('[', '').replace(']', ''))
            add_label_text('jf', label=" - > 均分", default_value=str(re1["jf"]).replace('[', '').replace(']', ''))
            add_label_text('jj', label=" - > 均绩", default_value=str(re1["jj"]).replace('[', '').replace(']', ''))
            add_checkbox('必修', callback=self.onall)
            add_plot('plot1', width=1080, height=400, label="成绩分布")
            add_line_series("plot1", name="成绩折线图", x=[x for x in range(1, len(self.list_cj))], y=data_fs,
                            color=[255, 0, 0, 255])
            add_scatter_series("plot1", name="成绩散点图", x=[x for x in range(1, len(self.list_cj))], y=data_fs,
                               outline=[255, 255, 0, 255], fill=[255, 255, 255, 100])
            add_simple_plot('cal', label="分析柱状图", value=self.zb_cha, height=300, width=1080, overlay="分析柱状图",
                            histogram=True)
            add_drawing("D", width=1000, height=1000)
            draw_circle('D', [500, 500], 450, color=[255, 255, 0, 255])
            self.draw_l(self.zb, [500, 500], 450)

            add_simple_plot('1', value=re1["jf"], label='均分', height=100, width=1080)
            add_simple_plot('2', value=re1["jj"], label='均绩', height=100, width=1080)
            set_mouse_move_callback(self.main_callback)  # 设置鼠标移动监听


class djcj:
    url = 'http://202.119.81.112:9080/njlgdx/kscj/djkscj_list'
    rr = None
    djcjlist = []

    def __init__(self, s):
        self.rr = s.get(url=self.url, headers=heard1)
        t = self.rr.text
        soup = BeautifulSoup(t, 'html.parser')
        table = soup.find('table', class_='Nsb_r_list Nsb_table')
        tr = table.find_all('tr')
        th = tr[0].find_all('th')
        self.djcjlist.append([th[0].get_text(), th[1].get_text(), th[2].get_text(), th[4].get_text()])
        for i in range(2, len(tr)):
            td = tr[i].find_all('td')
            self.djcjlist.append([td[0].get_text(), td[1].get_text(), td[4].get_text(), td[8].get_text()])
        return

    def paint(self):
        with tab('tab1', label='等级考试', parent='bar'):
            add_table('考试查询', self.djcjlist[0], width=1080, height=150)
            for x in range(1, len(self.djcjlist)):
                add_row('考试查询', self.djcjlist[x])
                pass


def paint(name, jwc_):
    selectedItem = kc(jwc_.s, jwc_.list['选课中心'], name)
    selectedItem.paint()


url_login = 'http://202.119.81.204/kaoshi/index.asp'
url_captcha = 'http://202.119.81.204/kaoshi/captcha.asp'


class sports:
    username = '919107820406'
    password = 'kuangyu1375sfms'

    def __init__(self):
        self.s = requests.session()
        r1 = self.s.get(url=url_captcha, headers=heard1)
        path = 'resource/captcha.bmp'
        with open(file=path, mode='wb') as f:
            f.write(r1.content)
        code = jwc.read_text(path)
        data = {
            'userID': self.username,
            'suerPassword': self.password,
            'userType': 'Student',
            'captchacode': code
        }
        index = 1
        r2 = self.s.post(url_login, data=data, headers=heard1)
        while r2.url == url_login:
            r1 = self.s.get(url=url_captcha, headers=heard1)
            path = 'resource/captcha.bmp'
            with open(file=path, mode='wb') as f:
                f.write(r1.content)
            code = jwc.read_text(path)
            data = {
                'userID': self.username,
                'suerPassword': self.password,
                'userType': 'Student',
                'captchacode': code
            }
            time.sleep(0.5)
            print('第{}次尝试登陆'.format(index))
            r2 = self.s.post(url_login, data=data, headers=heard1)
            index += 1
        r3 = self.s.get('http://202.119.81.204/kaoshi/student/query_score.asp')
        print(r3.content.decode('gbk'))

    @staticmethod
    def parse(path):
        with open(file=path, mode='rb')as f:
            text = f.read()
        soup = BeautifulSoup(text, 'html.parser')
        r = soup.find_all('td')
        isstart = False
        ll = []
        l = []
        i = 0
        for x in r:
            if isstart:
                if i >= 8 or x.text == '':
                    i = 0
                    ll.append(l.copy())
                    l.clear()
                    if x.text == '':
                        continue
                l.append(x.text)
                i += 1
            if not isstart and x.text == '体育成绩':
                isstart = True
        for y in ll:
            print(y)


if __name__ == '__main__':
    # s = sports()
    sports.parse('C:\\Users\\asus\\Desktop\\88.html')
