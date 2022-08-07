import os
import sys
import time
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import NETWORK_PATH, CONN_STR_FILE, IOT_SERVER, DEVICE_URL, DEVICE_PAIR_URL, CONN_TIMEOUT
from util import guarantee_dir, save_as_file, read_from_file, get_serial, is_connected

def claim_n_store():
    try:
        if not is_connected():
            return False
        serial = get_serial()
        # print('claim with serial: {}'.format(serial))
        if serial:
            data = {
                'serial': serial
            }
            res = requests.post('{}{}'.format(IOT_SERVER, DEVICE_PAIR_URL), data=data, allow_redirects=True, timeout=CONN_TIMEOUT)
            if res.status_code == 200:
                data = res.json().get('data')
                if 'device_conn_string' in data:
                    save_as_file(NETWORK_PATH, CONN_STR_FILE, data.get('device_conn_string'))
                    print('conn_string: {} store in file'.format(data['device_conn_string']))
                    os.system('/usr/bin/python3 /usr/local/etc/gardyn/device/iot/IoTSender.py')
                    os.system('systemctl restart iot-controller.service')
                    os.system('/usr/bin/python3 /usr/local/etc/gardyn/device/schedulers/camera.py')
    except Exception as e:
        print(e)
    
    
def verify(conn_string):
    try:
        if not is_connected():
            return False
        serial = get_serial()
        # print('verify with serial: {}'.format(serial))
        if serial:
            data = {
                'serial': serial
            }
            res = requests.post('{}{}'.format(IOT_SERVER, DEVICE_PAIR_URL), data=data, allow_redirects=True, timeout=CONN_TIMEOUT)
            if res.status_code == 200:
                data = res.json().get('data')
                if 'device_conn_string' not in data and os.path.isfile(os.path.join(NETWORK_PATH, CONN_STR_FILE)):
                    os.remove(os.path.join(NETWORK_PATH, CONN_STR_FILE))
                elif data['device_conn_string'] != conn_string:
                    save_as_file(NETWORK_PATH, CONN_STR_FILE, data.get('device_conn_string'))
                    print('conn_string: {} store in file'.format(data['device_conn_string']))
                    os.system('/usr/bin/python3 /usr/local/etc/gardyn/device/iot/IoTSender.py')
                    os.system('systemctl restart iot-controller.service')
                    os.system('/usr/bin/python3 /usr/local/etc/gardyn/device/schedulers/camera.py')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    while True:
        conn_string = read_from_file(NETWORK_PATH, CONN_STR_FILE)
        if conn_string:
            verify(conn_string)
            time.sleep(30)
        else:
            claim_n_store()
            time.sleep(10)