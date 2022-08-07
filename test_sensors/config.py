# coding=utf-8
import os

config = {}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

TEST_INTERVAL = config.get('TEST_INTERVAL', 5)

# camera settings
PHOTO_DIR = config.get('PHOTO_DIR', '/home/pi/webcam')
RESOLUTION = config.get('PHOTO_DIR', '2500x1900')

# dimmer settings
CHANNEL_DIMMER = config.get('CHANNEL_LED', 12)
FREQ_DIMMER = config.get('DIMMER_FREQ', 250)
INIT_DUTY_DIMMER = config.get('INIT_DUTY_DIMMER', 0)
LAST_SECS_DIMMER = config.get('LAST_SECS_DIMMER', 20)

# water pump switch settings
CHANNEL_WATER_PUMP = config.get('CHANNEL_WATER_PUMP', 18)
FREQ_WATER_PUMP = config.get('FREQ_WATER_PUMP', 50)
INIT_DUTY_WATER_PUMP = config.get('INIT_DUTY_WATER_PUMP', 0)
LAST_SECS_WATER_PUMP = config.get('LAST_SECS_WATER_PUMP', 30)

# water level settings
CHANNEL_WATER_LVL_IN = config.get('CHANNEL_WATER_LVL_IN', 19)
CHANNEL_WATER_LVL_OUT = config.get('CHANNEL_WATER_LVL_OUT', 26)

# LED settings
CHANNEL_LED = config.get('CHANNEL_LED', 18)
CHANNEL_BUTTON = config.get('CHANNEL_BUTTON', 13)
FREQ_LED = config.get('FREQ_LED', 100)
INIT_DUTY_LED = config.get('INIT_DUTY_LED', 100)
LAST_SECS_LIGHT_SWITCH = config.get('LAST_SECS_LIGHT_SWITCH', 60)

# Internal temp setting
CHANNEL_LED = config.get('CHANNEL_LED', 18)
CHANNEL_TEMP_INTER = config.get('CHANNEL_TEMP_INTER', 25)
LAST_SECS_TEMP_INTER = config.get('LAST_SECS_TEMP_INTER', 60)
INTERVAL_TEMP_INTER = config.get('INTERVAL_TEMP_INTER', 5)
THRESH_TEMP_INTER = config.get('THRESH_TEMP_INTER', 27)
