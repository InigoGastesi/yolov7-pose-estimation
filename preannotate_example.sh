#!bin/sh

python preannotate.py --source /usr/src/data/wavegarden/VICOM.T1.T2_optica.nueva/buenos \
    --output_folder /usr/src/data/wg_processed --poseweights ./yolov7-w6-pose.pt \
    --device 0