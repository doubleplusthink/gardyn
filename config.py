# coding=utf-8
import os

config = {}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

TEST_INTERVAL = config.get('TEST_INTERVAL', 5)

# camera settings
PHOTO_DIR = config.get('PHOTO_DIR', '/usr/local/etc/webcam')
RESOLUTION = config.get('PHOTO_DIR', '2500x1900')
OLD_IMAGE_1 = config.get('OLD_IMAGE_1', 'CAMERA_1_IMAGE.jpeg')
OLD_IMAGE_2 = config.get('OLD_IMAGE_2', 'CAMERA_2_IMAGE.jpeg')
MIN_IMAGE_SIZE = config.get('MIN_IMAGE_SIZE', 500 * 1024)

# dimmer settings
CHANNEL_DIMMER = config.get('CHANNEL_LED', 12)
FREQ_DIMMER = config.get('DIMMER_FREQ', 250)
INIT_DUTY_DIMMER = config.get('INIT_DUTY_DIMMER', 0)
LAST_SECS_DIMMER = config.get('LAST_SECS_DIMMER', 20)

# water pump switch settings
CHANNEL_WATER_PUMP = config.get('CHANNEL_WATER_PUMP', 24)
FREQ_WATER_PUMP = config.get('FREQ_WATER_PUMP', 50)
INIT_DUTY_WATER_PUMP = config.get('INIT_DUTY_WATER_PUMP', 0)
LAST_SECS_WATER_PUMP = config.get('LAST_SECS_WATER_PUMP', 30)
MAX_DUTY_PUMP = config.get('MAX_DUTY_PUMP', 30)

# water level settings
CHANNEL_WATER_LVL_IN = config.get('CHANNEL_WATER_LVL_IN', 19)
CHANNEL_WATER_LVL_OUT = config.get('CHANNEL_WATER_LVL_OUT', 26)
TIMEOUT_WATER_LVL = config.get('TIMEOUT_WATER_LVL', 1)

# LED settings
CHANNEL_LED = config.get('CHANNEL_LED', 18)
CHANNEL_BUTTON = config.get('CHANNEL_BUTTON', 13)
FREQ_LED = config.get('FREQ_LED', 8000)
INIT_DUTY_LED = config.get('INIT_DUTY_LED', 0)
LAST_SECS_LIGHT_SWITCH = config.get('LAST_SECS_LIGHT_SWITCH', 60)
RESET_THRESH = config.get('RESET_THRESH', 5)

# Internal temp setting
CHANNEL_LED = config.get('CHANNEL_LED', 18)
CHANNEL_TEMP_INTER = config.get('CHANNEL_TEMP_INTER', 25)
LAST_SECS_TEMP_INTER = config.get('LAST_SECS_TEMP_INTER', 60)
INTERVAL_TEMP_INTER = config.get('INTERVAL_TEMP_INTER', 5)
THRESH_TEMP_INTER = config.get('THRESH_TEMP_INTER', 70)

# Network settings
NETWORK_PATH = config.get('NETWORK_PATH', '/usr/local/network')
CONN_STR_FILE = config.get('CONN_STR_FILE', 'conn_string')
IOT_SERVER = config.get('IOT_SERVER', 'http://api-gardyn.eastus.cloudapp.azure.com')
CONN_TIMEOUT = config.get('CONN_TIMEOUT', 30)
DEVICE_PAIR_URL = config.get('DEVICE_PAIR_URL', '/api/device/pair')
DEVICE_URL = config.get('DEVICE_URL', '/api/device')
SENSOR_URL = config.get('SENSOR_URL', '/api/sensor')

# IoT settings
IOT_MSG_INTERVAL = config.get('IOT_MSG_INTERVAL', 30 * 60)

# Scheduler settings
LIGHT_SCHEDULE_FILE = config.get('LIGHT_SCHEDULE_FILE', '/usr/local/etc/schedules/light_schedule.json')
PUMP_SCHEDULE_FILE = config.get('PUMP_SCHEDULE_FILE', '/usr/local/etc/schedules/pump_schedule.json')

# Timezone setting
TIME_ZONE = config.get('TIME_ZONE', 'America/New_York')

# Blob Storage
STORAGE_SERVER = config.get('STORAGE_SERVER', 'https://gardyniotblob.blob.core.windows.net')
STORAGE_ACCOUNT_NAME = config.get('STORAGE_ACCOUNT_NAME', 'gardyniotblob')
STORAGE_ACCOUNT_KEY = config.get('STORAGE_ACCOUNT_KEY', 'uWo9hcAv2udRfFauLb5L6SSE4Qd+EU6qs0YzIR3iDxct4zj8dCqjoyhxIqTAzrWtpW/7jwRiTgFQo+EOgiHPRg==')
IMG_CONTAINER_NAME = config.get('IMG_CONTAINER_NAME', 'iot-camera-image')
LOG_CONTAINER_NAME = config.get('LOG_CONTAINER_NAME', 'device-log')
LOG_TAR_NAME = config.get('LOG_TAR_NAME', '/usr/local/etc/log.tar')
IMG_DIFF_THRESH = config.get('IMG_DIFF_THRESH', 0.7)

# sensor status folder
TEMP_STATUS = config.get('LIGHT_STATUS', '/usr/local/etc/sensors/temp_status')
WATER_LVL_STATUS = config.get('LIGHT_STATUS', '/usr/local/etc/sensors/water_lvl_status')
HUMIDITY_STATUS = config.get('LIGHT_STATUS', '/usr/local/etc/sensors/humidity_status')
LIGHT_STATUS = config.get('LIGHT_STATUS', '/usr/local/etc/sensors/light_status')
PREV_LIGHT_STATUS = config.get('PREV_LIGHT_STATUS', '/usr/local/etc/sensors/prev_light_status')
LIGHT_SCHEDULE_STATUS = config.get('LIGHT_SCHEDULE_STATUS', '/usr/local/etc/sensors/light_schedule_status')
PUMP_STATUS = config.get('PUMP_STATUS', '/usr/local/etc/sensors/pump_status')
PUMP_SCHEDULE_STATUS = config.get('PUMP_SCHEDULE_STATUS', '/usr/local/etc/sensors/pump_schedule_status')
CAMERA_STATUS = config.get('CAMERA_STATUS', '/usr/local/etc/sensors/camera_status')
TIME_ZONE_STATUS = config.get('TIME_ZONE_STATUS', '/usr/local/etc/sensors/time_zone')

# network switch script
NETWORK_SWITCH_SH = config.get('NETWORK_SWITCH_SH', '/usr/local/etc/network_switch.sh')
NETWORK_RESET_FILE = config.get('NETWORK_RESET_FILE', '/usr/local/network/reset')
NETWORK_CHECKER_SH = config.get('NETWORK_CHECKER_SH', '/usr/local/etc/network_checker.sh')

# version path
VERSION_PATH = config.get('VERSION_PATH', '/usr/local/etc/gardyn/version')

# network test server
REMOTE_SERVER = config.get('REMOTE_SERVER', 'www.bing.com')

