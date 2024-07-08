import threading
import requests
import json
import re
import os
from pprint import pprint


class HttpRequests:
    video_size = 1
    total_size = 0
    audio_size = 1
    atotal_size = 0

    def __init__(self, dirInput, urlInput, video_size=1, total_size=0,
                 userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30',
                 Referer='https://www.bilibili.com/'):
        # self.content_size = None                   #网页大小
        HttpRequests.total_size = total_size
        HttpRequests.video_size = video_size
        self.html_data = None  # 网页数据
        self.video_data = None  # 网页源码里的视频部分
        self.video_data_json = None  # 网页源码视频部分文本转字典
        self.video_url = None  # 视频链接
        self.audio_url = None  # 音频链接
        self.video_file = None  # 视频文件
        self.video_size = 0  # 视频大小
        self.total_size = 0  # 下载的大小
        self.audio_file = None  # 音频文件
        self.audio_size = 0  # 音频大小
        self.atotal_size = 0
        self.url = urlInput
        self.dir = dirInput
        self.headers = {}
        self.headers['user-agent'] = userAgent
        self.headers['referer'] = Referer

    def getWebSource(self):
        self.html_data = requests.get(self.url, headers=self.headers, stream=True).text

    # 获取网页源码大小
    # self.content_size = int(self.html_data.headers['content-length'])
    # print('total web source content size'+self.content_size)
    # pprint(self.html_data)
    # print(self.html_data.headers.get('Content-Length'))

    def getVideoUrl(self):
        # 获取网页源码里的视频部分
        self.video_data = re.findall('<script>window\.__playinfo__=(.*?)</script>', self.html_data)[0]
        # 将获取到的文本转字典
        self.video_data_json = json.loads(self.video_data)
        # 寻找视频文件的链接，还有音频文件的链接
        self.video_url = self.video_data_json['data']['dash']['video'][0]['backupUrl'][0]
        self.audio_url = self.video_data_json['data']['dash']['audio'][0]['backupUrl'][0]

    # pprint(self.video_data)

    # 这个废掉了，不用的了

    # 下载前先获取文件大小，以便之后弄进度条
    # def getFileSize(self):
    # self.video_size = requests.get(self.video_url).headers['Content-Length']
    # print(requests.get(self.video_url, headers=self.headers, stream=True).headers['Content-Length'])
    # print(str(requests.get(self.video_url, headers=self.headers, stream=True).headers).encode('utf8'))
    # self.video_size = requests.get(self.video_url, headers=self.headers, stream=True).headers['Content-Length']
    # print(self.video_size)
    # return self.video_size
    # print(str(requests.head(self.video_url)))
    # print(str(self.video_size.headers).encode('utf8'))
    # print(str(self.video_size.headers['Content-Length']))

    # 对视频文件进行请求
    def requestVideo(self,name):
        # self.video_file = requests.get(self.video_url, headers = self.headers, stream=True).content
        # print(len(str(self.video_file)))
        # self.audio_file = requests.get(self.audio_url, headers = self.headers, stream=True).content
        self.video_file = requests.get(self.video_url, headers=self.headers, stream=True)
        self.video_size = int(self.video_file.headers['Content-Length'])
        HttpRequests.video_size = self.video_size
        with open('{}\\video.mp4'.format(self.dir), 'wb') as f:
            for data in self.video_file.iter_content(chunk_size=1024):
                size = f.write(data)
                self.total_size += size
                HttpRequests.total_size = self.total_size

        trans_start = ".\\ffmpeg-5.0.1-full_build-shared\\bin\\ffmpeg -hide_banner -i " \
                          + self.dir + '\\' + 'video.mp4' \
                          + " -i " + self.dir + '\\' + 'audio.mp3' \
                          + " -c:v copy -c:a aac " \
                          + self.dir + '\\' + name + '.mp4'
        print(trans_start);
        os.popen(trans_start);

        print("Convert Done!");

            # print(total_size)
            # print('total size:', self.total_size)
            # print('progress:', total_size/int(self.video_size))
        # f.write(self.video_file)

    def requestAudio(self):
        self.audio_file = requests.get(self.audio_url, headers=self.headers, stream=True)
        self.audio_size = int(self.audio_file.headers['Content-Length'])
        HttpRequests.audio_size = self.audio_size

        with open('{}\\audio.mp3'.format(self.dir), 'wb') as f:
            #f.write(self.audio_file)
            for data in self.audio_file.iter_content(chunk_size=1024):
                size = f.write(data)
                self.atotal_size += size
                HttpRequests.atotal_size = self.atotal_size
            # print(total_size)
            # print('total size:', self.total_size)
            # print('progress:', total_size/int(self.video_size))
        # f.write(self.video_file)


def vmain(dir, website, name):
    a = HttpRequests(dir, website);
    a.getWebSource()
    a.getVideoUrl()
    # a.getFileSize()
    print("Video Downloading...");

    a.requestVideo(name)
    #request_v = threading.Thread(target=a.requestVideo, name='request_video')
    #request_a = threading.Thread(target=a.requestAudio, name='request_audio')
    #request_v.start()
    #request_a.start()
    #request_a.join()
    #request_v.join()
    # a.saveFile()
    print("Video Save complete");


def amain(dir, website):
    a = HttpRequests(dir, website);
    a.getWebSource()
    a.getVideoUrl()
    # a.getFileSize()
    print("Audio Downloading...");

    #a.requestVideo()
    #request_v = threading.Thread(target=a.requestVideo, name='request_video')
    request_a = threading.Thread(target=a.requestAudio, name='request_audio')
    #request_v.start()
    request_a.start()
    request_a.join()
    #request_v.join()
    # a.saveFile()
    print("Audio Save complete");
