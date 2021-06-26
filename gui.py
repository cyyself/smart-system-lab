import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QStringListModel, QTimer

from mainui import Ui_MainWindow
from DownPosMachine import DownPosMachine
from DB import DB
from DownPosMachine import DownPosMachine
from fuzzy_infer_machine import fuzzy_infer_machine
from credit_infer_machine import credit_infer_machine
import time
import threading
from credit_manager import credit_manager
from fuzzy_manager import fuzzy_manager
from realtime_api import realtime_api

import matplotlib.pyplot as plt

db = DB()
dpm = None
c_manager = credit_manager(db)
f_manager = fuzzy_manager(db)
baidu_data = realtime_api()

#def plot_fuzzy_set(set_id):

    

class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.DownMachineBtn.clicked.connect(self.connect_down_machine)
        self.sim_step.clicked.connect(self.sim_step_action)
        self.sim_clear.clicked.connect(self.sim_clear_action)
        self.sim_fuzzy.clicked.connect(self.sim_fuzzy_action)
        self.sim_credit.clicked.connect(self.sim_credit_action)
        self.ClearDownLog.clicked.connect(self.clear_dpm_log_action)
        self.ExpCreditResult.clicked.connect(self.dpm_credit_action)
        self.ExpFuzzyResult.clicked.connect(self.dpm_fuzzy_action)
        self.set_NS_Light(0)
        self.set_WE_Light(0)
        self.data_from_dpm = True
        # 可信度知识相关
        self.premiseInsert.clicked.connect(self.premise_insert)
        self.premiseDelete.clicked.connect(self.premise_delete)
        self.premiseUpdate.clicked.connect(self.premise_update)
        self.conclusionInsert.clicked.connect(self.conclusion_insert)
        self.conclusionDelete.clicked.connect(self.conclusion_delete)
        self.conclusionUpdate.clicked.connect(self.conclusion_update)
        self.creditInsert.clicked.connect(self.credit_insert)
        self.creditDelete.clicked.connect(self.credit_delete)
        self.creditUpdate.clicked.connect(self.credit_update)
        # 模糊知识相关
        self.fuzzyInsert.clicked.connect(self.fuzzy_insert)
        self.fuzzyDelete.clicked.connect(self.fuzzy_delete)
        self.fuzzyUpdate.clicked.connect(self.fuzzy_update)
        self.fuzzySetInsert.clicked.connect(self.fuzzy_set_insert)
        self.fuzzySetDelete.clicked.connect(self.fuzzy_set_delete)
        self.fuzzySetUpdate.clicked.connect(self.fuzzy_set_update)
        self.fuzzySetShow.clicked.connect(self.fuzzy_set_show)
        self.sim_log = []
        self.dpm_log = []
        self.sim_fim = fuzzy_infer_machine(db)
        self.sim_cim = credit_infer_machine(db)
        self.dpm_fim = fuzzy_infer_machine(db)
        self.dpm_cim = credit_infer_machine(db)
        self.timer=QTimer()
        self.timer.timeout.connect(self.refresh_dpm_log)
        self.timer.start(200)
    def connect_down_machine(self):
        global dpm
        if dpm == None:
            serial, ok = QInputDialog.getText(self, '连接下位机', '请输入下位机的位置，例如Windows上是COMx，UNIX下是/dev/x')
            if ok:
                try:
                    dpm = DownPosMachine(serial)
                    QMessageBox.information(self,"连接下位机","连接成功")
                    self.DownMachineBtn.setText("退出")
                except:
                    QMessageBox.critical(self,"连接下位机","连接失败")
                    dpm = None
                if dpm != None:
                    self.dpm_thread = threading.Thread(target=self.dpm_workder,args=())
                    self.dpm_thread.setDaemon(True)
                    self.dpm_thread.start()
        else:
            exit(0)
    def sim_step_action(self):
        traffic = self.traffic_value.value()
        speed = self.speed_value.value()
        temp = self.temp_value.value()
        rain = self.rain_value.value()
        snow = self.snow_value.value()
        wind = self.wind_value.value()
        self.sim_cim.update_environment(rain,snow,wind)
        self.sim_cim.update_realtime_info(traffic,speed,temp)
        cim_result = self.sim_cim.infer()
        self.sim_log.append("----- 开始推理，时间戳=%d -----"%(time.time()))
        if len(cim_result):
            self.sim_log.append("可信度推理得到结论：%s"%(str(cim_result)))
        else:
            self.sim_log.append("暂无可信度推理结论")
        green_time = self.sim_fim.infer(1,traffic)
        yellow_time = self.sim_fim.infer(2,speed)
        self.sim_log.append("模糊推理得到结论：新绿灯时间=%d"%(green_time))
        self.sim_log.append("模糊推理得到结论：新黄灯时间=%d"%(yellow_time))
        self.sim_log.append("----- 推理结束 -----")
        self.refresh_sim_log()
    def sim_clear_action(self):
        self.sim_log = []
        self.refresh_sim_log()
    def refresh_sim_log(self):
        slm = QStringListModel()
        slm.setStringList(self.sim_log)
        self.sim_result.setModel(slm)
    def sim_fuzzy_action(self):
        log = self.sim_fim.get_log()
        if len(log) >= 2:
            self.sim_fim.explain_log(log[-2],"sim_绿灯时间解释结果")
            self.sim_fim.explain_log(log[-1],"sim_黄灯时间解释结果")
        else:
            QMessageBox.critical(self,"模糊解释器","未找到模糊推理记录")
    def dpm_fuzzy_action(self):
        log = self.dpm_fim.get_log()
        if len(log) >= 2:
            self.dpm_fim.explain_log(log[-2],"dpm_绿灯时间解释结果")
            self.dpm_fim.explain_log(log[-1],"dpm_黄灯时间解释结果")
        else:
            QMessageBox.critical(self,"模糊解释器","未找到模糊推理记录")
    def sim_credit_action(self):
        log = self.sim_cim.get_log()
        if len(log):
            self.sim_cim.explain(log[-1],"sim_可信度推理机解释结果")
        else:
            QMessageBox.critical(self,"可信度解释器","未找到可信度推理记录")
    def dpm_credit_action(self):
        log = self.dpm_cim.get_log()
        if len(log):
            self.dpm_cim.explain(log[-1],"dpm_可信度推理机解释结果")
        else:
            QMessageBox.critical(self,"可信度解释器","未找到可信度推理记录")
    def refresh_dpm_log(self):
        slm = QStringListModel()
        slm.setStringList(self.dpm_log)
        self.dpm_result.setModel(slm)
    def clear_dpm_log_action(self):
        self.dpm_log = []
        self.refresh_dpm_log()
    def dpm_workder(self):
        global dpm
        ns_green = 15
        we_green = 15
        ns_yellow = 3
        we_yellow = 3
        while True:
            dpm.ticks = 0
            dpm.sum_time = 0
            dpm.lasttime = 0
            dpm.set_ns_green()
            self.set_NS_Light(3)
            dpm.set_we_red()
            self.set_WE_Light(1)
            self.dpm_log.append("正在测量南北方向车流量与车速")
            time.sleep(ns_green)
            if self.use_dpm.isChecked():
                ticks = dpm.ticks*4
                speed = 0
                if ticks != 0 and dpm.sum_time != 0:
                    speed = round(1 / (dpm.sum_time / dpm.ticks))
            else:
                speed,ticks = baidu_data.get_we()
            db.insert_sensor_result(0,ticks)
            dpm.stat[0] = ticks
            db.insert_sensor_result(2,speed)
            dpm.stat[2] = speed
            self.dpm_log.append("测量结束，南北方向车流=%d，南北方向平均车速=%d" % (ticks,speed))
            ticks = max(0,min(80,ticks))
            speed = max(0,min(45,speed))
            # 计算该方向新的红灯时间
            new_green_time = self.dpm_fim.infer(1,ticks)
            self.dpm_log.append("根据模糊推理结果，南北方向新绿灯时间=%f"%(new_green_time))
            db.insert_log(0,new_green_time)
            ns_green = new_green_time
            # 计算该方向新的黄灯时间
            new_yellow_time = self.dpm_fim.infer(2,speed)
            self.dpm_log.append("根据模糊推理结果，南北方向新黄灯时间=%f"%(new_yellow_time))
            db.insert_log(1,new_yellow_time)
            self.dpm_cim.update_realtime_info(ticks,speed)
            self.dpm_log.append("根据可信度推理结果，得到结论：%s"%(str(self.dpm_cim.infer())))
            ns_yellow = new_yellow_time
            dpm.set_ns_yellow()
            self.set_NS_Light(2)
            time.sleep(ns_yellow)
            dpm.set_ns_red()
            self.set_NS_Light(1)
            dpm.set_we_green()
            self.set_WE_Light(3)
            dpm.ticks = 0
            dpm.sum_time = 0
            dpm.lasttime = 0
            self.dpm_log.append("正在测量东西方向车流量与车速")
            time.sleep(we_green)
            if self.use_dpm.isChecked():
                ticks = dpm.ticks * 4
                speed = 0
                if ticks != 0 and dpm.sum_time != 0:
                    speed = round(1 / (dpm.sum_time / dpm.ticks))
            else:
                speed,ticks = baidu_data.get_we()
            db.insert_sensor_result(1,ticks)
            dpm.stat[1] = ticks
            db.insert_sensor_result(3,speed)
            dpm.stat[3] = speed
            self.dpm_log.append("测量结束，东西方向车流=%d，东西方向平均车速=%d" % (ticks,speed))
            ticks = max(0,min(80,ticks))
            speed = max(0,min(45,speed))
            # 计算该方向新的红灯时间
            new_green_time = self.dpm_fim.infer(1,ticks)
            self.dpm_log.append("根据模糊推理结果，东西方向新绿灯时间=%f"%(new_green_time))
            db.insert_log(2,new_green_time)
            we_green = new_green_time
            # 计算该方向新的黄灯时间
            new_yellow_time = self.dpm_fim.infer(2,speed)
            self.dpm_log.append("根据模糊推理结果，东西方向新黄灯时间=%f"%(new_yellow_time))
            db.insert_log(3,new_yellow_time)
            we_yellow = new_yellow_time
            self.dpm_cim.update_realtime_info(ticks,speed)
            self.dpm_log.append("根据可信度推理结果，得到结论：%s"%(str(self.dpm_cim.infer())))
            dpm.set_we_yellow()
            self.set_WE_Light(2)
            time.sleep(we_yellow)

    # 可信度知识展示
    def credit_show(self):
        credit_knowledge = c_manager.get_credit_knowledge()
        self.tableWidget.setRowCount(len(credit_knowledge))
        index_i, index_j = -1, -1
        for i in credit_knowledge:
            index_i += 1
            index_j = -1
            for j in credit_knowledge[i]:
                index_j += 1
                item = QTableWidgetItem(str(credit_knowledge[i][j]))
                if j == 'premise_id':
                    item = c_manager.get_premise_by_id(int(credit_knowledge[i][j]))
                    item = QTableWidgetItem(str(item))
                elif j == 'conclusion_id':
                    item = c_manager.get_conclusion_by_id(int(credit_knowledge[i][j]))
                    item = QTableWidgetItem(str(item))
                self.tableWidget.setItem(index_i, index_j, item)

    # 条件/前提插入
    def premise_insert(self):
        premis = self.premise.toPlainText()
        c_manager.insert_premise(premis)

    # 条件/前提删除
    def premise_delete(self):
        premise_id = self.premise.toPlainText()
        try:
            c_manager.delete_premise(int(premise_id))
        except:
            print("delete failed")

    # 条件/前提更新
    def premise_update(self):
        update_content = self.premise.toPlainText()
        try:
            id, content = update_content.split(',')
            c_manager.update_premise(id, content)
        except:
            print("update failed!")

    # 结论插入
    def conclusion_insert(self):
        conclusion = self.conclusion.toPlainText()
        c_manager.insert_conclusion(conclusion)

    # 结论删除
    def conclusion_delete(self):
        conclusion_id = self.conclusion.toPlainText()
        try:
            c_manager.delete_conclusion(int(conclusion_id))
        except:
            print("delete failed")

    # 结论更新
    def conclusion_update(self):
        update_content = self.conclusion.toPlainText()
        try:
            id, content = update_content.split(',')
            c_manager.update_conclusion(id, content)
        except:
            print("update failed!")

    # 可信度知识插入
    def credit_insert(self):
        premise_id = self.premise.toPlainText()
        conclusion_id = self.conclusion.toPlainText()
        pre_cred = self.CF.toPlainText()
        con_cred = self.lada.toPlainText()
        try:
            c_manager.insert_credit_knowledge(premise_id, conclusion_id, pre_cred, con_cred)
            self.credit_show()
        except:
            print("insert credit knowledge failed!")

    # 可信度知识删除
    def credit_delete(self):
        credit_id = self.credit_id.toPlainText()
        try:
            c_manager.delete_credit_knowledge(int(credit_id))
            self.credit_show()
        except:
            print("delete credit knowledge failed!")

    # 可信度知识修改
    def credit_update(self):
        credit_id = self.credit_id.toPlainText()
        premise_id = self.premise.toPlainText()
        conclusion_id = self.conclusion.toPlainText()
        pre_cred = self.CF.toPlainText()
        con_cred = self.lada.toPlainText()
        try:
            c_manager.update_credit_knowledge(credit_id, premise_id, conclusion_id, pre_cred, con_cred)
            self.credit_show()
        except:
            print("update credit knowledge failed!")

    # 模糊知识显示
    def fuzzy_show(self):
        fuzzy_knowledge = f_manager.get_fuzzy_knowledge()
        self.tableWidget_3.setRowCount(len(fuzzy_knowledge))
        index_i, index_j = -1, -1
        for i in fuzzy_knowledge:
            index_i += 1
            index_j = -1
            for j in fuzzy_knowledge[i]:
                index_j += 1
                item = QTableWidgetItem(str(fuzzy_knowledge[i][j]))
                if j == 'set_id_a' or j == 'set_id_b':
                    item = f_manager.get_fuzzy_set_name(int(fuzzy_knowledge[i][j]))
                    item = QTableWidgetItem(str(item))
                self.tableWidget_3.setItem(index_i, index_j, item)

    def fuzzy_insert(self):
        fuzzy_class = self.fuzzy_class.toPlainText()
        fuzzy_a = self.fuzzy_a.toPlainText()
        fuzzy_b = self.fuzzy_b.toPlainText()
        lamb = self.fuzzy_lambda.toPlainText()
        try:
            f_manager.insert_fuzzy_knowledge(int(fuzzy_class), lamb, int(fuzzy_a), int(fuzzy_b))
            self.fuzzy_show()
        except:
            print("insert fuzzy knowledge failed!")

    def fuzzy_delete(self):
        id = self.fuzzy_id.toPlainText()
        try:
            f_manager.delete_fuzzy_knowledge(int(id))
            self.fuzzy_show()
        except:
            print("delete fuzzy knowledge failed!")

    def fuzzy_update(self):
        id = self.fuzzy_id.toPlainText()
        fuzzy_class = self.fuzzy_class.toPlainText()
        fuzzy_a = self.fuzzy_a.toPlainText()
        fuzzy_b = self.fuzzy_b.toPlainText()
        lamb = self.fuzzy_lambda.toPlainText()
        try:
            f_manager.update_fuzzy_knowledge(int(id), int(fuzzy_class), lamb, int(fuzzy_a), int(fuzzy_b))
            self.fuzzy_show()
        except:
            print("update fuzzy knowledge failed!")

    def fuzzy_set_insert(self):
        fuzzy_set = self.fuzzy_a.toPlainText()
        try:
            f_manager.insert_fuzzy_set(fuzzy_set)
        except:
            print("insert fuzzy set failed!")

    def fuzzy_set_delete(self):
        id = self.fuzzy_a.toPlainText()
        try:
            f_manager.delete_fuzzy_set(int(id))
        except:
            print("delete fuzzy set failed!")

    def fuzzy_set_update(self):
        fuzzy_set = self.fuzzy_a.toPlainText()
        try:
            id, content = fuzzy_set.split(',')
            f_manager.update_fuzzy_set(int(id), content)
        except:
            print("update fuzzy_set failed!")
    
    def fuzzy_set_show(self):
        fuzzy_set_name = self.fuzzy_a.toPlainText()
        set_id = f_manager.get_fuzzy_set_id_by_name(fuzzy_set_name)
        if set_id == None:
            QMessageBox.critical(self,"错误","找不到模糊集名称")
        else:
            fuzzy_set = f_manager.get_fuzzy_set_by_id(set_id)
            x = fuzzy_set.keys()
            y = [fuzzy_set[key] for key in fuzzy_set.keys()]
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            plt.title(fuzzy_set_name)
            plt.xlabel("x")
            plt.ylabel("y")
            plt.plot(x,y,'b^-')
            plt.legend()
            plt.show()

    def set_NS_Light(self,status=0):
        if status == 0:
            self.NS_R_1.setStyleSheet("background-color: Black")
            self.NS_Y_1.setStyleSheet("background-color: Black")
            self.NS_G_1.setStyleSheet("background-color: Black")
            self.NS_R_2.setStyleSheet("background-color: Black")
            self.NS_Y_2.setStyleSheet("background-color: Black")
            self.NS_G_2.setStyleSheet("background-color: Black")
        elif status == 1:
            self.NS_R_1.setStyleSheet("background-color: Red")
            self.NS_Y_1.setStyleSheet("background-color: Black")
            self.NS_G_1.setStyleSheet("background-color: Black")
            self.NS_R_2.setStyleSheet("background-color: Red")
            self.NS_Y_2.setStyleSheet("background-color: Black")
            self.NS_G_2.setStyleSheet("background-color: Black")
        elif status == 2:
            self.NS_R_1.setStyleSheet("background-color: Black")
            self.NS_Y_1.setStyleSheet("background-color: Yellow")
            self.NS_G_1.setStyleSheet("background-color: Black")
            self.NS_R_2.setStyleSheet("background-color: Black")
            self.NS_Y_2.setStyleSheet("background-color: Yellow")
            self.NS_G_2.setStyleSheet("background-color: Black")
        elif status == 3:
            self.NS_R_1.setStyleSheet("background-color: Black")
            self.NS_Y_1.setStyleSheet("background-color: Black")
            self.NS_G_1.setStyleSheet("background-color: GreenYellow")
            self.NS_R_2.setStyleSheet("background-color: Black")
            self.NS_Y_2.setStyleSheet("background-color: Black")
            self.NS_G_2.setStyleSheet("background-color: GreenYellow")
    
    def set_WE_Light(self,status=0):
        if status == 0:
            self.WE_R_1.setStyleSheet("background-color: Black")
            self.WE_Y_1.setStyleSheet("background-color: Black")
            self.WE_G_1.setStyleSheet("background-color: Black")
            self.WE_R_2.setStyleSheet("background-color: Black")
            self.WE_Y_2.setStyleSheet("background-color: Black")
            self.WE_G_2.setStyleSheet("background-color: Black")
        elif status == 1:
            self.WE_R_1.setStyleSheet("background-color: Red")
            self.WE_Y_1.setStyleSheet("background-color: Black")
            self.WE_G_1.setStyleSheet("background-color: Black")
            self.WE_R_2.setStyleSheet("background-color: Red")
            self.WE_Y_2.setStyleSheet("background-color: Black")
            self.WE_G_2.setStyleSheet("background-color: Black")
        elif status == 2:
            self.WE_R_1.setStyleSheet("background-color: Black")
            self.WE_Y_1.setStyleSheet("background-color: Yellow")
            self.WE_G_1.setStyleSheet("background-color: Black")
            self.WE_R_2.setStyleSheet("background-color: Black")
            self.WE_Y_2.setStyleSheet("background-color: Yellow")
            self.WE_G_2.setStyleSheet("background-color: Black")
        elif status == 3:
            self.WE_R_1.setStyleSheet("background-color: Black")
            self.WE_Y_1.setStyleSheet("background-color: Black")
            self.WE_G_1.setStyleSheet("background-color: GreenYellow")
            self.WE_R_2.setStyleSheet("background-color: Black")
            self.WE_Y_2.setStyleSheet("background-color: Black")
            self.WE_G_2.setStyleSheet("background-color: GreenYellow")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.credit_show()
    myWin.fuzzy_show()
    myWin.show()
    sys.exit(app.exec_())