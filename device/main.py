# coding=utf-8
import os
import time
import sys
import json
import asyncio
from queue import Queue, Empty
from threading import Thread, Event

from config import NETWORK_PATH, CONN_STR_FILE, LIGHT_SCHEDULE_FILE, PUMP_SCHEDULE_FILE, LIGHT_STATUS, PUMP_STATUS, MAX_WATER_TIME
from util import read_from_file, is_connected
from iot.IoTDMListener import IoTDMListener
from iot.IoTSender import IoTSender
from iot.IoTClient import IoTClient
from schedulers.BaseScheduler import BaseScheduler
from sensors.LED import led
from sensors.Pump import pumper
from sensors.Button import Button
from sensors.PCBTemp import monitor_temp

def thread_pump(pump_q, status_q, pump_guardian_q):
    manual_interrupt = False
    schedule_off = False

    while True:
        try:
            sig = pump_q.get(True)
            if type(sig) == str and sig.upper() == 'ON':
                # manual_interrupt = True
                pumper.pump()
                status_q.put('pump')
                pump_guardian_q.put('ON')
            elif type(sig) == str and sig.upper() == 'OFF':
                # manual_interrupt = False
                pumper.stop()
                status_q.put('pump')
                pump_guardian_q.put('OFF')
            elif type(sig) == str and sig.upper() == 'AUTO_ON' and not schedule_off:
                if not manual_interrupt:
                    pumper.pump()
                    status_q.put('pump')
                    pump_guardian_q.put('ON')
            elif type(sig) == str and sig.upper() == 'AUTO_OFF' and not schedule_off:
                if not manual_interrupt:
                    pumper.stop()
                    status_q.put('pump')
                    pump_guardian_q.put('OFF')
            elif type(sig) == str and sig.upper() == 'SCHEDULE_OFF':
                schedule_off = True
                status_q.put('pump')
            elif type(sig) == str and sig.upper() == 'SCHEDULE_ON':
                schedule_off = False
                status_q.put('pump')

            # TODO: update status
            # iot_sender.send(led.LIGHT_DUTY, float(pumper.started))
        except Exception as e:
            print(e)
            pass

"""
    manual_on/manual_off/manual_boost for push-to-on button or app control button
    on/off/boost for scheduler
"""
def thread_light(light_q, status_q):
    schedule_off = False

    while True:
        try:
            sig = light_q.get(True)
            if type(sig) == str and sig.upper() == 'MANUAL_ON':
                led.turn_on()
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'MANUAL_OFF':
                led.turn_off()
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'MANUAL_BOOST':
                led.boost()
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'ON' and not schedule_off:
                led.turn_on()
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'OFF' and not schedule_off:
                led.turn_off()
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'BOOST' and not schedule_off:
                led.boost()
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'LIGHTER':
                led.lighter()
            elif type(sig) == str and sig.upper() == 'DIMMER':
                led.dimmer()
            elif type(sig) == dict and sig.get('percent'):
                led.adjust(sig.get('percent'))
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'SCHEDULE_OFF':
                schedule_off = True
                status_q.put('light')
            elif type(sig) == str and sig.upper() == 'SCHEDULE_ON':
                schedule_off = False
                status_q.put('light')
            # TODO: update status
            # iot_sender.send(led.LIGHT_DUTY, float(pumper.started))
        except Exception as e:
            print(e)
            pass

def thread_light_scheduler(light_q, light_event):
    light_scheduler = BaseScheduler(LIGHT_SCHEDULE_FILE, light_q, light_event)
    light_scheduler.run()

def thread_pump_scheduler(pump_q, pump_event):
    pump_scheduler = BaseScheduler(PUMP_SCHEDULE_FILE, pump_q, pump_event)
    pump_scheduler.run()

def thread_button_controller(light_q):
    led_button_status = ['MANUAL_OFF']
    btn = Button()
    def button_handler():
        # read from the file to avoid alway try to turn on first.
        led_status = read_from_file(os.path.dirname(LIGHT_STATUS), os.path.basename(LIGHT_STATUS))
        led_status = led_status if (led_status and led_status != '0') else None
        led_button_status[0] = 'MANUAL_OFF' if (led_status or led_button_status[0] == 'MANUAL_ON') else 'MANUAL_ON'
        light_q.put(led_button_status[0])

    btn.on_press(button_handler)

def thread_status_sync(iot_client, status_q):
    sender = IoTSender(iot_client)
    status_change = False
    while True:
        while not status_q.empty():
            try:
                status = status_q.get()
                status_change = True
            except Exception as e:
                print(e)
                pass
        if status_change:
            light_status = read_from_file(os.path.dirname(LIGHT_STATUS), os.path.basename(LIGHT_STATUS))
            pump_status = read_from_file(os.path.dirname(PUMP_STATUS), os.path.basename(PUMP_STATUS))
            sender.send_light_n_pump(light_status, pump_status)
            status_change = False
        time.sleep(1)

def thread_iot_sender(iot_client):
    while True:
        try:
            sender = IoTSender(iot_client)
            sender.run()
            # send every 30 mintues
            time.sleep(30 * 60)
        except Exception as e:
            print(str(e))
            pass

def thread_temp_interrupt():
    monitor_temp()


def thread_pump_guardian(pump_guardian_q, status_q):
    max_interval = MAX_WATER_TIME
    while True:
        sig = pump_guardian_q.get(block=True)
        if sig == 'ON':
            start_time = int(time.time())
            end_time = start_time + max_interval
            nsig = 'ON'
            while nsig != 'OFF':
                now = int(time.time())
                try:
                    nsig = pump_guardian_q.get(block=True, timeout=end_time - now)
                    if nsig == 'OFF':
                        continue
                except Empty as e:
                    print('running longer than 15 min, force it off.')
                    pumper.stop()
                    status_q.put('pump')
                    nsig = 'OFF'
                    continue


async def main():
    # [x] set the timezone for EST
    # [x] read connection string
    # [x] create scheduler for both pump and light
    # [x] create queue for both scheduler
    # [x] create two thread and pass the queue and schedules in
    # [x] add button event listner
    # [x] add temp interrupt listner
    # [x] in the main thread, listen the data from iot hub and push the data to queue

    conn_string = None
    light_q = Queue(maxsize=0)
    pump_q = Queue(maxsize=0)
    status_q = Queue(maxsize=0)
    pump_guardian_q = Queue(maxsize=0)

    light_event = Event()
    pump_event = Event()

    worker_pump = Thread(target=thread_pump, args=(pump_q, status_q, pump_guardian_q, ))
    worker_pump.setDaemon(True)
    worker_pump.start()
    worker_light = Thread(target=thread_light, args=(light_q, status_q,))
    worker_light.setDaemon(True)
    worker_light.start()
    worker_light_scheduler = Thread(target=thread_light_scheduler, args=(light_q, light_event,))
    worker_light_scheduler.setDaemon(True)
    worker_light_scheduler.start()
    worker_pump_scheduler = Thread(target=thread_pump_scheduler, args=(pump_q, pump_event,))
    worker_pump_scheduler.setDaemon(True)
    worker_pump_scheduler.start()
    worker_pump_guardian = Thread(target=thread_pump_guardian, args=(pump_guardian_q, status_q))
    worker_pump_guardian.setDaemon(True)
    worker_pump_guardian.start()
    worker_button_controller = Thread(target=thread_button_controller, args=(light_q,))
    worker_button_controller.setDaemon(True)
    worker_button_controller.start()
    worker_temp_interrupt = Thread(target=thread_temp_interrupt)
    worker_temp_interrupt.setDaemon(True)
    worker_temp_interrupt.start()


    while True:
        conn_string = read_from_file(NETWORK_PATH, CONN_STR_FILE)
        if conn_string and is_connected():
            break
        else:
            time.sleep(10)

    if conn_string:
        iot_client = IoTClient.get_client(conn_string)
        iot_client.connect()
        worker_sync = Thread(target=thread_status_sync, args=(iot_client, status_q,))
        worker_sync.setDaemon(True)
        worker_sync.start()
        worker_iot_sender = Thread(target=thread_iot_sender, args=(iot_client,))
        worker_iot_sender.setDaemon(True)
        worker_iot_sender.start()

        listener = IoTDMListener(iot_client, light_q, pump_q, light_event, pump_event, status_q)
        listener.run()

    pump_q.join()
    light_q.join()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
