import cv2
import numpy as np
import sys
yolo_repo_path = './ultralytics'
sys.path.append(yolo_repo_path)

from ultralytics import YOLO

class estimate_color(object):
    def __init__(
        self,
        color_model_path = "./model/color.pt"
    ):
        self.color_model_path = color_model_path
        self.color_model = YOLO(self.color_model_path)


    def color_detection(self,frame):
        results = self.color_model.predict(frame)

        color_name = results[0].names[results[0].probs.top5[0]]

        return color_name