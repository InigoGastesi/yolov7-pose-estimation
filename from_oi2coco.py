import pandas as pd
import cv2
import static_data_coco as sd
import os
import json
import pdb
import argparse
import ast
import logger as lg

class OI2Coco:
    def __init__(self):
        self.coco_annotation_dict=dict()
        self.ov_imagelist_info=dict()
    def save2JSON(self,out_file):
        with open(out_file, 'w') as f:
            json.dump(self.coco_annotation_dict, f)
        print(f'Data saved to {self}')     
    def generateBaseAnnotationData(self):
        # pdb.set_trace()
        self.coco_annotation_dict["info"]=sd.generation_info()
        self.coco_annotation_dict["licenses"]=sd.generate_license()
        self.coco_annotation_dict["images"]= []
        self.coco_annotation_dict["annotations"]=[]
        self.coco_annotation_dict["categories"]=sd.generate_static_categories()
        print("finishing generating data")
        return self.coco_annotation_dict
    def createPlaceForImageSpace(self,path):
        print("creating space for storing images")
        if not os.path.exists(path):
            os.makedirs(path)
            print(f'Folder created at {path}')
        else:
            print(f'Folder already exists at {path}')
        self.image_store_path=path
    def addImageAnnotation(self,img,image_id,store_images=True):
        ann=dict()
        filename=self.image_prefix+"_"+str(image_id)+".jpg"
        if store_images:
            
            cv2.imwrite(filename,img)
        ann["license"]= 4
        ann["file_name"]= filename
        ann["coco_url"]= ""
        ann["height"]= int(img.shape[0])
        ann["width"]= int(img.shape[1])
        ann["date_captured"]= "2013-11-14 17:02:52"
        ann["flickr_url"]= ""
        ann["id"]= image_id    
        self.coco_annotation_dict["images"].append(ann)
    def addAnnotation(self, detection, kpts, image_id, annotation_id):
        image_found = False
        ann=dict()
        ann["segmentation"]=[[]]
        ann["iscrowd"]=False
        ann['bbox'] = [int(detection[0]),int(detection[1]), int(detection[2]), int(detection[3])]
        ann['area'] = round(int(detection[2]) * int(detection[3]), 2)
        ann["category_id"] = 1
        ann["id"] = annotation_id
        ann["image_id"]=image_id
        ann["keypoints"]=kpts
        self.coco_annotation_dict["annotations"].append(ann)
    def getVideoPrefix_from_filename(self, videoname):
        self.image_prefix="video_1"
        return self.image_prefix

    def generateImages(self,dataframe, dst_folder):
        image_ann=[]
        counter = 0
        print(dataframe.size)
        image_list = list(dict.fromkeys(dataframe["ImageID"].tolist()))
        for img_item in image_list:
            image_annotation, isOK =  self.getImageANN(img_item, dst_folder, counter)
            if isOK:
                self.ov_imagelist_info[img_item]=image_annotation
                image_ann.append(image_annotation)
                counter = counter + 1
        return image_ann
        
    def getImageANN(self,image_id, dst_folder, index):
            ann=dict()
            image_found = False
            path_exists = True
            current_path = os.path.join(dst_folder, image_id+".jpg")
            cv_image=cv2.imread(current_path)
            if cv_image is None:
                log.error("image {} does not exist ".format(current_path))
            else:    
                image_found=True
                ann["license"]= 4
                ann["file_name"]= image_id+".jpg"
                ann["coco_url"]= ""
                ann["height"]= int(cv_image.shape[0])
                ann["width"]= int(cv_image.shape[1])
                ann["date_captured"]= "2013-11-14 17:02:52"
                ann["flickr_url"]= ""
                ann["id"]= index    
            return ann, image_found
    def generateAnnotations(self,dataframe):
        ann=[]
        for index, row in dataframe.iterrows(): 
            annotation, image_found = self.getAnnotation(row,index)
            if image_found:
                ann.append(annotation)
            # print("getting annother object {}".format(self.getAnnotation(row)))
        return ann    

    def getAnnotation(self, row, index):   
        image_found = False
        ann=dict()
        ann["segmentation"]=[[]]
        ann["iscrowd"]=False
        image_id=row["ImageID"]
        if image_id in self.ov_imagelist_info:
            image_found = True
        if image_found:    
            ann["image_id"]= self.ov_imagelist_info[image_id]["id"]
            # pdb.set_trace()
            xmin = float(row['XMin']) * self.ov_imagelist_info[image_id]['width']
            ymin = float(row['YMin']) * self.ov_imagelist_info[image_id]['height']
            xmax = float(row['XMax']) * self.ov_imagelist_info[image_id]['width']
            ymax = float(row['YMax']) * self.ov_imagelist_info[image_id]['height']
            dx = xmax - xmin
            dy = ymax - ymin
            ann['bbox'] = [round(a, 2) for a in [xmin , ymin, dx, dy]]
            ann['area'] = round(dx * dy, 2)
            ann["category_id"] = self.ov_categories[row["LabelName"]]
            ann["id"] = index
        return ann, image_found
    
# log=lg.getLogger()
# parser = argparse.ArgumentParser(description="script for converting OV annotations to COCO")
# parser.add_argument("--oi_input", type=str, help="input for the filtered csvs (filter_per_class.py and prepare_for_openimages_downloader is necessary)", required="true")
# parser.add_argument("--image_folder", type=str, required="true", help="path to the images folder")
# parser.add_argument("--categories", type=str, help="the specific categories from ov in an array [human-ead-things]", default="Human face, Human head")
# parser.add_argument("--prefix", type=str, help="prefix-for-formating the output file", default="unknown-class")
# parser.add_argument("--ovclassfile", type=str, help="class file with class description (default) open-image-csv/oidv7-class-descriptions-boxable.csv", default="open-image-csv/oidv7-class-descriptions-boxable.csv")
# args = parser.parse_args()      

# # get class descriptions
# # find the class
# # read the input csv
# # get categories (or generate) form generate annotation data
# #

# ov_dataframe = pd.read_csv(args.oi_input)
# print("reading ->  {}".format(args.oi_input))
# object = OI2Coco().generateAnnotationData(ov_dataframe, args.ovclassfile,
#                                          args.image_folder, 
#                                          args.categories)
# print(object)
# print("dumping the data to json")
# create_output_data=args.prefix+"-coco-"+args.oi_input.split("-")[0]+".json"
# print("saving {} file".format(create_output_data))
# with open(create_output_data, 'w') as f:
#     json.dump(object, f) 
# print("program is finished")        

#create json with: 
#info
#license
# images
    