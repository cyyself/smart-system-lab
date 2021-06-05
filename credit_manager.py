import time,getpass
class credit_manager:
    def __init__(self,db):
        self.conn = db.conn
    # Table premise {
    def get_premise_by_id(self,premise_id):
        premise = self.get_premise()
        return premise[premise_id]
    def reload_premise(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `premise_id`, `premise` FROM `premise`;')
        self.premise = dict()
        for x in cur.fetchall():
            self.premise[x[0]] = x[1]
    def get_premise(self):
        if not hasattr(self,'premise'):
            self.reload_premise()
        return self.premise
    def update_premise(self,premise_id,premise):
        cur = self.conn.cursor()
        cur.execute('UPDATE `premise` SET `premise` = ? WHERE `premise_id` = ?;',(premise,premise_id))
        self.conn.commit()
        self.reload_premise()
    def insert_premise(self,premise):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `premise` VALUES (NULL,?);',(premise,))
        self.conn.commit()
        self.reload_premise()
    def delete_premise(self,premise_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM `premise` WHERE `premise_id` = ?',(premise_id,))
        self.conn.commit()
        self.reload_conclusion()
    # Table premise }
    # Table conclusion {
    def get_conclusion_by_id(self,conclusion_id):
        conclusion = self.get_conclusion()
        return conclusion[conclusion_id]
    def reload_conclusion(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `conclusion_id`,`conclusion` FROM `conclusion`;')
        self.conclusion = dict()
        for x in cur.fetchall():
            self.conclusion[x[0]] = x[1]
    def get_conclusion(self):
        if not hasattr(self,'conclusion'):
            self.reload_conclusion()
        return self.conclusion
    def update_conclusion(self,conclusion_id,conclusion):
        cur = self.conn.cursor()
        cur.execute('UPDATE `conclusion` SET `conclusion` = ? WHERE `conclusion_id` = ?;',(conclusion,conclusion_id))
        self.conn.commit()
        self.reload_conclusion()
    def insert_conclusion(self,conclusion):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `conclusion` VALUES (NULL,?);',(conclusion,))
        self.conn.commit()
        self.reload_conclusion()
    def delete_conclusion(self,conclusion_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM `conclusion` WHERE `conclusion_id` = ?;',(conclusion_id,))
        self.conn.commit()
        self.reload_conclusion()
    # Table conclusion }
    # Table credit_knowledge {
    def reload_credit_knowledge(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `credit_id`,`premise_id`,`conclusion_id`,`pre_cred`,`con_cred`,`update_time`,`update_person` FROM `credit_knowledge`;')
        self.credit_knowledge = dict()
        for x in cur.fetchall():
            record = dict()
            record['credit_id'] = x[0]
            record['premise_id'] = x[1]
            record['conclusion_id'] = x[2]
            record['pre_cred'] = x[3]
            record['con_cred'] = x[4]
            record['update_time'] = x[5]
            record['update_person'] = x[6]
            self.credit_knowledge[x[0]] = record
    def get_credit_knowledge(self): # 可信度知识
        if not hasattr(self,'credit_knowledge'):
            self.reload_credit_knowledge()
        return self.credit_knowledge
    def update_credit_knowledge(self,credit_id,premise_id,conclusion_id,pre_cred,con_cred):
        cur = self.conn.cursor()
        cur.execute('UPDATE `credit_knowledge` SET `premise_id` = ?, `conclusion_id` = ?, `pre_cred` = ?, `con_cred` = ?, `update_time` = ?, `update_person` = ? WHERE `credit_id` = ?;',(premise_id,conclusion_id,pre_cred,con_cred,int(time.time()),getpass.getuser(),credit_id))
        self.conn.commit()
        self.reload_credit_knowledge()
    def insert_credit_knowledge(self,premise_id,conclusion_id,pre_cred,con_cred):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `credit_knowledge` VALUES(NULL,?,?,?,?,?,?);',(premise_id,conclusion_id,pre_cred,con_cred,int(time.time()),getpass.getuser()))
        self.conn.commit()
        self.reload_credit_knowledge()
    def delete_credit_knowledge(self,credit_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM `credit_knowledge` WHERE `credit_id` = ?;',(credit_id,))
        self.conn.commmit()
        self.reload_credit_knowledge()
    # Table credit_knowledge }
