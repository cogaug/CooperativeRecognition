import os, sys
import re
import argparse
import numpy as np
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from utils.measure import measure_each, measure_box
# from measure import measure_each, measure_box
class Savedata():
    def __init__(
        self,
        filename = "carla",
        data_size = 100,
        makefile = True
    ):  
        
        self.filename = filename
        self.data_size = data_size
        self.makefile = makefile
        self.filepath = os.path.abspath(__file__)
        self.output_file_path = self.filepath.replace("utils/save.py",'save/{}.txt'.format(self.filename))

        self.save_cnt = 0
        self.save_detction_cnt = 0
        self.measure_data = measure_each()
        self.measure_box = measure_box()

        self.location_aug_GT = [[520.7056274414062, 240.93679809570312], 
        [521.3056030273438, 237.43679809570312], 
        [530.0, 238.0], 
        [525.5, 241.0]]

        #location_car2, location_car3, location_vehicle1, location_person

        if self.makefile :
            self.make_file()
        print(">> save the data...")
        print()

    def readthetext_augemt(self):
        print(f"---------AP: {self.filename}------")
        # print()

        odd_lines = []
        even_lines = []
        location_aug = []
        file_cnt = 0
        def extract_floats(item):
            match = re.findall(r"\d+\.\d+", item)
            return [float(value) for value in match]
        
        def avg_precision(score):
            ap = np.mean(score)
            print("******ACC RESULTS******")

            print(f"each AP : {ap:.2f}%" )
            print()

            return ap
        with open(self.output_file_path, "r") as f:
            for idx, line in enumerate(f, start=1): 
                elements = line.strip().split("/") 
                if file_cnt<self.data_size :
                    if idx % 2 == 1: 
                        odd_lines.append(elements)
                    else:  
                        even_lines.append(elements)
                    file_cnt +=1
                elif file_cnt ==self.data_size :
                    for data in elements[:-1]: location_aug.append(extract_floats(data))
            
       
            # print(location_aug)
            # print(odd_lines)
            # print(len(odd_lines))
            # print(len(even_lines))
            # print(len(location_aug))
            # print(even_lines)

        # person
        score1 = self.measure_data.divde_data(odd_lines,self.location_aug_GT[3],gt_num=3) # person
        score2 = self.measure_data.divde_data(even_lines,self.location_aug_GT[2],gt_num=2) # car
        ap = avg_precision([score1,score2])
        return ap

    def readthetext_for_bbox(self):
        def extract_floats(item):
            match = re.findall(r"\d+\.\d+", item)
            return [float(value) for value in match]

        data = []
        with open(self.output_file_path, "r") as f:
  
            lines = f.readlines()
        for i in range(0,len(lines)-1):
            prevt = lines[i].strip().split("/")
            # print(prevt)
            data_local = []

            for j in range(0,len(prevt)-1):

                # print(prevt[j])
                float_results = extract_floats(prevt[j]) 
                # print(float_results)
                data_local.append(float_results)
                # print(data_local)

            data.append(data_local)
            # print(prevt[0])
            # print(prevt[1])
            # print(prevt[2])

        self.measure_box.organize_list(data,lines[-1])

    def make_file(self):
        with open(self.output_file_path, "w") as f:pass

    def save_to_augmentation(self, dataresult,local_GT):
        if len(dataresult)>0:
            if self.save_cnt< self.data_size:
                for data in dataresult:
                    with open(self.output_file_path, "a") as f:
                        f.write("%d/%s/%f/%s/%f/%f/%f\n" % (data[0], data[1], data[2], data[3], data[4][0]+local_GT[0][0],data[4][1]+local_GT[0][1],data[5]))
                self.save_cnt +=1
                return 0
            else:
                # self.readthetext_augemt(self.location_aug_GT)
                # with open(self.output_file_path, "a") as f:  
                #     f.write("GT ")
                for data in local_GT:
                    with open(self.output_file_path, "a") as f:
                        f.write("[%f, %f]/" % (data[0],data[1]))
                print("local GT",local_GT)
                print(">>>save all data!!")
                self.save_cnt = 0
                return 1


    def save_to_detection(self, dataset,local_GT):

        if self.save_detction_cnt< self.data_size:
            for data in dataset:
                with open(self.output_file_path, "a") as f:
                    f.write("%s [%f, %f]/ " % (data[1], data[4][0],data[4][1]))
            with open(self.output_file_path, "a") as f:  
                f.write("\n")

            self.save_detction_cnt +=1
        else:
            # self.readthetext(local_GT)
            if(self.save_detction_cnt == self.data_size):
                print("local_GT : ",local_GT)
                with open(self.output_file_path, "a") as f:  
                    f.write("GT ")
                for data in local_GT:
                    with open(self.output_file_path, "a") as f:
                        f.write("[%f, %f, %f, %f], " % (data[0],data[1],data[2],data[3]))
                
                # self.readthetext()
                print(">>>save all data!!")

                sys.exit()

                self.save_detction_cnt +=1
            
            print("local_GT : ",local_GT)
            
            

if __name__== "__main__" :
    
    
    parser = argparse.ArgumentParser(description="Choose a function to execute in Savedata class.")
    parser.add_argument(
        "--func", 
        choices=["readthetext_for_bbox", "readthetext_augemt"], 
        required=True,
        help="Choose which function to execute: 'readthetext_for_bbox' or 'readthetext_augemt'"
    )
    args = parser.parse_args()

    if args.func == "readthetext_for_bbox":
        filepath = "test1_results"

        sd = Savedata(
        # filename = "test2_results",
        filename = filepath,
        makefile = False
        )

    elif args.func == "readthetext_augemt":
        filepath = "test2_results"
        print(">>>>>"+"readthetext_augemt")
        sd_car = Savedata(
            # filename = "test2_results",
            filename = filepath+"_car",
            makefile = False
        )

        sd_truck = Savedata(
            # filename = "test2_results",
            filename = filepath+"_truck",
            makefile = False
        )
    if args.func == "readthetext_for_bbox":
        sd.readthetext_for_bbox()
    elif args.func == "readthetext_augemt":
        ap_car=sd_car.readthetext_augemt()
        ap_truck=sd_truck.readthetext_augemt()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(f">>>>total AP : {(ap_car+ap_truck)/2:.2f}%")

