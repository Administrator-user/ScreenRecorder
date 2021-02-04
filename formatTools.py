'''
formatTools.py

用于'ScreenRecorder'中的格式化操作
'''
import time

#格式化文件大小
def formatSize(size):
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

'''
格式化os.path.getctime返回值
原因:time.strftime()无法直接对os.path.getctime()的返回值格式化
执行流程:
1.使用time.ctime()转换时间格式并拆分;
2.列出月份列表(time.ctime()格式化后月份是字母格式);
3.格式化为tuple形式(年份,月份,日期,时,分,秒,1,1,0)
(倒数第2~3个在后方无需使用,可直接用任意数字代替);
4.将tuple中内容全部转为int形式;
5.使用time.strftime()进行格式化;
'''
def formatCtime(time_to_format):
      cList = time.ctime(time_to_format).split()
      monthList = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep",
                   "Oct","Nov","Dec"]
      formatTime = (cList[4],monthList.index(cList[1])+1,cList[2],cList[3][0:2],
                        cList[3][3:5],cList[3][6:8],1,1,0)
      formatTime = tuple([int(x) for x in formatTime])
      formatTime = time.strftime("%Y/%m/%d %H:%M:%S",formatTime)
      return formatTime
