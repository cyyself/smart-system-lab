import serial
import time
import threading
class DownPosMachine:
    def __init__(self,db,measuring_time=10,serialPort="/dev/cu.usbmodem143201",baudRate=9600):
        self.ser = serial.Serial(serialPort, baudRate)
        print("串口=%s，波特率=%d" % (serialPort, baudRate))
        time.sleep(3)
        self.ticks = 0
        self.sum_time = 0
        self.lasttime = 0
        self.measuring_time = measuring_time # 方向变换的时间
        self.t1 = threading.Thread(target=self.serial_recv,args=())
        self.t2 = threading.Thread(target=self.counting,args=())
        self.db = db
        self.stat = [0,0,0,0]
        self.t1.start()
    def serial_recv(self):
        self.ticks = 0
        self.sum_time = 0
        self.lasttime = 0
        while True:
            s = self.ser.readline()
            if s == b'posedge\r\n':
                self.lasttime = time.time()
            elif s == b'negedge\r\n':
                if self.lasttime != 0:
                    thistime = time.time() - self.lasttime
                    self.sum_time += thistime
                    self.ticks += 1
                    print("car passed, time = %f" % (thistime))
            else:
                print(s)
    def counting(self):
        while True:
            self.ticks = 0
            self.sum_time = 0
            self.lasttime = 0
            print("正在测量南北方向车流量与车速")
            time.sleep(self.measuring_time)
            ticks = self.ticks
            speed = 0
            if ticks != 0 and self.sum_time != 0:
                speed = round(100 / (self.sum_time / self.ticks))
            self.db.insert_sensor_result(0,ticks)
            self.stat[0] = ticks
            self.db.insert_sensor_result(2,speed)
            self.stat[2] = speed
            print("测量结束，南北方向车流=%d，南北方向平均车速=%d" % (ticks,speed))
            self.ticks = 0
            self.sum_time = 0
            self.lasttime = 0
            print("正在测量东西方向车流量")
            time.sleep(self.measuring_time)
            ticks = self.ticks
            speed = 0
            if ticks != 0 and self.sum_time != 0:
                speed = round(100 / (self.sum_time / self.ticks))
            self.db.insert_sensor_result(1,ticks)
            self.stat[1] = ticks
            self.db.insert_sensor_result(3,speed)
            self.stat[3] = speed
            print("测量结束，东西方向车流=%d，东西方向平均车速=%d" % (ticks,speed))
    def start_counting(self):
        self.t2.start()
    def set_ns_red(self):
        self.ser.write(b"3")
    def set_ns_yellow(self):
        self.ser.write(b"4")
    def set_ns_green(self):
        self.ser.write(b"5")
    def set_we_red(self):
        self.ser.write(b"6")
    def set_we_yellow(self):
        self.ser.write(b"7")
    def set_we_green(self):
        self.ser.write(b"8")
    def do_led_test(self):
        self.set_ns_red()
        time.sleep(1)
        self.set_ns_yellow()
        time.sleep(1)
        self.set_ns_green()
        time.sleep(1)
        self.set_we_red()
        time.sleep(1)
        self.set_we_yellow()
        time.sleep(1)
        self.set_we_green()
        time.sleep(1)