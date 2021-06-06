from fuzzy_manager import fuzzy_manager
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
    def explain_log(self,log,filename="tmp"):
        dot = Digraph(comment='解释器')
        prev = None
        for i in range(len(log)):
            dot.node(str(i),log[i])
            if prev is not None:
                dot.edge(str(prev),str(i))
            prev = i
        #print(dot.source)
        dot.render(filename,view=True)