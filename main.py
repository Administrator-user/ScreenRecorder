from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import ImageGrab
import pyaudio
import wave
import numpy as np
import threading
import time
import cv2
import sys
import os
import formatTools
import fileMerger

class grabWindow(QWidget):
      def __init__(self):
            super().__init__()
            apperPf = open("./apperanceProfile.inf","a+")
            apperPf.seek(0)
            apperInf = apperPf.read()
            assert apperInf[0]=="#" and len(apperInf)==7,"SYNTAX_ERROR-apperanceProfile.inf:Can't convert file contents to HEX color value"
            self.apperColor = apperInf
            self.fps = cv2.CAP_PROP_FPS
            self.createGui()
            self.posX = self.x()
            self.posY = self.y()
            self.m_flag = False
            self.delayTime = 3
            self.currentFourcc = "XVID"

      def mousePressEvent(self, event):
            if event.button()==Qt.LeftButton and not self.isMaximized():
                  self.m_flag=True
                  self.m_Position=event.globalPos()-self.pos()
                  event.accept()
                  self.setCursor(QCursor(Qt.SizeAllCursor))   
      def mouseMoveEvent(self, QMouseEvent):
            if Qt.LeftButton and self.m_flag and not self.isMaximized():  
                  self.move(QMouseEvent.globalPos()-self.m_Position)#更改窗口位置
                  self.posX = self.x()
                  self.posY = self.y()
                  QMouseEvent.accept()
      def mouseReleaseEvent(self, QMouseEvent):
            self.m_flag=False
            self.setCursor(QCursor(Qt.ArrowCursor))
      def closeEvent(self,event):
            os.remove("TempFiles/tickShot.jpg")
            event.accept()

      def createGui(self):
            #获取屏幕大小
            desktop = QApplication.desktop()
            width = desktop.width()
            height = desktop.height()
            #设置窗口大小+标题+图标+无边框+透明度
            self.setFixedSize(width*0.66,height*0.75)
            self.setWindowTitle("ScreenRecorder-v2.2.3")
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
                  background:#ececec;
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
                  background:#ececec;
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
                  background:#ececec;
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
            #录制列表/设置
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
            #视频列表
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
            def videoScanner():
                  videoList = os.listdir("./videos")
                  videoTable.setRowCount(len(videoList))
                  throwError = False
                  for i in range(len(videoList)):
                        name = videoList[i]
                        videoTable.setItem(i,0,QTableWidgetItem(name))
                        fileType = name.split(".")[1].upper()+"文件"
                        videoTable.setItem(i,1,QTableWidgetItem(fileType))
                        
                        createTime = os.path.getctime("videos/"+name)
                        formattedTime = formatTools.formatCtime(createTime)
                        videoTable.setItem(i,2,QTableWidgetItem(str(formattedTime)))

                        lenInf = open("./TempFiles/lengthInfo.txt","a+")
                        lenInf.seek(0)
                        lengths = lenInf.read()
                        try:
                              lenDict = eval(lengths)
                        except:
                              throwError = True
                              lenDict = {}
                        if name in lenDict:
                              videoTable.setItem(i,3,QTableWidgetItem(lenDict[name]))
                        else:
                              videoTable.setItem(i,3,QTableWidgetItem("/"))
                        lenInf.close()
                        
                        unFormatSize = os.path.getsize("videos/"+name)
                        fileSize = formatTools.formatSize(unFormatSize)
                        videoTable.setItem(i,4,QTableWidgetItem(fileSize))
            videoScanner()
            #提示组件
            videoTips = QWidget(videosWidget)
            videoTips.setStyleSheet('''
            QWidget{
                  border:none;
                  background:transparent;
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
            #刷新列表
            flushbtn = QToolButton(videosWidget)
            flushbtn.setStyleSheet('''
            QToolButton{
                  border:none;
                  border-radius:10px;
                  background:#ececec;
                  border-image:url(./ctrlButtons/videoList/refresh.svg);
            }
            QToolButton:hover{
                  background:#cfcfcf;
            }
            QToolButton:pressed{
                  background:#bfbfbf;
            }
            ''')
            flushbtn.setToolTip("刷新")
            flushbtn.setFixedSize(width*0.022,width*0.022)
            flushbtn.move(width*0.007,height*0.332)
            flushbtn.clicked.connect(videoScanner)
            #删除选中项
            def clearSelect():
                  clearItems = videoTable.selectedItems()
                  #获取选中行"名称"值+行号
                  clearNameItems = [i for i in clearItems if clearItems.index(i)%5==0]
                  clearNames = [i.text() for i in clearItems if clearItems.index(i)%5==0]
                  clearRows = [i.row() for i in clearItems if clearItems.index(i)%5==0]
                  #清空选中行"名称"值
                  for i in clearRows:
                        videoTable.setItem(i,0,QTableWidgetItem())
                  #删除选中项
                  for i in range(videoTable.rowCount()):
                        itemText = videoTable.itemAt(i,0).text()
                        if not itemText:
                              videoTable.removeRow(i)
                  #删除文件
                  for i in clearNames:
                        os.remove("videos/"+i)
                  #删除字典键值对
                  lenInfo = open("./TempFiles/lengthInfo.txt","a+")
                  lenInfo.seek(0)
                  try:
                        oldDict = eval(lenInfo.read())
                  except:
                        oldDict = {}
                  lenInfo.truncate(0)
                  for n in clearNames:
                        if n in oldDict:
                              del oldDict[n]
                  newDict = str(oldDict)
                  lenInfo.write(newDict)
                  lenInfo.close()
                  #判断行数
                  if videoTable.rowCount() < 1:
                        videoTips.show()
                  else:
                        videoTips.hide()
            clearSelection = QToolButton(videosWidget)
            clearSelection.setStyleSheet('''
            QToolButton{
                  border:none;
                  border-radius:10px;
                  background:#ececec;
                  border-image:url(./ctrlButtons/videoList/cleanSelect.svg);
            }
            QToolButton:hover{
                  background:#cfcfcf;
            }
            QToolButton:pressed{
                  background:#bfbfbf;
            }
            ''')
            clearSelection.setToolTip("删除选中项")
            clearSelection.setFixedSize(width*0.022,width*0.022)
            clearSelection.move(width*0.03,height*0.332)
            clearSelection.clicked.connect(clearSelect)
            #清空列表
            def clearList():
                  for f in os.listdir("videos"):
                        os.remove("videos/"+f)
                  lenFile = open("./TempFiles/lengthInfo.txt","a+")
                  lenFile.truncate(0)
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
            clearAll.setToolTip("清空列表")
            clearAll.setFixedSize(width*0.022,width*0.022)
            clearAll.move(width*0.053,height*0.332)
            clearAll.clicked.connect(clearList)
            #设置
            setupWidget = QWidget()
            recTabs.addTab(setupWidget,
            QIcon("./ctrlButtons/videoSetup/setupTabIcon.png"),"设置")
            recSetup = QWidget(setupWidget)
            recSetup.setStyleSheet('''
            QWidget{
                  background:transparent;
                  border:none;
                  border-style:outset;
                  border-radius:0px;
                  border-top-left-radius:15px;
                  border-color:#008dd7;
                  border-width:2px;
            }
            ''')
            recSetup.setFixedSize(width*0.3,height*0.2)
            recSetup.move(width*0.01,height*0.01)
            recLabel = QLabel("录制设置",recSetup)
            recLabel.setStyleSheet('''
            QLabel{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:35px;
                  color:#008dd7;
            }
            ''')
            recLabel.setFixedSize(width*0.05,height*0.02)
            recLabel.move(width*0.01,height*0.01)
            # 帧率设置
            fpsLabel = QLabel("FPS:",recSetup)
            fpsLabel.setStyleSheet('''
            QLabel{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:30px;
                  color:#000000;
            }
            ''')
            fpsLabel.setFixedSize(width*0.03,height*0.02)
            fpsLabel.move(width*0.02,height*0.03)
            autoFps = QRadioButton("自动",recSetup)
            autoFps.setStyleSheet('''
            QRadioButton{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:30px;
            }
            QRadioButton:indicator{
                  background:#ececec;
                  border:2px solid #000000;
                  border-radius:8px;
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
            autoFps.setFixedSize(width*0.05,height*0.02)
            autoFps.move(width*0.042,height*0.03)
            manualFps = QRadioButton("手动(           fps)",recSetup)
            manualFps.setStyleSheet('''
            QRadioButton{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:30px;
            }
            QRadioButton:indicator{
                  background:#ececec;
                  border:2px solid #000000;
                  border-radius:8px;
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
            manualFps.setFixedSize(width*0.09,height*0.02)
            manualFps.move(width*0.08,height*0.03)
            fpsInput = QLineEdit(recSetup)
            fpsInput.setAlignment(Qt.AlignCenter)
            fpsInput.setStyleSheet('''
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
            fpsInput.setFixedSize(width*0.03,height*0.02)
            fpsInput.move(width*0.12,height*0.0315)
            fpsInput.setValidator(QIntValidator())
            def fpsLimit():
                  try:
                        if manualFps.isChecked():
                              fpsInput.setEnabled(True)
                              fpsNow = int(fpsInput.text())
                              if fpsNow < 1:
                                    fpsInput.setText("1")
                              if fpsNow > 200:
                                    fpsInput.setText("200")
                        else:
                              fpsInput.setEnabled(False)
                  except:
                        pass
            autoFps.toggled.connect(fpsLimit)
            manualFps.toggled.connect(fpsLimit)
            fpsInput.textChanged.connect(fpsLimit)
            # 延时设置
            delayLabel = QLabel("延时:         秒(0-60)",recSetup)
            delayLabel.setStyleSheet('''
            QLabel{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:30px;
                  color:#000000;
            }
            ''')
            delayLabel.setFixedSize(width*0.09,height*0.02)
            delayLabel.move(width*0.02,height*0.05)
            delaySet = QLineEdit(recSetup)
            delaySet.setAlignment(Qt.AlignCenter)
            delaySet.setStyleSheet('''
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
            delaySet.setFixedSize(width*0.02,height*0.02)
            delaySet.move(width*0.045,height*0.05)
            delaySet.setValidator(QIntValidator())
            def delayLimit():
                  delayText = delaySet.text()
                  try:
                        delayNum = int(delayText)
                        if delayNum > 60:
                              delaySet.setText("60")
                              delayNum = 60
                        if delayNum < 1:
                              delaySet.setText("1")
                              delayNum = 1
                        self.delayTime = delayNum
                  except:
                        if not len(delayText) == 0:
                              delaySet.setText("3")
                              self.delayTime = 3
            delaySet.textChanged.connect(delayLimit)
            # 视频编码格式设置
            fourccLabel = QLabel("编码格式:",recSetup)
            fourccLabel.setStyleSheet('''
            QLabel{
                  background:transparent;
                  border:none;
                  font-family:Microsoft YaHei;
                  font-size:30px;
                  color:#000000;
            }
            ''')
            fourccLabel.setFixedSize(width*0.045,height*0.02)
            fourccLabel.move(width*0.02,height*0.07)
            fourccList = ["XVID","MPEG","CJPG","CMYK","FMP4","JPEG","LJPG","LMP4","MJPG","RGBT"]
            fourccChoose = QComboBox(recSetup)
            fourccChoose.addItems(fourccList)
            fourccChoose.setStyleSheet('''
            QComboBox{
                  combobox-popup:0;
                  background:#ececec;
                  border:none;
                  border-style:outset;
                  border-radius:10px;
                  border-color:%s;
                  border-width:2px;
                  font-family:Microsoft YaHei;
                  font-size:25px;
                  color:#000000;
            }
            QComboBox:drop-down{
                  width:30px;
                  height:30px;
                  border:none;
                  subcontrol-position:right;
                  subcontrol-origin:padding;
                  border-image:url(./ctrlButtons/videoSetup/comboDropDown.svg);
            }
            QMenu{
                  background:#ececec;
                  border:none;
                  border-radius:0px;
            }
            '''%(self.apperColor))
            fourccChoose.setFixedSize(width*0.05,height*0.02)
            fourccChoose.move(width*0.065,height*0.072)

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
                  lenInfo = open("./TempFiles/lengthInfo.txt","a+")
                  lenInfo.seek(0)
                  oldInfo = lenInfo.read()#读取原内容
                  oldInfo = oldInfo.replace("{","")
                  oldInfo = oldInfo.replace("}","")
                  lenInfo.truncate(0)
                  rowsPlus = videoTable.rowCount()+1
                  videoTable.setRowCount(rowsPlus)
                  videoTable.setItem(rowsPlus-1,0,QTableWidgetItem(itemName))
                  videoTable.setItem(rowsPlus-1,1,QTableWidgetItem("mp4文件"))
                  videoTable.setItem(rowsPlus-1,2,QTableWidgetItem(itemDate))
                  videoTable.setItem(rowsPlus-1,3,QTableWidgetItem(itemTime))
                  #写入信息
                  if oldInfo:
                        lenInfo.write("{"+oldInfo+",\'"+itemName+"\':\'"+itemTime+"\'}")
                  else:
                        lenInfo.write("{"+oldInfo+"\'"+itemName+"\':\'"+itemTime+"\'}")
                  
                  itemSize = formatTools.formatSize(os.path.getsize("videos/"+itemName))
                  videoTable.setItem(rowsPlus-1,4,QTableWidgetItem(itemSize))
                  lenInfo.close()
            def stopRecord():
                  self.escRec = True
                  #还原窗口
                  self.setFixedSize(width*0.66,height*0.75)
                  self.move(self.posX,self.posY)
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
            self.recTime = 0
            def displayTime():
                  self.returnTime = "00:00"
                  self.recTime = 0
                  while True:
                        if self.isRecording and not self.escRec:
                              time.sleep(1)
                              self.recTime += 1
                              recMin = str(int(self.recTime/60))
                              recSec = str(self.recTime%60)
                              if int(recMin)<10:
                                    recMin = "0"+str(recMin)
                              if int(recSec)<10:
                                    recSec = "0"+str(recSec)
                              self.returnTime = recMin+":"+recSec
                              recTimer.display(self.returnTime)
                        elif self.escRec:
                              recTime = 0
                              break
            #声音录制
            def recordSound():
                  CHUNK = 2048
                  FORMAT = pyaudio.paInt16
                  CHANNELS = 2
                  RATE = 48000
                  outputName = "TempFiles/soundOutput.wav"
                  p = pyaudio.PyAudio()
                  wf = wave.open(outputName,"wb")
                  wf.setnchannels(CHANNELS)
                  wf.setsampwidth(p.get_sample_size(FORMAT))
                  wf.setframerate(RATE)
                  frames = []
                  stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,
                  frames_per_buffer=CHUNK)
                  while True:
                        if self.isRecording:
                              data = stream.read(CHUNK)
                              frames.append(data)
                        if self.escRec:
                              break
                  stream.stop_stream()
                  stream.close()
                  wf.writeframes(b"".join(frames))
                  p.terminate()
            #屏幕录制
            def record():
                  try:
                        #录制
                        recordTick = tickScreen.isChecked()
                        if recordTick:
                              currentScreen = ImageGrab.grab(self.recordBox)#获取区域
                        else:
                              currentScreen = ImageGrab.grab()#获取全屏
                        heightS,widthS = currentScreen.size
                        currentTime = time.localtime()
                        recTime = time.strftime("%Y%m-%H%M%S",currentTime)
                        stopName = recTime+".mp4"
                        stopDate = time.strftime("%Y/%m %H:%M:%S",currentTime)

                        #将视频名称写入文件
                        videoName = "videos/"+recTime+".mp4"
                        tempFile = open("TempFiles/videoNameTemp.tmp","w+")
                        tempFile.write(videoName)
                        tempFile.close()

                        tempName = "TempFiles/videoOutput.avi"
                        currentFourcc = fourccChoose.currentText()
                        video = cv2.VideoWriter(tempName,cv2.VideoWriter_fourcc(*currentFourcc),
                                                self.fps,(heightS,widthS))#创建视频
                        imgNum = 0
                        pausebtn.setStyleSheet('''
                        QToolButton{
                              background:#ececec;
                              border-style:outset;
                              border-radius:7px;
                              border-width:0px;
                              border-image:url(./ctrlButtons/pauseRecord.png);
                        }
                        QToolButton:hover{
                              background:#d0d0d0;
                        }
                        QToolButton:pressed{
                              background:#bababa;
                        }
                        ''')
                        self.isRecording = True
                        for i in range(self.delayTime):
                              time.sleep(1)
                              recTimer.display(str(self.delayTime-i))
                        timerThread = threading.Thread(target=displayTime,name="TimeDisplay")
                        audioThread = threading.Thread(target=recordSound,name="SoundRecorder")
                        timerThread.start()
                        audioThread.start()
                        stopbtn.setEnabled(True)
                        pausebtn.setEnabled(True)
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
                        print("录制完成!请双击运行\"fileMerger.py\"以合并音视频")
                  except:
                        pass
            def grabReady():
                  try:
                        #global stopGrabX
                        #global stopGrabY
                        #stopGrabX = self.x()
                        #stopGrabY = self.y()
                        self.setFixedSize(width*0.4,height*0.05)
                        titleBar.hide()
                        contents.hide()
                        recWidget.show()
                        self.move(width*0.58,height*0.87)
                        minbtn.setEnabled(False)
                        maxbtn.setEnabled(False)
                        closebtn.setEnabled(False)
                        stopbtn.setEnabled(False)
                        pausebtn.setEnabled(False)
                        recTimer.display(str(self.delayTime))
                        isRecording = True
                        recordThread = threading.Thread(target=record,name="Recorder")
                        recordThread.start()
                        self.escRec = False
                  except:
                        pass
            def startRecord():
                  try:
                        grabReady()
                  except Exception as exc:
                        print(exc)
            recbtn.clicked.connect(startRecord)

            self.show()

if __name__ == "__main__":
      app = QApplication(sys.argv)
      print('''｢ScreenRecorder by Administrator-user｣
Loading project...''')
      loadTxt = "\r|{}{}| {}%"
      for i in range(51):
            done = "█"*i
            undone = " "*(50-i)
            for j in range(1,3):
                  print(loadTxt.format(done,undone,i*j),end="")
                  sys.stdout.flush()
                  time.sleep(0.02)
      window = grabWindow()
      sys.exit(app.exec_())
