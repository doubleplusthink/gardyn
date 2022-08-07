# coding=utf-8
import RPi.GPIO as GPIO
import time

from config import CHANNEL_DIMMER, FREQ_DIMMER, INIT_DUTY_DIMMER, LAST_SECS_DIMMER

def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CHANNEL_DIMMER, GPIO.OUT)
    return GPIO.PWM(CHANNEL_DIMMER, FREQ_DIMMER)

def clear():
    GPIO.cleanup()
    print('Dimmer test stopped at channel {}, GPIO cleaned up'.format(CHANNEL_DIMMER))
    print('----------------------------------------')

def dim():
    pwm = init()
    duty = INIT_DUTY_DIMMER
    pwm.start(duty)
    print('Dimmer test started at channel {}, will last for {} seconds.'.format(CHANNEL_DIMMER, LAST_SECS_DIMMER))
    start_time = int(time.time())
    try:
        while start_time + LAST_SECS_DIMMER > int(time.time()):
            if duty == 100:
                increasing = False
            elif duty == 0:
                increasing = True
            if increasing:
                duty += 10
            else: 
                duty -= 10
            pwm.ChangeDutyCycle(duty)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        clear()