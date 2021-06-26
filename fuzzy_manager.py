import time,getpass
class fuzzy_manager:
    def __init__(self,db):
        self.conn = db.conn
    # Table fuzzy element {
    def reload_set_element(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `element_id`,`set_id`,`x_pos`,`x_name`,`y` FROM `set_element` ORDER BY `x_pos`;')
        self.set_element = dict()
        for x in cur.fetchall():
            record = dict()
            record['element_id'] = x[0]
            record['set_id'] = x[1]
            record['x_pos'] = x[2]
            record['x_name'] = x[3]
            record['y'] = x[4]
            self.set_element[x[0]] = record
    def get_set_element(self):
        if not hasattr(self,'set_element'):
            self.reload_set_element()
        return self.set_element
    def update_fuzzy_element(self,element_id,set_id,x_pos,x_name,y):
        cur = self.conn.cursor()
        cur.execute('UPDATE `set_element` SET `set_id` = ?, `x_pos` = ?, `x_name` = ?, `y` = ? WHERE `element_id` = ?;',(set_id,x_pos,x_name,y,element_id))
        self.conn.commit()
        self.reload_set_element()
    def insert_fuzzy_element(self,set_id,x_pos,x_name,y):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `set_element` VALUES (NULL,?,?,?,?);',(set_id,x_pos,x_name,y))
        self.conn.commit()
        self.reload_set_element()
    def delete_fuzzy_element(self,element_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM `set_element` WHERE `element_id` = ?;',(element_id,))
        self.conn.commit()
        self.reload_set_element()
    def get_fuzzy_set_by_id(self,set_id):
        set_elem = self.get_set_element()
        fuzzy_set = dict()
        for id in set_elem:
            item = set_elem[id]
            if item['set_id'] == set_id:
                fuzzy_set[item['x_pos']] = item['y']
        return fuzzy_set
    def get_fuzzy_set_y(self,fuzzy_set,x):
        x_values = sorted(fuzzy_set.keys())
        if x < x_values[0]:
            return fuzzy_set[x_values[0]]
        elif x > x_values[-1]:
            return fuzzy_set[x_values[-1]]
        else:
            i = 0
            j = 1
            while j < len(x_values):
                if x_values[i] <= x and x <= x_values[j]:
                    return fuzzy_set[x_values[i]] + (fuzzy_set[x_values[j]] - fuzzy_set[x_values[i]]) * (x - x_values[i]) / (x_values[j] - x_values[i])
                i += 1
                j += 1
    def get_fuzzy_set_name(self,set_id):
        fuzzy_set = self.get_fuzzy_set()
        return fuzzy_set[set_id]
    def get_fuzzy_set_range(self,set_id):
        set = self.get_fuzzy_set_by_id(set_id)
        key = sorted(set.keys())
        return (key[0],key[-1])
    def get_fuzzy_matrix(self,set_id_a,set_id_b,step_a=10,step_b=10):
        set_a = self.get_fuzzy_set_by_id(set_id_a)
        set_b = self.get_fuzzy_set_by_id(set_id_b)
        key_a = sorted(set_a.keys())
        key_b = sorted(set_b.keys())
        range_a = range(key_a[0],key_a[-1]+step_a,step_a)
        range_b = range(key_b[0],key_b[-1]+step_b,step_b)
        val_a = [self.get_fuzzy_set_y(set_a,x) for x in range_a]
        val_b = [self.get_fuzzy_set_y(set_b,x) for x in range_b]
        matrix = []
        i = 0
        for a_val in range_a:
            j = 0
            line = []
            for b_val in range_b:
                line.append(max(min(float(val_a[i]),float(val_b[j])),(1-float(val_a[i]))))
                j += 1
            matrix.append(line)
            i += 1
        return matrix
    def print_fuzzy_matrix(self,set_id_a,set_id_b,step_a=10,step_b=10):
        set_a = self.get_fuzzy_set_by_id(set_id_a)
        set_b = self.get_fuzzy_set_by_id(set_id_b)
        key_a = sorted(set_a.keys())
        key_b = sorted(set_b.keys())
        range_a = range(key_a[0],key_a[-1]+step_a,step_a)
        range_b = range(key_b[0],key_b[-1]+step_b,step_b)
        val_a = [self.get_fuzzy_set_y(set_a,x) for x in range_a]
        val_b = [self.get_fuzzy_set_y(set_b,x) for x in range_b]
        print("模糊矩阵：" + self.get_fuzzy_set_name(set_id_a) + "/" + self.get_fuzzy_set_name(set_id_b))
        title_line = [str(set_id_a) + "/" + str(set_id_b)] + ["%0.3f" % x for x in range_b]
        print("\t".join(title_line))
        i = 0
        for a_val in range_a:
            j = 0
            line = ["%0.3f" % a_val]
            for b_val in range_b:
                line.append("%0.3f" % max(min(float(val_a[i]),float(val_b[j])),(1-float(val_a[i]))))
                j += 1
            print("\t".join(line))
            i += 1
    # Table fuzzy element }
    # Table fuzzy knowledge {
    def get_knowledge_id_by_class(self,fuzzy_class):
        fuzzy_knowledge = self.get_fuzzy_knowledge()
        res = []
        for i in fuzzy_knowledge:
            if fuzzy_knowledge[i]['fuzzy_class'] == fuzzy_class:
                res.append(i)
        return res
    def reload_fuzzy_knowledge(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `fuzzy_id`,`set_id_a`,`set_id_b`,`fuzzy_class`,`lambda`,`update_time`,`update_person` FROM `fuzzy_knowledge`;')
        self.fuzzy_knowledge = dict()
        for x in cur.fetchall():
            record = dict()
            record['fuzzy_id'] = x[0]
            record['set_id_a'] = x[1]
            record['set_id_b'] = x[2]
            record['fuzzy_class'] = x[3]
            record['lambda'] = x[4]
            record['update_time'] = x[5]
            record['update_person'] = x[6]
            self.fuzzy_knowledge[x[0]] = record
    def get_fuzzy_knowledge(self): # 模糊知识
        if not hasattr(self,'fuzzy_knowledge'):
            self.reload_fuzzy_knowledge()
        return self.fuzzy_knowledge
    def update_fuzzy_knowledge(self,fuzzy_id,fuzzy_class,lamb,set_id_a,set_id_b):
        cur = self.conn.cursor()
        cur.execute(
            'UPDATE `fuzzy_knowledge` SET `fuzzy_class` = ?, `lambda` = ?, `update_time` = ?, `update_person` = ?, `set_id_a` = ?, `set_id_b` = ? WHERE `fuzzy_id` = ?;',
            (fuzzy_class,lamb,int(time.time()),getpass.getuser(),set_id_a,set_id_b,fuzzy_id)
        )
        self.conn.commit()
        self.reload_fuzzy_knowledge()
    def insert_fuzzy_knowledge(self,fuzzy_class,lamb,set_id_a,set_id_b):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `fuzzy_knowledge` VALUES (NULL,?,?,?,?,?,?);',(fuzzy_class,lamb,int(time.time()),getpass.getuser(),set_id_a,set_id_b))
        self.conn.commit()
        self.reload_fuzzy_knowledge()
    def delete_fuzzy_knowledge(self,fuzzy_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM `fuzzy_knowledge` WHERE `fuzzy_id` = ?;',(fuzzy_id,))
        self.conn.commit()
        self.reload_fuzzy_knowledge()
    # Table fuzzy knowledge }
    # Table fuzzy set {
    def reload_fuzzy_set(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `set_id`,`set_name` FROM `fuzzy_set`;')
        self.fuzzy_set = dict()
        for x in cur.fetchall():
            self.fuzzy_set[x[0]] = x[1]
    def get_fuzzy_set(self):
        if not hasattr(self,'fuzzy_set'):
            self.reload_fuzzy_set()
        return self.fuzzy_set
    def update_fuzzy_set(self,set_id,set_name):
        cur = self.conn.cursor()
        cur.execute('UPDATE `fuzzy_set` SET `set_name` = ? WHERE `set_id` = ?;',(set_name,set_id))
        self.conn.commit()
        self.reload_fuzzy_set()
    def insert_fuzzy_set(self,set_name):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `fuzzy_set` VALUES (NULL,?);',(set_name,))
        self.conn.commit()
        self.reload_fuzzy_set()
    def delete_fuzzy_set(self,set_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM `fuzzy_set` WHERE `set_id` = ?;',(set_id,))
        self.conn.commit()
        self.reload_fuzzy_set()
    # Table fuzzy set }
