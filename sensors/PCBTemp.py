# coding=utf-8

# sudo apt-get install python-smbus
import smbus
import os
import sys
import time
import RPi.GPIO as GPIO
import time
import json
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Custom i2c class
from sensors.i2c import i2c
from config import CHANNEL_LED, CHANNEL_TEMP_INTER, LAST_SECS_TEMP_INTER, INTERVAL_TEMP_INTER, THRESH_TEMP_INTER, IOT_SERVER, SENSOR_URL, CONN_TIMEOUT
from util import get_serial

################################################################################
class TempSensorPCT2075(i2c):
	"""
	Abstract the PCT2075 digital temperature sensor
	DataSheet found here:
		http://www.nxp.com/documents/data_sheet/PCT2075.pdf
	"""

	# Register Addresses
	REG_TEMP  = 0x0	# W: r/w, Temperature register: contains two 8-bit data bytes; to store the measured Temp data [15:5].
	REG_CONF  = 0x1	# B: r/w, Configuration register: contains a single 8-bit data byte; to set the device operating condition; default = 0.
	REG_THYST = 0x2	# W: r/w, Hysteresis register: contains two 8-bit data bytes; to store the hysteresis Thys limit; default = 75 C.
	REG_TOS   = 0x3	# W: r/w, Overtemperature shutdown threshold register: contains two 8-bit data bytes; to store the overtemperature shutdown Tots limit; default = 80 C.
	REG_TIDLE = 0x4	# B: r/w, Temperature conversion cycle default to 100 ms.

	def __init__(self, address=None, busID=None, interface=None):
		# Call super init
		super(self.__class__, self).__init__(address, busID, interface)

		self.prev_temp_f = None
		self.prev_temp_c = None

	def readTemperatureCF(self, address):
		# varaibles for temperature data
		temperature_c = None
		temperature_f = None
	
		# read temp value from sensor
		temperature = self.readWordSwapped(address)
		#print hex(temperature)
		# check to make sure data is valid
		if (temperature == None):
			# return None
			return [None, None]
		else:
			# shift value since temp is the most significant 11 bits
			temperature_shifted = temperature >> 5
			# if MSB == 1 (11bit value) then result is negative (convert from 2's comp)
			if (temperature_shifted & 0x400):
				# convert from 2s comp --> invert (aka XOR with all 1s) then add 1. and make sure to mask for only 11 bits
				temperature_shifted_2s_comp = ((temperature_shifted ^ 0xFFFF) & 0x7FF) + 1
				# convert to celcius and throw on a minus sign
				temperature_c = (-1) * (temperature_shifted_2s_comp * 0.125)
				# convert to fahrenheit
				temperature_f = temperature_c * (9.0/5.0) + 32
			else:
				# convert shifter value to celcius (value * 0.125)
				temperature_c = temperature_shifted * 0.125
				# convert celcius to fahrenheit
				temperature_f = temperature_c * (9.0/5.0) + 32

			self.prev_temp_f = temperature_f
			self.prev_temp_c = temperature_c
			print("C={}	F={}".format(temperature_c, temperature_f))
			#print ("C={:+08.3f}".format(temperature_c),
			#		"F={:+08.3f}".fo rmat(temperature_f))
					
			return int(temperature_c)

	def writeTemperatureCF(self, address, temperature):
		self.writeWord(address, temperature)

	def interrupt_handler(self, channel):
		try:
			temp = self.readTemperatureCF(self.REG_TEMP)
			print("temp: {}".format(temp))
			serial = get_serial()
			status = {
				'temp': temp
			}
			if serial:
				data = {
					'sensor_type': 4,    # 4 for pcb_temp
					'status': json.dumps(status)
				}
				res = requests.post('{}{}/{}'.format(IOT_SERVER, SENSOR_URL, serial), data=data, allow_redirects=True, timeout=CONN_TIMEOUT)
		except Exception as e:
			print(e)
			pass

def monitor_temp():
	temp0_addr = 0x48	# right-side temp sensor

	# i2c bus object 
	bus = smbus.SMBus(1)
	if not GPIO.getmode():
		GPIO.setmode(GPIO.BCM)     # Numbers GPIOs by GPIO pin, not physical location
	GPIO.setup(CHANNEL_TEMP_INTER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    #PUD_DOWN
	
	temp0 = TempSensorPCT2075(temp0_addr, None, bus)

	# print ("Write: REG_THYST={} C".format(THRESH_TEMP_INTER))
	temp0.writeTemperatureCF(TempSensorPCT2075.REG_THYST, THRESH_TEMP_INTER)

	THYST = temp0.readTemperatureCF(TempSensorPCT2075.REG_THYST)
	print("Hysteresis temperature set: {}".format(THYST)) 

	# print ("Write: REG_TOS={} C")
	temp0.writeTemperatureCF(TempSensorPCT2075.REG_TOS, THRESH_TEMP_INTER)

	SHUTDOWN = temp0.readTemperatureCF(TempSensorPCT2075.REG_TOS)
	print("Shutdown temperature set: {}".format(SHUTDOWN))

	GPIO.add_event_detect(CHANNEL_TEMP_INTER, GPIO.BOTH, callback=temp0.interrupt_handler, bouncetime=1000)