import json
import os
import threading

from dearpygui.core import *
from dearpygui.simple import *

import jiaowuchu
import zhlg

path = os.getcwd()
per_info_path = 'resource\\per_Info.json'
cookie_path = 'resource\\cookie.json'
index = 0


# 打包语句：
# pyinstaller -w main.py jiaowuchu.py print_tool.py zhlg.py -i D:\mixed_file\daima\Python\mypro\resource\icon.ico

def mesbox(title, text, interval):
    size_main = get_main_window_size()
    if interval > 0:

        t = threading.Timer(interval, lambda: delete_item(title))
        t.setDaemon(True)
        t.start()
    else:
        add_window(title, width=200, height=60, x_pos=int(size_main[0] / 2) - 100, y_pos=int(size_main[1] / 2) - 30,
                   no_move=True, on_close=lambda x, y: delete_item(title))
        add_label_text('', default_value=text, parent=title)
    return


def wjson(key, value):
    with open(cookie_path, 'r', encoding='utf-8')as f:
        content = json.load(f)
        content[key] = value
    with open(cookie_path, 'w', encoding='utf-8')as f:
        json.dump(content, f)


def login(sender, data):
    global index
    if index == 0:
        index += 1
    else:
        return
    size_main = get_main_window_size()
    with window('提示', width=200, height=60, x_pos=int(size_main[0] / 2) - 100, y_pos=int(size_main[1] / 2) - 30):
        add_label_text('', default_value='正在登录…………')
    jwc = None
    lg = None
    if os.path.exists(cookie_path):
        with open(cookie_path, 'r', encoding='utf-8') as f:
            cookie = json.load(f)
            # if 'zhlg' in cookie:
            #     lg = zhlg.zhlg(get_value('name'), get_value('pwd_2'), cookie['zhlg'])
            #     if lg.islogin:
            #         print('智慧理工 cookie登录成功')
            #     else:
            #         cookie.pop('zhlg')
            #         lg = None
            if 'jwc' in cookie:
                jwc = jiaowuchu.jwc(get_value('name'), get_value('pwd_2'), cookie['jwc'])
                if jwc.islogin:
                    print('教务处 cookie登录成功')
                else:
                    cookie.pop('jwc')
                    jwc = None
        with open(cookie_path, 'w', encoding='utf-8') as f:
            json.dump(cookie, f)
    if not os.path.exists(per_info_path):
        f = open(per_info_path, 'w')
        json.dump(
            {"username": get_value('name'), "jwc_password": get_value('pwd'), "zhlg_password": get_value('pwd_2')}, f)
        f.close()
        if lg is None:
            lg = zhlg.zhlg(get_value('name'), get_value('pwd_2'), None)
            if lg.islogin:
                wjson('zhlg', lg.s.cookies.get_dict())
        if jwc is None:
            jwc = jiaowuchu.jwc(get_value('name'), get_value('pwd'), None)
            if jwc.islogin and jwc.ck is not None:
                wjson('jwc', jwc.ck)
    else:
        if lg is None:
            lg = zhlg.zhlg(data[0], data[2], None)
            if lg.islogin:
                wjson('zhlg', lg.s.cookies.get_dict())
        if jwc is None:
            jwc = jiaowuchu.jwc(data[0], data[1], None)
            if jwc.islogin and jwc.ck is not None:
                wjson('jwc', jwc.ck)
    delete_item('提示')
    # if not lg.islogin:
    #     mesbox('错误', '智慧理工登录失败', -1)
    #     return
    if not jwc.islogin:
        mesbox('错误', '教务处登录失败', -1)
        return
    # 已经登录成功
    set_main_window_size(1920, 1080)  # 全屏
    jwc.paint()
    # 考试
    cj = jiaowuchu.cj(jwc.s)
    cj.paint()
    # 等级考试
    djcj = jiaowuchu.djcj(jwc.s)
    djcj.paint()
    # 智慧理工
    lg.paint()


def drop_item(name):
    item_list = get_all_items()
    for x in item_list:
        if name in get_item_label(x):
            delete_item(x)


def update(sender, data):
    show_item('name')
    show_item('pwd')
    show_item('pwd_2')
    hide_item('login')
    set_item_label(sender, '确定')
    set_item_callback('update', callback=reset)


def reset(sender, data):
    with open(per_info_path, 'r')as f:
        username = json.load(f)['username']
    if username != get_value('name'):
        os.remove('resource\\yxkc.json')
    f = open(per_info_path, 'w')
    json.dump({"username": get_value('name'), "jwc_password": get_value('pwd'), "zhlg_password": get_value('pwd_2')},
              f)
    f.close()
    show_item('login')
    hide_item('name')
    hide_item('pwd')
    hide_item('pwd_2')
    set_item_label(sender, '重置')
    mesbox('提示', '账户重置成功，请登录', 2)


def apply_theme(sender, data):
    set_theme(data)


if __name__ == '__main__':
    set_main_window_title('NJUST')
    set_main_window_size(400, 200)
    set_main_window_pos(550, 300)

    add_additional_font('C:/Windows/Fonts/SIMHEI.TTF', 16, glyph_ranges='chinese_full')
    with window('loginwin', x_pos=0, y_pos=0, no_move=True, autosize=True, no_title_bar=True,
                no_scrollbar=True):
        add_additional_font('C:/Windows/Fonts/SIMHEI.TTF', 16, glyph_ranges='chinese_full')
        themes = ["Dark", "Light", "Classic", "Dark 2", "Grey", "Dark Grey", "Cherry", "Purple", "Gold", "Red"]
        with menu_bar('menu_bar'):  # 设置主题
            add_menu('主题')
            for x in themes:
                add_menu_item(x, callback=lambda a, b: set_theme(b), callback_data=x)
            end()
        add_input_text('name', label='用户名', show=False)
        add_input_text('pwd', label='教务处密码', password=True, show=False)
        add_input_text('pwd_2', label='智慧理工密码', password=True, show=False)
        if os.path.exists(per_info_path):
            f = open(per_info_path)
            json_data = json.load(f)
            f.close()
            data = [json_data["username"], json_data["jwc_password"], json_data["zhlg_password"]]
            add_button('login', label='登录', callback=login, parent='loginwin', callback_data=data, tip='登录教务处和智慧理工',
                       width=400, height=25)
            add_button('update', label='重置', callback=update, parent='loginwin', tip="重置账户", width=400, height=25)
            pass
        else:
            show_item('name')
            show_item('pwd')
            show_item('pwd_2')
            add_button('login', label='登录', callback=login, parent='loginwin', callback_data=None, tip='登录教务处和智慧理工')
    start_dearpygui()
