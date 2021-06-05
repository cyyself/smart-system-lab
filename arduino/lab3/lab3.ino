// 端口定义
int SENSOR = 2;
int NS_R = 3;
int NS_Y = 4;
int NS_G = 5;
int WE_R = 6;
int WE_Y = 7;
int WE_G = 8;

int SENSOR_last = 0; // 记录传感器上次的状态，用于检测下降沿

void setup() {
  pinMode(SENSOR,INPUT);
  pinMode(NS_R,OUTPUT);
  pinMode(NS_Y,OUTPUT);
  pinMode(NS_G,OUTPUT);
  pinMode(WE_R,OUTPUT);
  pinMode(WE_Y,OUTPUT);
  pinMode(WE_G,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int SENSOR_curr = digitalRead(SENSOR);
  if (SENSOR_curr != SENSOR_last) {
    if (SENSOR_last == HIGH) {
      Serial.println("posedge");
    }
    else if (SENSOR_last == LOW) { // 检测到下降沿，发送tick
      Serial.println("negedge");
    }
    SENSOR_last = SENSOR_curr; // 更新last状态
  }
  char serial_read;
  while ((serial_read = Serial.read()) != -1) {
    // 读取上位机发送的字节，设置到对应的灯
    if (serial_read == '3') {
      digitalWrite(NS_R,HIGH);
      digitalWrite(NS_Y,LOW);
      digitalWrite(NS_G,LOW);
    }
    else if (serial_read == '4') {
      digitalWrite(NS_R,LOW);
      digitalWrite(NS_Y,HIGH);
      digitalWrite(NS_G,LOW);
    }
    else if (serial_read == '5') {
      digitalWrite(NS_R,LOW);
      digitalWrite(NS_Y,LOW);
      digitalWrite(NS_G,HIGH);
    }
    else if (serial_read == '6') {
      digitalWrite(WE_R,HIGH);
      digitalWrite(WE_Y,LOW);
      digitalWrite(WE_G,LOW);
    }
    else if (serial_read == '7') {
      digitalWrite(WE_R,LOW);
      digitalWrite(WE_Y,HIGH);
      digitalWrite(WE_G,LOW);
    }
    else if (serial_read == '8') {
      digitalWrite(WE_R,LOW);
      digitalWrite(WE_Y,LOW);
      digitalWrite(WE_G,HIGH);
    }
  }
  delay(100);
}
