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

    def __init__(self, parent=None, width=14, height=5, dpi=100):
        plt.rcParams['font.family'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = self.fig.add_subplot(2, 1, 1)
        #self.axes1 = self.fig.add_subplot(2, 1, 2)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        self.setWindowTitle("音乐播放器^_^")
        self.setWindowIcon(QIcon('icon/音乐.png'))
        self.fileName = ""
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
        #画图测试
        self.widget = Mydemo(width=500, height=5, dpi=100)
        self.verticalLayout.addWidget(self.widget)
        #data = list(range(1000))
        #self.widget.axes.plot(data)
        #print("start")
        self.cnt = 0
        #打开文件
        self.pushButton.clicked.connect(lambda: self.btn_openFile_click())
        self.startbtn.clicked.connect(lambda:self.btn_start_click())
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
        self.wf.close()
        # 将波形数据转换为数组
        wave_data = np.frombuffer(str_data, dtype=np.short)

        wave_data.shape = -1, 2
        wave_data = wave_data.T
        time = np.arange(0, nframes) * (1.0 / framerate)
        # 绘制波形
        # plt.subplot(211)
        #plt.plot(time, wave_data[0])
        # plt.subplot(212)
        self.cnt = len(time)
        self.widget.axes.plot(time, wave_data[0])
        #print(time)
        #ax = self.widget.axes.plot.xlim(0,500)
        self.widget.axes.xaxis.set_minor_locator(xminorLocator)
        self.widget.axes.axvline(self.player.position() / 1000)
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

    def player_timer(self):
        self.slider_time.setMinimum(0)
        self.slider_time.setMaximum(self.player.duration())
        self.slider_time.setValue(self.slider_time.value() + 1000)

        self.lab_time.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        #self.show_lab.setText(str(self.player.position()))
        #print("test",self.player.position()/1000)
        #print(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        #self.show_tim_lab.setText(str(self.slider_time.value()))
        try:
            self.cnt = (self.player.position())/(self.player.duration())
            #print("cnt=",self.cnt)
            
            self.widget.axes.axvline(self.player.position()/1000)
            print("time", self.player.position()/1000)
            self.widget.draw()
        except:
            print("dur time",self.player.position())

        self.lab_duration.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))

        # 进度条满了之后回零
        if self.player.duration() == self.slider_time.value():
            self.slider_time.setValue(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())
