"""
file: i2c.py
description: Abstracts some functionality of the i2c interface
"""

import smbus
import sys

class i2c(object):
	"""
	Abstract some basic i2c functionality using the smbus module to provide
	consistency
	"""

	def __init__(self, address=None, busID=None, interface=None):
		"""
		address - The I2C address of the device you want to communicate with
		busID - The I2C bus ID to use if not providing an interface
		interface - An SMBus interface to use instead of initializing one
		"""
		
	

		if address is not None:
			self.address = address
		else:
			print("ERROR: must provide an address")

		if busID is None and interface is None:
			print("ERROR: must provide either a busID or an i2c interface object (SMBus)")
			sys.exit(1)

		elif interface is not None:
			self.interface = interface

		else:
			self.busID = busID
			try:
				self.interface = smbus.SMBus(self.busID)
			except IOError as e:
				print("IOError: {}".format(e))
				sys.exit(1)

		# Defaults that can be overwritten
		self.maxReadAttempts = 3
		self.maxWriteAttempts = 3


	def readByte(self, regAddress):
		"""
		Read byte from I2C bus
		"""

		attempts = 0
		while attempts < self.maxReadAttempts:
			try:
				byte = self.interface.read_byte_data(self.address, regAddress)
				
				return byte
			except Exception as e:
				attempts += 1

		return None

	def readWord(self, regAddress):
		"""
		Read word from I2C bus
		"""

		attempts = 0
		while attempts < self.maxReadAttempts:
			try:
				word = self.interface.read_word_data(self.address, regAddress)
				
				return word
			except Exception as e:
				return None

	def readWordSwapped(self, regAddress):
		"""
		Most I2C transmit MSByte first, so the recieved word byte order needs to
		be swapped for most devices
		"""

		data = self.readWord(regAddress)

		if (data == None):
			return None
		else:
			# Swap bytes
			return ((data & 0xFF) << 8) | ((data & 0xFF00) >> 8)

	def readBlock(self, regAddress, numBytes):
		"""
		Read block from I2C bus (returns list = [first_byte_received,
		second byte_received, ...]
		"""

		attempts = 0
		while attempts < self.maxReadAttempts:
			try:
				byte_list = self.interface.read_i2c_block_data(self.address,
					regAddress, numBytes)
		
				return byte_list
			except IOError as e:
				attempts += 1
				return None

	def writeByte(self, regAddress, data=0):
		"""
		Write byte to I2C bus
		"""

		attempts = 0
		while attempts < self.maxWriteAttempts:
			try:
				self.interface.write_byte_data(self.address, regAddress, data)
				
				return True
			except IOError as e:
				self.baseLogger.log.warning("IOError in writeByte: {}".format(e))
				attempts += 1
				return False

	def writeWord(self, regAddress, data=0):
		"""
		Write word to I2C bus
		"""

		attempts = 0
		while attempts < self.maxWriteAttempts:
			try:
				self.interface.write_word_data(self.address, regAddress, data)
				return True
			except IOError as e:
				attempts += 1
				return False

	def writeWordSwapped(self, regAddress, data=0):
		"""
		Most I2C transmit MSByte first, so the transmitted word byte order
		needs to be swapped for most devices
		"""

		# Swap bytes
		data = ((data & 0xFF) << 8) | ((data & 0xFF00) >> 8)
		return self.writeWord(regAddress, data)

	def writeBlock (self, regAddress, dataList=[]):
		"""
		Write block to I2C bus (sends list = [first_byte_transmitted,
		second byte_transmitted, ...]
		"""

		attempts = 0
		while attempts < self.maxWriteAttempts:
			try:
				self.interface.write_i2c_block_data(self.address, regAddress, dataList)
				
				return True
			except IOError as e:
				attempts += 1
				return False

	#
	# 	Initiates a register-address-less read / write used by some sensors
	#		- offers alternative over sensors that need clock stretching for extended conversion time
	# 		- M=master, S=slave, W=write bit set, R=read dbit set, pkts=byte packets
	# 		- standard I2C read protocol: M[slave_address,W] M[slave_register_addr] M[slave_address,R] S[data_packets]
	# 									 |--------------------------------readByte------------------------------------|
	# 								or	 |--------------------------------readWordSwapped-----------------------------|
	# 								or 	 |--------------------------------readBurst-----------------------------------|
	# 		- "stretched" I2C read protocol: M[slave_address,W] M[slave_register_addr] {TIME DELAY FOR CONVERSION} M[slave_address,R] S[data_packets]
	# 										 |--------------sendWrite----------------| |----------delay----------| |--------sendRead x #pkts--------|
	#
	def sendRead(self):
		attempts = 0
		while attempts < self.maxReadAttempts:
			try:
				byte = self.interface.read_byte(self.address)
				
				return byte
			except IOError as e:
				attempts += 1
				return None

	def sendWrite(self, regAddress):
		attempts = 0
		while attempts < self.maxWriteAttempts:
			try:
				self.interface.write_byte(self.address, regAddress)
				
				return True
			except IOError as e:
				attempts += 1
				return False
