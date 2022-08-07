# coding=utf-8
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import LIGHT_SCHEDULE_FILE, PUMP_SCHEDULE_FILE

class MsgReader:
    def __init__(self, light_q, pump_q, light_event, pump_event):
        self.light_q = light_q
        self.pump_q = pump_q
        self.light_event = light_event
        self.pump_event = pump_event

    def read(self, properties):
        print(properties)
        if properties:
            self.device = properties.get('device', '')
            self.type = properties.get('type', '')
            self.data = properties.get('data', '')
            self.msg_handler()
    
    def msg_handler(self):
        if self.device.upper() == 'LED' or self.device.upper() == 'LIGHT':
            self.led_handler()
        if self.device.upper() == 'PUMP':
            self.pump_handler()

    def led_handler(self):
        if self.type == 'on-off':
            if self.data == 'on':
                self.light_q.put('on')
            elif self.data == 'off':
                self.light_q.put('off')
            elif self.data == 'boost':
                self.light_q.put('boost')
        elif self.type == 'reschedule':
            if self.data:
                with open(LIGHT_SCHEDULE_FILE, 'w') as fp:
                    fp.write(json.dump(self.data))
                    self.light_event.set()
        # elif self.type == 'lighter-dimmer':
        #     if self.data == 'lighter':
        #         led.lighter()
        #     elif self.data == 'dimmer':
        #         led.dimmer()
    
    def pump_handler(self):
        if self.type == 'on-off':
            if self.data == 'on':
                self.pump_q.put('on')
            elif self.data == 'off':
                self.pump_q.put('off')
        elif self.type == 'last_sec':
            last_sec = int(self.data) if self.data else None 
            self.pump_q.put(last_sec)
        elif self.type == 'reschedule':
            if self.data:
                with open(PUMP_SCHEDULE_FILE, 'w') as fp:
                    fp.write(json.dump(self.data))
                    self.pump_event.set()
                    