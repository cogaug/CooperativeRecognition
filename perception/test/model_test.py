from ultralytics import YOLO
from ultralytics.yolo.utils.plotting import Colors
import cv2
import numpy as np
import sys
import os
import torch
import time
import copy

class ASL_process():
    def __init__(
        self

    ):
        self.ASL_model = YOLO('/home/kkk/ultralytics/runs/detect/train20/weights/best.pt')  # load an official model

        self.colors = Colors()
        
        self.detect_thre = 0


        self.txt_color=(250, 250, 250)

        self.radius = 5

        # self.path1 ="/home/kkk/Segment-and-Track-Anything/assets/charger.MOV"
        # self.path1 ="/home/kkk/Segment-and-Track-Anything/assets/test/vending.MOV"
        # self.path1 ="/media/kkk/hard_disk/videos/231115_1732.mp4"
        self.path1 ="/media/kkk/hard_disk/bag2video/20231127/20231127.mp4"


    def run(self):

        self.capture = cv2.VideoCapture(self.path1)  

        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)   # capture size width
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)  # capture size height

        object_cnt = 0
        entire_cnt = 0

        while True:
            ret, frame = self.capture.read()
            frame = np.array(frame)
            print(frame.shape)
            size = frame.shape
            # frame = cv2.resize(frame, dsize=(640, 480), interpolation=cv2.INTER_AREA)
            frame = cv2.resize(frame, dsize=(size[1], size[0]), interpolation=cv2.INTER_AREA)
            # frame = cv2.flip(frame, -1)
            results=self.ASL_model.predict(source=frame,save=False, save_txt=False)
            
            lw = max(round(sum(frame.shape) / 2 * 0.003), 2) 

            names = results[0].names
            boxes = results[0].boxes.cpu().numpy()

            class_name = np.array([])
            class_num = list()
            
            shape  = (self.width,self.height)

            if len(boxes.xyxy)==0:
                print("No ASL detected")


            if boxes is not None:
                for j, d in enumerate(reversed(boxes)):
                    box = d.xyxy.squeeze()
                    conf = d.conf.squeeze()
                    cls = d.cls.squeeze()
             
                    color = self.colors(j)
                    if conf >0.65:
                        c = int(cls)
                        # print("C : ",c)
                        class_num.append(c)
                        label = (f'{names[c]} ' if names else f'{c}') + (f'{conf:.2f}' if True else '')
                        # YOLO.annotator.box_label(boxes, label, color=YOLO.colors(c, True))
                        class_name=np.append(class_name,(f'{names[c]}' if names else f'{c}'))
                        p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))


                        #center of box
                        box_center = (int((p2[0] +  p1[0])//2),int((p2[1] +  p1[1])//2) )

                        # cv2.circle(frame,box_center,self.radius+10,(0,0,255),-1)

                        cv2.rectangle(frame, p1, p2, color, 2)

                        tf = max(   lw - 1, 1)  # font thickness
                        w, h = cv2.getTextSize(label, 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
                        outside = p1[1] - h >= 3
                        p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
                        cv2.rectangle(frame, p1, p2, color, -1, cv2.LINE_AA)  # filled
                        cv2.putText(frame,
                                    label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                                    0,
                                    lw / 3,
                                    self.txt_color,
                                    thickness=tf,

                                    lineType=cv2.LINE_AA)
                        object_cnt+=1
                        print("object_cnt_:",object_cnt)
            cv2.imshow('detection video', frame)

            cv2.waitKey(3)
            time.sleep(0.01)
            entire_cnt+=1
            print("entire_cnt:",entire_cnt)

            frame = None

        self.cap.release() 
        cv2.destroyAllWindows()

if __name__== "__main__" :
    # rospy.init_node('image_feature', anonymous=True)
    cap = ASL_process()
    cap.run()