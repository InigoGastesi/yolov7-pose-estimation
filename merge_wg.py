import shutil
import glob
import os
import tqdm
import json
from typing import Any, Dict, Optional
import argparse

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_folder", type=str)
    parser.add_argument("--output_folder", type=str)
    return parser.parse_args()

def copy_images(path, output_path):
    for img in glob.glob(os.path.join(path, "*")):
        shutil.copy(img, output_path)

def coco_merge(input_extend, input_add):

    data_extend = input_extend
    with open(input_add, "r") as f:
        data_add = json.load(f)

    output: Dict[str, Any] = {
        k: data_extend[k] for k in data_extend if k not in ("images", "annotations")
    }

    output["images"], output["annotations"] = [], []

    for i, data in enumerate([data_extend, data_add]):


        cat_id_map = {}
        for new_cat in data["categories"]:
            new_id = None
            for output_cat in output["categories"]:
                if new_cat["name"] == output_cat["name"]:
                    new_id = output_cat["id"]
                    break

            if new_id is not None:
                cat_id_map[new_cat["id"]] = new_id
            else:
                new_cat_id = max(c["id"] for c in output["categories"]) + 1
                cat_id_map[new_cat["id"]] = new_cat_id
                new_cat["id"] = new_cat_id
                output["categories"].append(new_cat)

        img_id_map = {}
        for image in data["images"]:
            n_imgs = len(output["images"])
            img_id_map[image["id"]] = n_imgs
            image["id"] = n_imgs

            output["images"].append(image)

        for annotation in data["annotations"]:
            n_anns = len(output["annotations"])
            annotation["id"] = n_anns
            annotation["image_id"] = img_id_map[annotation["image_id"]]
            annotation["category_id"] = cat_id_map[annotation["category_id"]]

            output["annotations"].append(annotation)
    return output

def merge(input_folder, output_folder):
    os.makedirs(os.path.join(output_folder), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "annotations"), exist_ok=True)
    output_images = os.path.join(output_folder, "images")
    output_json = os.path.join(output_folder, "annotations", "annotations.json")

    for i, video in enumerate(tqdm.tqdm(glob.glob(os.path.join(input_folder, "*")))):
        if i == 0:
            first = os.path.join(video,"annotations.json")
            with open(first, "r") as f:
                first_data = json.load(f)
            copy_images(os.path.join(video, "images"), output_images)
            continue
        if i == 1:
            coco_add = os.path.join(video,"annotations.json")
            data = coco_merge(first_data, coco_add)
            copy_images(os.path.join(video, "images"), output_images)
            continue
        coco_add = os.path.join(video,"annotations.json")
        data = coco_merge(data, coco_add)
        copy_images(os.path.join(video, "images"), output_images)



    with open(output_json, "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    opt = parser()
    merge(opt.input_folder, opt.output_folder)
