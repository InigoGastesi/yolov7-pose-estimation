import json
import cv2
import random
import os
import numpy as np

def draw_kpts(imagen, keypoints):
    imagen_con_keypoints = np.copy(imagen)
    kpts = (keypoints[i:i+3] for i in range(0, len(keypoints), 3))
    for x,y,z in kpts:
        cv2.circle(imagen_con_keypoints, (int(x), int(y)), 5, (0, 255, 0), -1)  # Dibuja un círculo en el punto
        
    return imagen_con_keypoints
def draw_bbox(img, bbox):
    img = cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
    return img
with open("/usr/src/data/wg_dataset_2/annotations/annotations.json") as f:
    data = json.load(f)

images = data["images"]
annotations = data["annotations"]
index = random.randint(0,129440)
ann = annotations[index]
ann_id = ann["image_id"]
for img in images:
    if img["id"] == ann_id:
        img_path = os.path.join("/usr/src/data/wg_dataset_2/images", img["file_name"])

img = cv2.imread(img_path)
kpts = ann["keypoints"]
bbox = ann["bbox"]
img = draw_kpts(img, kpts)
img = draw_bbox(img, bbox)
cv2.imwrite("debug.jpg", img)