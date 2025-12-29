from ultralytics import YOLO
from ultralytics.yolo.utils.plotting import Colors
import cv2
import numpy as np
import sys
import os
import torch
import time
import copy

class Image_process():
    def __init__(
        self

    ):
        self.ASL_model = YOLO('/home/kkk/ultralytics/runs/detect/train20/weights/best.pt')  # load an official model

        self.colors = Colors()
        
        self.detect_thre = 0


        self.txt_color=(250, 250, 250)

        self.radius = 5

        # self.path1 ="/home/kkk/Segment-and-Track-Anything/assets/charger.MOV"
        self.path1 ="/media/kkk/hard_disk/inavi/test_image/14.png"


    def run(self):

     

        frame = cv2.imread(self.path1)
        frame = np.array(frame)
        print(frame.shape)
        size = frame.shape

        # frame = cv2.resize(frame, dsize=(640, 480), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, dsize=(size[1], size[0]), interpolation=cv2.INTER_AREA)
        # frame = cv2.flip(frame, -1)

        results=self.ASL_model.predict(source=frame,save=False, save_txt=False)
        
        lw = max(round(sum(frame.shape) / 2 * 0.003), 2) 

        names = results[0].names
        boxes = results[0].boxes.cpu().numpy()

        class_name = np.array([])
        class_num = list()
        
        # # cv2.imshow('detection image', frame)


        if len(boxes.xyxy)==0:
            print("No detected")


        if boxes is not None:
            for j, d in enumerate(reversed(boxes)):
                box = d.xyxy.squeeze()
                conf = d.conf.squeeze()
                cls = d.cls.squeeze()
            
                color = self.colors(j)
                if conf >0.3:
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

        cv2.imshow('detection image', frame)

        cv2.waitKey(0)


    cv2.destroyAllWindows()

if __name__== "__main__" :
    cap = Image_process()
    cap.run()