import cv2
import sys, os
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import json
def inside(r, q):
    rx, ry, rw, rh = r
    qx, qy, qw, qh = q
    return rx > qx and ry > qy or rx + rw < qx + qw and ry + rh < qy + qh

def inside_hog(cnt, hogs):
	rx, ry, rw, rh = cnt
	for hog in hogs:
		qx, qy, qw, qh = hog
		pad_w, pad_h = int(0.18*qw), int(0.05*qh)
		if rx > qx+pad_w and ry > qy+pad_h and rx + rw < qx + qw - pad_w and ry + rh < qy + qh - pad_h:
			return 1
	return 0

def draw_detections(img, rects, thickness = 1):
    for x, y, w, h in rects:
        # the HOG detector returns slightly larger rectangles than the real objects.
        # so we slightly shrink the rectangles to get a nicer output.
        pad_w, pad_h = int(0.18*w), int(0.05*h)
        cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), thickness)

results = []
# read the image
filePath = '../images/exampleinput5.jpg'
img = cv2.imread(filePath)
# cv2.imshow('a', img)
# process image for human
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# get human bounding rectangle
found, w = hog.detectMultiScale(img, winStride=(5,5), padding=(10,10), scale=1.05)
found_filtered = []
for ri, r in enumerate(found):
    for qi, q in enumerate(found):
        if ri != qi and inside(r, q):
            break
    else:
        found_filtered.append(r)
draw_detections(img, found_filtered, 3)

# get contours
imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 120, 255, 0)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

# use only contours inside the human bounding rectangle
cnt_filtered = []
for cnt in contours:
	r = cv2.boundingRect(cnt)
	if inside_hog(r, found_filtered):
		cnt_filtered.append(cnt)
# use only contours that are not inside of other ones
cnt_filtered_final = []
for cnt in cnt_filtered:
	r = cv2.boundingRect(cnt)
	for cnt2 in cnt_filtered:
		q = cv2.boundingRect(cnt2)
		if r != q and inside(r, q):
			break
	else:
		cnt_filtered_final.append(cnt)
# if none turned up, use max area contours
if len(cnt_filtered_final) == 0:
	for cnt in cnt_filtered:
		area = cv2.contourArea(cnt)
		if area > 1000:
			cnt_filtered_final.append(cnt)
# draw and save details
cv2.drawContours(img, cnt_filtered_final, -1, (0,0,255), 2)
detailspath = filePath.split('.')[0] + 'details.' + filePath.split('.')[1]
 

# get path names for images
# get path names for images
imageNames = os.listdir("../images/polyvore_images")
# get the histograms for each image
images = []
histograms = []
for i in xrange(1, len(imageNames)):
	image = cv2.imread('../images/polyvore_images/' + imageNames[i])
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	images.append(image)
	mask = cv2.inRange(image, np.array([5, 5, 5]), np.array([256, 256, 256]))
	hist = cv2.calcHist([image], [0, 1, 2], mask, [8, 8, 8], [0, 255, 0, 255, 0, 255])
	hist = cv2.normalize(hist).flatten()
	histograms.append(hist)

# get the histogram for detected human
mask = np.zeros((img.shape[0],img.shape[1]), np.uint8)
for h,cnt in enumerate(cnt_filtered_final):
    cv2.drawContours(mask,[cnt],0,255,-1)
# throw away skin color

orig = cv2.imread(filePath)
histogram = []
hist = cv2.calcHist([orig], [0, 1, 2], mask, [8, 8, 8], [0, 255, 0, 255, 0, 255])
hist = cv2.normalize(hist).flatten()
histogram.append(hist)
# compare histograms to find alike images
results = {}
for i in xrange(1, len(histograms)):
	score = 1 - cv2.compareHist(histograms[i], histogram[0], cv2.cv.CV_COMP_BHATTACHARYYA)
	results[i] = score
results = sorted([(v, k) for (k, v) in results.items()], reverse = 1)

path = "../images/polyvore_images/"
out = []
for i in xrange(18):
	out.append(path + imageNames[results[i][1]])

print json.dumps(out)


