# For standard deviation filter, see this awesome explanation
# http://stackoverflow.com/questions/11456565/opencv-mean-sd-filter
# Image data is from the book Algorithms for Image processing and Computer Vision
import numpy
import cv2

img = cv2.imread('/home/inu/code/pyqt-book/data/T3.PGM', 0)

k_size = 21
img_f = img.astype(numpy.float)
mu = cv2.blur(img_f, (k_size, k_size))
mu2 = cv2.blur(img_f * img_f, (k_size, k_size))
sd_filtered_f = numpy.sqrt(mu2 - mu * mu)
sd_filtered = sd_filtered_f.astype(numpy.uint8)

_, thresholded = cv2.threshold(sd_filtered, 6, 255, cv2.THRESH_BINARY)

cv2.imshow('img', img)
cv2.imshow('sd filtered', sd_filtered)
cv2.imshow('thresholded', thresholded)
cv2.waitKey()
