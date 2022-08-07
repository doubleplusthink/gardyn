import time
import os
import sys
from queue import Queue
from threading import Event
from azure.iot.device import MethodResponse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from iot.MsgReader import MsgReader
from iot.DMHandler import DMHandler
from config import NETWORK_PATH, CONN_STR_FILE
from util import read_from_file
from iot.IoTClient import IoTClient


class IoTDMListener:
    
    def __init__(self, iot_client, light_q, pump_q, light_event, pump_event):
        self.light_q = light_q
        self.pump_q = pump_q
        self.client = iot_client
        self.dm_reader = DMHandler(light_q, pump_q, light_event, pump_event)
        self.method_request = None

    def run(self):
        while True:
            try:                
                self.method_request = self.client.receive_method_request()  # Wait for method calls
                self.dm_reader.parse(self.method_request.name, self.method_request.payload)
                status = 200  # set return status code
                payload = {"result": True, "data": 'success'}  # set response payload
                method_response = MethodResponse.create_from_method_request(self.method_request, status, payload)
                self.client.send_method_response(method_response)  # send response
            except Exception as e:
                if self.method_request:
                    status = 500  # set return status code
                    payload = {"result": False, "data": str(e)}  # set response payload
                    method_response = MethodResponse.create_from_method_request(self.method_request, status, payload)
                    self.client.send_method_response(method_response)  # send response
                print(str(e))
                pass
            except KeyboardInterrupt:
                print("DMListener interrupted")
                break

if __name__ == "__main__":
    conn_string = None
    while True:
        conn_string = read_from_file(NETWORK_PATH, CONN_STR_FILE)
        if conn_string:
            break
        else:
            time.sleep(10)
    if conn_string:
        iot_client = IoTClient.get_client(conn_string)
        iot_client.connect()
        listener = IoTDMListener(iot_client, Queue(maxsize=0), Queue(maxsize=0), Event(), Event())
        listener.run()