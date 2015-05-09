import cv2
import sys, os
import numpy as np
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

# read the image
filePath = sys.argv[1]
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
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
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
# if len(cnt_filtered_final) == 0:
# 	for cnt in cnt_filtered:
# 		area = cv2.contourArea(cnt)
# 		if area > 1000:
# 			cnt_filtered_final.append(cnt)
# draw and save details
cv2.drawContours(img, cnt_filtered_final, -1, (0,0,255), 2)
detailspath = filePath.split(".")[0] + "details." + filePath.split(".")[1]
cv2.imwrite(detailspath, img)

# get path names for images
polyvorePath = sys.argv[2] + "/public/images/polyvore_images/"
polyvoreImageNames = os.listdir(polyvorePath)
if '.DS_Store' in polyvoreImageNames:
	polyvoreImageNames.remove('.DS_Store')

# get the histograms for each image
histograms = []
for i in xrange(0, len(polyvoreImageNames)):
	polyvoreImg = cv2.imread(polyvorePath + polyvoreImageNames[i])
	mask = cv2.inRange(polyvoreImg, np.array([1, 1, 1]), np.array([250, 250, 250]))
	polyvoreImgHSV = cv2.cvtColor(polyvoreImg, cv2.COLOR_BGR2HSV)
	skinMask = cv2.inRange(polyvoreImgHSV, np.array([0, 48, 80], dtype = "uint8"), np.array([20, 245, 245], dtype = "uint8"))
	mask = mask - skinMask
	hist = cv2.calcHist([polyvoreImg], [0, 1, 2], mask, [8, 8, 8], [0, 255, 0, 255, 0, 255])
	hist = cv2.normalize(hist).flatten()
	histograms.append(hist)

# get the histogram for detected human and throw away skin color
mask = None 
if len(found_filtered) > 0:
	mask = np.zeros((img.shape[0],img.shape[1]), np.uint8)
	if len(cnt_filtered_final) == 0:
		draw_detections(mask, found_filtered, -1)
	else:
		for h,cnt in enumerate(cnt_filtered_final):
		    cv2.drawContours(mask,[cnt],0,255,-1)
	skinMask = cv2.inRange(hsv, np.array([0, 48, 80], dtype = "uint8"), np.array([20, 245, 245], dtype = "uint8"))
	mask = mask - skinMask

orig = cv2.imread(filePath)
origHist = cv2.calcHist([orig], [0, 1, 2], mask, [8, 8, 8], [0, 255, 0, 255, 0, 255])
origHist = cv2.normalize(origHist).flatten()

# compare histograms to find alike images
results = {}
for i in xrange(0, len(histograms)):
	score = 1-cv2.compareHist(histograms[i], origHist, cv2.cv.CV_COMP_BHATTACHARYYA)
	results[i] = score
results = sorted([(v, k) for (k, v) in results.items()], reverse = 1)

path = "../images/polyvore_images/"
out = []
for i in xrange(18):
	out.append(path + polyvoreImageNames[results[i][1]])

print json.dumps(out)