#coding=utf-8
import pigpio
import RPi.GPIO as GPIO
import time

from config import CHANNEL_LED, CHANNEL_BUTTON, FREQ_LED, INIT_DUTY_LED, LAST_SECS_LIGHT_SWITCH

def init():
    print('LED Switch test started at channel {}'.format(CHANNEL_LED))
    GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by GPIO pin, not physical location
    GPIO.setup(CHANNEL_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set buttonPin's mode is input, and pull up to high level(3.3V)
    return pigpio.pi()

def clear():
    GPIO.cleanup()                     # Release resource

def stop(pwm):
    pwm.stop()
    GPIO.cleanup()
    print('LED Switch test started at channel {}, GPIO cleaned up'.format(CHANNEL_LED))
    print('----------------------------------------')

def start_led_switch_test():
    try:
        pwm = init()
        pwm.set_PWM_dutycycle(CHANNEL_LED, INIT_DUTY_LED)                 # Started PWM at 100% duty cycle
        start_time = int(time.time())
        # button 
        led_status_map = ['off', 'on']
        led_status = 1
        sleep_interval = 0.08
        pressed = 0
        print('LED is {}, press the button to switch on/off'.format(led_status_map[led_status]))

        while True:
            time.sleep(sleep_interval)
            if start_time + LAST_SECS_LIGHT_SWITCH <= int(time.time()):
                op = input("LED Test Switch has run {} seconds, do you want to continue?(y/n)".format(LAST_SECS_LIGHT_SWITCH))
                if not op == 'no' and not op == 'n' :
                    start_time = int(time.time())
                else:
                    break
            if GPIO.input(CHANNEL_BUTTON) == GPIO.HIGH:
                if pressed == 1:
                    print('Button pressed, switching LED {}'.format(led_status_map[led_status]))
                    pwm.set_PWM_dutycycle(CHANNEL_LED, led_status * INIT_DUTY_LED)
                    pressed = 0
            else:
                # only trigger the first catch, do nothing if it's holding
                if pressed == 0:
                    pressed = 1
                    led_status = 0 if led_status == 1 else 1
        
        stop(pwm)

    except KeyboardInterrupt:
        stop(pwm)
    
