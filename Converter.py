import os
import subprocess
import threading
import time
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from tkinter import *
import tkinter.filedialog

class ConverterPage(Screen):
    # kivy中Converter界面类

    def setSize(self, w, h):
        # 设置界面大小
        Window.size = (w, h);

    def selectInputFile(self):
        # 选择输入文件位置，调用tkinter的资源管理器

        tk = Tk()
        tk.destroy()
        tk.mainloop()

        filename = tkinter.filedialog.askopenfilename(title='Select Your Input File',
                                                      filetypes=[('mp4', '*.mp4'),
                                                                 ('flv', '*.flv'),
                                                                 ('mkv', '*.mkv'),
                                                                 ('mp3', '*.mp3'),
                                                                 ('All Files', '*')]
                                                      ,initialdir='C:\\')

        if filename == '':
            print("error")
        else:
            filename = str(filename).replace('/','\\')
            print("filename: " + filename)
            self.inPosition.text = filename
            self.inputFormatLabel.text = os.path.splitext(self.inPosition.text)[-1]

    def selectOutputFile(self):
        # 选择输出文件位置，调用tkinter的资源管理器

        tk = Tk()
        tk.destroy()
        tk.mainloop()

        filename = tkinter.filedialog.askdirectory(title='Select Your Output File', initialdir='C:\\')

        if filename == '':
            print("error")
        else:
            filename = str(filename).replace('/', '\\')
            print("filename: " + filename)
            self.outPosition.text = filename

    def convert(self):
        # 进行转码工作的方法

        FFmpeg = ffmpeg(self.inPosition.text,
                        self.outPosition.text,
                        self.outputName.text,
                        self.outputFormat.text,
                        self.bps.text,
                        self.outputWidth.text,
                        self.outputHeight.text,
                        self.inputFormatLabel.text)
        # 实例化ffmpeg对象

        self.total = FFmpeg.getDuration()
        # 调用ffmpeg类的getDuration方法，获取被转码视频总时长

        def openPopen():
            # 创建线程执行的任务

            self.shell = subprocess.Popen(FFmpeg.cmd(), stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          universal_newlines=True,
                                          encoding='utf8',
                                          bufsize=99999)
            # 创建管道，获取file对象
            # 这个bufsize比较关键，之前卡在这里相当久

            while subprocess.Popen.poll(self.shell) is None:
                # subprocess.Popen.poll状态：
                # 0 正常结束
                # 1 sleep
                # 2 子进程不存在
                # 5 kill
                # None 在运行
                # 当管道还在运行的时候：

                progress = self.shell.stdout.readline();
                # 用readline()读取管道输出内容

                a = progress.split(' ')
                for i in a:
                    if a[0] == 'frame=' and i != '' and i[0] == 't':
                        c = i.split('=')
                        d = c[1]
                        e = d.split(':')
                        current_time = float(e[0]) * 3600 + float(e[1]) * 60 + float(e[2])
                        # 通过一系列小学生操作，得到当前的转码进度（当前时刻）

                        self.pgbar.value = current_time / FFmpeg.getDuration() * 100
                        # 更新进度条进度

                        self.percentage.text = str( round(self.pgbar.value , 2) ) + '%'
                        #更新Label数字

                        break;


            self.pgbar.value = 0
            self.percentage.text = 'Completed!'
            # 管道结束后进度条归零，显示completed

            time.sleep(3)
            # 等待3秒

            self.percentage.text = '0%'
            #恢复进度label为0

        #方法结束

        t1 = threading.Thread(target=openPopen, name="converting")
        # 创建线程执行上面的方法

        t1.start()
        # 启动线程

    def clickStart(self):
        # 按下Start按钮操作

        #self.outputFormat.text = "flv"
        #self.bps.text = "1000"
        #self.outputWidth.text = "1920"
        #self.outputHeight.text = "1080"

        self.logger.text += "User hits the start button.\n"
        # 状态栏输出按下按钮事件

        self.logger.text += "Input: " + self.inPosition.text + "\n"
        self.logger.text += "Output: " + self.outPosition.text + "\n"
        # 状态栏输出文件输入、输出位置

        self.logger.text += "Input Format: " + self.inputFormatLabel.text + "\n"
        self.logger.text += "Output Format: " + self.outputFormat.text + "\n"
        self.logger.text += "Bits per second: " + self.bps.text + " Kbps\n"
        # 状态栏输出输入、输出格式

        self.logger.text += "\nStarting to convert...\n"

        self.convert()
        #调用convert方法

        self.logger.text += "Converting..."

class ffmpeg:

    def __init__(self, inputFile, outputFile, outputName, outputFormat, bps, outputWidth, outputHeight, inputFormat):
        #将前端填入的数据批量导入

        self.input_file = inputFile
        self.output_file = outputFile
        self.output_name = outputName
        self.output_format = outputFormat
        self.bps = bps
        self.outputWidth = outputWidth
        self.outputHeight = outputHeight
        self.inputFormat = inputFormat

    def getDuration(self):
        # 获取被转码视频总时长

        s = os.popen(".\\ffmpeg-5.0.1-full_build-shared\\bin\\ffprobe -v error -select_streams v -show_entries stream=duration -i " + self.input_file);
        # 创建管道

        for text in s.readlines():
            # 读取管道输出内容

            if text.startswith('duration='):
                text = text.replace('duration=', '');
                text = text.replace('\n', '');
                return float(text);
            # 将"duration=xxx\n"中代表时长的数字提取出来，并返回

    def cmd(self):
        #返回用来调用ffmpeg.exe的命令

        cmd = ".\\ffmpeg-5.0.1-full_build-shared\\bin\\ffmpeg -hide_banner" + " -i " + self.input_file

        if self.outputWidth!='' and self.outputHeight !='':
            cmd += " -s " + self.outputWidth + "x" + self.outputHeight
        # 如果长宽为空，命令中就不加入-s，以默认长宽输出

        if self.bps!='':
            cmd += " -b:v " + self.bps + "k"
        # 如果比特率为空，命令中就不加入-b:v，以比特率输出

        if self.output_file!='':
            cmd += " " + self.output_file + '\\'
        else:
            cmd += " " + 'C:\\Users\\Zhou_\\Videos\\'
        # 如果输出目录为空，就设为users的视频

        if self.output_name!='':
            cmd += self.output_name
        else:
            cmd += 'output'
        # 如果输出文件名为空，就设为output

        if self.output_format!='':
            cmd += '.' + self.output_format
        else:
            cmd += self.inputFormat
        # 如果输出格式为空，就设为跟输入文件一样

        # 搭积木组成调用ffmpeg的命令
        # 返回后用在命令行里
        # 要考虑前端的文本框什么都不填的情况
        print(cmd);

        return cmd;
