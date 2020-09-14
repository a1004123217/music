from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QSizePolicy,QVBoxLayout
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from musciUI import Ui_MainWindow
from scipy.signal import detrend
from pydub import AudioSegment
import json
import matplotlib.pyplot as plt
import numpy as np
import struct
import wave
import os
import sys
import time
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import pyqtgraph as pg
import librosa.display
chunk = 1024
mpl.rcParams['agg.path.chunksize'] = 40000
# 将该路径文件从mp3转为wav
def change_format(path):
    new_path = path.replace('mp3', 'wav')
    # 将mp3文件转换成wav
    sound = AudioSegment.from_mp3(path)
    sound.export(new_path, format="wav")


# FigureCanvas 对象

class Mydemo(FigureCanvas):

    def __init__(self, parent=None, width=10000, height=5, dpi=100):
        plt.rcParams['font.family'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.axis('off')
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        plt.subplots_adjust(left=0.0, bottom=0.0, top=3.0, right=1)
        #plt.xlim(100,200)
        self.axes = self.fig.add_subplot(3, 1, 1)
        #self.axes.set_xlim([0,100])
        self.axes.xaxis.set_major_locator(MultipleLocator(10))
        self.axes1 = self.fig.add_subplot(3, 1, 2)
        self.axes2 = self.fig.add_subplot(3,1,3)
        #self.axes.yticks([])
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #FigureCanvas.setSizePolicy(self,
                                   #QSizePolicy.Expanding,
                                   #QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        self.setWindowTitle("音乐播放器^_^")
        self.setWindowIcon(QIcon('icon/音乐.png'))
        self.music_flag.setVisible(False)
        self.music_flag.setText("0")
        self.fileName = ""
        self.dbtxt = ""
        self.cur_song = ''
        self.is_pause = True
        self.y_temp = np.zeros(chunk)
        #self.figure = plt.figure(figsize=(14,5))
        #self.widget = FigureCanvas()
        #self.wf = []
        #self.wf = wave.Wave_read("")
        self.playlist = QMediaPlaylist()  # 播放列表
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)  # 列表循环
        self.player = QMediaPlayer(self)
        self.player.setPlaylist(self.playlist)
        self.player.setVolume(50.0)
        self.music = []
        self.sr = 0
        self.time = []
        self.data = []
        #画图测试
        self.widget = Mydemo(width=100000, height=5, dpi=100)
        self.verticalLayout.addWidget(self.widget)
        self.setLayout(self.verticalLayout)
        #data = list(range(1000))
        self.beatnum = 0
        self.downbeatnum = 0
        self.wavedata = []
        self.data = []
        self.beatidx = []
        #self.widget.axes.plot(data)
        #print("start")
        self.cnt = 0
        #打开文件
        self.pushButton.clicked.connect(lambda: self.btn_openFile_click())
        self.startbtn.clicked.connect(lambda:self.btn_start_click())
        self.db_btn.clicked.connect(lambda :self.btn_opendbtxt_click())
        #设置音乐进度
        self.slider_time.sliderMoved[int].connect(lambda: self.player.setPosition(self.slider_time.value()))

        # 计时器:控制进度条和进度时间
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.player_timer)

        #音乐可视化
        #self.visualization()

    def visualization(self):
        #plt.figure(figsize=(14, 5))
        #plt.title("Demo")

        params = self.wf.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        # 读取波形数据
        xminorLocator = MultipleLocator(20)

        str_data = self.wf.readframes(nframes)
        #print("str data",str_data)
        self.wf.close()
        # 将波形数据转换为数组
        #wave_data = np.fromstring(str_data, dtype=np.int16)
        wave_data = np.fromstring(str_data, dtype=np.short)
        time = np.arange(0, nframes) * (1.0 / framerate)
        self.time = time
        self.cnt = len(time)
        if nchannels==2:
            wave_data.shape = -1, 2
        wave_data = wave_data.T

        if nchannels==2:
            self.wavedata = wave_data[0]
            self.widget.axes.plot(time, wave_data[0], 'b')
        else:
            self.wavedata = wave_data
            self.widget.axes.plot(time,wave_data,'b')
        #wave_data = wave_data * 1.0 / (max(abs(wave_data)))

        #print("time",self.time.shape,"\nwave_data[0]",self.wavedata.shape)

        #print("time = ",self.time)
        #print(time)
        #ax = self.widget.axes.plot.xlim(0,500)
        #self.widget.axes.xaxis.set_minor_locator(xminorLocator)
        #self.widget.axes.axvline(self.player.position() / 1000)
        self.widget.draw()

        #print("end")

        #self.widget.show()

    def btn_openFile_click(self):
        self.playlist.clear()  # 读取歌曲前，清空playlist
        self.fileName, filetype = QFileDialog.getOpenFileName(self, '选择文件', '', '音频文件 (*.mp3; *.wav)')
        if len(self.fileName) == 0:
            print("取消选择")
            return
        else:
            print('当前歌曲路径：' + self.fileName)
            self.cur_song = os.path.basename(self.fileName)
            #self.lab_name.setText(self.cur_song)
            self.lineEdit.setText(self.cur_song)

            # 如果是mp3格式，则将mp3转换wav，保存到同一目录下
            if self.cur_song[-3:] == 'mp3':
                change_format(self.fileName)
                self.fileName = self.fileName.replace('mp3', 'wav')
                print('new' + self.fileName)

            # 将音频文件添加到playlist
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(self.fileName)))

            # 可视化部分wave
            self.wf = wave.open(self.fileName)
            #print("wave data",self.wf)
            #self.music, self.sr = librosa.load(self.fileName)

            self.visualization()
        if self.is_pause is False:
            self.player.pause()
            self.startbtn.setText('播放')

    def btn_start_click(self):

        if self.is_pause:
            self.is_pause = False
            self.player.play()
            self.startbtn.setText('暂停')
            print('当前播放歌曲： ' + self.cur_song)
        else:
            self.is_pause = True
            self.player.pause()
            self.startbtn.setText('播放')

    def btn_opendbtxt_click(self):
        self.dbtxt, filetype = QFileDialog.getOpenFileName(self, '选择文件', '', '文本文件 (*.txt; *.json)')
        #print(filetype)
        if self.dbtxt[-4:] == '.txt':
            print(self.dbtxt)
            if len(self.dbtxt) == 0:
                return
            data = np.loadtxt(self.dbtxt)
            #print(len(data))
            try:
                idx = np.argwhere(data[:,1]==1)
                self.idx = idx
                self.downbeatnum = len(idx)
                for i in range(len(data)):
                    self.widget.axes1.axvline(data[i,0],color='r')
                    if i in idx:
                        self.widget.axes2.axvline(data[i,0],color='g')
            except:
                for i in range(len(data)):
                    self.widget.axes1.axvline(data[i],color='r')
                #self.widget.axes1.axvline(data[i, 0], color='black')
        #self.widget.axes2.scatter(data[idx,0],data[idx,1],s=1.0)
        #self.widget.axes1.plot(data[:,0],data[:,1],'g')
        else:
            #print(self.dbtxt)
            #file = self.dbtxt[:-5] + '.json'
            self.data = np.load(self.dbtxt)
            #print(file)
            self.data = self.data['markers']
            print(self.data)
        self.widget.draw()
        #print(self.dbtxt)
    def player_timer(self):
        self.slider_time.setMinimum(0)
        self.slider_time.setMaximum(self.player.duration())
        if self.is_pause == False:
            self.slider_time.setValue(self.slider_time.value() + 1000)
        #print("slider time",self.slider_time.value())
        self.lab_time.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        #self.show_lab.setText(str(self.player.position()))
        #self.show_tim_lab.setText(str(self.slider_time.value()))
        #print(self.music_flag.text())
        music_num = (self.player.position()/1000)//100+1
        print(self.player.duration()/1000)
        print("play list:",self.player.playlist())
        len1 = 0
        len2 = 0
        try:
            if float(self.music_flag.text())!=music_num and len(self.time)!=0:
                time_idx = np.argwhere(self.time<=music_num*100)
                self.widget.axes.lines.remove(self.widget.axes.lines[0])
                #self.widget.axes.clf()
                self.widget.axes.plot(self.time[time_idx],self.wavedata[time_idx],'b')
                #self.widget.axes.xlim(music_num*100-100,music_num*100)
                self.widget.axes.set_xlim(music_num*100-100,music_num*100)
                #self.widget.axes.axvline
                #print('fig 1',len(self.widget.axes.lines))
                #plt.xlim([music_num*100-100,music_num*100])
                #self.music_flag.setText(str(music_num))
                # print(data[:,0])

                #self.widget.axes1.lines.remove(self.widget.axes1.lines[:-1])
                #self.widget.axes2.lines.remove(self.widget.axes2.lines[:-1])
                if len(self.data)!=0:
                    try:
                        self.beatidx = np.argwhere(self.data[:,0]<music_num*100)
                    except:
                        self.beatidx = np.argwhere(self.data < music_num * 100)
                #print(self.beatidx)
                self.widget.axes1.set_xlim(music_num * 100 - 100, music_num * 100)
                self.widget.axes2.set_xlim(music_num * 100 - 100, music_num * 100)
                try:
                    if len(self.beatidx)!=0:
                        for i in self.beatidx:
                            self.widget.axes1.axvline(self.data[i, 0], color='r')
                            if i in self.idx:
                                self.widget.axes2.axvline(self.data[i, 0], color='g')
                except:
                    for i in range(len(self.data)):
                        self.widget.axes1.axvline(self.data[i],color='r')
                    print("error")
        except:
            print("error")
            #print("music num",music_num)
        if len(self.widget.axes.lines)>3:
            #print("line1",len(self.widget.axes.lines))
            self.widget.axes.lines.remove(self.widget.axes.lines[3])
        #     #print(self.widget.axes.lines[1])
        #if len(self.widget.axes1.lines)>self.beatnum:
            #print("line2",len(self.widget.axes1.lines))
            #self.widget.axes1.lines.remove(self.widget.axes1.lines[self.beatnum])
        #if len(self.widget.axes2.lines)>self.downbeatnum:
            #print("line3", len(self.widget.axes2.lines))
            #self.widget.axes2.lines.remove(self.widget.axes2.lines[self.downbeatnum])
            #print("axes2",len(self.widget.axes2.lines))
            #print("axe1",len(self.widget.axes1.lines))
        self.widget.axes.axvline(self.player.position()/1000)
        #print("axv line",len(self.widget.axes.lines))
        #self.widget.axes1.axvline(self.player.position() / 1000)
        #self.widget.axes2.axvline(self.player.position() / 1000)
            #print(self.widget.axes.lines)
            #print("time", self.player.position()/1000)
        #print("beatnum",self.beatnum)
        #print("downbeatnum",self.downbeatnum)
        self.widget.draw()

        #print(len(self.widget.axes.lines))
        #if self.widget.axes.lines[1] != None:
            #print("line1",self.widget.axes.lines[1])

        self.lab_duration.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        #print('total time=',self.player.duration()/1000)
        # 进度条满了之后回零
        if self.player.duration() == self.slider_time.value():
            self.slider_time.setValue(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())
