# coding=utf-8
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sensors.temp_humidity import get_temp_n_hum
from sensors.WaterLevel import WaterLevel
from config import TEMP_STATUS, WATER_LVL_STATUS, HUMIDITY_STATUS
from util import guarantee_dir

def detect_sensor():
    guarantee_dir(os.path.dirname(TEMP_STATUS))
    guarantee_dir(os.path.dirname(HUMIDITY_STATUS))
    guarantee_dir(os.path.dirname(WATER_LVL_STATUS))
    
    """
        measure the temp and humidity
    """
    try:
        temp, humidity = get_temp_n_hum()
    except Exception as e:
        print(str(e))
        temp = humidity = 'error'
    with open(TEMP_STATUS, 'w') as fp:
        fp.write(str(temp))
    with open(HUMIDITY_STATUS, 'w') as fp:
        fp.write(str(humidity))

    """
        measure the water_lvl
    """
    try:
        w = WaterLevel()
        water_lvl = w.measure()
    except Exception as e:
        print(str(e))
        water_lvl = 'error'
    with open(WATER_LVL_STATUS, 'w') as fp:
        fp.write(str(water_lvl))


if __name__ == '__main__':
    detect_sensor()