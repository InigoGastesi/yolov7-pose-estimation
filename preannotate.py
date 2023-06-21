import argparse
import cv2
import time
import torch
import argparse
import numpy as np
import matplotlib.pyplot as plt
from torchvision import transforms
from utils.datasets import letterbox
from utils.torch_utils import select_device
from models.experimental import attempt_load
from utils.general import non_max_suppression_kpt,strip_optimizer,xyxy2xywh
from utils.plots import output_to_keypoint, plot_skeleton_kpts,colors,plot_one_box_kpt
from from_oi2coco import OI2Coco
import json
import glob
import os

def make_dir(source, output):
    for i, video in enumerate(glob.glob(f"{source}/*.mp4")):
        os.makedirs(os.path.join(output, f"video_{i}"), exist_ok=True)
        os.makedirs(os.path.join(output, f"video_{i}", "images"), exist_ok=True)


@torch.no_grad()
def run(poseweights="yolov7-w6-pose.pt",source="", output_folder="", device='cpu',view_img=False,
        save_conf=False,line_thickness = 3,hide_labels=False, hide_conf=True, store_images=True, img_path="images/"):
    make_dir(source, output_folder)
    
    
    device = select_device(opt.device) #select device
    half = device.type != 'cpu'

    model = attempt_load(poseweights, map_location=device)  #Load model
    _ = model.eval()
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names
    for i, video in enumerate(glob.glob(f"{source}/*.mp4")):
        coco_handler = OI2Coco()
        coco_handler.createPlaceForImageSpace(os.path.join(output_folder, f"video_{i}"))
        coco_handler.generateBaseAnnotationData()
        coco_handler.getVideoPrefix_from_filename(f"video_{i}")
        frame_count = 0  #count no of frames
        annotation_id=0
        total_fps = 0  #count total fps
        time_list = []   #list to store time
        fps_list = []    #list to store fps
        cap = cv2.VideoCapture(video)    #pass video to videocapture object
       
        if (cap.isOpened() == False):   #check if videocapture not opened
            print('Error while trying to read video. Please check path again')
            raise SystemExit()

        else:
            frame_width = int(cap.get(3))  #get video frame width
            frame_height = int(cap.get(4)) #get video frame height

            
            vid_write_image = letterbox(cap.read()[1], (frame_width), stride=64, auto=True)[0] #init videowriter
            resize_height, resize_width = vid_write_image.shape[:2]
            out = cv2.VideoWriter(f"{output_folder}/video_{i}/video{i}_keypoint.mp4",
                            cv2.VideoWriter_fourcc(*'mp4v'), 30,
                            (resize_width, resize_height))
            while(cap.isOpened): #loop until cap opened or video not complete
            
                print("Frame {} Processing".format(frame_count+1))

                ret, frame = cap.read()  #get frame and success from video capture
                if ret: #if success is true, means frame exist
                    orig_image = frame #store frame
                    # put here the image annotation: 

                    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB) #convert frame to RGB
                    image, ratio, _ = letterbox(image, (frame_width), stride=64, auto=True)
                    print(ratio)
                    image_ = image.copy()
                    image = transforms.ToTensor()(image)
                    image = torch.tensor(np.array([image.numpy()]))
                
                    image = image.to(device)  #convert image data to device
                    image = image.float() #convert image to float precision (cpu)
                    start_time = time.time() #start time for fps calculation
                
                    with torch.no_grad():  #get predictions
                        output_data, _ = model(image)

                    output_data = non_max_suppression_kpt(output_data,   #Apply non max suppression
                                                0.25,   # Conf. Threshold.
                                                0.65, # IoU Threshold.
                                                nc=model.yaml['nc'], # Number of classes.
                                                nkpt=model.yaml['nkpt'], # Number of keypoints.
                                                kpt_label=True)
                
                    output = output_to_keypoint(output_data)

                    im0 = image[0].permute(1, 2, 0) * 255 # Change format [b, c, h, w] to [h, w, c] for displaying the image.
                    im0 = im0.cpu().numpy().astype(np.uint8)
                    
                    im0 = cv2.cvtColor(im0, cv2.COLOR_RGB2BGR) #reshape image format to (BGR)
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                    coco_handler.addImageAnnotation(im0,frame_count, store_images=True)

                    for i, pose in enumerate(output_data):  # detections per image
                    
                        if len(output_data):  #check if no pose
                            for c in pose[:, 5].unique(): # Print results
                                n = (pose[:, 5] == c).sum()  # detections per class
                                print("No of Objects in Current Frame : {}".format(n))
                            
                            for det_index, (*xyxy, conf, cls) in enumerate(reversed(pose[:,:6])): #loop over poses for drawing on frame
                                c = int(cls)  # integer class
                                kpts = pose[det_index, 6:]
                                kpts_list = kpts.cpu().numpy().tolist()
                                for j in range(len(kpts_list)):
                                    if (j+1) % 3 == 0:
                                        if kpts_list[j] < 0.5:
                                            kpts_list[j] = 0
                                            kpts_list[j-1] = 0
                                            kpts_list[j-2] = 0
                                        else:
                                            kpts_list[j] = 2
                            

                                label = None if opt.hide_labels else (names[c] if opt.hide_conf else f'{names[c]} {conf:.2f}')
                                keypoint_list = plot_one_box_kpt(xyxy, im0, label=label, color=colors(c, True), 
                                            line_thickness=opt.line_thickness,kpt_label=True, kpts=kpts, steps=3, 
                                            orig_shape=im0.shape[:2])
                                
                                coco_handler.addAnnotation(xyxy,kpts_list,frame_count,annotation_id, len(keypoint_list)/2, ratio)
                                # print(json.dumps(coco_handler.coco_annotation_dict, indent = 4))
                        annotation_id= annotation_id + 1        

                    
                    end_time = time.time()  #Calculatio for FPS
                    fps = 1 / (end_time - start_time)
                    total_fps += fps
                    frame_count += 1
                    
                    fps_list.append(total_fps) #append FPS in list
                    time_list.append(end_time - start_time) #append time in list
                    
                    # Stream results
                    if view_img:
                        cv2.imshow("YOLOv7 Pose Estimation Demo", im0)
                        cv2.waitKey(1)  # 1 millisecond
                    out.write(im0)
                    
                else:
                    break

        cap.release()
        coco_handler.save2JSON()

        # coco_handler.save2JSON("results.json")
        # cv2.destroyAllWindows()
        avg_fps = total_fps / frame_count
        print(f"Average FPS: {avg_fps:.3f}")
        
        #plot the comparision graph
        # plot_fps_time_comparision(time_list=time_list,fps_list=fps_list)


def plot_fps_time_comparision(time_list,fps_list):
    plt.figure()
    plt.xlabel('Time (s)')
    plt.ylabel('FPS')
    plt.title('FPS and Time Comparision Graph')
    plt.plot(time_list, fps_list,'b',label="FPS & Time")
    plt.savefig("FPS_and_Time_Comparision_pose_estimate.png")
    


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--poseweights', nargs='+', type=str, default='yolov7-w6-pose.pt', help='model path(s)')
    parser.add_argument('--source', type=str, help='folder with videos', required=True) #video source
    parser.add_argument('--output_folder', type=str, required=True)
    parser.add_argument('--device', type=str, default='cpu', help='cpu/0,1,2,3(gpu)')   #device arugments
    parser.add_argument('--view-img', action='store_true', help='display results')  #display results
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels') #save confidence in txt writing
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)') #box linethickness
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels') #box hidelabel
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences') #boxhideconf
    return parser.parse_args()



def main(opt):
    run(**vars(opt))

if __name__ == "__main__":
    opt = parse_opt()
    strip_optimizer(opt.device,opt.poseweights)
    main(opt)