import serial
import time
import threading
class DownPosMachine:
    def __init__(self,serialPort="/dev/cu.usbmodem14401",measuring_time=10,baudRate=9600):
        self.ser = serial.Serial(serialPort, baudRate)
        print("串口=%s，波特率=%d" % (serialPort, baudRate))
        time.sleep(3)
        self.ticks = 0
        self.sum_time = 0
        self.lasttime = 0
        self.measuring_time = measuring_time # 方向变换的时间
        self.t1 = threading.Thread(target=self.serial_recv,args=())
        self.t1.setDaemon(True)
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