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
            #录制组件
            recWidget = QWidget(self)
            recWidget.setFixedSize(width*0.4,height*0.05)
            recWidget.setStyleSheet('''
            QWidget{
                  background:#ececec;
                  border-style:outset;
                  border-radius:15px;
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
            def displayTime():
                  global recTime
                  recTime = 0
                  while True:
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
                  wait = 1/fps
                  start = 3#延时
                  currentScreen = ImageGrab.grab()
                  heightS,widthS = currentScreen.size
                  video = cv2.VideoWriter("testVideo.avi",cv2.VideoWriter_fourcc(*"XVID"),
                                          fps,(heightS,widthS))#创建视频
                  imgNum = 0
                  recTimer.display(start)
                  for i in range(start):
                        time.sleep(1)
                        recTimer.display(start-i)
                  timerThread = threading.Thread(target=displayTime)
                  timerThread.start()
                  while True:
                        imgNum += 1
                        captureImg = ImageGrab.grab()#获取屏幕
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
      window = grabWindow()
      sys.exit(app.exec)
