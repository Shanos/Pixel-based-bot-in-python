from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random as rng
rng.seed(12345)

def thresh_callback(val, src_gray):
    threshold = val
    # Detect edges using Canny
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)
    # Find contours
    _, contours, hierarchy = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # Draw contours
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)):
        color = (255, 255, 255)
        cv.drawContours(drawing, contours, i, color, 3, cv.LINE_8, hierarchy, 0)
    # Show in a window
    cv.imshow('Contours', drawing)
    something, drawing_w, drawing_h = drawing.shape[::-1]
    middle_height = int(drawing_h/2)
    crop_drawing = drawing[middle_height:middle_height+1, 0:drawing_w]
    cv.imshow('cropped', crop_drawing)
    cv.imwrite('test.png', drawing)

def find_contours(image):
    src = cv.imread(cv.samples.findFile(image))
    if src is None:
        print('Could not open or find the image:', image)
        # exit(0)
    # Convert image to gray and blur it
    src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    src_gray = cv.blur(src_gray, (3,3))
    # Create Window
    source_window = 'Source'
    cv.namedWindow(source_window)
    cv.imshow(source_window, src)
    max_thresh = 255
    thresh = 100 # initial threshold
    #cv.createTrackbar('Canny Thresh:', source_window, thresh, max_thresh, thresh_callback)
    thresh_callback(thresh, src_gray)
    cv.waitKey()

find_contours('wtf_yellow.png')
