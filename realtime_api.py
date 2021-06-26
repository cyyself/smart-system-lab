import urllib.request
from urllib.parse import quote_plus, urlencode
import json
import time
class realtime_api: # 百度地图API，查询重庆大学虎溪校区附近的大学城中路与大学城南路的十字路口红绿灯
    def __init__(self):
        with open("api_key.txt","r",encoding="ascii") as file: # 需要将百度地图的api_key放在api_key.txt中
            self.api_key = file.read().strip()
        self.city = "重庆市"
        self.road_name_we = "大学城南路"
        self.road_name_ns = "大学城中路"
        self.speed_we = 40
        self.speed_ns = 40
        self.traffic_we = 10
        self.traffic_ns = 10
        self.update_ns()
        self.update_we()
    def online_query_we(self,debug=False):
        if debug:
            content = '{"status":0,"message":"成功","description":"大学城南路：双向畅通。","evaluation":{"status":1,"status_desc":"双向畅通"},"road_traffic":[{"road_name":"大学城南路"}]}'
        else:
            params = {'road_name':self.road_name_we,'city':self.city,'ak':self.api_key}
            url = "http://api.map.baidu.com/traffic/v1/road?" + urlencode(params,quote_via=quote_plus)
            content = urllib.request.urlopen(url).read().decode("utf-8")
        return json.loads(content)
    def online_query_ns(self,debug=False):
        if debug:
            content = '{"status":0,"message":"成功","description":"大学城中路：双向畅通；南向北,慕贤路附近严重拥堵；北向南,从雒城印象到思贤路行驶缓慢。","evaluation":{"status":1,"status_desc":"双向畅通"},"road_traffic":[{"congestion_sections":[{"congestion_distance":430,"speed":12.65,"status":4,"congestion_trend":"加重","section_desc":"南向北,慕贤路附近"},{"congestion_distance":240,"speed":18.93,"status":2,"congestion_trend":"持平","section_desc":"北向南,从雒城印象到思贤路"}],"road_name":"大学城中路"}]}'
        else:
            params = {'road_name':self.road_name_ns,'city':self.city,'ak':self.api_key}
            url = "http://api.map.baidu.com/traffic/v1/road?" + urlencode(params,quote_via=quote_plus)
            content = urllib.request.urlopen(url).read().decode("utf-8")
        return json.loads(content)
    def update_we(self,debug=False):
        try:
            status_we = self.online_query_we(debug)
            self.traffic_we = status_we['evaluation']['status'] * 10
            speed_sum = 0
            speed_cnt = 0
            for x in status_we['road_traffic']:
                if 'congestion_sections' in x:
                    for y in x['congestion_sections']:
                        speed_sum += y['speed']
                        speed_cnt += 1
            if speed_cnt == 0:
                self.speed_we = 40 # 由于百度地图API没有拥堵的情况下没有数据，因此选择默认值40
            else:
                self.speed_we = int(speed_sum / speed_cnt)
            print(status_we)
            self.last_we = time.time()
        except:
            print("联网获取东西向数据失败")
            pass
    def update_ns(self,debug=False):
        try:
            status_ns = self.online_query_ns(debug)
            self.traffic_ns = status_ns['evaluation']['status'] * 10
            speed_sum = 0
            speed_cnt = 0
            for x in status_ns['road_traffic']:
                if 'congestion_sections' in x:
                    for y in x['congestion_sections']:
                        speed_sum += y['speed']
                        speed_cnt += 1
            if speed_cnt == 0:
                self.speed_ns = 40 # 由于百度地图API没有拥堵的情况下没有数据，因此选择默认值40
            else:
                self.speed_ns = int(speed_sum / speed_cnt)
            print(status_ns)
            self.last_ns = time.time()
        except:
            print("联网获取南北向数据失败")
            pass
    def get_ns(self):
        if time.time() - self.last_ns > 10:
            self.update_ns()
        return self.speed_ns,self.traffic_ns
    def get_we(self):
        if time.time() - self.last_we > 10:
            self.update_we()
        return self.speed_we,self.traffic_we

if __name__ == "__main__":
    api = realtime_api()
    print(api.get_ns())
    print(api.get_we())