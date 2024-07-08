import time
import request_useful
import Converter
import threading
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.config import Config
from tkinter import *
import tkinter.filedialog

# -*- coding:utf-8 -*-

Config.set('graphics','resizable',True)

class MainPage(Screen):
	def switchToConvert(self):
		Window.size=(800,445);

	def switchToDownload(self):
		Window.size=(800,445);

	def create(self):
		Window.size= (282,500)
		Window.clearcolor= (95/255,95/255,95/255,1)

class Download(Screen):
	savePosition = ObjectProperty(None)
	website = ObjectProperty(None)

	def setSize(self, w, h):
		# 设置界面大小
		Window.size = (w, h);

	def selectOutputFile(self):
		tk = Tk()
		tk.destroy()
		tk.mainloop()

		filename = tkinter.filedialog.askdirectory(title='Select Your Output File', initialdir='C:\\')

		if filename == '':
			print("error")
		else:
			filename = str(filename).replace('/', '\\')
			print("filename: " + filename)
			self.savePosition.text = filename

	def progress(self):
		time.sleep(1)
		self.videoSize.text = str(request_useful.HttpRequests.video_size)
		while (1):
			if request_useful.HttpRequests.total_size / request_useful.HttpRequests.video_size != 1:
				#print('progress:', request_useful.HttpRequests.total_size / request_useful.HttpRequests.video_size)
				self.ids[
					'pgbar'].value = 100 * request_useful.HttpRequests.total_size / request_useful.HttpRequests.video_size
			else:
				break

	def aprogress(self):
		time.sleep(2)
		self.audioSize.text = str(request_useful.HttpRequests.audio_size)
		while (1):
			if request_useful.HttpRequests.atotal_size / request_useful.HttpRequests.audio_size != 1:
				#print('progress:', request_useful.HttpRequests.atotal_size / request_useful.HttpRequests.audio_size)
				self.ids[
					'pgbar2'].value = 100 * request_useful.HttpRequests.atotal_size / request_useful.HttpRequests.audio_size
			else:
				break

	# 将i的值传递给进度条
	def Down(self):
		print(request_useful.HttpRequests.total_size, request_useful.HttpRequests.video_size)
		request_useful.vmain(str(self.savePosition.text), str(self.webUrl.text), self.saveName.text);
		print(request_useful.HttpRequests.total_size, request_useful.HttpRequests.video_size)
		self.ids['pgbar'].value = 0
		request_useful.HttpRequests.total_size = 0
		request_useful.HttpRequests.video_size = 1

#TO DO音频下载函数

	def aDown(self):
		print(request_useful.HttpRequests.atotal_size, request_useful.HttpRequests.audio_size)
		request_useful.amain(str(self.savePosition.text), str(self.webUrl.text));
		print(request_useful.HttpRequests.atotal_size, request_useful.HttpRequests.audio_size)
		self.ids['pgbar2'].value = 0
		request_useful.HttpRequests.atotal_size = 0
		request_useful.HttpRequests.audio_size = 1

	def btn(self):
		# 开线程下载，防止下载时整个窗口卡住
		print('hit the button')
		a = self.webUrl.text
		b = a.split('/')[4]
		print(b)
		c = b.split('?')[0]
		self.bv.text = c

		print('Save:', self.savePosition.text)
		down_thread = threading.Thread(target=self.Down, name='download_thread')
		down_thread.start()
		adown_thread = threading.Thread(target=self.aDown, name='adownload_thread')
		adown_thread.start()
		# 开线程显示进度
		progress_thread = threading.Thread(target=self.progress, name='progress_thread')
		progress_thread.start()
		aprogress_thread = threading.Thread(target=self.aprogress, name='aprogress_thread')
		aprogress_thread.start()

	# self.ids['pgbar'].value = 0
	# request_useful.main(str(self.savePosition.text),str(self.website.text));
	pass



class MyApp(App):
	def build(self):
		sm=ScreenManager()
		sm.add_widget(MainPage(name='MainPage'))
		sm.add_widget(Download(name='Download'))
		sm.add_widget(Converter.ConverterPage(name='Converter'))
		sm.current='MainPage'
		MP=MainPage()
		self.title = 'InfiniteX Bili Downloader and Format Converter'
		MP.create()
		return sm

Builder.load_file('kvfile.kv')

if __name__ == "__main__":
	MyApp().run()
