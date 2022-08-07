# coding=utf-8
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sensors.Camera import camera
from common.image import compare
from storage import ImageStorage
from util import get_serial, read_from_file
from config import CAMERA_STATUS, MIN_IMAGE_SIZE

def upload_images(images):
    image_storage = ImageStorage()
    serial = get_serial()
    for image_path in images:
        if image_path and os.path.isfile(image_path):
            if os.path.getsize(image_path) > MIN_IMAGE_SIZE:
                image_storage.upload(image_path)
                target = '{}_{}.jpg'.format(os.path.basename(image_path).split('_')[0], serial)
                image_storage.copy(image_path, target)
            os.remove(image_path)

def remove_images(images):
    for image_path in images:
        if image_path and os.path.isfile(image_path):
            os.remove(image_path)

def run():
    image_path_1, image_path_2 = camera.take_photos()
    old_path_1, old_path_2 = camera.get_old_photos()
    images = [image_path_1, image_path_2]
    # if not compare(image_path_1, old_path_1):
    #     camera.replace_photo(image_path_1, old_path_1)
    #     images.append(image_path_1)
    # if not compare(image_path_2, old_path_2):
    #     camera.replace_photo(image_path_2, old_path_2)
    #     images.append(image_path_2)
    try:
        if len(images) > 0:
            upload_images(images)
    except Exception as e:
        print('Image Uploading Error:', e)
    finally:
        remove_images([image_path_1, image_path_2])

if __name__ == '__main__':
    camera_status = read_from_file(os.path.dirname(CAMERA_STATUS), os.path.basename(CAMERA_STATUS))
    if camera_status != 'off':
        run()
