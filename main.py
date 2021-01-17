from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import ImageGrab
import numpy as np
import threading
import time
import cv2
import sys

class grabWindow(QWidget):
      def __init__(self):
            super().__init__()
            self.createGui()

      def mousePressEvent(self, event):
            if event.button()==Qt.LeftButton and not self.isMaximized():
                  self.m_flag=True
                  self.m_Position=event.globalPos()-self.pos()
                  event.accept()
                  self.setCursor(QCursor(Qt.SizeAllCursor))   
      def mouseMoveEvent(self, QMouseEvent):
            if Qt.LeftButton and self.m_flag and not self.isMaximized():  
                  self.move(QMouseEvent.globalPos()-self.m_Position)#更改窗口位置
                  QMouseEvent.accept()
      def mouseReleaseEvent(self, QMouseEvent):
            self.m_flag=False
            self.setCursor(QCursor(Qt.ArrowCursor))

      def createGui(self):
            #获取屏幕大小
            desktop = QApplication.desktop()
            width = desktop.width()
            height = desktop.height()
            #设置窗口大小+标题+图标+无边框+透明度
            self.setFixedSize(width*0.66,height*0.75)
            self.setWindowTitle("​")
            self.setWindowIcon(QIcon("./icon.png"))
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setWindowOpacity(0.9)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAcceptDrops(True)

            #标题栏
            titleBar = QWidget(self)
            titleBar.setFixedSize(width*0.66,height*0.04)
            titleBar.setStyleSheet('''
            QWidget{
                  background:#008dd7;
                  border-style:outset;
                  border-top-left-radius:15px;
                  border-top-right-radius:15px;
            }
            ''')
            #标题栏按键
            minbtn = QToolButton(titleBar)
            maxbtn = QToolButton(titleBar)
            closebtn = QToolButton(titleBar)
            for btn in [minbtn,maxbtn,closebtn]:
                  btn.setFixedSize(height*0.02,height*0.02)
            minbtn.setShortcut("Alt+N")
            maxbtn.setShortcut("Alt+X")
            closebtn.setShortcut("Alt+F4")
            minbtn.setToolTip("最小化(Alt+N)")
            maxbtn.setToolTip("最大化(Alt+X)")
            closebtn.setToolTip("关闭(Alt+F4)")
            minbtn.setStyleSheet('''
            QToolButton{
                  background:#00ff00;
                  border-style:outset;
                  border-radius:5px;
            }
            QToolButton:hover{
                  background:#00dd00;
            }
            QToolButton:pressed{
                  background:#00cc00;
            }
            ''')
            maxbtn.setStyleSheet('''
            QToolButton{
                  background:#eeee00;
                  border-style:outset;
                  border-radius:5px;
            }
            QToolButton:hover{
                  background:#cccc00;
            }
            QToolButton:pressed{
                  background:#bbbb00;
            }
            ''')
            closebtn.setStyleSheet('''
            QToolButton{
                  background:#ff3333;
                  border-style:outset;
                  border-radius:5px;
            }
            QToolButton:hover{
                  background:#dd1111;
            }
            QToolButton:pressed{
                  background:#cc0000;
            }
            ''')
            titleLay = QHBoxLayout(titleBar)
            titleLay.setAlignment(Qt.AlignTop)
            titleLay.setAlignment(Qt.AlignRight)
            titleLay.addWidget(minbtn)
            titleLay.addWidget(maxbtn)
            titleLay.addWidget(closebtn)
            #组件栏
            contents = QWidget(self)
            contents.setFixedSize(width*0.66,height*0.71)
            contents.setStyleSheet('''
            QWidget{
                  background:#ececec;
                  border-style:outset;
                  border-bottom-left-radius:15px;
                  border-bottom-right-radius:15px;
                  border-color:#008dd7;
                  border-width:3px;
            }
            ''')
            contents.move(0,height*0.04)
            #窗口默认按键功能
            def showMin():
                  self.showMinimized()
            minbtn.clicked.connect(showMin)
            def showMax():
                  if self.isMaximized():
                        self.showNormal()
                        titleBar.setFixedSize(width*0.66,height*0.04)
                        contents.setFixedSize(width*0.66,height*0.71)
                  else:
                        self.showMaximized()
                        titleBar.setFixedSize(width,height*0.04)
                        contents.setFixedSize(width,height*0.96)
                        contents.move(0,height*0.04)
            maxbtn.clicked.connect(showMax)
            def close():
                  self.close()
            closebtn.clicked.connect(close)
            #录制按键
            recbtn = QPushButton(contents)
            recbtn.setStyleSheet('''
            QPushButton{
                  background:#ececec;
                  border-image:url(./ctrlButtons/startRecord.png);
            }
            QPushButton:hover{
                  background:#dbdbdb;
            }
            QPushButton:pressed{
                  background:#cecece;
            }
            ''')
            recbtn.setFixedSize(width*0.15,width*0.15)
            recbtn.move(width*0.02,height*0.03)
            #全屏/部分录制
            areaTitle = QLabel("区域设置",contents)
            areaTitle.setFixedSize(width*0.07,height*0.03)
            areaTitle.setStyleSheet('''
            QLabel{
                  background:transparent;
                  font-family:Microsoft YaHei;
                  font-size:45px;
                  color:#0088ff;
                  border:none;
            }
            ''')
            areaTitle.move(width*0.19,height*0.03)
            fullScreen = QRadioButton("全屏录制",contents)
            fullScreen.setStyleSheet('''
            QRadioButton{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:35px;
            }
            QRadioButton:indicator{
                  background:#ececec;
                  border:2px solid #000000;
                  border-radius:15px;
            }
            QRadioButton::indicator:checked{
                  background:#0099ff;
                  border:2px solid #000000;
            }
            QRadioButton::indicator::unchecked{
                  background:#ececec;
                  border:2px solid #000000;
            }
            ''')
            fullScreen.setChecked(True)
            fullScreen.setFixedSize(width*0.1,height*0.03)
            fullScreen.move(width*0.195,height*0.08)
            tickScreen = QRadioButton("区域录制",contents)
            tickScreen.setStyleSheet('''
            QRadioButton{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:35px;
            }
            QRadioButton:indicator{
                  background:#ececec;
                  border:2px solid #000000;
                  border-radius:15px;
            }
            QRadioButton::indicator:checked{
                  background:#0099ff;
                  border:2px solid #000000;
            }
            QRadioButton::indicator::unchecked{
                  background:#ececec;
                  border:2px solid #000000;
            }
            ''')
            tickScreen.setFixedSize(width*0.1,height*0.03)
            tickScreen.move(width*0.195,height*0.11)
            #选区宽/高/坐标设置
            tickWidth = QLineEdit(contents)
            tickWidth.setAlignment(Qt.AlignCenter)
            tickWidth.setValidator(QIntValidator(1,width,self))
            tickWidth.setText(str(int(width*0.5)))
            tickWidth.setStyleSheet('''
            QLineEdit{
                  backcground:#ececec;
                  border-style:outset;
                  border-radius:10px;
                  border-color:#008dd7;
                  border-width:2px;
                  font-family:Microsoft YaHei;
                  font-size:30px;
            }
            ''')
            tickWidth.setFixedSize(width*0.05,height*0.03)
            tickWidth.move(width*0.26,height*0.11)
            tickMulti = QLabel("*",contents)
            tickMulti.setStyleSheet('''
            QLabel{
                  font-family:Microsoft YaHei;
                  font-size:30px;
                  border:none
            }
            ''')
            tickMulti.setFixedSize(width*0.005,height*0.03)
            tickMulti.move(width*0.312,height*0.11)
            tickHeight = QLineEdit(contents)
            tickHeight.setAlignment(Qt.AlignCenter)
            tickHeight.setValidator(QIntValidator(1,height,self))
            tickHeight.setText(str(int(height*0.5)))
            tickHeight.setStyleSheet('''
            QLineEdit{
                  backcground:#ececec;
                  border-style:outset;
                  border-radius:10px;
                  border-color:#008dd7;
                  border-width:2px;
                  font-family:Microsoft YaHei;
                  font-size:30px;
            }
            ''')
            tickHeight.setFixedSize(width*0.05,height*0.03)
            tickHeight.move(width*0.317,height*0.11)
            #录制区域X/Y坐标
            posLabel = QLabel("坐标:",contents)
            posLabel.setStyleSheet('''
            QLabel{
                  font-family:Microsoft YaHei;
                  font-size:35px;
                  border:none;
            }
            ''')
            posLabel.setFixedSize(width*0.03,height*0.03)
            posLabel.move(width*0.233,height*0.142)
            #区域X坐标
            tickPosX = QLineEdit(contents)
            tickPosX.setAlignment(Qt.AlignCenter)
            tickPosX.setValidator(QIntValidator(1,height,self))
            tickPosX.setText("0")
            tickPosX.setStyleSheet('''
            QLineEdit{
                  backcground:#ececec;
                  border-style:outset;
                  border-radius:10px;
                  border-color:#008dd7;
                  border-width:2px;
                  font-family:Microsoft YaHei;
                  font-size:30px;
            }
            ''')
            tickPosX.setFixedSize(width*0.05,height*0.03)
            tickPosX.move(width*0.26,height*0.142)
            #间隔符
            tickInterval = QLabel(",",contents)
            tickInterval.setStyleSheet('''
            QLabel{
                  font-family:Microsoft YaHei;
                  font-size:30px;
                  border:none
            }
            ''')
            tickInterval.setFixedSize(width*0.005,height*0.03)
            tickInterval.move(width*0.312,height*0.144)
            #区域Y坐标
            tickPosY = QLineEdit(contents)
            tickPosY.setAlignment(Qt.AlignCenter)
            tickPosY.setValidator(QIntValidator(1,height,self))
            tickPosY.setText("0")
            tickPosY.setStyleSheet('''
            QLineEdit{
                  background:#ececec;
                  border-style:outset;
                  border-radius:10px;
                  border-color:#008dd7;
                  border-width:2px;
                  font-family:Microsoft YaHei;
                  font-size:30px;
            }
            ''')
            tickPosY.setFixedSize(width*0.05,height*0.03)
            tickPosY.move(width*0.317,height*0.142)
            #录制区域预览
            tickShow = QLabel(contents)
            tickShow.setFixedSize(width*0.25,height*0.25)
            tickShow.move(width*0.37,height*0.03)
            tickImage = ImageGrab.grab()
            tickImage.save("tickShot.jpg")
            tickShow.setStyleSheet('''
            QLabel{
                  background:#ececec;
                  border-style:outset;
                  border-radius:10px;
                  border-image:url(./tickShot.jpg);
            }
            ''')
            tickArea = QWidget(contents)
            tickArea.setStyleSheet('''
            QWidget{
                  background:#0088ff;
                  border:style:outset;
                  border-radius:0px;
            }
            ''')
            tickArea.setFixedSize(width*0.125,height*0.125)
            tickArea.move(tickShow.x(),tickShow.y())
            #录制区域元组
            self.recordBox = (int(tickPosX.text()),int(tickPosY.text()),
                              int(tickPosX.text())+int(tickWidth.text()),
                              int(tickPosY.text())+int(tickHeight.text()))
            def changeTick():
                  try:
                        tickArea.setFixedSize(int(tickWidth.text())*0.25,
                                              int(tickHeight.text())*0.25)
                        tickArea.move(tickShow.x()+int(tickPosX.text())*0.25,
                                      tickShow.y()+int(tickPosY.text())*0.25)
                        self.recordBox = (int(tickPosX.text()),int(tickPosY.text()),
                                     int(tickPosX.text())+int(tickWidth.text()),
                                     int(tickPosY.text())+int(tickHeight.text()))
                  except:
                        pass
            tickWidth.textChanged.connect(changeTick)
            tickHeight.textChanged.connect(changeTick)
            tickPosX.textChanged.connect(changeTick)
            tickPosY.textChanged.connect(changeTick)
            #录制组件
            recWidget = QWidget(self)
            recWidget.setFixedSize(width*0.4,height*0.05)
            recWidget.setStyleSheet('''
            QWidget{
                  background:#ececec;
                  border:none;
                  border-style:outset;
                  border-radius:10px;
                  border-color:#008dd7;
                  border-width:3px;
            }
            ''')
            recWidget.hide()
            #计时组件
            recTimer = QLCDNumber(recWidget)
            recTimer.setSegmentStyle(QLCDNumber.Flat)
            recTimer.setStyleSheet('''
            QLCDNumber{
                  background:transparent;
                  border:2px solid #0000ff;
                  color:#0066ff;
            }
            ''')
            recTimer.setFixedSize(width*0.1,height*0.04)
            recTimer.move(width*0.005,height*0.005)
            recTime = 0
            recTimer.display(str(int(recTime/60))+":"+str(recTime%60))
            #停止录制
            stopbtn = QToolButton(recWidget)
            self.escRec = False
            stopbtn.setStyleSheet('''
            QToolButton{
                  background:#ff3333;
                  border-style:outset;
                  border-radius:7px;
                  border-width:0px;
            }
            QToolButton:hover{
                  background:#dd1111;
            }
            QToolButton:pressed{
                  background:#cc0000;
            }
            ''')
            stopbtn.setToolTip("停止(Ctrl+Q)")
            stopbtn.setShortcut("Ctrl+Q")
            stopbtn.setFixedSize(width*0.02,width*0.02)
            stopbtn.move(width*0.135,height*0.01)
            def stopRecord():
                  self.escRec = True
                  self.setFixedSize(width*0.66,height*0.75)
                  self.move(stopGrabX,stopGrabY)
                  titleBar.show()
                  contents.show()
                  recWidget.hide()
                  minbtn.setEnabled(True)
                  maxbtn.setEnabled(True)
                  closebtn.setEnabled(True)
            stopbtn.clicked.connect(stopRecord)
            #暂停录制
            pausebtn = QToolButton(recWidget)
            self.isRecording = True
            pausebtn.setStyleSheet('''
            QToolButton{
                  background:#ececec;
                  border-style:outset;
                  border-radius:7px;
                  border-width:0px;
                  border-image:url(./ctrlButtons/pauseRecord.png)
            }
            QToolButton:hover{
                  background:#d0d0d0;
            }
            QToolButton:pressed{
                  background:#bababa;
            }
            ''')
            pausebtn.setToolTip("暂停(Ctrl+P)")
            pausebtn.setShortcut("Ctrl+P")
            pausebtn.setFixedSize(width*0.02,width*0.02)
            pausebtn.move(width*0.11,height*0.01)
            def determinePause():
                  if self.isRecording:
                        pausebtn.setStyleSheet('''
                        QToolButton{
                              background:#ececec;
                              border-style:outset;
                              border-radius:7px;
                              border-width:0px;
                              border-image:url(./ctrlButtons/continueRecord.png)
                        }
                        QToolButton:hover{
                              background:#d0d0d0;
                        }
                        QToolButton:pressed{
                              background:#bababa;
                        }
                        ''')
                        self.isRecording = False
                  else:
                        pausebtn.setStyleSheet('''
                        QToolButton{
                              background:#ececec;
                              border-style:outset;
                              border-radius:7px;
                              border-width:0px;
                              border-image:url(./ctrlButtons/pauseRecord.png)
                        }
                        QToolButton:hover{
                              background:#d0d0d0;
                        }
                        QToolButton:pressed{
                              background:#bababa;
                        }
                        ''')
                        self.isRecording = True
            pausebtn.clicked.connect(determinePause)
            #时间记录
            def displayTime():
                  global recTime
                  recTime = 0
                  while True:
                        if self.isRecording:
                              time.sleep(1)
                              recTime += 1
                              recMin = str(int(recTime/60))
                              recSec = str(recTime%60)
                              if int(recMin)<10:
                                    recMin = "0"+str(recMin)
                              if int(recSec)<10:
                                    recSec = "0"+str(recSec)
                              recTimer.display(recMin+":"+recSec)
            #录制功能
            def record():
                  fps = 24#帧率
                  start = 3#延时
                  recordTick = tickScreen.isChecked()
                  if recordTick:
                        currentScreen = ImageGrab.grab(self.recordBox)#获取区域
                  else:
                        currentScreen = ImageGrab.grab()#获取全屏
                  heightS,widthS = currentScreen.size
                  currentTime = time.localtime()
                  recTime = time.strftime("%Y%m%d-%H%M%S",currentTime)
                  videoName = "videos/"+recTime+".avi"
                  video = cv2.VideoWriter(videoName,cv2.VideoWriter_fourcc(*"XVID"),
                                          fps,(heightS,widthS))#创建视频
                  imgNum = 0
                  recTimer.display(start)
                  for i in range(start):
                        time.sleep(1)
                        recTimer.display(start-i)
                  timerThread = threading.Thread(target=displayTime)
                  timerThread.start()
                  while True:
                        if self.isRecording:
                              imgNum += 1
                              if recordTick:
                                    captureImg = ImageGrab.grab(self.recordBox)#获取区域
                              else:
                                    captureImg = ImageGrab.grab()#获取全屏
                              frame = cv2.cvtColor(np.array(captureImg),cv2.COLOR_RGB2BGR)
                              video.write(frame)#写入视频
                        if self.escRec:
                              break
                  stopRecord()
                  video.release()
                  cv2.destroyAllWindows()
            def grabReady():
                  try:
                        global stopGrabX
                        global stopGrabY
                        stopGrabX = self.x()
                        stopGrabY = self.y()
                        self.setFixedSize(width*0.4,height*0.05)
                        titleBar.hide()
                        contents.hide()
                        recWidget.show()
                        self.move(width*0.58,height*0.87)
                        minbtn.setEnabled(False)
                        maxbtn.setEnabled(False)
                        closebtn.setEnabled(False)
                        escRec = False
                        isRecording = True
                        recordThread = threading.Thread(target=record)
                        recordThread.start()
                  except Exception as exc:
                        print(exc)
            def startRecord():
                  try:
                        grabReady()
                  except Exception as exc:
                        print(exc)
            recbtn.clicked.connect(startRecord)

            self.show()

if __name__ == "__main__":
      app = QApplication(sys.argv)
      print('''
ScreenRecorder-v1.0.0
made by Administrator-user
Loading project...''')
      window = grabWindow()
      sys.exit(app.exec)
