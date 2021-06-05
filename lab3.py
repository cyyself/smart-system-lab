#!/usr/bin/env python3
import time

from fuzzy_manager import fuzzy_manager
from credit_manager import credit_manager
from DB import DB
from DownPosMachine import DownPosMachine

db = DB()

def init_credit_knowledge(): # 初始化可信度知识
    cm = credit_manager(db)
    # 添加前提
    cm.insert_premise("下雨")
    cm.insert_premise("下雪")
    cm.insert_premise("下冰雹")
    cm.insert_premise("晴天")
    cm.insert_premise("风速等级大于5级")
    cm.insert_premise("eval(F3&F7)#车速小 and 车流量大")
    # 添加结论
    cm.insert_conclusion("红灯时间+5s")
    cm.insert_conclusion("红灯时间-5s")
    cm.insert_conclusion("红灯时间+10s")
    cm.insert_conclusion("红灯时间-10s")
    cm.insert_conclusion("报警，可能发生事故")
    # 添加可信度知识
    cm.insert_credit_knowledge(premise_id=1,conclusion_id=1,pre_cred=0.8,con_cred=0.7);# 下雨 and 红灯延长5s
    cm.insert_credit_knowledge(premise_id=2,conclusion_id=3,pre_cred=0.9,con_cred=0.9);# 下雪 and 红灯延长10s
    cm.insert_credit_knowledge(premise_id=4,conclusion_id=2,pre_cred=0.7,con_cred=0.5);# 晴天 and 红灯减少5s
    cm.insert_credit_knowledge(premise_id=5,conclusion_id=4,pre_cred=0.7,con_cred=0.6);# 大风 and 红灯减少10s

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
    fm.insert_fuzzy_knowledge(1,0.8,1,4)# 车流量小/绿灯时间短,lambda=0.8
    fm.insert_fuzzy_knowledge(1,0.8,2,5)# 车流量适中/绿灯时间适中,lambda=0.8
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
"""
dpm = DownPosMachine(db)

dpm.start_counting()
"""
class fuzzy_infer_machine:
    def __init__(self,db):
        self.db = db
        self.fm = fuzzy_manager(db)
    def infer(self,traffic,speed):
        return None
    def inner_product(self,x,y): # 计算内积
        assert len(x) == len(y), "inner_product only available for same size"
        return max([min(x[i],y[i]) for i in range(len(x))])
    def outer_product(self,x,y): # 计算外积
        assert len(x) == len(y), "outer_product only available for same size"
        return min([max(x[i],y[i]) for i in range(len(x))])
    def dot_product(self,x,y): # 计算B' = D*R(A,B)的过程
        return [max([min(x[i],y[i][j]) for i in range(len(x))]) for j in range(len(y[0]))]
    def infer(self,class_id,input,delta=3,explain=False):
        knowledges_id = self.fm.get_knowledge_id_by_class(class_id)
        knowledges = self.fm.get_fuzzy_knowledge()
        # 模糊化-预处理
        input_range = self.fm.get_fuzzy_set_range(knowledges[knowledges_id[0]]['set_id_a'])
        for x in knowledges_id:
            assert self.fm.get_fuzzy_set_range(knowledges[x]['set_id_a']) == input_range, "fuzzy set range for input can't be different"
        input_range = range(input_range[0],input_range[1]+1)
        input_fuzzy_mtx = [0 for _ in input_range] # 将车流量模糊化的结果
        # 模糊化-三角法
        i = 0
        for x in input_range:
            if abs(x - input) <= delta:
                input_fuzzy_mtx[i] = 1 - abs(input - x) / delta
            else:
                input_fuzzy_mtx[i] = 0.0
            i += 1
        max_deg = 0
        max_deg_knowledge = -1
        # 计算贴近度
        for kid in knowledges_id:
            fuzzy_set = self.fm.get_fuzzy_set_by_id(knowledges[kid]['set_id_a'])
            fuzzy_vector = [self.fm.get_fuzzy_set_y(fuzzy_set,x) for x in input_range]
            deg = (self.inner_product(fuzzy_vector,input_fuzzy_mtx)+(1-self.outer_product(fuzzy_vector,input_fuzzy_mtx)))/2
            if deg > max_deg:
                max_deg = deg
                max_deg_knowledge = kid
        if max_deg_knowledge != -1:
            if explain:
                if max_deg >= knowledges[max_deg_knowledge]['lambda']:
                    print("解释：C=%f,成功匹配模糊知识%d,lambda=%f"%(max_deg,max_deg_knowledge,knowledges[max_deg_knowledge]['lambda']))
                else:
                    print("解释：C=%f,无法匹配模糊知识%d,lambda=%f"%(max_deg,max_deg_knowledge,knowledges[max_deg_knowledge]['lambda']))
        else:
            return 15 # 无法匹配任何结论（按照我们的设计实际不会存在这种情况）
        # 计算模糊矩阵R(A,B)
        set_id_a = knowledges[max_deg_knowledge]['set_id_a']
        set_id_b = knowledges[max_deg_knowledge]['set_id_b']
        fuzzy_mtx = self.fm.get_fuzzy_matrix(set_id_a,set_id_b,1,1)
        # 复合计算，B'=D*R(A,B)
        result = self.dot_product(input_fuzzy_mtx,fuzzy_mtx)
        # 去模糊化-重心法
        result_range = self.fm.get_fuzzy_set_range(set_id_b)
        fz = sum([(result_range[0] + i)*result[i] for i in range(len(result))])
        fm = sum(result)
        return fz / fm 
        
fim = fuzzy_infer_machine(db)


for i in range(0,81):
    print(i,fim.infer(1,i))

for i in range(0,46):
    print(i,fim.infer(2,i))
"""
class infer_machine:
    def __init__(self,db):
        self.db = db
        self.fm = fuzzy_manager(db)
        self.cm = credit_manager(db)
    def load_knowledge(self):
        print(self.fm.get_fuzzy_knowledge())
        print(self.cm.get_credit_knowledge())
        print(self.cm.get_premise_by_id(1))
        print(self.cm.get_conclusion_by_id(1))
    def get_cf_p(self,premise_id):
        premise = self.cm.get_conclusion_by_id(premise_id)
        if premise == "下雨":
            return 0.5
        elif premise == "下雪":
            return 0.5
        elif premise == "下冰雹":
            return 0.5
        elif premise == "晴天":
            return 0.5
        elif premise == "风速等级大于5级":
            return 0.5
        elif premise == "通行速度缓慢":
            
        elif premise[0:5] == "eval(":

im = infer_machine(db)
im.load_knowledge()
"""
#test_fuzzy_matrix_cal()