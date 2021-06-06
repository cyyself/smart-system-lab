from credit_manager import credit_manager
from graphviz import Digraph
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
    def update_environment(self,rain,snow,wind):
        rain = max(0,min(100,rain))
        snow = max(0,min(100,snow))
        wind = max(0,min(100,wind))
        self.cf_p['下雨'] = rain / 100
        self.cf_p['下雪'] = snow / 100
        self.cf_p['大风'] = wind / 100
    def update_realtime_info(self,traffic,speed,temp=20):
        speed = max(0,min(45,speed))
        traffic = max(0,min(traffic,80))
        temp = max(0,min(40,temp))
        #self.cf_p['车速大'] = speed / 45
        self.cf_p['车流量大'] = traffic / 80
        self.cf_p['车速小'] = 1 - (speed / 45)#self.cf_p['车速大']
        #self.cf_p['车流量小'] = 1 - self.cf_p['车流量大']
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
        self.log.append(cf_p)
        if return_cf_p:
            return cf_p
        else:
            return set(cf_p.keys()) - set(self.cf_p.keys()) # 返回新得出的结论
    def explain(self,cf_p,filename="tmp"):
        dot = Digraph(comment='解释器')
        for key in cf_p:
            dot.node(key,"CF_p(%s)=%f"%(key,cf_p[key]))
        #node_vis = set()
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
                    """
                    if each_premise not in node_vis:
                        dot.node(each_premise,"CF_p(%s)=%f"%(each_premise,cf_p[each_premise]))
                        node_vis.add(each_premise)
                    """
                    dot.edge(each_premise,conclusion)
        dot.render(filename,view=True)
    def get_log(self):
        return self.log