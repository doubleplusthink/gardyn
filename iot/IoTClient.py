#coding=utf-8
from azure.iot.device import IoTHubDeviceClient, MethodResponse

class IoTClient:
    __client = None
    def __init__(self, conn_string):
        if IoTClient.__client != None:
            raise Exception("IoTClient is singleton, you've created somewhere else already.")
        else:
            IoTClient.__client = IoTHubDeviceClient.create_from_connection_string(conn_string)

    @staticmethod
    def get_client(conn_string):
        if IoTClient.__client == None:
            IoTClient(conn_string)
        return IoTClient.__client

    @staticmethod
    async def connect():
        if IoTClient.__client is not None:
            await IoTClient.__client.connect()

    @staticmethod
    async def disconnect():
        if IoTClient.__client is not None:
            await IoTClient.__client.disconnect()
        