import time
import os
import sys
import iothub_client
from queue import Queue

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError
from iot.MsgReader import MsgReader
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import NETWORK_PATH, CONN_STR_FILE
from util import read_from_file

# choose AMQP or AMQP_WS as transport protocol
PROTOCOL = IoTHubTransportProvider.AMQP
WAIT_COUNT = 10

class IoTListener:
    RECEIVE_CONTEXT = 0

    def __init__(self, conn_string, light_q, pump_q, light_event, pump_event):
        self.light_q = light_q
        self.pump_q = pump_q
        self.client = IoTHubClient(conn_string, PROTOCOL)
        self.client.set_message_callback(self.receive_message_callback, self.RECEIVE_CONTEXT)
        self.msgReader = MsgReader(light_q, pump_q, light_event, pump_event)

    def receive_message_callback(self, message, counter):
        message_buffer = message.get_bytearray()
        print("Data: <<<{}>>> & Size={}".format(message_buffer[:len(message_buffer)].decode('utf-8'), len(message_buffer)))
        properties = message.properties().get_internals()
        self.msgReader.read(properties)
        return IoTHubMessageDispositionResult.ACCEPTED

    def print_last_message_time(self):
        try:
            last_message = self.client.get_last_message_receive_time()
            print ("Last Message: {}".format(time.asctime(time.localtime(last_message))))
            print ("Actual time : {}".format(time.asctime()))
        except IoTHubClientError as iothub_client_error:
            if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
                print ("No message received")
            else:
                print (iothub_client_error)

    def run(self):
        try:
            while True:
                print ("IoTHubClient waiting for commands, press Ctrl-C to exit")
                status_counter = 0
                while status_counter <= WAIT_COUNT:
                    status = self.client.get_send_status()
                    print ("Send status: {}" .format(status))
                    time.sleep(10)
                    status_counter += 1

        except IoTHubError as iothub_error:
            print("Unexpected error {} from IoTHub".format(iothub_error))
            return
        except KeyboardInterrupt:
            print ("IoTHubClient sample stopped")
            self.print_last_message_time(self.client)

if __name__ == "__main__":
    conn_string = None
    while True:
        conn_string = read_from_file(NETWORK_PATH, CONN_STR_FILE)
        if conn_string:
            break
        else:
            time.sleep(10)
    if conn_string:
        listener = IoTListener(conn_string, Queue(maxsize=0), Queue(maxsize=0))
        listener.run()
    
# def print_last_message_time(client):
#     try:
#         last_message = client.get_last_message_receive_time()
#         print ( "Last Message: %s" % time.asctime(time.localtime(last_message)) )
#         print ( "Actual time : %s" % time.asctime() )
#     except IoTHubClientError as iothub_client_error:
#         if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
#             print ( "No message received" )
#         else:
#             print ( iothub_client_error )