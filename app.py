# coding=utf-8
import os
from threading import Thread
from flask import Flask, request, jsonify


from config import NETWORK_PATH, NETWORK_CHECKER_SH, NETWORK_RESET_FILE

app = Flask('app')

def save_network_info(ssid, passphrase):
    if not os.path.isdir(NETWORK_PATH):
        os.mkdir(NETWORK_PATH)
    f_ssid = open(os.path.join(NETWORK_PATH, 'ssid'), 'w')
    f_ssid.write(ssid)
    f_ssid.close()
    f_pass = open(os.path.join(NETWORK_PATH, 'passphrase'), 'w')
    f_pass.write(passphrase)
    f_pass.close()

def restart_network():
    if os.path.isfile(NETWORK_RESET_FILE):
        os.remove(NETWORK_RESET_FILE)
        # restart the service in case the iot conn has been cut off.
        os.system('systemctl restart conn-string')
        os.system('systemctl restart iot-controller')
        

@app.route('/wifi', methods=['GET', 'POST'])
def hello_world():
    params = request.args or request.json or request.form
    ssid = params.get('ssid')
    passphrase = params.get('passphrase')
    if ssid and passphrase:
        save_network_info(ssid, passphrase)
        
        worker = Thread(target=restart_network)
        worker.setDaemon(True)
        worker.start()

        fp = os.popen("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | md5sum | cut -d ' ' -f 1")
        serial = fp.read().splitlines()[0]
        fp.close()
        # print('serial number: {}'.format(serial))
        res = {
            'code': 200,
            'data': serial,
            'page': ''
        }
        return jsonify(res)
    
    return jsonify({'code': 500, 'data': '', 'page': ''})

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    res = {
        'code': 200,
        'data': 'ok',
        'page': ''
    }
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8010)
