import sqlite3,time
class DB:
    def __init__(self):
        self.conn = sqlite3.connect("db.sqlite",check_same_thread=False)
        # init db for new database
        cur = self.conn.cursor()
        cur.execute('create table if not exists conclusion ( conclusion_id INTEGER constraint conclusion_pk primary key autoincrement, conclusion text );');
        cur.execute('create table if not exists premise ( premise_id INTEGER constraint premise_pk primary key autoincrement, premise text not null );');
        cur.execute('create table if not exists credit_knowledge ( credit_id INTEGER constraint credit_knowledge_pk primary key autoincrement, premise_id INTEGER not null references premise, conclusion_id INTEGER not null constraint credit_knowledge_conclusion_conclusion_id_fk references conclusion, pre_cred float not null, con_cred float not null, update_time DATETIME not null, update_person text not null );')
        cur.execute('create table if not exists fuzzy_set ( set_id INTEGER constraint set_pk primary key autoincrement, set_name TEXT );');
        cur.execute('create table if not exists set_element ( element_id INTEGER constraint set_element_pk primary key autoincrement, set_id INTEGER references fuzzy_set, x_pos INTEGER, x_name TEXT, y FLOAT not null );  ')
        cur.execute('create table if not exists fuzzy_knowledge ( fuzzy_id INTEGER constraint knowledge_pk primary key autoincrement, fuzzy_class INTEGER, lambda FLOAT, update_time DATETIME, update_person TEXT, set_id_a INTEGER, set_id_b INTEGER, constraint fuzzy_knowledge_fuzzy_set_set_id_set_id_fk foreign key (set_id_a, set_id_b) references fuzzy_set (set_id, set_id) );');
        cur.execute('create table if not exists log ( log_id INTEGER constraint log_pk primary key autoincrement, control_id INTEGER, control_value INTEGER, time DATETIME );');
        cur.execute('create table if not exists sensor_result ( sr_id INTEGER constraint sensor_result_pk primary key autoincrement, sensor_id INTEGER, sensor_result int, time DATETIME );');
        self.conn.commit()
    # Table log { 用于记录上位机传送给下位机的输出信号
    def reload_log(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `log_id`,`control_id`,`control_value`,`time` FROM `log`;')
        self.log = dict()
        for x in cur.fetchall():
            record = dict()
            record['log_id'] = x[0]
            record['control_id'] = x[1]
            record['control_value'] = x[2]
            record['time'] = x[3]
            self.log[x[0]] = record
    def get_log(self): # 上位机传递给下位机的控制数据
        if not hasattr(self,'log'):
            self.reload_log()
        return self.log
    def insert_log(self,control_id,control_value):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `log` VALUES (NULL,?,?,?);',(control_id,control_value,int(time.time())))
        self.conn.commit()
        self.reload_log()
    # Table log }
    # Table sensor_result { 用于记录上位机传递给下位机的数据
    def reload_sensor_result(self):
        cur = self.conn.cursor()
        cur.execute('SELECT `sr_id`,`sensor_id`,`sensor_result`,`time` FROM `sensor_result`;')
        self.sensor_result = dict()
        for x in cur.fetchall():
            record = dict()
            record['sr_id'] = x[0]
            record['sensor_id'] = x[1]
            record['sensor_result'] = x[2]
            record['time'] = x[3]
            self.sensor_result[x[0]] = record
    def get_sensor_result(self):
        if not hasattr(self,'sensor_result'):
            self.reload_sensor_result()
        return self.sensor_result
    def insert_sensor_result(self,sensor_id,sensor_result):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO `sensor_result` VALUES(NULL,?,?,?);',(sensor_id,sensor_result,int(time.time())))
        self.conn.commit()
        self.reload_sensor_result()
    # Table sensor_result }
