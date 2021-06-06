#!/usr/bin/env python3
import time
from fuzzy_manager import fuzzy_manager
from credit_manager import credit_manager
from DB import DB
from DownPosMachine import DownPosMachine
from fuzzy_infer_machine import fuzzy_infer_machine
from credit_infer_machine import credit_infer_machine

db = DB()

def init_credit_knowledge(): # 初始化可信度知识
    cm = credit_manager(db)
    # 添加前提
    cm.insert_premise("下雨|下雪|大风") # 1
    cm.insert_premise("恶劣天气") # 2
    cm.insert_premise("车速小&车流量大") # 3
    cm.insert_premise("可能发生事故") # 4
    cm.insert_premise("高温") # 5
    # 添加结论
    cm.insert_conclusion("恶劣天气") # 1
    cm.insert_conclusion("黄灯时间+2") # 2
    cm.insert_conclusion("可能发生事故") # 3
    cm.insert_conclusion("发出事故警报") # 4
    cm.insert_conclusion("发出高温警报") # 5
    # 添加可信度知识
    cm.insert_credit_knowledge(premise_id=1,conclusion_id=1,pre_cred=0.7,con_cred=1) # 下雨|下雪|大风 -> 恶劣天气 lambda=0.7 cf=1
    cm.insert_credit_knowledge(premise_id=2,conclusion_id=2,pre_cred=0.5,con_cred=1) # 恶劣天气 -> 黄灯时间+2s
    cm.insert_credit_knowledge(premise_id=3,conclusion_id=3,pre_cred=0.5,con_cred=0.8) # 车速小&车流量大 -> 可能发生事故
    cm.insert_credit_knowledge(premise_id=4,conclusion_id=4,pre_cred=0.4,con_cred=0.9) # 可能发生事故->发出警报
    cm.insert_credit_knowledge(premise_id=5,conclusion_id=5,pre_cred=0.7,con_cred=0.9) # 高温->高温警报
def init_fuzzy_knowledge(): # 初始化模糊知识
    fm = fuzzy_manager(db)
    # 添加模糊集
    fm.insert_fuzzy_set("车流量小")
    fm.insert_fuzzy_set("车流量适中")
    fm.insert_fuzzy_set("车流量大")
    fm.insert_fuzzy_set("绿灯时间长")
    fm.insert_fuzzy_set("绿灯时间适中")
    fm.insert_fuzzy_set("绿灯时间短")
    fm.insert_fuzzy_set("车速小")
    fm.insert_fuzzy_set("车速适中")
    fm.insert_fuzzy_set("车速大")
    fm.insert_fuzzy_set("黄灯时间短")
    fm.insert_fuzzy_set("黄灯时间适中")
    fm.insert_fuzzy_set("黄灯时间长")
    # 添加模糊集元素
    # 1-车流量小
    fm.insert_fuzzy_element(1,0,"车流量0",1)
    fm.insert_fuzzy_element(1,20,"车流量20",0.5)
    fm.insert_fuzzy_element(1,40,"车流量40",0)
    fm.insert_fuzzy_element(1,80,"车流量80",0)
    # 2-车流量适中
    fm.insert_fuzzy_element(2,0,"车流量0",0)
    fm.insert_fuzzy_element(2,20,"车流量20",0.5)
    fm.insert_fuzzy_element(2,40,"车流量40",1)
    fm.insert_fuzzy_element(2,60,"车流量60",0.5)
    fm.insert_fuzzy_element(2,80,"车流量80",0)
    # 3-车流量大
    fm.insert_fuzzy_element(3,0,"车流量0",0)
    fm.insert_fuzzy_element(3,40,"车流量40",0)
    fm.insert_fuzzy_element(3,60,"车流量60",0.5)
    fm.insert_fuzzy_element(3,80,"车流量80",1)
    # 4-绿灯时间短
    fm.insert_fuzzy_element(4,10,"绿灯时间10s",1)
    fm.insert_fuzzy_element(4,20,"绿灯时间20s",0.5)
    fm.insert_fuzzy_element(4,30,"绿灯时间30s",0)
    # 5-绿灯时间适中
    fm.insert_fuzzy_element(5,10,"绿灯时间10s",0)
    fm.insert_fuzzy_element(5,20,"绿灯时间20s",1)
    fm.insert_fuzzy_element(5,30,"绿灯时间30s",0)
    # 6-绿灯时间长
    fm.insert_fuzzy_element(6,10,"绿灯时间10s",0)
    fm.insert_fuzzy_element(6,20,"绿灯时间20s",0.5)
    fm.insert_fuzzy_element(6,30,"绿灯时间30s",1)
    # 7-车速小
    fm.insert_fuzzy_element(7,0,"车速0",1)
    fm.insert_fuzzy_element(7,15,"车速15",0.5)
    fm.insert_fuzzy_element(7,30,"车速30",0)
    fm.insert_fuzzy_element(7,45,"车速45",0)
    # 8-车速适中
    fm.insert_fuzzy_element(8,0,"车速0",0)
    fm.insert_fuzzy_element(8,15,"车速15",1)
    fm.insert_fuzzy_element(8,30,"车速30",1)
    fm.insert_fuzzy_element(8,45,"车速45",0)
    # 9-车速大
    fm.insert_fuzzy_element(9,0,"车速0",0)
    fm.insert_fuzzy_element(9,15,"车速15",0)
    fm.insert_fuzzy_element(9,30,"车速30",0.5)
    fm.insert_fuzzy_element(9,45,"车速45",1)
    # 10-黄灯时间短
    fm.insert_fuzzy_element(10,3,"黄灯时间3s",1)
    fm.insert_fuzzy_element(10,4,"黄灯时间4s",0.5)
    fm.insert_fuzzy_element(10,5,"黄灯时间5s",0)
    # 11-黄灯时间适中
    fm.insert_fuzzy_element(11,3,"黄灯时间3s",0.5)
    fm.insert_fuzzy_element(11,4,"黄灯时间4s",1)
    fm.insert_fuzzy_element(11,5,"黄灯时间5s",0.5)
    # 12-黄灯时间长
    fm.insert_fuzzy_element(12,3,"黄灯时间3s",0)
    fm.insert_fuzzy_element(12,4,"黄灯时间4s",0.5)
    fm.insert_fuzzy_element(12,5,"黄灯时间5s",1)
    # 添加模糊知识
    fm.insert_fuzzy_knowledge(1,0.7,1,4)# 车流量小/绿灯时间短,lambda=0.7
    fm.insert_fuzzy_knowledge(1,0.7,2,5)# 车流量适中/绿灯时间适中,lambda=0.7
    fm.insert_fuzzy_knowledge(1,0.7,3,6)# 车流量大/绿灯时间长,lambda=0.7
    fm.insert_fuzzy_knowledge(2,0.4,9,12)# 车速小/黄灯时间长,lambda=0.4
    fm.insert_fuzzy_knowledge(2,0.4,8,11)# 车速适中/黄灯时间适中,lambda=0.4
    fm.insert_fuzzy_knowledge(2,0.6,7,10)# 车速大/黄灯时间段,lambda=0.6

def test_fuzzy_matrix_cal():
    fm = fuzzy_manager(db)
    fuzzy_knowledge = fm.get_fuzzy_knowledge()
    for x in fuzzy_knowledge:
        item = fuzzy_knowledge[x]
        fm.print_fuzzy_matrix(item['set_id_a'],item['set_id_b'])

def db_init():
    init_credit_knowledge()
    init_fuzzy_knowledge()
#db_init()


fim = fuzzy_infer_machine(db)

def test_fuzzy_infer():
    for i in range(0,81):
        print(i,fim.infer(1,i))

    for i in range(0,46):
        print(i,fim.infer(2,i))
"""
print(fim.get_log())
test_fuzzy_infer()
print(fim.get_log())
"""
cim = credit_infer_machine(db)

cim.update_realtime_info(50,0)
print(cim.parse_exp("下雨|下雪|大风"))
print(cim.parse_exp("恶劣天气"))
print(cim.cal_cf_p("恶劣天气"))
print(cim.cal_cf_p("下雨|下雪"))
print(cim.cal_cf_p("车速小&车流量大"))
cf_p = cim.infer(True)
cim.explain(cf_p)

#test_fuzzy_matrix_cal()


dpm = DownPosMachine()

def running_thread():
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
        print("正在测量南北方向车流量与车速")
        time.sleep(ns_green)
        ticks = dpm.ticks
        speed = 0
        if ticks != 0 and dpm.sum_time != 0:
            speed = round(10 / (dpm.sum_time / dpm.ticks))
        db.insert_sensor_result(0,ticks)
        dpm.stat[0] = ticks
        db.insert_sensor_result(2,speed)
        dpm.stat[2] = speed
        print("测量结束，南北方向车流=%d，南北方向平均车速=%d" % (ticks,speed))
        ticks = max(0,min(80,ticks))
        speed = max(0,min(45,speed))
        # 计算该方向新的红灯时间
        new_green_time = fim.infer(1,ticks)
        fim.explain_log(fim.get_log()[-1])
        print("根据模糊推理结果，南北方向新绿灯时间=%f"%(new_green_time))
        ns_green = new_green_time
        # 计算该方向新的黄灯时间
        new_yellow_time = fim.infer(2,speed)
        print("根据模糊推理结果，南北方向新黄灯时间=%f"%(new_yellow_time))
        cim.update_realtime_info(ticks,speed)
        print("根据可信度推理结果，得到结论：",cim.infer())
        ns_yellow = new_yellow_time
        dpm.set_ns_yellow()
        time.sleep(ns_yellow)
        dpm.set_ns_red()
        dpm.set_we_green()
        dpm.ticks = 0
        dpm.sum_time = 0
        dpm.lasttime = 0
        print("正在测量东西方向车流量")
        time.sleep(we_green)
        ticks = dpm.ticks
        speed = 0
        if ticks != 0 and dpm.sum_time != 0:
            speed = round(10 / (dpm.sum_time / dpm.ticks))
        db.insert_sensor_result(1,ticks)
        dpm.stat[1] = ticks
        db.insert_sensor_result(3,speed)
        dpm.stat[3] = speed
        print("测量结束，东西方向车流=%d，东西方向平均车速=%d" % (ticks,speed))
        ticks = max(0,min(80,ticks))
        speed = max(0,min(45,speed))
        # 计算该方向新的红灯时间
        new_green_time = fim.infer(1,ticks)
        print("根据模糊推理结果，东西方向新绿灯时间=%f"%(new_green_time))
        we_green = new_green_time
        # 计算该方向新的黄灯时间
        new_yellow_time = fim.infer(2,speed)
        print("根据模糊推理结果，东西方向新黄灯时间=%f"%(new_yellow_time))
        we_yellow = new_yellow_time
        cim.update_realtime_info(ticks,speed)
        print("根据可信度推理结果，得到结论：",cim.infer())
        dpm.set_we_yellow()
        time.sleep(we_yellow)

#running_thread()