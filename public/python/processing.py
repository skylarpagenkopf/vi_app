import cv2
import sys
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
filePath = sys.argv[1]
img = cv2.imread(filePath)

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
detailspath = filePath.split(".")[0] + "details." + filePath.split(".")[1]
cv2.imwrite(detailspath, img)

# compute histogram for inside the main contours and throw away skin color

# compare to the other images

# print array of results image paths
path = "../images/polyvore_images/"
results = [path + "fb780c1075b8efd5c10d9654c01b37aba4e3e78b.jpg",
			path + "fba961a8869edd73a1c29ad6d08b9049ecd9eedb.jpg",
			path + "fbdb75015c6d7fb96977b8c0fc7e0bb6acfaf993.jpg",
			path + "fbdf4661036f163ebaa107d3ff3383f9e7ae69b2.jpg",
			path + "fbf669fcfcbe22e4dc9e3706f730f50e3f53033f.jpg",
			path + "fca81eaeb1a82edfaffe4c3f2910a395c2c012a2.jpg",
			path + "fd12d99f1e36a06857bd9a8d2641e5940b78ef06.jpg",
			path + "fdfac74f9b0947ce7a35e3b65735ce9b8ee6c907.jpg",
			path + "fe9a112528eab6feed307ead80e8181a9b2ca83c.jpg",
			path + "fef5f79cd9c6fdef6320c6bbad0426b2814aa32d.jpg",
			path + "fbf669fcfcbe22e4dc9e3706f730f50e3f53033f.jpg",
			path + "fca81eaeb1a82edfaffe4c3f2910a395c2c012a2.jpg",
			path + "fd12d99f1e36a06857bd9a8d2641e5940b78ef06.jpg",
			path + "fdfac74f9b0947ce7a35e3b65735ce9b8ee6c907.jpg",
			path + "fe9a112528eab6feed307ead80e8181a9b2ca83c.jpg",
			path + "fef5f79cd9c6fdef6320c6bbad0426b2814aa32d.jpg",
			path + "fca81eaeb1a82edfaffe4c3f2910a395c2c012a2.jpg",
			path + "fd12d99f1e36a06857bd9a8d2641e5940b78ef06.jpg"]
print json.dumps(results)