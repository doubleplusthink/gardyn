# coding=utf-8
import os
import time
from shutil import copyfile
from config import PHOTO_DIR, RESOLUTION, OLD_IMAGE_1, OLD_IMAGE_2
from util import guarantee_dir, get_serial

class Camera:
    def __init__(self):
        self.path = guarantee_dir(PHOTO_DIR)
        self.old_image_1_path = os.path.join(PHOTO_DIR, OLD_IMAGE_1)
        self.old_image_2_path = os.path.join(PHOTO_DIR, OLD_IMAGE_2)

    def take_photos(self):
        serial = get_serial()
        start_time = int(time.time())
        image_1 = 'camera1_{}_{}.jpg'.format(serial, start_time)
        image_2 = 'camera2_{}_{}.jpg'.format(serial, start_time)
        image_1_path = os.path.join(self.path, image_1)
        image_2_path = os.path.join(self.path, image_2)
        try:
            os.system('sudo fswebcam -d /dev/video0 -r {} -S 2 -F 10 {}'.format(RESOLUTION, image_1_path))
            os.system('sudo fswebcam -d /dev/video1 -r {} -S 2 -F 10 {}'.format(RESOLUTION, image_2_path))

        except Exception as e:
            print('Failed when taking photos - {}'.format(e))
            print('----------------------------------------')
        finally:
            return image_1_path, image_2_path
            
    def get_old_photos(self):
        return self.old_image_1_path, self.old_image_2_path

    def replace_photo(self, new_image_path, old_image_path):
        if os.path.isfile(new_image_path) and (old_image_path == self.old_image_1_path or old_image_path == self.old_image_2_path):
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)
            copyfile(new_image_path, old_image_path)
        
        
camera = Camera()