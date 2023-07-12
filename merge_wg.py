import shutil
import glob
import os
import tqdm
from pyodi.apps.coco import coco_merge

for video in tqdm.tqdm(glob.glob("/usr/src/data/wg_processed/*")):
    for img in glob.glob(os.path.join(video, "images","*.jpg")):
        shutil.copy(img, "/usr/src/data/wg_dataset_2/images")

output = "/usr/src/data/wg_dataset_2/annotations.json"

for i, video in tqdm.tqdm(enumerate(glob.glob("/usr/src/data/wg_processed/*"))):
    if i == 0:
        first = os.path.join(video,"annotations.json")
        continue
    if i == 1:
        coco_add = os.path.join(video,"annotations.json")
        coco_merge(first, coco_add, output)
        continue
    coco_add = os.path.join(video,"annotations.json")
    coco_merge(output, coco_add, output)