import logging
import os
import tkinter as tk
import webbrowser
import requests
import tkinter.messagebox as mes_box
from tkinter import ttk
from tkinter import *
from retrying import retry
from pygame import mixer
import threading
from PIL import ImageTk, Image
import time
from mutagen.mp3 import MP3

class SetUI(object):
    def __init__(self, master, callback,weight=1200, height=600):
        self.callback = callback
        self.path = './音乐'
        self.num = 0
        self.pause_cond = threading.Condition()
        self.video = {}
        self.current_index = 0
        self.ui_weight = weight
        self.ui_height = height
        self.title = " 每日新觉音乐播放器"
        self.ui_root = master
        self.ui_root.geometry('1200x600+10+10')
        self.ui_root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.ui_url = tk.StringVar()
        self.ui_var = tk.IntVar()
        self.ui_var.set(1)
        self.show_result = None
        self.song_num = None
        self.response_data = None
        self.song_url = None
        self.song_photo=None
        self.song_name = None
        self.song_author = None
        self.ui_root.attributes("-alpha", 0.9)
        self.is_paused = False
        self.playlist_folder = './音乐'
        self.ui_root.iconbitmap(r".\icons\music.ico")
        self.ui_root.iconbitmap()
        img1 = Image.open(r"./icons/pause.png")
        img1 = img1.resize((120, 90))
        self.pause_image = ImageTk.PhotoImage(img1)
        img1 = Image.open("./icons/goon.jpg")
        img1 = img1.resize((120, 90))
        self.goonimg = ImageTk.PhotoImage(img1)
        self.search_image = ImageTk.PhotoImage(Image.open("./icons/search24.png"))
        img = Image.open("./icons/Bf.png")
        img = img.resize((100, 100))
        self.play_image = ImageTk.PhotoImage(img)
        self.playing = False
        self.ui_root.protocol("WM_DELETE_WINDOW", self.on_closing)  # 绑定关闭窗口事件
        self.volume = 0
        self.paused = False

    def on_closing(self):
        mixer.init()
        self.playing = False  # 停止音乐播放
        mixer.music.stop()
        self.ui_root.destroy()  # 销毁窗口
        self.callback()  # 调用回调函数
        mixer.quit()  # 释放 mixer 资源
    def set_volume(self, val):
        self.volume = float(val) / 100
        if self.playing:
            mixer.music.set_volume(self.volume)

    def set_ui(self):
        # Frame空间
        self.canvas_root = tk.Canvas(self.ui_root, width=1200, height=600)
        im = Image.open('./icons/bgp.jpg').resize((1200, 600))
        self.bg_img = ImageTk.PhotoImage(im)
        self.canvas_root.create_image(0, 0, image=self.bg_img, anchor='nw')
        self.canvas_root.pack()
        # ui界面中菜单设计
        ui_menu = tk.Menu(self.canvas_root)
        self.ui_root.config(menu=ui_menu)
        file_menu = tk.Menu(ui_menu, tearoff=0)
        ui_menu.add_cascade(label='菜单', menu=file_menu)
        file_menu.add_command(label='使用说明', command=lambda: webbrowser.open('https://mp.weixin.qq.com/s/CLSjtF8q6xGOBQMYYbG-eQ'))
        file_menu.add_command(label='私聊作者', command=lambda: webbrowser.open('https://mp.weixin.qq.com/s/SNhyM8f7Bfi_ZhRjWjzy7w'))
        file_menu.add_command(label='聊天助手',command=lambda: webbrowser.open('https://chat.kunshanyuxin.com'))

        # 控件内容设置
        input_link = tk.Label(self.canvas_root, font=('楷体', 14), text="请输入歌名：")
        self.entry_style = tk.Entry(self.canvas_root, textvariable=self.ui_url, highlightcolor='Fuchsia', highlightthickness=2,
                                    width=30)
        self.entry_style.bind("<Return>", lambda event: self.func3(event=None))
        search_button = tk.Button(self.ui_root, image=self.search_image,bg='white', bd=0, command=self.get_KuWoMusic)
        self.volume_scale = Scale(self.canvas_root, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_scale.set(self.volume * 100)
        self.volume_scale.place(x=700, y=100)
        self.canvas_width = 500
        self.canvas_height = 20
        self.canvas=self.canvas_root
        self.time_label = Label(self.canvas_root, text="0.00 / 0.00")
        self.time_label.place(x=600,y=200)

        # 更新进度条
        self.current_time = 0
        self.progress = self.canvas.create_rectangle(500, 450, 900, 460, fill="black")

        self.canvas.itemconfig(self.progress, fill="red")
        self.bg = self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill="black")
        # 设置搜索按钮位置
        # 表格样式

        columns = ("序号", "歌手", "歌曲", "专辑")
        self.show_result = ttk.Treeview(self.canvas_root,height=50,show="headings", columns=columns)
        self.download_button = tk.Button(self.canvas_root,text="下载", font=('楷体', 14), fg='Purple', width=10, height=1, padx=5,
                                    pady=5, command=self.theadsong1)
        self.pause_Button = tk.Button(self.canvas_root, image=self.pause_image, text="暂停", font=('楷体', 14), fg='Purple',
                                         width=10, height=1, padx=5,
                                         pady=5, command=self.theadsong)
        self.label = tk.Label(self.canvas_root)  # 进度条
        self.label1 = tk.Label(self.canvas_root)  # 歌曲名


        scroll_var = tk.StringVar()

        # 创建一个 Scrollbar 控件，设置其 orient 和 command 属性
        scrollbar = tk.Scrollbar(self.canvas_root, orient=tk.VERTICAL, command=scroll_var.set)
        scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor=tk.NE)
        self.videolist = Listbox(self.canvas_root, background='#023f51', highlightthickness=0,font=('楷体', '15'), yscrollcommand=None, height=24, width=28)
        # self.videolist.bind("<Return>", self.func3(event=None))
        scrollbar.config(command=self.videolist.yview)
        # self.videolist.place(relx=0, rely=0, relheight=1.0, relwidth=0.95)
        tk.Button(self.canvas_root, text="我的列表", font=('楷体', '15'),command=self.test).place(x=900, y=20)
        tk.Button(self.canvas_root, text="删除列表", font=('楷体', '15'),command=self.delete_).place(x=1060, y=20)
        self.button5 = tk.Button(self.canvas_root,text="播放",image=self.play_image,font=('楷体', '15'), command=self.func5)
        # 创建搜索按钮
        input_link.place(x=450, y=30)
        search_button.place(x=770, y=30,width=30,height=25)
        self.entry_style.place(x=550, y=30)
        self.show_result.place(x=5, y=5, width=400, height=570)
        self.download_button.place(x=405, y=30, width=45, height=25)
        self.pause_Button.place(x=410, y=480, width=110, height=90)
        self.button5.place(x=790, y=480, width=110, height=90)

        self.videolist.place(x=900, y=60)

        # 设置表头
        self.show_result.heading("序号", text="序号")
        self.show_result.heading("歌手", text="歌手")
        self.show_result.heading("歌曲", text="歌曲")
        self.show_result.heading("专辑", text="专辑")
        # 设置列
        self.show_result.column("序号", width=40)
        self.show_result.column("歌手", width=100)
        self.show_result.column("歌曲", width=150)
        self.show_result.column("专辑", width=150)

    # 鼠标点击
        self.show_result.bind('<ButtonRelease-1>', self.get_song_url)

    def get_total_time(self, song_name):
        audio = MP3('{}'.format(song_name))
        time_music = audio.info.length
        return time_music


    def testing(self):
        self.pause_Button.config(image=self.pause_image)
        selected_file_path = './音乐'
        if os.path.exists(selected_file_path):
            pathfile = selected_file_path
            videolists = []
            for path, dirs, files in os.walk(pathfile):
                if not dirs:
                    for fil in files:
                        # 仅筛选出音乐文件
                        if os.path.splitext(fil)[-1] in ['.mp3', '.ogg', '.flac', 'mp4a', '.mod', '.wv', '.ape', 'mid',
                                                         '.midi', '.tta', '.tak']:
                            videolists.append(path + f"\{fil}")
                else:
                    for di in dirs:
                        for fil in files:
                            if os.path.splitext(fil)[-1] in ['.mp3', '.ogg', '.flac', 'mp4a', '.mod', '.wv', '.ape',
                                                             'mid', '.midi', '.tta', '.tak']:
                                videolists.append(path + di + f"\{fil}")
            # 判断列表是否为空
            if videolists:
                for vi in videolists:
                    p, f = os.path.split(vi)
                    self.videolist.insert(END, f)
                    self.video[f] = vi
                    self.videolist.place(x=900, y=60)
            else:
                tk.messagebox.showwarning("Warning", "未识别到可播放文件")

        else:
            tk.messagebox.showwarning("Warning", "指定的音乐文件夹不存在")

    def delete_(self):
        selected_index = self.videolist.curselection()
        if selected_index:
            # selected_index = self.videolist.curselection()[0]  # 获取当前选中项的索引
            selected_song = self.videolist.get(selected_index)  # 获取当前选中的歌曲文件名
            selected_path = os.path.join(self.playlist_folder, selected_song)  # 获取歌曲的完整路径
            os.remove(selected_path)  # 删除该歌曲文件
            self.videolist.delete(selected_index, selected_index)  # 删除该项
        else:
            tk.messagebox.showinfo("提示", "请先选中要删除的歌曲！")

    def progess(self):
        # 利用临时变量，避免在循环中重复计算产生误差
        for i in range(1, 101):
            progress_str = '{}%|{}'.format(i, int(i / 4 % 26) * '■')

            self.label.config(text=progress_str)
            self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            time.sleep(0.01)
        self.ui_root.after(2000, self.label.destroy)
        self.ui_root.update()  # 刷新界面，以便立即展示控件的删除操作
        self.label = tk.Label(self.canvas_root)  # 进度条

    @retry(stop_max_attempt_number=5)
    def get_KuWoMusic(self):
        # 清空treeview表格数据
        for item in self.show_result.get_children():
            self.show_result.delete(item)
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept - encoding': 'gzip, deflate',
            'accept - language': 'zh - CN, zh;q = 0.9',
            'cache - control': 'no - cache',
            'Connection': 'keep-alive',
            'csrf': 'HH3GHIQ0RYM',
            'Referer': 'http://www.kuwo.cn/search/list?key=%E5%91%A8%E6%9D%B0%E4%BC%A6',
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.51 Safari/537.36',
            'Cookie': '_ga=GA1.2.218753071.1648798611; _gid=GA1.2.144187149.1648798611; _gat=1; '
                      'Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1648798611; '
                      'Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1648798611; kw_token=HH3GHIQ0RYM'
        }
        search_input = self.ui_url.get()
        if len(search_input) > 0:
            search_url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?'
            search_data = {
                'key': search_input,
                'pn': '1',
                'rn': '80',
                'httpsStatus': '1',
                'reqId': '858597c1-b18e-11ec-83e4-9d53d2ff08ff'
            }
            try:
                self.response_data = requests.get(search_url, params=search_data, headers=headers).json()
                songs_data = self.response_data['data']['list']
                if int(self.response_data['data']['total']) <= 0:
                    mes_box.showerror(title='错误', message='搜索: {} 不存在.'.format(search_input))
                else:
                    for i in range(len(songs_data)):
                        self.show_result.insert('', i, values=(i + 1, songs_data[i]['artist'], songs_data[i]['name'],
                                                               songs_data[i]['album']))
            except TimeoutError:
                mes_box.showerror(title='错误', message='搜索超时，请重新输入后再搜索！')
        else:
            mes_box.showerror(title='错误', message='未输入歌曲或歌手，请输入后搜索！')

    def get_song_url(self, event):
        # treeview中的左键单击
        for item in self.show_result.selection():
            item_text = self.show_result.item(item, "values")
            # 获取
            self.song_num = int(item_text[0])
        # 获取下载歌曲的地址
        if self.song_num is not None:

            songs_data = self.response_data['data']['list']
            songs_req_id = self.response_data['reqId']
            song_rid = songs_data[self.song_num - 1]['rid']
            music_url = 'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={}&type=convert_url3' \
                        '&httpsStatus=1&reqId={}' \
                .format(song_rid, songs_req_id)
            response_data = requests.get(music_url).json()

            self.song_url = response_data['data'].get('url')
            self.song_name = songs_data[self.song_num - 1]['name']
            self.song_author = songs_data[self.song_num - 1]['artist']
            self.song_photo=songs_data[self.song_num - 1]['pic']
            print(self.song_photo)
        else:
            mes_box.showerror(title='错误', message='未选择要播放的歌曲，请选择')

    def download_music(self):
        mixer.init()
        # lines = self.videolist.curselection()
        if not os.path.exists('./音乐'):
            os.mkdir("./音乐/")
        if self.song_num is not None:
            song_name = self.song_name + '--' + self.song_author + ".mp3"
            try:
                save_path = os.path.join('./音乐/{}'.format(song_name)) \
                    .replace('\\', '/')
                true_path = os.path.abspath(save_path)
                resp = requests.get(self.song_url)
                with open(true_path, 'wb') as file:
                    file.write(resp.content)
                    self.progess()
                    self.test()

                tk.messagebox.showwarning('提示', '下载完成')
            except Exception as e:
                logging.error("Error: %s", str(e), exc_info=True)
                mes_box.showerror(title='下载歌曲时发生错误', message='错误提示：{}'.format(e.__class__.__name__))
        else:
            mes_box.showerror(title='错误', message='未选择要播放的歌曲，请选择后播放')


    def func5(self):
        self.playing=True
        t = threading.Thread(target=self.play, daemon=True)
        t.start()
    def func3(self,event):
        self.playing=True
        t = threading.Thread(target=self.get_KuWoMusic, daemon=True)
        t.start()

    def func4(self):
        mixer.init()
        if mixer.music.get_busy():
            mixer.music.stop()
            t1 = threading.Thread(target=self.play, daemon=True)
            t1.start()
        else:
            tk.messagebox.showinfo('提示','当前没有音乐正在播放')

    def play(self):
        mixer.init()
        res = []
        self.file_name(res)
        while self.playing:  # 优化为条件语句，只有在 playing 为 True 时才循环
            selection = self.videolist.curselection()
            if selection:
                self.label1.destroy()
                self.pause_Button.config(image=self.pause_image)
                self.num = selection[0]
                self.label1 = tk.Label(self.canvas_root, bg='lightblue', text='Playing....' + res[self.num])  # 歌曲名
                self.label1.place(x=540, y=480)
                mixer.music.load(res[self.num])
                mixer.music.play()
                self.duration = self.get_total_time(res[self.num])
                self.canvas.coords(self.progress, 0, 0, 0, self.canvas_height)
                self.paused = True
                self.total_time = self.duration
                self.current_time = 0
                self.update_time_label()
                self.paused = False
                t = threading.Thread(target=self.update_progress)
                t.start()
                print(self.duration)
                mixer.music.set_volume(self.volume)

                self.videolist.selection_clear(0, END)
            elif not mixer.music.get_busy():
                self.label1.destroy()
                self.num = (self.num + 1) % len(res)
                if self.num >= len(res):
                    self.num = 0
                mixer.music.load(res[self.num])
                self.canvas.coords(self.progress, 0, 0, 0, self.canvas_height)
                self.paused = True
                self.total_time = self.duration
                self.current_time = 0
                self.update_time_label()
                self.paused = False
                t = threading.Thread(target=self.update_progress)
                t.start()
                duration = self.get_total_time(res[self.num])
                print(duration)
                mixer.music.play()
                self.label1 = tk.Label(self.canvas_root, bg='lightblue', text='Playing....' + res[self.num])  # 歌曲名
                self.label1.place(x=540, y=480)
            time.sleep(0.1)
        else:
            time.sleep(0.1)




    def file_name(self, res):
        for x in os.listdir(self.path):
            (filename1, extension) = os.path.splitext(x)
            if extension == '.mp3':
                res.append(os.path.join(self.path, x))
    def ui_center(self):
        ws = self.ui_root.winfo_screenwidth()
        hs = self.ui_root.winfo_screenheight()
        x = int((ws / 2) - (self.ui_weight / 2))
        y = int((hs / 2) - (self.ui_height / 2))
        self.ui_root.geometry('{}x{}+{}+{}'.format(self.ui_weight, self.ui_height, x, y))
    def update_time_label(self):
        self.time_label.config(text="{:.2f} / {:.2f}".format(self.current_time, self.total_time))

    def update_progress(self):
        if not self.paused:
            current_progress = self.canvas.coords(self.progress)[2]
            if current_progress < self.canvas_width:
                self.canvas.move(self.progress, 1, 0)
                self.canvas.move(self.bg, 1, 0)
                self.current_time += 0.1
            else:
                self.canvas.coords(self.progress, 0, 0, 0, self.canvas_height)
                self.current_time = 0

            self.canvas.update()
            time.sleep(0.1)

            if self.total_time == 0:
                self.total_time = self.current_time

            self.update_time_label()
            self.update_progress()

    def pause(self):
        mixer.init()
        self.playing = not self.playing
        if self.playing:
            mixer.music.unpause()
            self.paused = False
            t = threading.Thread(target=self.update_progress)
            t.start()
            self.pause_Button.config(image=self.pause_image)
            self.button5.configure(state='normal')

        else:
            mixer.music.pause()
            self.paused = True
            self.pause_Button.config(image=self.goonimg)
            self.button5.configure(state='disable')
            # 等待其他线程
            self.pause_cond.acquire()
            self.pause_cond.wait()
            self.pause_cond.release()

    def makedir(self):
        if not os.path.exists('./音乐'):
            os.mkdir("./音乐/")

    def theadsong1(self):
        song=threading.Thread(target=self.download_music,args=())
        song.setDaemon(True)
        song.start()
        pass

    def theadsong(self):
        song=threading.Thread(target=self.pause,args=())
        song.setDaemon(True)
        song.start()
        pass

    def test1(self):
        self.videolist.delete(0,tk.END)
        self.ui_root.after(10,self.testing)
    def test(self):
        updata = threading.Thread(target=self.test1, args=())
        updata.setDaemon(True)
        updata.start()

    def other_thread(self):
        while True:
            # 如果音乐暂停，休眠线程
            if not self.playing:
                self.pause_cond.acquire()
                self.pause_cond.wait()
                self.pause_cond.release()
            # 其他线程的操作
            pass


    def loop(self):
        self.ui_root.protocol("WM_DELETE_WINDOW", self.on_closing)  # 绑定关闭窗口事件
        self.makedir()
        self.ui_center()  # 窗口居中
        self.set_ui()
        t=threading.Thread(target=self.other_thread)
        t.setDaemon(True)
        t.start()
        self.testing()



