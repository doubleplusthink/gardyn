# coding=utf-8

from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.08
#MAX_EXPECTED_AMPS = 1.2
#ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
#ina.configure(ina.RANGE_12V)
def read_ina219():
    ina = INA219(SHUNT_OHMS)
    ina.configure()
    print('Start reading from pump voltage sensor')
    print('Bus Voltage: {} V'.format(float(ina.voltage())))
    try:
        print('Bus Current: {} mA'.format(float(ina.current())))
        print('Power: {} mW'.format(float(ina.power())))
        print('Shunt Voltage: {} mV'.format(ina.shunt_voltage()))
        print('----------------------------------------')
    except DeviceRangeError as e:
        print(e)

if __name__ == '__main__':
    read_ina219()

            
            