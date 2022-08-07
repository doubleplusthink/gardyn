# coding=utf-8
import os
import subprocess
import time
from config import PHOTO_DIR, RESOLUTION
from util import guarantee_dir

def take_photos():
    try:
        print('Camera test starting...')
        path = guarantee_dir(PHOTO_DIR)
        image_1 = 'camera_1_{}'.format(int(time.time()))
        image_2 = 'camera_2_{}'.format(int(time.time()))
        os.system('sudo fswebcam -d /dev/video0 -r {} {}'.format(RESOLUTION, os.path.join(path, image_1)))
        os.system('sudo fswebcam -d /dev/video1 -r {} {}'.format(RESOLUTION, os.path.join(path, image_2)))
        print('Camera test stopped, photos taken {} and {}').format(image_1, image_2)
        print('----------------------------------------')

    except Exception as e:
        print('Failed when taking photos - {}'.format(e))
        print('----------------------------------------')