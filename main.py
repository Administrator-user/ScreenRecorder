from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import ImageGrab
import numpy as np
import threading
import time
import cv2
import sys
import os

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
      def closeEvent(self,event):
            os.remove("TempFiles/tickShot.jpg")
            event.accept()

      #格式化文件大小
      def formatSize(self,size):
            resultSize = size
            units = ["B","KB","MB","GB"]
            unitIndex = 0
            while resultSize >= 1:
                  resultSize /= 1024
                  unitIndex += 1
            resultSize *= 1024
            unitIndex -= 1
            unit = units[unitIndex]
            result = str(round(resultSize,2))+unit
            return result

      def createGui(self):
            #获取屏幕大小
            desktop = QApplication.desktop()
            width = desktop.width()
            height = desktop.height()
            #设置窗口大小+标题+图标+无边框+透明度
            self.setFixedSize(width*0.66,height*0.75)
            self.setWindowTitle("ScreenRecorder-v2.0.0")
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
            tickImage.save("TempFiles/tickShot.jpg")
            tickShow.setStyleSheet('''
            QLabel{
                  background:#ececec;
                  border-style:outset;
                  border-radius:10px;
                  border-image:url(./TempFiles/tickShot.jpg);
            }
            ''')
            tickArea = QWidget(contents)
            tickAreaOpacity = QGraphicsOpacityEffect()
            tickAreaOpacity.setOpacity(0.6)
            tickArea.setGraphicsEffect(tickAreaOpacity)
            tickArea.setAutoFillBackground(True)
            tickArea.setStyleSheet('''
            QWidget{
                  background:#ececec;
                  border-style:outset;
                  border-radius:2px;
                  border:3px dashed #0088ff;
            }
            ''')
            tickArea.setFixedSize(width*0.125,height*0.125)
            tickArea.move(tickShow.x(),tickShow.y())
            #录制区域获取
            def changeTick():
                  try:
                        if tickScreen.isChecked():
                              #判断是否超出范围
                              if int(tickWidth.text()) > width:
                                    tickWidth.setText(str(width))
                              if int(tickHeight.text()) > height:
                                    tickHeight.setText(str(height))
                              if int(tickPosX.text()) > width-int(tickWidth.text()):
                                    tickPosX.setText(str(width-int(tickWidth.text())))
                              if int(tickPosY.text()) > height-int(tickHeight.text()):
                                    tickPosY.setText(str(height-int(tickHeight.text())))
                              #设置预览窗口大小
                              tickArea.setFixedSize(int(tickWidth.text())*0.25,
                                                    int(tickHeight.text())*0.25)
                              tickArea.move(tickShow.x()+int(tickPosX.text())*0.25,
                                            tickShow.y()+int(tickPosY.text())*0.25)
                              self.recordBox = (int(tickPosX.text()),int(tickPosY.text()),
                                           int(tickPosX.text())+int(tickWidth.text()),
                                           int(tickPosY.text())+int(tickHeight.text()))
                        else:
                              tickArea.setFixedSize(width*0.25,height*0.25)
                              tickArea.move(tickShow.x(),tickShow.y())
                              self.recordBox = (0,0,width,height)
                  except:
                        pass
            changeTick()
            tickWidth.textChanged.connect(changeTick)
            tickHeight.textChanged.connect(changeTick)
            tickPosX.textChanged.connect(changeTick)
            tickPosY.textChanged.connect(changeTick)
            fullScreen.toggled.connect(changeTick)
            tickScreen.toggled.connect(changeTick)
            #录制列表
            recTabs = QTabWidget(contents)
            recTabs.setIconSize(QSize(50,50))
            recTabs.setMovable(True)
            recTabs.setStyleSheet('''
            QTabWidget{
                  background:transparent;
                  border:none;
            }
            QTabWidget:tab-bar{
                  border:0px;
            }
            QTabBar{
                  border:none;
            }
            QTabBar:tab{
                  background:#0088ff;
                  border:none;
                  border-style:outset;
                  border-radius:0px;
                  border-width:0px;
                  border-top-left-radius:15px;
                  border-top-right-radius:15px;
                  min-width:170px;
                  min-height:70px;
                  font-family:Microsoft YaHei;
                  font-size:30px;
                  color:#000000;
                  padding:0px;
                  margin-left:3px;
            }
            QTabBar::tab:hover{
                  background:#22aefa;
                  color:#222222;
            }
            QTabBar::tab:selected{
                  background:#33cffb;
                  color:#333333;
            }
            ''')
            recTabs.setFixedSize(width*0.66,height*0.41)
            recTabs.move(0,height*0.3)
            videosWidget = QWidget()
            recTabs.addTab(videosWidget,
                           QIcon("./ctrlButtons/videoList/listTabIcon.svg"),"视频列表")
            videoTable = QTableWidget(0,5,videosWidget)
            videoTable.setHorizontalHeaderLabels(["名称","类型","创建时间","时长","大小"])
            videoTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            videoTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            videoTable.setSelectionBehavior(QAbstractItemView.SelectRows)
            videoTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            videoTable.setStyleSheet('''
            QTableWidget{
                  border:none;
                  border-style:outset;
                  border-radius:10px;
                  border-width:2px;
                  border-color:#0088ff;
            }
            QTableWidget:item{
                  font-family:Microspft YaHei;
                  font-size:25px;
                  background:#ececec;
                  color:#000000;
            }
            QTableWidget::item:selected{
                  background:#66aaff;
                  color:#222222;
            }
            ''')
            videoTable.horizontalHeader().setStyleSheet('''
            QHeaderView{
                  border:none;
                  border-style:outset;
                  border-radius:0px;
                  border-top-left-radius:5px;
                  border-top-right-radius:5px;
                  border-color:#0088ff;
                  border-width:2px;
            }
            QHeaderView:section{
                  font-family:Microsoft YaHei;
                  font-size:25px;
            }
            ''')
            videoTable.horizontalHeader().setHighlightSections(False)
            videoTable.verticalHeader().setStyleSheet('''
            QHeaderView{
                  border:none;
                  border-style:outset;
                  border-radius:0px;
                  border-top-left-radius:5px;
                  border-bottom-left-radius:5px;
                  border-color:#0088ff;
                  border-width:2px;
            }
            QHeaderView:section{
                  font-family:Consolas;
                  font-size:25px;
            }
            ''')
            videoTable.setFixedSize(width*0.645,height*0.32)
            videoTable.move(width*0.005,height*0.01)
            #遍历videos文件夹
            videoList = os.listdir("./videos")
            videoTable.setRowCount(len(videoList))
            for i in range(len(videoList)):
                  name = videoList[i]
                  videoTable.setItem(i,0,QTableWidgetItem(name))
                  fileType = name.split(".")[1]+"文件"
                  videoTable.setItem(i,1,QTableWidgetItem(fileType))
                  
                  '''
                  格式化时间
                  原因:time.strftime()无法直接对os.path.getctime()的返回值格式化
                  执行流程:
                  1.获取创建时间;
                  2.使用time.ctime()转换时间格式并拆分;
                  3.列出月份列表(time.ctime()格式化后月份是字母格式);
                  4.格式化为tuple形式(年份,月份,日期,时,分,秒,1,1,0)
                  (倒数第2~3个在后方无需使用,可直接用任意数字代替);
                  5.将tuple中内容全部转为int形式;
                  6.使用time.strftime()进行格式化;
                  7.以str形式添加进QTableWidget中;
                  '''
                  createTime = os.path.getctime("videos/"+name)
                  cList = time.ctime(createTime).split()
                  monthList = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep",
                               "Oct","Nov","Dec"]
                  formatTime = (cList[4],monthList.index(cList[1])+1,cList[2],cList[3][0:2],
                                cList[3][3:5],cList[3][6:8],1,1,0)
                  formatTime = tuple([int(x) for x in formatTime])
                  formatTime = time.strftime("%Y/%m/%d %H:%M:%S",formatTime)
                  videoTable.setItem(i,2,QTableWidgetItem(str(formatTime)))
                  
                  unFormatSize = os.path.getsize("videos/"+name)
                  fileSize = self.formatSize(unFormatSize)
                  videoTable.setItem(i,4,QTableWidgetItem(fileSize))
            #提示组件
            videoTips = QWidget(videosWidget)
            videoTips.setStyleSheet('''
            QWidget{
                  border:none;
                  background:#transparent;
                  border-radius:15px;
                  border-image:url(./ctrlButtons/videoList/tipsImage.png);
            }
            ''')
            videoTips.setFixedSize(width*0.215,height*0.24)
            videoTips.move(width*0.22,height*0.07)
            if videoTable.rowCount() < 1:
                  videoTips.show()
            else:
                  videoTips.hide()
            #清空列表
            def clearList():
                  for f in os.listdir("videos"):
                        os.remove("videos/"+f)
                  videoTable.setRowCount(0)
                  videoTips.show()
            clearAll = QToolButton(videosWidget)
            clearAll.setStyleSheet('''
            QToolButton{
                  border:none;
                  border-radius:10px;
                  background:#ececec;
                  border-image:url(./ctrlButtons/videoList/cleanList.svg);
            }
            QToolButton:hover{
                  background:#cfcfcf;
            }
            QToolButton:pressed{
                  background:#bfbfbf;
            }
            ''')
            clearAll.setFixedSize(width*0.022,width*0.022)
            clearAll.move(width*0.007,height*0.332)
            clearAll.clicked.connect(clearList)
            
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
            #添加行
            def addInfo(itemName,itemDate,itemTime):
                  rowsPlus = videoTable.rowCount()+1
                  videoTable.setRowCount(rowsPlus)
                  videoTable.setItem(rowsPlus-1,0,QTableWidgetItem(itemName))
                  videoTable.setItem(rowsPlus-1,1,QTableWidgetItem("avi文件"))
                  videoTable.setItem(rowsPlus-1,2,QTableWidgetItem(itemDate))
                  videoTable.setItem(rowsPlus-1,3,QTableWidgetItem(itemTime))
                  itemSize = self.formatSize(os.path.getsize("videos/"+itemName))
                  videoTable.setItem(rowsPlus-1,4,QTableWidgetItem(itemSize))
            def stopRecord():
                  self.escRec = True
                  #还原窗口
                  self.setFixedSize(width*0.66,height*0.75)
                  self.move(stopGrabX,stopGrabY)
                  titleBar.show()
                  contents.show()
                  recWidget.hide()
                  minbtn.setEnabled(True)
                  maxbtn.setEnabled(True)
                  closebtn.setEnabled(True)
                  #删除空行
                  for n in range(videoTable.rowCount()):
                        if not videoTable.item(n,0).text():
                              videoTable.removeRow(n)
                  #判断行数
                  if videoTable.rowCount() < 1:
                        videoTips.show()
                  else:
                        videoTips.hide()
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
            #暂停录制
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
            self.returnTime = "00:00"
            def displayTime():
                  global recTime
                  recTime = 0
                  self.returnTime = "00:00"
                  while True:
                        if self.isRecording or not self.escRec:
                              time.sleep(1)
                              recTime += 1
                              recMin = str(int(recTime/60))
                              recSec = str(recTime%60)
                              if int(recMin)<10:
                                    recMin = "0"+str(recMin)
                              if int(recSec)<10:
                                    recSec = "0"+str(recSec)
                              self.returnTime = recMin+":"+recSec
                              recTimer.display(self.returnTime)
                        else:
                              recTime = 0
                              continue
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
                  stopName = recTime+".avi"
                  stopDate = time.strftime("%Y/%m/%d %H:%M:%S",currentTime)
                  videoName = "videos/"+recTime+".avi"
                  video = cv2.VideoWriter(videoName,cv2.VideoWriter_fourcc(*"XVID"),
                                          fps,(heightS,widthS))#创建视频
                  imgNum = 0
                  recTimer.display(start)
                  for i in range(start):
                        time.sleep(1)
                        recTimer.display(start-i)
                  timerThread = threading.Thread(target=displayTime,
                                                 name="TimeDisplay")
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
                  addInfo(stopName,stopDate,self.returnTime)
                  stopRecord()
                  video.release()
                  cv2.destroyAllWindows()
                  time.sleep(0.3)
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
                        self.escRec = False
                        isRecording = True
                        recordThread = threading.Thread(target=record,
                                                        name="Recorder")
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
      print('''ScreenRecorder v2.0.0
made by Administrator-user
Loading project...''')
      window = grabWindow()
      sys.exit(app.exec)
