from fuzzy_manager import fuzzy_manager
from credit_manager import credit_manager
from graphviz import Digraph
class fuzzy_infer_machine:
    def __init__(self,db):
        self.db = db
        self.fm = fuzzy_manager(db)
        self.log = []
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
    def infer(self,class_id,input,delta=3):
        knowledges_id = self.fm.get_knowledge_id_by_class(class_id)
        knowledges = self.fm.get_fuzzy_knowledge()
        cur_log = []
        cur_log.append("开始执行推理，class=%d，输入=%d"%(class_id,input))
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
        cur_log.append("进行模糊化，delta=%d"%(delta))
        # 计算贴近度
        max_deg = 0
        max_deg_knowledge = -1
        for kid in knowledges_id:
            fuzzy_set = self.fm.get_fuzzy_set_by_id(knowledges[kid]['set_id_a'])
            fuzzy_vector = [self.fm.get_fuzzy_set_y(fuzzy_set,x) for x in input_range]
            deg = (self.inner_product(fuzzy_vector,input_fuzzy_mtx)+(1-self.outer_product(fuzzy_vector,input_fuzzy_mtx)))/2
            cur_log.append("计算输入与知识%d前提模糊集%d的贴近度C=%f。"%(kid,knowledges[kid]['set_id_a'],deg))
            if deg > max_deg:
                max_deg = deg
                max_deg_knowledge = kid
        if max_deg_knowledge != -1 and max_deg >= knowledges[max_deg_knowledge]['lambda']:
            cur_log.append("计算最大贴近度=%f，成功匹配模糊知识%d,lambda=%f"%(max_deg,max_deg_knowledge,knowledges[max_deg_knowledge]['lambda']))
            # 计算模糊矩阵R(A,B)
            set_id_a = knowledges[max_deg_knowledge]['set_id_a']
            set_id_b = knowledges[max_deg_knowledge]['set_id_b']
            fuzzy_mtx = self.fm.get_fuzzy_matrix(set_id_a,set_id_b,1,1)
            cur_log.append("成功计算模糊矩阵")
            # 复合计算，B'=D*R(A,B)
            result = self.dot_product(input_fuzzy_mtx,fuzzy_mtx)
            cur_log.append("成功进行复合计算")
            # 去模糊化-重心法
            result_range = self.fm.get_fuzzy_set_range(set_id_b)
            fz = sum([(result_range[0] + i)*result[i] for i in range(len(result))])
            fm = sum(result)
            cur_log.append("通过重心法进行去模糊化，得到输出=%f"%(fz/fm))
            self.log.append(cur_log)
            return fz / fm
        else:
            cur_log.append("无法匹配模糊知识")
            self.log.append(cur_log)
            return 15 # 无法匹配任何结论（按照我们的设计实际不会存在这种情况）
    def get_log(self):
        return self.log
class credit_infer_machine:
    def __init__(self,db):
        self.db = db
        self.cm = credit_manager(db)
        self.cf_p = dict()
        self.cf_p['下雨'] = 0.4
        self.cf_p['下雪'] = 0.2
        self.cf_p['大风'] = 0.5
        self.log = []
    def parse_exp(self,s):
        s = s.replace(" ","")
        s = s.replace("&"," & ")
        s = s.replace("|"," | ")
        return s.split(" ")
    def get_cf_p(self,s,cf_p=None):
        if cf_p is None:
            cf_p = self.cf_p
        if s in cf_p:
            return cf_p[s]
        else:
            return 0
    def cal_cf_p(self,s,cf_p=None):
        if cf_p is None:
            cf_p = self.cf_p
        token = self.parse_exp(s)
        lastval = None
        lasttoken = None
        for x in token:
            if x == '&' or x == '|':
                lasttoken = x
            else:
                if lasttoken is not None:
                    if lasttoken == '&':
                        lastval = min(lastval,self.get_cf_p(x,cf_p))
                    else:
                        lastval = max(lastval,self.get_cf_p(x,cf_p))
                    lasttoken = None
                else:
                    lastval = self.get_cf_p(x,cf_p)
        return lastval
    def update_realtime_info(self,traffic,speed,temp=30):
        speed = max(0,min(45,speed))
        traffic = max(0,min(traffic,80))
        temp = max(0,min(40,temp))
        self.cf_p['车速大'] = speed / 45
        self.cf_p['车流量大'] = traffic / 80
        self.cf_p['车速小'] = 1 - self.cf_p['车速大']
        self.cf_p['车流量小'] = 1 - self.cf_p['车流量大']
        self.cf_p['高温'] = temp / 40
    def infer(self,return_cf_p=False):
        cf_p = self.cf_p.copy()
        premises = self.cm.get_premise()
        conclusions = self.cm.get_conclusion()
        knowledges = self.cm.get_credit_knowledge()
        update = True
        while update:
            update = False
            for kid in knowledges:
                knowledge = knowledges[kid]
                premise = premises[knowledge['premise_id']]
                conclusion = conclusions[knowledge['conclusion_id']]
                val = self.cal_cf_p(premise,cf_p)
                if val >= knowledge['pre_cred']:
                    if self.get_cf_p(conclusion,cf_p) != val * knowledge['con_cred']:
                        update = True
                        cf_p[conclusion] = val * knowledge['con_cred']
        if return_cf_p:
            return cf_p
        else:
            return set(cf_p.keys()) - set(self.cf_p.keys()) # 返回新得出的结论
    def explain(self,cf_p):
        dot = Digraph(comment='解释器')
        node_vis = set()
        premises = self.cm.get_premise()
        conclusions = self.cm.get_conclusion()
        knowledges = self.cm.get_credit_knowledge()
        for kid in knowledges:
            knowledge = knowledges[kid]
            premise = premises[knowledge['premise_id']]
            conclusion = conclusions[knowledge['conclusion_id']]
            if conclusions[knowledge['conclusion_id']] in cf_p.keys():
                for each_premise in self.parse_exp(premise):
                    if each_premise == '&' or each_premise == '|':
                        continue
                    if each_premise not in node_vis:
                        dot.node(each_premise,"CF_p(%s)=%f"%(each_premise,cf_p[each_premise]))
                        node_vis.add(each_premise)
                    dot.edge(each_premise,conclusion)
        print(dot.source)
        dot.render("Digraph.gv",view=True)
