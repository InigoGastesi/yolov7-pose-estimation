#!bin/sh

python preannotate.py --source /usr/src/data/test_wg \
    --output_folder /usr/src/data/test_wg --poseweights ./yolov7-w6-pose.pt \
    --device 0