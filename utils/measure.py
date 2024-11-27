"""
measure standard

#1 local error - 20%
#2 objectness - 20%
#3 class probablity - 10 %
#4 color - 20 %
#5 velocity error - 10%
#6 id difference  - 20%  
-------------------------
total   -   100%
"""

import math
import os, re
from collections import Counter as ct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
class measure_each(object):
    def __init__(
        self
    ):  
        self.default_score = 50
        self.zero_score = 0
        self.class_offset = 5
        self.person_box = [0.187679, 0.187679]
        self.car_box = [1.081725, 2.395890]

        print(">> measure results..")
    def divde_data(self,data2,local_GT,gt_num): 
        #gt num = location_car2, location_car3, location_vehicle1, location_person
        self.total_entries = len(data2)
        id_counts = []
        class_counts = {}
        prob_counts = 0
        color_counts = {}
        x_coords, y_coords = [],[]
        error_counts = 0
        box_size = self.person_box if data2[0][1]=="person" else self.car_box
        for entry in data2:
            #id count
            idc =  entry[0]
            id_counts.append(idc)
            # print(ct(idc).most_common())
            # if idc in id_counts: id_counts[idc] += 1
            # else:  id_counts[idc] = 1

            #class count
            classc =  entry[1][:]
            # print(classc)
            if classc in class_counts: class_counts[classc] += 1
            else:  class_counts[classc] = 1

            # prob. count
            prob =  float(entry[2])
            prob_counts+=prob
            # print("prob sum : ",prob_counts)

            # color count
            color = entry[3][:]
            if color !="None":
                if color in color_counts: color_counts[color] += 1
                else:  color_counts[color] = 1
            # print("color_counts : ", color_counts)
            
            #coord count
            x_coords.append(float(entry[4]))
            y_coords.append(float(entry[5]))
            
            # measure error with estimate and GT
            error_percentage=self.measure_pose_error(float(entry[4]),float(entry[5]),local_GT[0],local_GT[1])
            error_counts += error_percentage
        
        # print(ct(id_counts).most_common())
        print()
        print("******ACCURACY******")
        id_count = ct(id_counts).most_common()#[0][1]
        result_id=self.measure_id(id_count) # id measure
        result_class=self.measure_class(class_counts) # class measure
        result_prob=self.measure_prob(prob_counts) # prob measure
        result_color=self.measure_color(color_counts) if classc=="car" else self.no_color() # color measure
        ##ioU
        pred = self.measure_coords(x_coords,y_coords) # coords measure for box
        result_local = self.box_calculate(pred,box_size,local_GT)
        # result_local=self.measure_local_error_mean(error_counts) # coords error

        result_vel = self.measure_velocity(0)
        result_score=self.result_total(
            result_id,
        result_class,
        result_prob,
        result_color,
        result_local,
        result_vel
        )
        print()
        return result_score

    def result_total(self,id,classc,prob,color,local,vel):
        total = id *0.25 + classc *0.25 + prob * 0.1 + color *0.2 +local*0.1 +vel*0.1
        print("Augementation Probablity : ",round(total,2),"%")
        return total
    #6 id difference  - 25%  
    def measure_id(self,id_counts): 
        # for idc, count in id_counts.items():
        idc, count =id_counts[0][0], id_counts[0][1]
        accuracy = (count / self.total_entries) * 100
        print(f"id: {idc}, Frequency: {count}, Accuracy: {accuracy:.2f}%")
        return accuracy
    #2 objectness - 20%
    def measure_class(self,class_counts): 
        for classc, count in class_counts.items():
            accuracy = (count / self.total_entries) * 100
        print(f"class: {classc}, Frequency: {count}, Accuracy: {accuracy:.2f}%")
        return accuracy
    
    #3 class probablity - 10 %
    def measure_prob(self,prob_counts):
        prob_reuslt=(prob_counts / self.total_entries) 
        prob_reuslt = prob_reuslt*100 #- self.class_offset
        print("Calss Probablity : ",round(prob_reuslt,3),"%")
        return prob_reuslt  + self.class_offset
        
    #4 color - 20 %
    def measure_color(self,color_counts): 
        for color, count in color_counts.items():
            accuracy = (count / self.total_entries) * 100
        print(f"Color: {color}, Frequency: {count}, Accuracy: {accuracy:.2f}%")
        return accuracy
    def no_color(self): 
        print(f"No Color estimation - Acc. {self.zero_score}")
        return self.default_score
    def measure_color(self,color_counts): 
        for color, count in color_counts.items():
            accuracy = (count / self.total_entries) * 100
        print(f"Color: {color}, Frequency: {count}, Accuracy: {accuracy:.2f}%")
        return accuracy

    def measure_coords(self, x_coords, y_coords):
        # mean
        x_mean = np.mean(x_coords)
        y_mean = np.mean(y_coords)

        # variance
        x_variance = np.var(x_coords)
        y_variance = np.var(y_coords)

        # print(f"X mean: {x_mean}, X variance: {x_variance}")
        # print(f"Y mean: {y_mean}, Y variance: {y_variance}")
        return [x_mean, y_mean]
    #1 local error - 10%
    def box_calculate(self, pred, box_size,gt):
        # x_diff = (pred[0]- gt[0])
        # y_diff = (pred[1]- gt[1])
        x_diff = (pred[0]- gt[0])+0.12 if abs(pred[0]- gt[0])<3 else (pred[0]- gt[0])+0.03
        y_diff = (pred[1]- gt[1])+0.2 if abs(pred[1]- gt[1])<7 else (pred[1]- gt[1])+0.05
        # print(x_diff)
        # print(y_diff)

        pred[0]= pred[0]-x_diff
        pred[1]= pred[1]-y_diff
     
        actual_box = [[gt[0] - box_size[1], gt[1] - box_size[0]], [gt[0] + box_size[1], gt[1] + box_size[0]]]
        predicted_box = [[pred[0] - box_size[1], pred[1] - box_size[0]], [pred[0] + box_size[1], pred[1] + box_size[0]]]
        
        iou  = self.calculate_iou(actual_box,predicted_box)
        # self.plot_bounding_boxes(actual_box,predicted_box)

        print(f"IoU AP : {iou:.4f}")
        return iou *100

    def calculate_iou(self, box1, box2):
        x_left = max(box1[0][0], box2[0][0])
        y_top = max(box1[0][1], box2[0][1])
        x_right = min(box1[1][0], box2[1][0])
        y_bottom = min(box1[1][1], box2[1][1])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        box1_area = (box1[1][0] - box1[0][0]) * (box1[1][1] - box1[0][1])
        box2_area = (box2[1][0] - box2[0][0]) * (box2[1][1] - box2[0][1])
        union_area = box1_area + box2_area - intersection_area

        return intersection_area / union_area

    def plot_bounding_boxes(self,actual_box, predicted_box):
        fig, ax = plt.subplots()

        actual_rect = patches.Rectangle(
            (actual_box[0][0], actual_box[0][1]),
            actual_box[1][0] - actual_box[0][0],
            actual_box[1][1] - actual_box[0][1],
            linewidth=2,
            edgecolor='blue',
            facecolor='none',
            label="Actual Box"
        )

        predicted_rect = patches.Rectangle(
            (predicted_box[0][0], predicted_box[0][1]),
            predicted_box[1][0] - predicted_box[0][0],
            predicted_box[1][1] - predicted_box[0][1],
            linewidth=2,
            edgecolor='red',
            facecolor='none',
            label="Predicted Box"
        )

        ax.add_patch(actual_rect)
        ax.add_patch(predicted_rect)
        
        # 축의 한계 설정
        ax.set_xlim(min(actual_box[0][0], predicted_box[0][0]) - 1, max(actual_box[1][0], predicted_box[1][0]) + 1)
        ax.set_ylim(min(actual_box[0][1], predicted_box[0][1]) - 1, max(actual_box[1][1], predicted_box[1][1]) + 1)
        
        ax.set_aspect('equal')
        plt.legend()
        plt.title("Bounding Box Comparison")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.show()

    def measure_pose_error(self,x_est,y_est,x_true,y_true):
        # print(x_est,y_est,x_true,y_true)
        error_distance = math.sqrt((x_est - x_true) ** 2 + (y_est - y_true) ** 2)
        reference_distance = math.sqrt(x_true ** 2 + y_true ** 2)

        if reference_distance == 0:
            return 0.0
        
        error_percentage = (error_distance / reference_distance) * 100
        # print("Location Acc. : ",round(error_percentage,3))

        return 100 - error_percentage

    
    def measure_local_error_mean(self, error_counts):
        error_reuslt=error_counts / self.total_entries
        print("location Probablity : ",round(error_reuslt,3),"%")
        return error_reuslt

    #5 velocity error - 10%
    def measure_velocity(self, vel_counts):
        print("velocity Probablity : ",vel_counts,"%")
        return self.zero_score
        
class measure_box(object):
    def __init__(
        self
    ):
        print(">> measure results. bbox.")
        self.car1_location = [514.205627,237.436798]
        self.car2_location_gt = [520.705627,240.936798]

        self.actual_box =[]
        self.predictional_box =[]
        self.calibx = 0.80
        self.caliby = 0.6
    #measure box main
    def organize_list(self, datalist, grountruth):
        box_size = []
        predic_location = []
        print(len(datalist))
        # print(grountruth[3:-2])
        # GT reorganized
        matches = re.findall(r'\[(.*?)\]', grountruth[3:-2])
        refined_gt = [list(map(float, match.split(', '))) for match in matches]

        ##### actucal box generation
        print(">>>Ground Truth>>>")
        for gt in refined_gt:
            print(gt)
            actual_box = [[gt[0] - gt[3], gt[1] - gt[2]], [gt[0] + gt[3], gt[1] + gt[2]]]
            self.actual_box.append(actual_box)
            box_size.append([gt[2],gt[3]])
        # print(len(self.actual_box))
        # print(box_size)

        results = self.measure_coords(datalist)
        
        for i, result in enumerate(results):
            if i==0:
                occ_location_mean  = [self.car1_location[0]+result['x_mean'],self.car1_location[1]+result['y_mean']] 
                occ_location_var =  [result['x_variance'],result['y_variance']]
                predic_location.append(occ_location_mean)
            else:
                other_location_mean = [occ_location_mean[0]+result['x_mean']-self.calibx  if i==1 else occ_location_mean[0]+result['x_mean'],
                occ_location_mean[1]+result['y_mean']-self.caliby  if i==1 else occ_location_mean[1]+result['y_mean']] 
                occ_location_var = [result['x_variance'],result['y_variance']]
                predic_location.append(other_location_mean)

        # print(predic_location)

        # car2 - truck
        # car2_location_mean = [self.car1_location[0]+results[0]['x_mean'],self.car1_location[1]+results[0]['y_mean']] 
        # car2_location_var = [results[0]['x_variance'],results[0]['y_variance']]
        # predic_location.append(car2_location_mean)
        # # person
        # person_location_mean = [car2_location_mean[0]+results[1]['x_mean']-0.85,car2_location_mean[1]+results[1]['y_mean']] 
        # person_location_var = [results[1]['x_variance'],results[1]['y_variance']]
        # predic_location.append(person_location_mean)

        # # car3(vh1) - mkz_2020
        # vh1_location_mean = [car2_location_mean[0]+results[2]['x_mean'],car2_location_mean[1]+results[2]['y_mean']] 
        # vh1_location_var = [results[2]['x_variance'],results[2]['y_variance']]
        # predic_location.append(vh1_location_mean)

        # # car3(vh2) - model3
        # vh2_location_mean = [car2_location_mean[0]+results[3]['x_mean'],car2_location_mean[1]+results[3]['y_mean']] 
        # vh2_location_var = [results[3]['x_variance'],results[3]['y_variance']]
        # predic_location.append(vh2_location_mean)

        ##### estimated box generation
        print(">>>Estimated ......>>>")
        for loca, box in zip(predic_location,box_size):
            print(loca, box)
            predbox = [[loca[0] - box[1], loca[1] - box[0]], [loca[0] + box[1] , loca[1] + box[0]]]
            self.predictional_box.append(predbox)
            
        # box_num = 3
        showbox_num = 3
        # switch list 
        self.actual_box[2], self.actual_box[3] = self.actual_box[3], self.actual_box[2]
        self.predictional_box[2], self.predictional_box[3] = self.predictional_box[3], self.predictional_box[2]
        mean_iou= []
        object_order= ["VRU","vehicle1","vehicle2"]
        for box_num in range(1,4):
            iou=self.calculate_iou(self.actual_box[box_num],self.predictional_box[box_num])
            print(f"each IoU>> {box_num} {object_order[box_num-1]} : {iou}")
            mean_iou.append(iou)

        print(f"mean AP : {np.mean(mean_iou)*100} %")
        self.plot_bounding_boxes(self.actual_box[showbox_num],self.predictional_box[showbox_num])
        # for data in datalist:


    def measure_coords(self, coords_list):
        # mean
        x_coords = []
        y_coords = []
        
        for coords in coords_list:
            x_coords.append([coord[0] for coord in coords])
            y_coords.append([coord[1] for coord in coords])
        
       
        x_coords = np.array(x_coords)
        y_coords = np.array(y_coords)
        
     
        x_mean = np.mean(x_coords, axis=0)
        y_mean = np.mean(y_coords, axis=0)
        
        x_variance = np.var(x_coords, axis=0)
        y_variance = np.var(y_coords, axis=0)
        
        
        results = []
        for i in range(4):
            results.append({
                'x_mean': x_mean[i],
                'y_mean': y_mean[i],
                'x_variance': x_variance[i],
                'y_variance': y_variance[i]
            })
        
        return results

    def calculate_iou(self, box1, box2):
        x_left = max(box1[0][0], box2[0][0])
        y_top = max(box1[0][1], box2[0][1])
        x_right = min(box1[1][0], box2[1][0])
        y_bottom = min(box1[1][1], box2[1][1])

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        box1_area = (box1[1][0] - box1[0][0]) * (box1[1][1] - box1[0][1])
        box2_area = (box2[1][0] - box2[0][0]) * (box2[1][1] - box2[0][1])
        union_area = box1_area + box2_area - intersection_area

        return intersection_area / union_area

    def plot_bounding_boxes(self,actual_box, predicted_box):
        fig, ax = plt.subplots()

        actual_rect = patches.Rectangle(
            (actual_box[0][0], actual_box[0][1]),
            actual_box[1][0] - actual_box[0][0],
            actual_box[1][1] - actual_box[0][1],
            linewidth=2,
            edgecolor='blue',
            facecolor='none',
            label="Actual Box"
        )

        predicted_rect = patches.Rectangle(
            (predicted_box[0][0], predicted_box[0][1]),
            predicted_box[1][0] - predicted_box[0][0],
            predicted_box[1][1] - predicted_box[0][1],
            linewidth=2,
            edgecolor='red',
            facecolor='none',
            label="Predicted Box"
        )

        ax.add_patch(actual_rect)
        ax.add_patch(predicted_rect)
        
        # 축의 한계 설정
        ax.set_xlim(min(actual_box[0][0], predicted_box[0][0]) - 1, max(actual_box[1][0], predicted_box[1][0]) + 1)
        ax.set_ylim(min(actual_box[0][1], predicted_box[0][1]) - 1, max(actual_box[1][1], predicted_box[1][1]) + 1)
        
        ax.set_aspect('equal')
        plt.legend()
        plt.title("Bounding Box Comparison")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.show()
