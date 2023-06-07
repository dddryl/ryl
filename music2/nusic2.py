import tkinter.messagebox
from tkinter.ttk import *
import Online
from tkinter import filedialog
from tkinter import ttk
import os
import tkinter as tk
import tkinter.messagebox
from tkinter import *
import pygame
from PIL import Image, ImageTk

def get_img(filename, width, height):
    im = Image.open(filename).resize((width, height))
    im = ImageTk.PhotoImage(im)
    return im

class gui:
    def __init__(self):
        path, file = os.path.split(__file__)
        self.path = path
        self.file = file
        self.video = {}
        self.file_formats = [
            '.wav', '.mp3', '.ogg', '.flac', 'mp4a', '.mod', '.wv', '.ape', 'mid', '.midi', '.tta', '.tak'
        ]
        self.win = tk.Tk()
        self.select_path = tk.StringVar()
        self.format_var = tk.StringVar(value='All')
        self.pause_resume = tkinter.StringVar(self.win, value='播放')
        self.play_video1 = Button(self.win, textvariable='',  command='').place(x=200, y=250)
        self.win.geometry("1000x563")
        self.win.geometry('1000x563+100+70')
        self.win.resizable(False, False)
        self.win.title("每日新觉音乐播放器")
        self.win.attributes("-alpha",0.8)
        self.img = Image.open("./icons/paly.jpg")
        self.img = self.img.resize((100, 100))
        self.play = ImageTk.PhotoImage(self.img)
        self.img1 = Image.open("./icons/bgm.jpg")
        self.img1 = self.img1.resize((100, 100))
        self.play1 = ImageTk.PhotoImage(self.img1)

    def url_gui(self):
        self.win.withdraw()
        self.new_window=tk.Toplevel(self.win)
        child=Online.SetUI(self.new_window,self.open_main)
        child.loop()

    def open_main(self):
        self.win.deiconify()

    def select_file(self):
        selected_file_path = filedialog.askdirectory()
        self.select_path.set(selected_file_path)
        self.testing()

    def testing(self):
        self.videolist.delete(0, END)
        mps = []
        folder_path = self.select_path.get()
        if os.path.exists(folder_path):
            if self.format_var.get() == 'All':
                for path, dirs, file in os.walk(folder_path):
                    for fil in file:
                        file_ext = os.path.splitext(fil)[-1]
                        if file_ext in self.file_formats:
                            mps.append(os.path.join(path, fil))
            else:
                file_format = f'*{self.format_var.get()}'
                for path, dirs, file in os.walk(folder_path):
                    for fil in file:
                        file_ext = os.path.splitext(fil)[-1]
                        if file_ext == file_format:
                            mps.append(os.path.join(path, fil))
            if len(mps) == 0:
                tk.messagebox.showwarning("Error", "未识别到可播放文件")
            else:
                for mp in mps:
                    p, f = os.path.split(mp)
                    self.videolist.insert(END, f)
                    self.video[f] = mp
        else:
            tk.messagebox.showinfo('提示', '找不到该路径，请检查路径是否正确')


    def main(self):
        self.win.iconbitmap(".\icons\music.ico")
        self.win.iconbitmap()

        """
        背景图
        """
        canvas_root = tk.Canvas(self.win, width=1000, height=563)
        im_root = get_img('./icons/Bgp.jpg', 1000, 563)
        canvas_root.create_image(500, 277, image=im_root)
        canvas_root.pack()

        # VideoList
        tk.Label(self.win, bg='LightSkyBlue', text="音乐列表", font=('Helvetica', '20')).place(x=750, y=5)
        tk.Button(self.win, text="在线听歌", font=('楷体', 17), command=self.url_gui).place(x=550, y=500)

        self.videolist = Listbox(self.win, background='#023f51', highlightthickness=0,font=('楷体', '15'),height=30, width=50)
        self.videolist.place(x=700, y=50)

        # Label
        tk.Label(self.win, font=('楷体', 15), text="输入文件路径：").place(x=1, y=10)

        # Entry
        tk.Entry(self.win, textvariable=self.select_path).place(x=150, y=10, width=300, height=25)

        # Combobox for format selection
        tk.Label(self.win, font=('楷体', 15), text="文件格式：").place(x=10, y=50)
        self.format_comboBox = ttk.Combobox(self.win, textvariable=self.format_var, state='readonly', width=14)
        self.format_comboBox['values'] = ['All', '.wav', '.mp3', '.ogg', '.flac', 'mp4a', '.mod', '.wv', '.ape', 'mid', '.midi', '.tta', '.tak']
        self.format_comboBox.place(x=140, y=50)
        self.format_comboBox.current(0)

        def play_video():
            lines = self.videolist.curselection()
            if len(lines) > 0:
                for line in lines:
                    audio = self.video[self.videolist.get(line)]
                    if self.pause_resume.get() == '播放':
                        pygame.mixer.init()
                        pygame.mixer.music.load(audio)
                        pygame.mixer.music.play(0, 0.0, 0)
                        pygame.mixer.music.set_volume(0.5)
                        self.pause_resume.set('暂停')
                        self.play_video1.config(image=self.play1)
                    elif self.pause_resume.get() == '暂停':
                        pygame.mixer.music.pause()
                        self.pause_resume.set('继续播放')
                        self.play_video1.config(image=self.play)
                    elif self.pause_resume.get() == '继续播放':
                        pygame.mixer.music.unpause()
                        self.pause_resume.set('暂停')
                        self.play_video1.config(image=self.play1)
            else:
                tk.messagebox.showwarning("Error", "请选择要播放的文件")

        def delete_():
            self.videolist.delete(0, END)

        flie = PhotoImage(file="./icons/stop.png")
        # 调整图片尺寸适应按钮大小
        photoimage = flie.subsample(3, 3)
        # 调整图片
        # 调整图片尺寸适应按钮大小
        # Button
        self.play_video1 = Button(self.win, textvariable=self.pause_resume, image=self.play, command=play_video)
        self.play_video1.place(x=200, y=250)

        Button(self.win, text="删除列表", command=delete_).place(x=920, y=5)
        Button(self.win, text="文件选择", image=photoimage, command=self.select_file).place(x=460, y=16)
        self.win.mainloop()

if __name__ == '__main__':

    app=gui()
    app.main()

