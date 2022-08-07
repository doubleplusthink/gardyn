# coding=utf-8
import time
import argparse

from config import TEST_INTERVAL
from test.camera import take_photos
from test.dimmer import dim
from test.interrupt_temp import start_interrupt_temp
from test.led_open_switch import start_led_switch_test
from test.temp_humidity import get_temp_n_hum
from test.water_level import get_water_lvl
from test.water_pump_sensor import read_ina219
from test.water_pump_switch import pump

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tester', help='testers that will run')
parser.add_argument('-i', '--interval', help='time interval between each test')
parser.add_argument('-s', '--skip', help='testers that will skip')
args = parser.parse_args()

def main():
    tester_map = {
        'camera': take_photos, # camera test
        'dim': dim, # dimmer test
        'internal_temp': start_interrupt_temp, # interanl temp alarm
        'led_switch': start_led_switch_test, # led switch test
        'temp_n_hum': get_temp_n_hum, # temperature and humidity
        'water_lvl': get_water_lvl, # water level
        'pump': pump    # water pump switch
    }
    interval = args.interval if args.interval is not None else TEST_INTERVAL
    testers = args.tester.split(',') if args.tester is not None else ['all']
    skips = args.skip.split(',') if args.skip is not None else []

    test_all = True if 'all' in testers else False
    for tester in tester_map:
        if (test_all or tester in testers) and tester not in skips:
            tester_map[tester]()

if __name__ == '__main__':
    main()

    
