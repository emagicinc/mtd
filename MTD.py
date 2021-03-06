#!/usr/bin/env python
# -*- coding: utf-8 -*-
from project.models import *
from project.newListDlg import NewListDlg
from util.db import DB
from PyQt4 import QtCore, QtGui, QtXml, QtNetwork, QtWebKit
import PixmapCache
import pandas as pd
from UI.Ui_mainWindow import Ui_MainWindow
from util.common import copyTree, copyTemplate, initCourseList, readFile, strippedPath, correctCodec, getSelTxt, \
    outTxt, resultToId, getGuid, getFlds, date_uxStamp, execSql, makeImageList, makeAudioList, getMediaFile, \
    parseCourseList, getEmptyItem, writeCourseList, writeItemFile, writeDb, getOpenFileName, \
    copyFile, gotoQASection, saveEditItem, updateChapTree, verifyCourseName, outputStream, getCourse, getCourseInfo, \
    resetCombo, setItemId, getCourseList, getId, getExistingDir, deleteItemFile, getItemIdFromDb, \
    connectDb, closeDb, parseDbCourse, writeColDb, dbToQASection, saveEditData, warn, \
    getUserList, toList, getModelId, loadConf, resetModelCombo, getOnlineId
from util.keyMap import getKey
from util import SMMessageBox
from ctypes import c_bool, c_int, WINFUNCTYPE, windll, cdll, CDLL
from ctypes.wintypes import UINT
import Preferences as Prefs
import codecs, zlib, struct, binascii, shutil, os, random, sqlite3, chardet, win32con, \
    win32api, json, re, time
import win32com.client
from datetime import datetime
from PIL import Image
from bs4 import BeautifulSoup
import sip
sip.setapi('QVariant', 2)

WM_HOTKEY = 0x0312

PixmapCache.addSearchPath(":/images")
PixmapCache.addSearchPath("./background")


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent,
                                         QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint)

        self.ui = Ui_MainWindow()
        self.setPostition()
        self.ui.setupUi(self)
        self.curFile = None
        self.setWindowIcon(QtGui.QIcon(':/images/icon.png'))
        self.progName = "MTD"
        self.ver = "V 1.0.0"
        self.setWindowTitle("""%s   %s""" % (self.progName, self.ver))

        self.db = DB("./mtdo.db")  # 以下测试全部通过
        self.se = self.db.se
        # 获取当前任务ID:title的字典
        self.curListId = "278927047"
        self.curTaskId = None
        self.curSubtaskId = None
        self.curMenuSender = None  # 右键菜单发起对象
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.lists = None  # 所有清单
        self.tasks = None  # 所有任务
        self.records = None  # 所有记录
        self.subtasks = None  # 所有子任务
        self.units = None  # 所有单位
        self.wh = 31  # 测试用,控件高度
        self.timer = QtCore.QTimer(self)  # 用来计时
        self.timer.timeout.connect(self.showTime)  # 显示时间

        self.ui.taskLW.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.taskLW.customContextMenuRequested.connect(
                self.taskMenuShow)
        self.ui.listTaskLW.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listTaskLW.customContextMenuRequested.connect(
                self.taskMenuShow)

        self.settingsStyle = self.loadStyleSheet('./qss/emagic.settings.qss')  # TODO:临时修改
        self.topStyle = self.loadStyleSheet('./qss/emagic.top.qss')
        self.leftStyle = self.loadStyleSheet('./qss/emagic.left.qss')
        self.mainStyle = self.loadStyleSheet('./qss/emagic.main.qss')  # TODO:临时修改,需要修改路径,重新编译
        self.stkStyle = self.loadStyleSheet('./qss/emagic.stk.qss')  # TODO:临时修改,需要修改路径,重新编译
        #        self.dlgStyle = self.loadStyleSheet(':/qss/emagic.dlg.qss')#各设置窗口
        self.centralStyle = self.loadStyleSheet(':/qss/emagic.central.qss')  # 主体部分
        self.ui.configWidget.setStyleSheet(self.settingsStyle)
        self.ui.topWidget.setStyleSheet(self.topStyle)
        self.ui.leftWidget.setStyleSheet(self.leftStyle)
        # self.ui.mainWidget.setStyleSheet(self.mainStyle)
        self.ui.mainStk.setStyleSheet(self.stkStyle)
        self.ui.centralwidget.setStyleSheet(self.centralStyle)  # 这个级别最高，位于顶层
        self.moveable = False

        self.initialize()

    # ###############################################
    # ##                新代码开始                 ###
    # ###############################################

    def setPostition(self):
        """设置窗口位置"""
        desktop = QtGui.QApplication.desktop()
        rect = desktop.screenGeometry()
        self.move(rect.width() / 2 - 430, rect.height() / 4)

    def loadStyleSheet(self, qssFile):
        """载入样式表"""
        file = QtCore.QFile(qssFile)
        file.open(QtCore.QFile.ReadOnly)
        styleSheet = file.readAll()
        file.close()
        styleSheet = str(styleSheet, encoding='utf8')
        return styleSheet

    @QtCore.pyqtSlot()
    def on_inboxBtn_clicked(self):
        """收件箱"""
        self.curListId = self.db.getData(List, List.onlineId, 'inbox', List.title)
        tasks = self.db.dic(Task, self.curListId)
        self.ui.mainStk.setCurrentIndex(4)
        self.ui.listTaskLW.clear()
        for k, v in tasks.items():
            self.__setItem(k, v, self.ui.listTaskLW)

    @QtCore.pyqtSlot()
    def on_starListBtn_clicked(self):
        """星标清单"""
        # query = self.se.query(List).filter(List.title != 'inbox')
        # res = query.all()
        # 测试用
        self.ui.noteTE.setFixedHeight(self.wh)
        self.wh += 31

    @QtCore.pyqtSlot()
    def on_addListBtn_clicked(self):
        """添加清单"""
        # todo, listLW增加右键菜单: 重命名, 复制, 删除, 添加成员
        dlg = NewListDlg(self)
        dlg.exec_()

    def addList(self, title):
        """响应newList的回调"""
        item = self.add(title, '27', self.lists, List, self.ui.listLW)
        listIcon = QtGui.QIcon(PixmapCache.getIcon('list.png'))
        item.setIcon(listIcon)

    def add(self, name, prefix, lists, base, obj=None, parentId=None, batch=None):
        """通用新增数据方法"""
        if name not in lists.values():
            item = None
            tid = self.getOnlineId(prefix, lists)
            if obj:  # 有控件传入,则给控件新增item
                item = QtGui.QListWidgetItem(obj)
                item.setText(name)
                item.setData(32, tid)
            if parentId:
                line = base(
                        onlineId=tid,
                        title=name,
                        parentId=parentId,
                        )
            else:
                line = base(
                        onlineId=tid,
                        title=name,
                        )
            self.se.add(line)
            lists[tid] = name  # 更新self.tasks
            if not batch:
                self.se.commit()
            return item

    def getOnlineId(self, prefix, lists):
        """通用方法, 根据前缀prefix返回onlineId"""
        while True:
            tid = """%s%s""" % (prefix, getOnlineId())
            if tid not in lists.keys():
                break
        return tid

    @QtCore.pyqtSlot()
    def on_manageListBtn_clicked(self):
        """添加清单"""
        print('manage')
        # 切到清单页
        # 双击进入清单
        # 对清单进行重命名
        # 可对清单进行转换(转成任务,子任务,注意考虑清单下已有任务的情况),转移(到另一个清单下)

    @QtCore.pyqtSlot(str)
    def on_searchLE_textChanged(self, key):
        """搜索"""
        hits = {}
        index = self.ui.mainStk.currentIndex()
        tasks = self.tasks
        # obj = self.ui.taskLW
        if index == 4:  # 列表页taskPage
            obj = self.ui.listTaskLW
            tasks = self.db.dic(Task, self.curListId)
        else:
            # 切换到首页
            self.ui.mainStk.setCurrentIndex(0)
            obj = self.ui.taskLW
        obj.clear()
        for k, v in tasks.items():
            if re.search(r'%s' % key, v):
                hits[k] = v

        for k, v in hits.items():
            self.__setItem(k, v, obj)

    def initialize(self):
        # 初始化
        # self.db = DB("./mtdo.db")  # 以下测试全部通过
        # self.se = self.db.se
        # 获取当前任务ID:title的字典
        # self.curListId = "278927047"
        # self.curTaskId = None
        # self.curSubtaskId = None
        # self.hour = 0
        # self.min = 0
        self.ui.mainStk.setCurrentIndex(0)
        #        print(self.tasks)
        self.tasks = self.db.dic(Task)
        self.records = self.db.dic(Record)
        self.subtasks = self.db.dic(Subtask)
        self.lists = self.db.dic(List)
        self.units = self.db.dic(Unit)

        for k, v in self.tasks.items():
            self.__setItem(k, v, self.ui.taskLW)
        for k, v in self.lists.items():
            self.__setItem(k, v, self.ui.listLW)

    def __setItem(self, itemId, title, obj):
        """根据item列表对ListWidget进行设置;"""
        item = QtGui.QListWidgetItem(obj)
        item.setText(title)
        item.setData(32, itemId)  # 编号
        if obj.objectName() == "listLW":
            listIcon = QtGui.QIcon(PixmapCache.getIcon('list.png'))
            item.setIcon(listIcon)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    #    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    #    def on_taskLW_itemClicked(self):
    #        """
    #        taskLW中item单击;
    #        """
    #        item = self.ui.taskLW.currentItem()
    #        #TODO:切换到子任务界面
    #        print(item.text(), item.data(32))

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def on_listLW_itemClicked(self, item):
        """
        listLW中item单击;
        """
        # 转到taskPage的页面
        self.curListId = item.data(32)
        self.gotoListPage()

    def gotoListPage(self):
        """转到清单页, 公用方法"""
        self.ui.mainStk.setCurrentIndex(4)
        tasks = self.db.dic(Task, self.curListId)
        self.ui.listTaskLW.clear()
        unitId = self.db.getData(List, List.unitId, self.curListId)
        resetCombo(self.ui.unitCombo, self.units, True, unitId, 'findData')
        for k, v in tasks.items():
            self.__setItem(k, v, self.ui.listTaskLW)
            #        print(item.text(), item.data(32))

    def addTask(self, le, lw, name=None):
        """添加任务的公用方法"""
        # le为LineEdit控件
        # lw为ListWidget控件
        title = name
        batch = True
        if not name:
            title = le.text()
            le.clear()
            batch = None
        self.add(title, '23', self.tasks, Task, lw, self.curListId, batch)
        # if title not in self.tasks.values():
        #     item = QtGui.QListWidgetItem(lw)
        #     # TODO: id应做成一个通用的方法
        #     taskId = self.getOnlineId('23', self.tasks)
        #     item.setText(title)
        #     item.setData(32, taskId)
        #     task = Task(
        #             onlineId=taskId,
        #             title=title,
        #             parentId=self.curListId,
        #             )
        #     self.se.add(task)
        #     self.tasks[taskId] = title  # 更新self.tasks
        #     if not name:  # 传入title的话,表示要批量处理
        #         self.se.commit()

    @QtCore.pyqtSlot()
    def on_addListTaskLE_returnPressed(self):
        """taskPage下的添加任务"""
        self.addTask(self.ui.addListTaskLE, self.ui.listTaskLW)

    @QtCore.pyqtSlot()
    def on_addTaskLE_returnPressed(self):
        """用le添加任务"""
        self.addTask(self.ui.addTaskLE, self.ui.taskLW)

    @QtCore.pyqtSlot()
    def on_importBtn_clicked(self):
        """导入任务@指定清单"""
        file = getOpenFileName('打开文件', None, 'file', self)
        df = pd.read_table(file)
        for i in df.values:
            self.addTask(self.ui.addListTaskLE, self.ui.listTaskLW, i[0])
        self.se.commit()

    @QtCore.pyqtSlot()
    def on_unitBtn_clicked(self):
        """更新单位@指定清单"""
        title = self.ui.unitCombo.currentText()
        unitId = self.ui.unitCombo.itemData(
                self.ui.unitCombo.currentIndex()
                )
        self.add(title, '14', self.units, Unit)
        # if title not in self.units.values():
        #     unitId = self.getOnlineId('14', self.units)
        #     unit = Unit(
        #             onlineId=unitId,
        #             title=title,
        #             )
        #     self.se.add(unit)
        #     self.se.commit()

        self.db.update(List, self.curListId, 'unitId', unitId)  # 将id作为当前清单的unitId
        # self.units[unitId] = title
        resetCombo(self.ui.unitCombo, self.units, True, unitId, 'findData')

    @QtCore.pyqtSlot()
    def on_randomBtn_clicked(self):
        """随机挑选任务@指定清单"""
        # todo, 后期要根据星级、标签、日期匹配（周几）来进行随机选择（制定随机模式）
        tasks = self.db.dic(Task, self.curListId)
        taskId = random.choice(list(tasks.keys()))
        self.__gotoTaskPage(self.tasks.get(taskId), taskId)

    @QtCore.pyqtSlot()
    def on_addListTaskBtn_clicked(self):
        """新增任务@指定清单"""
        self.on_addListTaskLE_returnPressed()

    @QtCore.pyqtSlot()
    def on_addTaskBtn_clicked(self):
        """新增任务"""
        self.on_addTaskLE_returnPressed()

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def on_taskLW_itemDoubleClicked(self, item):
        """
        taskLW 中item双击;
        """
        self.gotoTaskPage(item)

    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    def on_listTaskLW_itemDoubleClicked(self, item):
        """
        listTaskLW 中item双击;
        """
        self.gotoTaskPage(item)

    def gotoTaskPage(self, item):
        """转到任务页面,公共方法"""
        self.__gotoTaskPage(item.text(), item.data(32))

    def __gotoTaskPage(self, title, taskId):
        """转到任务页面"""
        self.curTaskId = taskId
        self.ui.mainStk.setCurrentIndex(1)
        self.ui.taskLE.setText(title)
        note = self.db.getNote(Note, self.curTaskId)
        if note is not None:
            self.ui.noteTE.setText(note)
            if len(note) < 25:
                self.ui.noteTE.setFixedHeight(31)
        else:
            self.ui.noteTE.setFixedHeight(31)
        subtasks = self.db.dic(Subtask, taskId)
        self.ui.subtaskLW.clear()
        for k, v in subtasks.items():
            self.__setItem(k, v, self.ui.subtaskLW)

    @QtCore.pyqtSlot()
    def on_taskLE_editingFinished(self):
        """修改任务名称"""
        title = self.ui.taskLE.text()
        self.db.update(Task, self.curTaskId, 'title', title)

    @QtCore.pyqtSlot()
    def on_addSubtaskLE_returnPressed(self):
        """添加子任务"""
        title = self.ui.addSubtaskLE.text()
        # item = QtGui.QListWidgetItem(self.ui.subtaskLW)
        self.add(title, '13', self.subtasks, Subtask, self.ui.subtaskLW, self.curTaskId)
        # subtaskId = self.getOnlineId('13', self.subtasks)
        # item.setText(title)
        # item.setData(32, subtaskId)
        # subtask = Subtask(onlineId=subtaskId, title=title, parentId=self.curTaskId)
        # self.se.add(subtask)
        # self.se.commit()
        # self.subtasks[subtaskId] = title  # 更新self.tasks

    @QtCore.pyqtSlot()
    def on_addSubtaskBtn_clicked(self):
        """新增子任务"""
        self.on_addSubtaskLE_returnPressed()

    #    @QtCore.pyqtSlot(QtGui.QListWidgetItem)
    #    def on_subtaskLW_itemDoubleClicked(self, item):
    #        """
    #        subtaskLW 中item双击;
    #        """
    #        #转到第3页
    #        #时钟，开始按钮（可切换成暂停），终止按钮
    #        self.ui.mainStk.setCurrentIndex(2)
    #        self.curSubtaskId = item.data(32)
    #        self.ui.timerTitleLbl.setText(item.text())
    #        self.ui.lcdLN.display("00:00:00")

    @QtCore.pyqtSlot()
    def on_onManualBtn_clicked(self):
        """进入手动记录界面"""
        self.ui.mainStk.setCurrentIndex(3)
        title = self.tasks.get(self.curTaskId)
        self.ui.recordTitleLbl.setText(title)
        current = QtCore.QDateTime.currentDateTime()
        self.ui.todayDE.setDateTime(current)
        self.ui.hourSpin.setValue(0)
        self.ui.minuteSpin.setValue(0)
        self.ui.minCountSpin.setValue(0)
        self.ui.maxCountSpin.setValue(0)

    @QtCore.pyqtSlot()
    def on_timerBtn_clicked(self):
        """进入计时界面"""
        self.ui.mainStk.setCurrentIndex(2)
        #        self.curSubtaskId = item.data(32)
        title = self.tasks.get(self.curTaskId)
        self.ui.timerTitleLbl.setText(title)
        self.ui.lcdLN.display("00:00:00")

    @QtCore.pyqtSlot()
    def on_startBtn_clicked(self):
        """开始计时"""
        if self.ui.startBtn.text() in ['开始', '继续']:
            if self.ui.startBtn.text() == '开始':
                self.hour = 0
                self.min = 0
                self.sec = 0
            self.ui.startBtn.setText('暂停')
            self.timer.start(1000)
            self.showTime()
        else:  # 暂停
            self.ui.startBtn.setText('继续')
            self.timer.stop()
            #            self.showTime()

    @QtCore.pyqtSlot()
    def on_rangeCB_toggled(self):
        """范围CB是否选中"""
        active = self.ui.rangeCB.isChecked()
        self.ui.maxCountSpin.setVisible(active)
        self.ui.slashLbl.setVisible(active)

    @QtCore.pyqtSlot()
    def on_resetBtn_clicked(self):
        """重置计时"""
        self.ui.startBtn.setText('开始')
        self.timer.stop()
        self.hour = 0
        self.min = 0
        self.sec = 0

    def showTime(self):
        def cv(s):
            """在数字前补0,并转成字符"""
            s = """0%s""" % s
            return s[-2:]

        self.sec += 1
        if self.sec == 60:
            self.min += 1
            self.sec = 0
        if self.min == 60:
            self.hour += 1
            self.min = 0
        text = """%s:%s:%s""" % (cv(self.hour), cv(self.min), cv(self.sec))
        self.ui.lcdLN.display(text)

    @QtCore.pyqtSlot()
    def on_stopBtn_clicked(self):
        """停止计时"""
        self.ui.startBtn.setText('开始')
        self.timer.stop()
        self.ui.mainStk.setCurrentIndex(3)
        title = self.tasks.get(self.curTaskId)
        self.ui.recordTitleLbl.setText(title)
        current = QtCore.QDateTime.currentDateTime()
        self.ui.todayDE.setDateTime(current)
        self.ui.hourSpin.setValue(self.hour)
        self.ui.minuteSpin.setValue(self.min)
        # TODO: 要控制单位的显示
        # TODO: 增加倒计时的功能

    @QtCore.pyqtSlot()
    def on_saveBtn_clicked(self):
        """储存记录"""
        # 注意,如果从任务一级就开始记录,就必须指定是储存任务还是子任务
        # TODO: 要可以修改记录
        # TODO: taskPage内增加一个随机挑选任务的按钮
        # TODO: taskPage内增加按星级/标签/常用等方式筛选,任务表要添加星级字段
        # TODO: 增加weekPlan表,用来随机挑选任务用,任务界面增加星期选项
        # TODO: 可以增加40-50秒以上算作一分钟的设置
        # 不足一分钟提示
        text = self.ui.recordTitleLbl.text()
        recordId = self.getOnlineId('33', self.records)
        # 计算时间
        if self.sec >= 45:
            self.min += 1
        usageTime = self.hour * 60 + self.min  # 记录分钟数
        # 计算工作量
        minCount = None
        maxCount = None
        workLoad = self.ui.minCountSpin.value()
        date = self.ui.todayDE.dateTime()
        date = date.toPyDateTime()
        if self.ui.rangeCB.isChecked():
            minCount = self.ui.minCountSpin.value()
            maxCount = self.ui.maxCountSpin.value()
            workLoad = maxCount - minCount
        if usageTime > 0:
            record = Record(
                    onlineId=recordId,
                    title=text,
                    createdAt=date,
                    updatedAt=date,
                    parentId=self.curTaskId,
                    usageTime=usageTime,
                    workLoad=workLoad,
                    minCount=minCount,
                    maxCount=maxCount
            )
            self.se.add(record)
            self.se.commit()
            self.records[recordId] = text
        self.gotoResultPage()

    @QtCore.pyqtSlot()
    def on_viewBtn_clicked(self):
        """查看当天记录"""
        # todo, 应该可以看本周记录/本月记录
        self.gotoResultPage()

    def gotoResultPage(self):
        """
        记录储存后转到结果页面
        显示当天的学习记录
        """
        self.ui.mainStk.setCurrentIndex(5)
        today = datetime.now().date()  # 取日期部分
        for n in range(self.ui.resultLayout.count()):
            item = self.ui.resultLayout.itemAt(n)
            self.ui.resultLayout.removeItem(item)
        res = self.se.query(Record).filter(func.date(Record.updatedAt) == today)
        totalUsage = 0
        for i in res:
            infoLbl = QtGui.QLabel()
            workLoad = self.getWorkLoad(i.workLoad, i.minCount, i.maxCount)
            infoLbl.setText(
                    """%s\n时间：%s分%s\n"""
                    """记录日期：%s"""
                    % (i.title, i.usageTime, workLoad, i.createdAt)
                    )
            totalUsage += i.usageTime
            self.ui.resultLayout.addWidget(infoLbl)
        self.ui.usageTimeLbl.setText("""今日: %s分钟""" % str(totalUsage))

    def getWorkLoad(self, workLoad, minCount=None, maxCount=None):
        """根据传来的参数组成相应的字符串"""
        content = ""
        if workLoad > 0:
            # todo, 注意要传入单位
            content += """\n工作量：%s 页""" % workLoad
        if minCount is not None:
            content += """\n范围：%s - %s 页""" % (minCount, maxCount)
        return content


        # self.curTaskId = item.data(32)
        # self.ui.mainStk.setCurrentIndex(1)
        # self.ui.taskLbl.setText(item.text())
        # subtasks = self.db.dic(Subtask, item.data(32))
        # self.ui.subtaskLW.clear()
        # for k, v in subtasks.items():
        #     self.__setItem(k, v, self.ui.subtaskLW)

    # 创建右键菜单
    def taskMenuShow(self):
        """显示右键菜单"""
        self.curMenuSender = self.sender()
        menu = QtGui.QMenu(self.curMenuSender)
        for k, v in self.lists.items():
            act = QtGui.QAction(v, self, triggered=self.transferTask)
            act.setData(k)
            menu.addAction(act)
        menu.exec_(QtGui.QCursor.pos())

    def transferTask(self):
        """将任务转移到另一个清单"""
        obj = self.sender()
        parentId = obj.data()
        item = self.curMenuSender.currentItem()
        taskId = item.data(32)
        pid = self.db.getData(Task, Task.parentId, taskId)
        if parentId != pid:
            self.db.update(Task, taskId, 'parentId', parentId)
            self.curListId = parentId  # 转到目标List下
            self.gotoListPage()  # 跳转到清单页
            # if self.ui.mainStk.currentIndex() != 0:  # 如果不在首页, 则做一个从移除操作
            #     row = self.curMenuSender.currentRow()
            #     self.curMenuSender.takeItem(row)

    def getTime(self, start):
        """获取时间差"""
        now = time.time()
        interval = int((now - start) / 60)
        sec = int((now - start - interval * 60))
        return """%s分%s秒""" % (interval, sec)

    @QtCore.pyqtSlot()
    def on_closeBtn_clicked(self):
        """退出"""
        self.quit()

    @QtCore.pyqtSlot()
    def on_exitBtn_clicked(self):
        """退出"""
        self.quit()

    @QtCore.pyqtSlot()
    def on_minimizeBtn_clicked(self):
        """最小化@顶部"""
        self.showMinimized()

    def quit(self):
        """退出"""
        self.close()

    def closeEvent(self, event):
        """响应关闭事件,注意,这里实际上是被self.quit调用"""
        sys.exit()

    def eventFilter(self, watched, event):
        """
        基本思路:给快捷键LE安装eventFilter,然后调用keyPressEvent
        Method called to filter the event queue.
        
        @param watched the QObject being watched
        @param event the event that occurred
        @return always False
        """
        if event.type() == QtCore.QEvent.KeyPress:
            self.keyPressEvent(event)
            return True

        return False

    def mousePressEvent(self, event):
        """实现标题栏拖动：1"""
        if event.buttons() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            rect = self.ui.topWidget.rect()
            if rect.contains(event.pos()):
                self.moveable = True
        event.accept()

    def mouseMoveEvent(self, event):
        """实现标题栏拖动：2"""
        if event.buttons() == QtCore.Qt.LeftButton and self.moveable:
            self.move(event.globalPos() - self.dragPosition)
        event.accept()

    def mouseReleaseEvent(self, event):
        """实现标题栏拖动：3"""
        if self.moveable:
            self.moveable = False

            #    def catureQustion(self):
            #        """响应全局快捷键"""
            ##        from project.collectorDlg import CollectorDlg
            #        dlg = CollectorDlg(self)
            #        dlg.exec_()

    def writeNotes(self, pr):
        """响应来自collectorWgtOK按钮点击"""
        file = './knowledge.txt'
        qtxt = pr.ui.questionLE.text()
        atxt = pr.ui.answerLE.text()
        if atxt != "" and qtxt != "":
            content = """%s\t%s\n""" % (qtxt, atxt)
            outputStream(self, content, file, 'append2')


class GlobalHotKeyApp(QtGui.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.keyMap = {
            "ALT": 0x0001,
            "NONE": 0x000,
            "CONTROL": 0x0002,
            "SHIFT": 0x0004,
            "WIN": 0x0008,
            "F11": win32con.VK_F11,
            "F12": win32con.VK_F12,
            "R": ord("R"),
            "S": ord("S"),
            "A": ord("A"),
        }
        prototype = WINFUNCTYPE(c_bool, c_int, c_int, UINT, UINT)
        # paramflags: 1.窗口句柄; 2.热键序号；3.MOD键，4，热键
        paramflags = (1, 'hWnd', 0), (1, 'id', 0), (1, 'fsModifiers', 0), (1, 'vk', 0)
        self.RegisterHotKey = prototype(('RegisterHotKey', windll.user32), paramflags)

    def register(self):
        """热键注册"""
        # 检查有无设置数据库
        #        db = Prefs.getCourse("db")
        #        if not QtCore.QFile.exists(db):
        #            dlg = DbPathDlg()
        #            dlg.exec_()
        #        else:
        self.mw = MainWindow()
        #            captureQModKey = Prefs.getShortcut("captureQMod")
        #            captureQMod = getKey(captureQModKey)
        #            captureQKey = Prefs.getShortcut("captureQ")
        #            captureQ = getKey(captureQKey)
        self.mw.show()

    #            if captureQMod and captureQ:
    #                r1 = self.RegisterHotKey(c_int(self.mw.winId()), 1, captureQMod, captureQ)
    #                if not r1:#全局捕捉问题
    #                    QtGui.QMessageBox.critical(self.mw, '热键冲突', """<p>无法注册全局热键 %s + %s.</p>\
    #                        <p>请重新选择热键!</p>""" % (captureQModKey, captureQKey))
    #            snagQModKey = Prefs.getShortcut("snagQMod")
    #            snagQMod = getKey(snagQModKey)
    #            snagAModKey = Prefs.getShortcut("snagAMod")
    #            snagAMod = getKey(snagAModKey)

    #            captureAModKey = Prefs.getShortcut("captureAMod")
    #            captureAMod = getKey(captureAModKey)
    #            snagQKey = Prefs.getShortcut("snagQ")
    #            snagQ = getKey(snagQKey)
    #            snagAKey = Prefs.getShortcut("snagA")
    #            snagA = getKey(snagAKey)


    #            captureAKey = Prefs.getShortcut("captureA")
    #            captureA = getKey(captureAKey)
    #            if snagQMod and snagQ:
    #                r1 = self.RegisterHotKey(c_int(self.winId()), 1, snagQMod, snagQ)
    #                if not r1:#问题区抓图
    #                    QtGui.QMessageBox.critical(self, '热键冲突', """<p>无法注册全局热键 %s + %s.</p>\
    #                        <p>请重新选择热键!</p>""" % (snagQModKey, snagQKey))
    #            if snagAMod and snagA:
    #                r2 = self.RegisterHotKey(c_int(self.winId()), 2, snagAMod, snagA)
    #                if not r2:#答案区抓图
    #                    QtGui.QMessageBox.critical(self, '热键冲突', """<p>无法注册全局热键 %s + %s.</p>\
    #                        <p>请重新选择热键!</p>""" % (snagAModKey, snagAKey))

    #            if captureAMod and captureA:
    #                r4 = self.RegisterHotKey(c_int(self.winId()), 4, captureAMod, captureA)
    #                if not r4:#全局捕捉答案
    #                    QtGui.QMessageBox.critical(self, '热键冲突', """<p>无法注册全局热键 %s + %s.</p>\
    #                        <p>请重新选择热键!</p>""" % (captureAModKey, captureAKey))

    def winEventFilter(self, msg):
        #        print(msg.message)
        if msg.message == WM_HOTKEY:
            #            import imp
            #            imp.reload(globalKey)
            #            if msg.wParam in (1, 2):#表示抓图到Q/区
            ##                self.snagit()
            #                self.grabImage(msg.wParam)
            if msg.wParam == 1:  # 全局抓Q
                self.mw.catureQustion()
            # elif msg.wParam == 4: #全局抓A
            #                self.captureAnswer()
            else:
                pass  # 后期可改为增加从其它软件取文本快捷键
            return True, 0

        return False, 0


if __name__ == '__main__':
    import sys

    app = GlobalHotKeyApp(sys.argv)
    app.register()

    QtGui.QApplication.setQuitOnLastWindowClosed(False)

    r = app.exec_()

    sys.exit(r)
