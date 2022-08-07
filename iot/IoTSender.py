#coding=utf-8
import json
import time
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sensors.temp_humidity import get_temp_n_hum
from sensors.WaterLevel import WaterLevel
from config import NETWORK_PATH, CONN_STR_FILE, IOT_MSG_INTERVAL, TEMP_STATUS, \
    WATER_LVL_STATUS, HUMIDITY_STATUS, LIGHT_STATUS, PUMP_STATUS, CAMERA_STATUS, \
    LIGHT_SCHEDULE_STATUS, PUMP_SCHEDULE_STATUS, PREV_LIGHT_STATUS, VERSION_PATH, \
    TIME_ZONE_STATUS, TIME_ZONE
from util import read_from_file, guarantee_dir
from iot.IoTClient import IoTClient

class IoTSender:

    def __init__(self, iot_client):
        self.client = iot_client
        self.water_lvl = WaterLevel()
        guarantee_dir(os.path.dirname(TEMP_STATUS))
        guarantee_dir(os.path.dirname(HUMIDITY_STATUS))
        guarantee_dir(os.path.dirname(WATER_LVL_STATUS))
        
    def run(self):
        try:
            self.send()
            time.sleep(3)
        except Exception as e:
            print("Unexpected error {} from IoTHub".format(str(e)))
            pass
            
    def send(self, light=None, pump=None):
        """
            measure the temp and humidity
        """
        try:
            temp, humidity = get_temp_n_hum()
        except Exception as e:
            temp = humidity = 'error'
        with open(TEMP_STATUS, 'w') as fp:
            fp.write(str(temp))
        with open(HUMIDITY_STATUS, 'w') as fp:
            fp.write(str(humidity))

        """
            measure the water_lvl
        """
        try:
            water_lvl = self.water_lvl.measure()
        except Exception as e:
            water_lvl = 'error'
            pass
        with open(WATER_LVL_STATUS, 'w') as fp:
            fp.write(str(water_lvl))
            
        light = read_from_file(os.path.dirname(LIGHT_STATUS), os.path.basename(LIGHT_STATUS)) if light is None else light
        pump = read_from_file(os.path.dirname(PUMP_STATUS), os.path.basename(PUMP_STATUS)) if pump is None else pump
        message = self.message_wrapper(temp, humidity, water_lvl, light, pump)
        # print("Sending message: {}".format(message.get_string()))
        self.client.send_message(message)
    
    def send_light_n_pump(self, light=None, pump=None):
        temp = read_from_file(os.path.dirname(TEMP_STATUS), os.path.basename(TEMP_STATUS))
        humidity = read_from_file(os.path.dirname(HUMIDITY_STATUS), os.path.basename(HUMIDITY_STATUS))
        water_lvl = read_from_file(os.path.dirname(WATER_LVL_STATUS), os.path.basename(WATER_LVL_STATUS))
        if not temp or not humidity or not water_lvl:
            self.send(light, pump)
        else:
            message = self.message_wrapper(temp, humidity, water_lvl, light, pump)
            self.client.send_message(message)

    def message_wrapper(self, t, h, w, l, p):
        """
            read schedule_status
            1 => 'on'
            2 => 'off'
        """
        light_schedule = read_from_file(os.path.dirname(LIGHT_SCHEDULE_STATUS), os.path.basename(LIGHT_SCHEDULE_STATUS))
        pump_schedule = read_from_file(os.path.dirname(PUMP_SCHEDULE_STATUS), os.path.basename(PUMP_SCHEDULE_STATUS))
        prev_light = read_from_file(os.path.dirname(PREV_LIGHT_STATUS), os.path.basename(PREV_LIGHT_STATUS))
        camera_status = read_from_file(os.path.dirname(CAMERA_STATUS), os.path.basename(CAMERA_STATUS))
        light_schedule = 2 if light_schedule == 'off' else 1
        pump_schedule = 2 if pump_schedule == 'off' else 1
        camera_status = 2 if camera_status == 'off' else 1
        data = {
            "temp": t,
            "humidity": h,
            "water_lvl": w,
            "light": l,
            "pump": p,
            "light_schedule": light_schedule,
            "pump_schedule": pump_schedule,
            "prev_light": prev_light,
            "camera_status": camera_status
        }
        
        data['version'] = read_from_file(os.path.dirname(VERSION_PATH), os.path.basename(VERSION_PATH)) or 'unknown'
        data['timezone'] = read_from_file(os.path.dirname(TIME_ZONE_STATUS), os.path.basename(TIME_ZONE_STATUS)) or TIME_ZONE

        return json.dumps(data)
    
if __name__ == '__main__':
    conn_string = read_from_file(NETWORK_PATH, CONN_STR_FILE)
    if conn_string:
        iot_client = IoTClient.get_client(conn_string)
        iot_client.connect()
        sender = IoTSender(iot_client)
        sender.run()
