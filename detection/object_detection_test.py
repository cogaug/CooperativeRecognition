"""
this is the detection module for test 
"""
import cv2
import numpy as np
import sys
from math import cos, sin, radians
from detection.color_estimation import estimate_color
# from sklearn.cluster import KMeans

yolo_repo_path = './ultralytics'
sys.path.append(yolo_repo_path)

from ultralytics import YOLO
from ultralytics.utils.plotting import Colors
sys.path.remove(yolo_repo_path)


# CARLA world coordinate
#(Xw : West, Yw: North, Zw: dowm)
# CARLA camera coordinate
#(Xc : West, Yc: up, Zc: North)
# (Xw,Yw,Zw) --> (Xc, Zc, -Yc)

class yolov8_detection(object):
    def __init__(
        self,
        model = "./model/yolov8n.pt"
    ):  
    
        self.model = YOLO(model)
        # print(self.model)

        self.colors = Colors()
        self.txt_color=(0, 0, 0)
        self.radius = 5
        self.confidence = 0.64
        
        #depth instance
        self.far = 1000.0 
        self.calibx = 2
        self.caliby = 0.8
        #color 
        self.ce = estimate_color(color_model_path = "./model/color.pt")

        self.depth_margin = 20
        
        #camera intrinsic
        self.k = self.get_camera_intrinsics()

        # depth distance reference value
        self.depth_ref = 2.0 #m

    def get_camera_intrinsics(self):
        width = 800
        height = 600
        fov = 90

        fx =  width / (2.0 * np.tan(fov * np.pi / 360.0))
        fy = fx

        cx = width /2.0
        cy = height /2.0

        K = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0,  0,  1]
        ])
        return K

    def depth_procss(self,depth,center,camera_transform):
        # print("depth shape:", depth.shape)
        
        # CARLA world coordinate
        # (Xw : West, Yw: North, Zw: dowm)
        # CARLA camera coordinate
        # (Xc : West, Yc: up, Zc: North)
        # (Xw,Yw,Zw) --> (Xc, Zc, -Yc)

        camera_location = camera_transform.location
        camera_rotation = camera_transform.rotation
        yaw = radians(camera_rotation.yaw)
        pitch = radians(camera_rotation.pitch)
        roll = radians(camera_rotation.roll)

        R_map = np.array([
        [0,0,1],
        [1,0,0],
        [0,-1,0] 
        ])
       
        R_z = np.array([
            [cos(yaw), -sin(yaw), 0],
            [sin(yaw), cos(yaw), 0],
            [0, 0, 1]
        ])
        R_y = np.array([
            [cos(pitch), 0, sin(pitch)],
            [0, 1, 0],
            [-sin(pitch), 0, cos(pitch)]
        ])
        R_x = np.array([
            [1, 0, 0],
            [0, cos(roll), -sin(roll)],
            [0, sin(roll), cos(roll)]
        ])
        # print("R_z : ",R_z)
        # print("R_y : ",R_y)
        # print("R_x : ",R_x)

        rotation_matrix = R_z @ R_y @ R_x @ R_map

        # print("rotation_matrix : ",rotation_matrix)
        x1 = depth.shape[1]//2 #- self.depth_margin

        # x2 =  depth.shape[1]//2 + self.depth_margin

        
        y1 =  depth.shape[0]//2  #- self.depth_margin
        # y2 =  depth.shape[0]//2 + self.depth_margin
        print("x1, y1 : ",center)
        R = depth[y1,x1, 2].astype(np.uint32)
        G = depth[y1,x1, 1].astype(np.uint32)
        B = depth[y1,x1, 0].astype(np.uint32)
        print(R,G,B)
        print(depth[y1,x1])
        # R = depth[y1,x1:x2, 0].astype(np.uint32)
        # G = depth[y1,x1:x2, 1].astype(np.uint32)
        # B = depth[y1,x1:x2, 2].astype(np.uint32)
        depth_int24 = R + G * 256 + B * 256 * 256
        depth_normalized = depth_int24 / (256 * 256 * 256 - 1)
        distance = depth_normalized * self.far #/100
        
        # distance = [i for i in distance if i >2]
        print("depth distance:", distance)
        print("depth median:", np.max(np.unique(distance)))

        if distance > self.depth_ref:
            xc = (center[0] - self.k[0][2])*distance / self.k[0][0]
            yc = (center[1] - self.k[1][2])*distance / self.k[1][1]
            zc = distance

            cam_coords = np.array([xc, yc, zc])
            # print(" cam_coords:", cam_coords)
            # vehicle_coords = np.dot(rotation_matrix, cam_coords) + np.array([camera_location.x, camera_location.y, camera_location.z])
            vehicle_coords = np.dot(rotation_matrix, cam_coords) #+ np.array([camera_location.x, camera_location.y, camera_location.z])
        

            car_x, car_y, car_z = vehicle_coords[:3]

            return (car_x+self.calibx, car_y+self.caliby)
        
        else:
            return (-1, -1)
        # # Convert to meters
        # # Far plane distance in meters
        
        # distance = round((depth_normalized * self.far)/100,4)
        # print("car estimated depth : {} m".format(distance))

    def make_box(self,frame, depth,camera_transform):
        print("depth.shape :",depth.shape)
        print("camera_transform :",camera_transform)
        # print("vehicle_transform :",vehicle_transform)

        # camera_to_world = camera_transform.get_matrix()
        # world_to_vehicle = vehicle_transform.get_inverse_matrix()
        size = frame.shape
        if size[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
            # depth = cv2.cvtColor(depth, cv2.COLOR_RGBA2RGB)

            #depth processing
        
            

        # frame = cv2.resize(frame, dsize=(size[1]//2, size[0]//2),
        results=self.model.track(source=frame,persist=True,tracker="bytetrack.yaml")
        if results and results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().cpu().tolist()
        else: track_ids =[]
        # track_ids = results[0].boxes.id.int().cpu().tolist()
        # results=self.model.predict(source=frame,save=False, save_txt=False)

        lw = max(round(sum(frame.shape) / 2 * 0.003), 2) 

        names = results[0].names
        boxes = results[0].boxes.cpu().numpy()

        class_name = np.array([])
        class_num = list()
        
        total_object_list = list()

        # print("track_ids and boxes : ",track_ids, boxes)

        # shape  = (self.width,self.height)

        if boxes is not None:
            for j, (d, id) in enumerate(zip(reversed(boxes), track_ids)):

                box = d.xyxy.squeeze()
                conf = d.conf.squeeze()
                cls = d.cls.squeeze()
                velocity = 0
                print("conf : ",conf)

                color = self.colors(j)
                if conf >self.confidence:
                    object_list = list()    

                    c = int(cls)
                    # print("C : ",c)
                    class_num.append(c)
                    label = (f'{id} 'if id else "No id ")+(f'{names[c]} ' if names else f'{c}') + (f'{conf:.2f}' if True else '') 
                    # YOLO.annotator.box_label(boxes, label, color=YOLO.colors(c, True))
                    class_name=np.append(class_name,(f'{names[c]}' if names else f'{c}'))
                    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
                    print("Label : ",label)
                    if id !=None:
                        object_list.append(id)
                    if names[c] != None:
                        object_list.append(names[c])
                        object_list.append(conf.item())
                    #color estimation
                    if names[c] !="person":
                        color_reuslts = self.ce.color_detection(frame[p1[1]:p2[1], p1[0]:p2[0]])
                        print("color_results: ",color_reuslts)
                        object_list.append(color_reuslts)
                    else:
                        object_list.append("None")
                    #center of box
                    box_center = (int((p2[0] +  p1[0])/2),int((p2[1] +  p1[1])/2) )

                    cv2.circle(frame,box_center,self.radius+3,(0,0,255),-1)
                    #depth extraction
                    # car coordinate estimation
                    # self.depth_procss(box_center,camera_transform,vehicle_transform)
                    car_epose=self.depth_procss(depth[p1[1]:p2[1], p1[0]:p2[0]],box_center,camera_transform)
                    object_list.append([car_epose[0],car_epose[1]])

                    object_list.append(velocity)
                    print(f"Detected Position : ",car_epose)
                    print("-*"*10)
                    # label += f' {distance:.2f}m'
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
                    total_object_list.append(object_list)
            print("total_object_list :", total_object_list)
        return frame, total_object_list
  
# if __name__ == '__main__':
#     y8 = yolov8_detection(
#         model ="./model/yolov8n.pt"
#         )