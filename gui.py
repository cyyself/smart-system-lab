import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox
from PyQt5.QtCore import QStringListModel
from mainui import Ui_MainWindow
from DownPosMachine import DownPosMachine
from DB import DB
from DownPosMachine import DownPosMachine
from fuzzy_infer_machine import fuzzy_infer_machine
from credit_infer_machine import credit_infer_machine
import time
import threading

db = DB()
dpm = None

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
        self.sim_log = []
        self.dpm_log = []
        self.sim_fim = fuzzy_infer_machine(db)
        self.sim_cim = credit_infer_machine(db)
        self.dpm_fim = fuzzy_infer_machine(db)
        self.dpm_cim = credit_infer_machine(db)
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
            dpm.set_we_red()
            self.dpm_log.append("正在测量南北方向车流量与车速")
            self.refresh_dpm_log()
            time.sleep(ns_green)
            ticks = dpm.ticks
            speed = 0
            if ticks != 0 and dpm.sum_time != 0:
                speed = round(10 / (dpm.sum_time / dpm.ticks))
            db.insert_sensor_result(0,ticks)
            dpm.stat[0] = ticks
            db.insert_sensor_result(2,speed)
            dpm.stat[2] = speed
            self.dpm_log.append("测量结束，南北方向车流=%d，南北方向平均车速=%d" % (ticks,speed))
            self.refresh_dpm_log()
            ticks = max(0,min(80,ticks))
            speed = max(0,min(45,speed))
            # 计算该方向新的红灯时间
            new_green_time = self.dpm_fim.infer(1,ticks)
            self.dpm_log.append("根据模糊推理结果，南北方向新绿灯时间=%f"%(new_green_time))
            self.refresh_dpm_log()
            db.insert_log(0,new_green_time)
            ns_green = new_green_time
            # 计算该方向新的黄灯时间
            new_yellow_time = self.dpm_fim.infer(2,speed)
            self.dpm_log.append("根据模糊推理结果，南北方向新黄灯时间=%f"%(new_yellow_time))
            db.insert_log(1,new_yellow_time)
            self.refresh_dpm_log()
            self.dpm_cim.update_realtime_info(ticks,speed)
            self.dpm_log.append("根据可信度推理结果，得到结论：%s"%(str(self.dpm_cim.infer())))
            self.refresh_dpm_log()
            ns_yellow = new_yellow_time
            dpm.set_ns_yellow()
            time.sleep(ns_yellow)
            dpm.set_ns_red()
            dpm.set_we_green()
            dpm.ticks = 0
            dpm.sum_time = 0
            dpm.lasttime = 0
            self.dpm_log.append("正在测量东西方向车流量与车速")
            self.refresh_dpm_log()
            time.sleep(we_green)
            ticks = dpm.ticks
            speed = 0
            if ticks != 0 and dpm.sum_time != 0:
                speed = round(10 / (dpm.sum_time / dpm.ticks))
            db.insert_sensor_result(1,ticks)
            dpm.stat[1] = ticks
            db.insert_sensor_result(3,speed)
            dpm.stat[3] = speed
            self.dpm_log.append("测量结束，东西方向车流=%d，东西方向平均车速=%d" % (ticks,speed))
            self.refresh_dpm_log()
            ticks = max(0,min(80,ticks))
            speed = max(0,min(45,speed))
            # 计算该方向新的红灯时间
            new_green_time = self.dpm_fim.infer(1,ticks)
            self.dpm_log.append("根据模糊推理结果，东西方向新绿灯时间=%f"%(new_green_time))
            self.refresh_dpm_log()
            db.insert_log(2,new_green_time)
            we_green = new_green_time
            # 计算该方向新的黄灯时间
            new_yellow_time = self.dpm_fim.infer(2,speed)
            self.dpm_log.append("根据模糊推理结果，东西方向新黄灯时间=%f"%(new_yellow_time))
            self.refresh_dpm_log()
            db.insert_log(3,new_yellow_time)
            we_yellow = new_yellow_time
            self.dpm_cim.update_realtime_info(ticks,speed)
            self.dpm_log.append("根据可信度推理结果，得到结论：%s"%(str(self.dpm_cim.infer())))
            self.refresh_dpm_log()
            dpm.set_we_yellow()
            time.sleep(we_yellow)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())