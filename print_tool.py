# coding: utf-8

import json
import sys
from datetime import datetime, timedelta
from uuid import uuid4 as uid
import socket
import re
import openpyxl as xl


# 安卓手机只能提前提醒10分钟，需要手动修改。

class GenerateCal:
    def __init__(self, rl):
        # 定义全局参数
        self.first_week = "20200224"  # 第一周周一的日期
        self.inform_time = 25  # 提前 N 分钟提醒
        self.g_name = f'{datetime.now().strftime("%Y.%m")} 课程表@{socket.gethostname()}'  # 全局课程表名
        self.g_color = "#ff9500"  # 预览时的颜色（可以在 iOS 设备上修改）
        self.a_trigger = ""

        # 读取文件，返回 dict(class_timetable) 时间表
        try:
            with open("resource/conf_classTime.json", 'r', encoding='UTF-8') as f:
                self.class_timetable = json.loads(f.read())
                f.close()
        except:
            print("时间配置文件 conf_classTime.json 似乎有点问题")
            sys.exit()
        self.class_info = rl

    def set_attribute(self, data):
        print('data')
        print(data)
        self.first_week = data[0]
        self.inform_time = data[1]
        try:
            self.inform_time = int(self.inform_time)  # 提前 N 分钟提醒
            if self.inform_time <= 60:
                self.a_trigger = f'-P0DT0H{self.inform_time}M0S'
            elif 60 < self.inform_time <= 1440:
                minutes = self.inform_time % 60
                hours = self.inform_time // 60
                self.a_trigger = f'-P0DT{hours}H{minutes}M0S'
            else:
                minutes = self.inform_time % 60
                hours = (self.inform_time // 60) - 24
                days = self.inform_time // 1440
                self.a_trigger = f'-P{days}DT{hours}H{minutes}M0S'
            c = 1
        except ValueError:
            if self.inform_time in "nN":
                self.a_trigger = ""
            else:
                print("输入数字有误！")

    def main_process(self):
        utc_now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

        # 开始操作，先写入头
        ical_begin_base = f'''BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:{self.g_name}
X-APPLE-CALENDAR-COLOR:{self.g_color}
X-WR-TIMEZONE:Asia/Shanghai
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
X-LIC-LOCATION:Asia/Shanghai
BEGIN:STANDARD
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
TZNAME:CST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
'''
        try:
            with open(f"日历课表.ics", "w", encoding='UTF-8') as f:  # 追加要a
                f.write(ical_begin_base)
                f.close()
        except:
            print("写入失败！可能是没有权限，请重试。")
            sys.exit()
        else:
            print("文件头写入成功！")

        initial_time = datetime.strptime(self.first_week, "%Y%m%d")  # 将开始时间转换为时间对象
        i = 1
        for obj in self.class_info:
            # 计算课程第一次开始的日期 first_time_obj，公式：7*(开始周数-1) （//把第一周减掉） + 周几 - 1 （没有周0，等于把周一减掉）
            try:
                delta_time = 7 * (obj['StartWeek'] - 1) + obj['Weekday'] - 1
            except TypeError:
                print("类型错误")

            if obj['WeekStatus'] == 1:  # 单周
                if obj["StartWeek"] % 2 == 0:  # 若单周就不变，双周加7
                    delta_time += 7
            elif obj['WeekStatus'] == 2:  # 双周
                if obj["StartWeek"] % 2 != 0:  # 若双周就不变，单周加7
                    delta_time += 7
            first_time_obj = initial_time + timedelta(days=delta_time)  # 处理完单双周之后 first_time_obj 就是真正开始的日期
            if obj["WeekStatus"] == 0:  # 处理隔周课程
                extra_status = "1"
            else:
                extra_status = f'2;BYDAY={weekdays[int(obj["Weekday"] - 1)]}'  # BYDAY 是周 N，隔周重复需要带上

            try:  # 尝试处理纯数字的课程序号
                obj["ClassSerial"] = obj["ClassSerial"]
                serial = f'课程序号：{obj["ClassSerial"]}'
            except ValueError:
                obj["ClassSerial"] = obj["ClassSerial"]
                serial = f'课程序号：{obj["ClassSerial"]}'
            except KeyError:  # 如果没有这个 key，直接略过
                serial = ""

            # 计算课程第一次开始、结束的时间，后面使用RRule重复即可，格式类似 20200225T120000
            for x in self.class_timetable:
                if obj['ClassTimeId'] == x['name']:
                    final_stime_str = first_time_obj.strftime("%Y%m%d") + "T" + x["startTime"]
                    final_etime_str = first_time_obj.strftime("%Y%m%d") + "T" + x["endTime"]
                    break
            delta_week = 7 * int(obj["EndWeek"] - obj["StartWeek"])
            stop_time_obj = first_time_obj + timedelta(days=delta_week + 1)
            stop_time_str = stop_time_obj.strftime("%Y%m%dT%H%M%SZ")  # 注意是utc时间，直接+1天处理
            # 教师可选，在此做判断
            try:
                teacher = f'教师：{obj["Teacher"]}\t'
            except KeyError:
                teacher = ""

            # 生成此次循环的 event_base
            if self.a_trigger:
                _alarm_base = f'''BEGIN:VALARM\nACTION:DISPLAY\nDESCRIPTION:This is an event reminder
TRIGGER:{self.a_trigger}\nX-WR-ALARMUID:{uid()}\nUID:{uid()}\nEND:VALARM\n'''
            else:
                _alarm_base = ""
            _ical_base = f'''\nBEGIN:VEVENT
CREATED:{utc_now}\nDTSTAMP:{utc_now}\nSUMMARY:{obj["ClassName"]}
DESCRIPTION:{teacher}{serial}\nLOCATION:{obj["Classroom"]}
TZID:Asia/Shanghai\nSEQUENCE:0\nUID:{uid()}\nRRULE:FREQ=WEEKLY;UNTIL={stop_time_str};INTERVAL={extra_status}
DTSTART;TZID=Asia/Shanghai:{final_stime_str}\nDTEND;TZID=Asia/Shanghai:{final_etime_str}
X-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\n{_alarm_base}END:VEVENT\n'''

            # 写入文件
            with open(f"日历课表.ics", "a", encoding='UTF-8') as f:
                f.write(_ical_base)
                print(f"第{i}条课程信息写入成功！")
                i += 1
                f.close()

        # 拼合头尾
        with open(f"日历课表.ics", "a", encoding='UTF-8') as f:
            f.write("\nEND:VCALENDAR")
            print(f"尾部信息写入成功！")
            f.close()


# 课表exel表格生成 用于适配华为服务一课表
class CreateExcel:
    def __init__(self, soup):
        data = self.parseKb(soup)
        self.createXlsx(data)

    @staticmethod
    def toWeek(s: str) -> int:
        if s == '一':
            return 1
        elif s == '二':
            return 2
        elif s == '三':
            return 3
        elif s == '四':
            return 4
        elif s == '五':
            return 5
        elif s == '六':
            return 6
        elif s == '日' or s == '天':
            return 7

    def toTime(self, s: list) -> list:
        timeList = []
        for x in s:
            timeList.append([self.toWeek(x[0]), int(x[1]), int(x[2])])
        return timeList

    def parseKc(self, kc_) -> dict:
        attrs = kc_.find_all('td')
        name = attrs[3].text
        teacher = attrs[4].text
        date = attrs[5].text
        address = attrs[7].text
        dates = re.findall(r'星期(\w)[(](\d+)-(\d+)小节[)]', date)
        dates = self.toTime(dates)
        addresses = []
        temp = address.split(',')
        for i in range(0, len(temp)):
            if i == 0:
                addresses.append(temp[i])
            else:
                if temp[i - 1] != temp[i]:
                    addresses.append(temp[i])
        return {
            'name': name,
            'teacher': teacher,
            'address': addresses,
            'dates': dates
        }

    @staticmethod
    def createXlsx(data):
        workbook = xl.Workbook()
        sheet1 = workbook.active
        for i in range(len(data)):
            sheet1.append(data[i])
        workbook.save('excel课表.xlsx')  # 保存

    def parseKb(self, soup):
        # 课程周数 begin
        dataList = soup.find_all(class_='kbcontent1')
        weeks = {}
        for x in dataList:
            xx = x.text
            if xx.strip() == '':
                continue
            xx = xx.split('----')
            temp = []
            for x_ in xx:
                if x_ == '':
                    continue
                temp.append(re.findall(r'([^-\d]+)\d', x_))
                t = re.findall(r'(\d+)[,(-]', x_)
                if len(t) == 2:
                    temp[len(temp) - 1].append("{}-{}周".format(t[0], t[1]))
                elif len(t) == 1:
                    temp[len(temp) - 1].append(t[0] + "周")
                else:
                    temp[len(temp) - 1].append("{}周".format(','.join(t)))

            for y in temp:
                weeks[y[0]] = y[1]
        # end
        # 课程信息 begin
        dataList = soup.find(id='dataList')
        kc = dataList.find_all('tr')
        kc = kc[1:]
        data = [[''] * 8 for _ in range(14)]
        for x in kc:
            temp = self.parseKc(x)
            for x in temp['dates']:
                for i in range(x[1], x[2] + 1):
                    if i > 13:
                        continue
                    t = data[i]
                    if t[x[0]] == '':
                        t[x[0]] = "{}[{}][{}][{}]".format(temp['name'], temp['teacher'], ']['.join(temp['address']),
                                                          weeks[temp['name']])
                    else:
                        t[x[0]] += ",{}[{}][{}][{}]".format(temp['name'], temp['teacher'], ']['.join(temp['address']),
                                                            weeks[temp['name']])
            pass
        # end
        return data
