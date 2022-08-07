# coding=utf-8
import RPi.GPIO as GPIO
import time
from test.water_pump_sensor import read_ina219

from config import CHANNEL_WATER_PUMP, FREQ_WATER_PUMP, INIT_DUTY_WATER_PUMP, LAST_SECS_WATER_PUMP

def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CHANNEL_WATER_PUMP, GPIO.OUT)
    return GPIO.PWM(CHANNEL_WATER_PUMP, FREQ_WATER_PUMP)

def clear():
    GPIO.cleanup()
    print('Water Pump test stopped at channel {}, GPIO has been cleaned up'.format(CHANNEL_WATER_PUMP))
    print('----------------------------------------')
    read_ina219()

def pump():
    read_ina219()
    pwm = init()
    duty = INIT_DUTY_WATER_PUMP
    pwm.start(duty)
    print('Water Pump test started at channel {}, will last for {} seconds.'.format(CHANNEL_WATER_PUMP, LAST_SECS_WATER_PUMP))
    start_time = int(time.time())
    increasing = True
    try:
        while start_time + LAST_SECS_WATER_PUMP > int(time.time()):
            if duty == 100:
                increasing = False
            elif duty == 0:
                increasing = True
            if increasing:
                duty += 10
            else: 
                duty -= 10
            pwm.ChangeDutyCycle(duty)
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        clear()