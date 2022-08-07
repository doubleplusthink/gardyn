# coding=utf-8
import sys
import os
from skimage.measure import compare_ssim as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import IMG_DIFF_THRESH

"""
    compare the original image with new image that just took
    return True to keep the old one
    return False when you want to replace the new image with the original one
"""
def compare(newImg, originImg):
    try:
        if os.path.isfile(originImg) and os.path.isfile(newImg):
            originImg = cv2.imread(originImg)
            newImg = cv2.imread(newImg)
            originImg = cv2.cvtColor(originImg, cv2.COLOR_BGR2GRAY)
            newImg = cv2.cvtColor(newImg, cv2.COLOR_BGR2GRAY)
            score = ssim(originImg, newImg)
            return score >= IMG_DIFF_THRESH
        else:
            return False
    except Exception as e:
        return False