# coding=utf-8
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from util import guarantee_dir, read_from_file
from config import LIGHT_SCHEDULE_FILE, PUMP_SCHEDULE_FILE, LIGHT_SCHEDULE_STATUS, \
    PUMP_SCHEDULE_STATUS, CAMERA_STATUS, VERSION_PATH, LOG_TAR_NAME, TIME_ZONE_STATUS
from storage import LogStorage

class DMHandler:

    def __init__(self, light_q, pump_q, light_event, pump_event, status_q):
        self.light_q = light_q
        self.pump_q = pump_q
        self.light_event = light_event
        self.pump_event = pump_event
        self.status_q = status_q
        self.log_storage = LogStorage()
        """
            check if the light schedule or pump schedule has been turned off in the file.
        """
        guarantee_dir(os.path.dirname(LIGHT_SCHEDULE_STATUS))
        guarantee_dir(os.path.dirname(PUMP_SCHEDULE_STATUS))

        light_status = read_from_file(os.path.dirname(LIGHT_SCHEDULE_STATUS), os.path.basename(LIGHT_SCHEDULE_STATUS))
        pump_status = read_from_file(os.path.dirname(PUMP_SCHEDULE_STATUS), os.path.basename(PUMP_SCHEDULE_STATUS))
        
        if light_status == 'off':
            light_q.put('schedule_off')
        if pump_status == 'off':
            pump_q.put('schedule_off')
            

    def parse(self, method_name, payload):
        try:
            if method_name and getattr(self, method_name):
                getattr(self, method_name)(payload)
            else:
                raise Exception('method {} not supported'.format(method_name))
        except Exception as e:
            print(e) 

    def reschedule(self, payload):
        if not payload:
            raise Exception('payload is not provided')
        
        payload = json.loads(payload) if type(payload) == str else payload
        device = payload.get('device', '').upper()
        data = payload.get('data', '')

        if not device:
            raise Exception('device not provided')
        elif device not in ['LED', 'LIGHT', 'LIGHTS', 'PUMP']:
            raise Exception('device: {} not supported'.format(device))
        elif not data:
            raise Exception('schedule not provided')
        
        if device == 'LED' or device == 'LIGHT' or device == 'LIGHTS':
            with open(LIGHT_SCHEDULE_FILE, 'w') as fp:
                json.dump(data, fp)
            self.light_event.set()
        elif device == 'PUMP':
            with open(PUMP_SCHEDULE_FILE, 'w') as fp:
                json.dump(data, fp)
            self.pump_event.set()

    def light_adjust(self, payload):
        if not payload:
            raise Exception('payload is not provided')
        payload = json.loads(payload) if type(payload) == str else payload

        if payload.get('percent'):
            self.light_q.put(payload)

    def light_on(self, payload):
        self.light_q.put('manual_on')

    def lighter(self, payload):
        self.light_q.put('lighter')

    def dimmer(self, payload):
        self.light_q.put('dimmer')

    def light_off(self, payload):
        self.light_q.put('manual_off')

    def light_boost(self, payload):
        self.light_q.put('manual_boost')

    def pump_on(self, payload):
        self.pump_q.put('on')

    def pump_off(self, payload):
        self.pump_q.put('off')

    def light_schedule_on(self, payload):
        with open(LIGHT_SCHEDULE_STATUS, 'w') as fp:
            fp.write('on')
        self.light_q.put('schedule_on')

    def light_schedule_off(self, payload):
        with open(LIGHT_SCHEDULE_STATUS, 'w') as fp:
            fp.write('off')
        self.light_q.put('schedule_off')
        
    def pump_schedule_on(self, payload):
        with open(PUMP_SCHEDULE_STATUS, 'w') as fp:
            fp.write('on')
        self.pump_q.put('schedule_on')

    def pump_schedule_off(self, payload):
        with open(PUMP_SCHEDULE_STATUS, 'w') as fp:
            fp.write('off')
        self.pump_q.put('schedule_off')

    def reboot(self, payload):
        os.system('reboot')

    def camera_on(self, payload):
        with open(CAMERA_STATUS, 'w') as fp:
            fp.write('on')

    def camera_off(self, payload):
        with open(CAMERA_STATUS, 'w') as fp:
            fp.write('off')

    def log(self, payload):
        os.system('tar cvf {} /var/log'.format(LOG_TAR_NAME))
        self.log_storage.upload(LOG_TAR_NAME)
        if os.path.isfile(LOG_TAR_NAME):
            os.remove(LOG_TAR_NAME)

    def change_timezone(self, payload):
        payload = json.loads(payload) if type(payload) == str else payload
        timezone = payload.get('timezone')
        with open(TIME_ZONE_STATUS, 'w') as fp:
            fp.write(timezone)
            self.status_q.put('timezone')
            self.light_event.set()
            self.pump_event.set()

    def upgrade(self, payload):
        if not payload:
            return False
        payload = json.loads(payload) if type(payload) == str else payload
        path = payload.get('path')
        uri = payload.get('uri')
        services = payload.get('services')
        version = payload.get('version')
        # skip if path is None or path is not start with '/usr/local/etc'
        if not path or not path.startswith('/usr/local/etc/'):
            return False
        if version:
            with open(VERSION_PATH, 'w') as fp:
                fp.write(version)
        res = os.system('wget {} -O {}'.format(uri, path))
        if res == 0:
            for service in services:
                if not service == 'iot-controller':
                    os.system('systemctl restart {}'.format(service))
            if 'iot-controller' in services:
                os.system('systemctl restart iot-controller')