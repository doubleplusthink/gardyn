#coding=utf-8
import pigpio
import time
import os

from common.util import guarantee_dir
from config import CHANNEL_LED, CHANNEL_BUTTON, FREQ_LED, LAST_SECS_LIGHT_SWITCH, LIGHT_STATUS, PREV_LIGHT_STATUS

class LED:
    # 0 => off
    # 1 => on
    LIGHT_STATUS = 0
    LIGHT_DUTY = 0
    DUTY_INTERVAL = 10
    MIN_DUTY = 0
    MAX_DUTY = 255
    HALF_DUTY = 128
    INTERRUPT = False

    def __init__(self, init_status = 0):
        self.LIGHT_STATUS = init_status
        self.LIGHT_DUTY = init_status * 100
        self.pwm = pigpio.pi()

    def save_status(self, light_duty):
        d = os.path.dirname(LIGHT_STATUS)
        guarantee_dir(d)
        status = str(int(light_duty * 100 / self.MAX_DUTY))
        with open(LIGHT_STATUS, 'w') as fp:
            fp.write(status)
    
    def save_prev_status(self, light_duty):
        d = os.path.dirname(PREV_LIGHT_STATUS)
        guarantee_dir(d)
        status = str(int(light_duty * 100 / self.MAX_DUTY))
        with open(PREV_LIGHT_STATUS, 'w') as fp:
            fp.write(status)
        
    def get_old_status(self):
        duty = 0
        if os.path.isfile(PREV_LIGHT_STATUS):
            with open(PREV_LIGHT_STATUS, 'r') as fp:
                duty = int(int(fp.read()) * self.MAX_DUTY / 100)
        return duty

    def start(self):
        print('led starting')
        if not self.pwm:
            self.pwm = pigpio.pi()
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.MIN_DUTY)
        self.save_status(self.MIN_DUTY)


    def stop(self):
        if self.pwm:
            self.pwm.set_PWM_frequency(CHANNEL_LED, 0)
            self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.MIN_DUTY)
            # self.pwm.stop()
        # self.pwm = None
        print('led stopped')

    def turn_on(self):
        if self.INTERRUPT:
            return False
        if not hasattr(self, 'pwm') or not self.pwm:
            self.start()
        self.LIGHT_STATUS = 1
        old_duty = self.get_old_status()
        self.LIGHT_DUTY = self.LIGHT_STATUS * 128 if not old_duty else old_duty
        print("Changing it to {}".format(self.LIGHT_DUTY))
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
        self.save_status(self.LIGHT_DUTY)

    def boost(self):
        if self.INTERRUPT:
            return False
        if not hasattr(self, 'pwm') or not self.pwm:
            self.start()
        self.LIGHT_STATUS = 1
        self.LIGHT_DUTY = self.LIGHT_STATUS * self.MAX_DUTY
        print("Changing it to {}".format(self.LIGHT_DUTY))
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
        self.save_status(self.LIGHT_DUTY)

    def turn_off(self):
        if self.INTERRUPT:
            return False
        if hasattr(self, 'pwm'):
            self.LIGHT_STATUS = 0
            self.LIGHT_DUTY = self.LIGHT_STATUS * 0
            print("Changing it to {}".format(self.LIGHT_DUTY))
            self.pwm.set_PWM_frequency(CHANNEL_LED, 0)
            self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
            self.save_status(self.LIGHT_DUTY)
            self.stop()


    def lighter(self):
        if self.INTERRUPT:
            return False
        self.LIGHT_STATUS = 1
        self.LIGHT_DUTY = min(self.MAX_DUTY, self.LIGHT_DUTY + self.DUTY_INTERVAL)
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
        self.save_status(self.LIGHT_DUTY)

    def dimmer(self):
        if self.INTERRUPT:
            return False
        self.LIGHT_DUTY = min(self.MIN_DUTY, self.LIGHT_DUTY - self.DUTY_INTERVAL)
        if not self.LIGHT_DUTY:
            self.LIGHT_STATUS = 0
            self.pwm.set_PWM_frequency(CHANNEL_LED, self.MIN_DUTY)
        else:
            self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
        self.save_status(self.LIGHT_DUTY)

    def adjust(self, percent):
        if self.INTERRUPT:
            return False
        p = int(percent)
        new_light_duty = int(p * self.MAX_DUTY / 100)
        if not hasattr(self, 'pwm') or not self.pwm:
            self.start()
        self.LIGHT_DUTY = min(max(self.MIN_DUTY, new_light_duty), self.MAX_DUTY)
        if not self.LIGHT_DUTY:
            self.turn_off()
        else:
            self.LIGHT_STATUS = 1
            self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
            self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
            self.save_status(self.LIGHT_DUTY)
            self.save_prev_status(self.LIGHT_DUTY)
    
    def blink(self, times):
        self.INTERRUPT = True
        if not hasattr(self, 'pwm') or not self.pwm:
            self.start()
        old_duty = self.LIGHT_DUTY
        self.pwm.set_PWM_frequency(CHANNEL_LED, FREQ_LED)
        for i in range(times):
            self.blink_once()
        
        self.LIGHT_DUTY = old_duty
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
        if not self.LIGHT_DUTY:
            self.pwm.set_PWM_frequency(CHANNEL_LED, 0)
        self.INTERRUPT = False

    def blink_once(self):
        self.LIGHT_DUTY = 0 if self.LIGHT_DUTY > 0 else self.HALF_DUTY
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
        time.sleep(1)
        self.LIGHT_DUTY = 0 if self.LIGHT_DUTY > 0 else self.HALF_DUTY
        self.pwm.set_PWM_dutycycle(CHANNEL_LED, self.LIGHT_DUTY)
        time.sleep(1)


led = LED()
