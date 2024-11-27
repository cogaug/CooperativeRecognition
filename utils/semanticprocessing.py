import yaml
import os, time
import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
class CAR_SIP(object):
    def __init__(
        self,
        vehicle_semantic_name = "vehicle1",
        showthetosm = True,
        detect_dist_margin = 2
    ):  

        self.path = "~/car_rec_expansion/SemanticDB/"
        self.vehicle_semantic_name = vehicle_semantic_name
        self.showthetosm = showthetosm
        self.detect_dist_margin  = detect_dist_margin 
        self.semantic_path =  os.path.expanduser(
            self.path+self.vehicle_semantic_name+".yaml")

        self.car_eculidian_margin = 2.0 #m
        with open(self.semantic_path, 'r') as file:
            try:
                data = yaml.safe_load(file)
                # print(data)
                self.extract_yaml(data['Vehicle'])
            except yaml.YAMLError as exc:
                print(f"Error reading YAML file: {exc}")

        print(">>",self.vehicle_semantic_name+" Semantic Information Processing..")
    
    def info_integrated(self,vehicle_info):
        self.vehicle_info = vehicle_info
        print(self.vehicle_info)
        print()

    def euclidean_distance(self,point1, point2):
        a, b = point1
        c, d = point2
        distance = math.sqrt((c - a) ** 2 + (d - b) ** 2)
        # print("euclidean : ",distance)
        return distance
    def remove_duplicates(self,match_result):
        unique_result = []
        seen = set()

        for item in match_result:
            item_tuple = (item[0], item[1], tuple(item[2]))
            if item_tuple not in seen:
                seen.add(item_tuple)
                unique_result.append(item)

        return unique_result

    def extract_yaml(self, yamldata):
        self.tosm = yamldata
        self.symbol = yamldata.get('Symbol', {})
        self.explicit = yamldata.get('Explicit', {})
        self.implicit = yamldata.get('Implicit', {})
        own_info = []

        if self.showthetosm:
            print(">> ",self.vehicle_semantic_name+" semantic information ------")
            print("name : ",self.symbol["name"])
            print("id   : ",self.symbol["id"])
            print("type : ",self.symbol["type"])

            print("size       :",self.explicit["size"])
            print("color      :",self.explicit["color"])
            print("pose       :",self.explicit["pose"])
            print("velocity   :",self.explicit["velocity"])
            print("CoordinateFrame   :",self.explicit["CoordinateFrame"])

            print("isInsideof    :",self.implicit["isInsideof"])
            print("isKeyObject   :",self.implicit["isKeyObject"])
            print("isMovable     :",self.implicit["isMovable"])
            print("purpose       :",self.implicit["purpose"])
            own_info.append(self.symbol["type"])
            own_info.append(self.explicit["color"])

            self.own_info = own_info
    def matching(self,detected_info,other_car):
        # 0:class,1:color,2:pose
        print("detected_info:",detected_info)
        match_result = []
        for i,tosm in enumerate(self.vehicle_info):  # carsmf 
            tosm["Explicit"]["pose"][0] = other_car[i].x
            tosm["Explicit"]["pose"][1] = other_car[i].y
            # print("tosm pose:",tosm["Explicit"]["pose"][:2])

            for info in detected_info:   # detected information list
            # object attribute
                if len(info) != 0:
                    distance = self.euclidean_distance(
                        tosm["Explicit"]["pose"][:2], info[2]
                        )
                    if tosm["Symbol"]["type"] == info[0]:
                        print(
                        ">match type : ", info[0], 
                        " and ",
                        tosm["Symbol"]["name"])
                        if(distance< self.detect_dist_margin):
                            print(">>distance : ",distance)
                            if (tosm["Explicit"]["color"]== info[1]):

                                print(">>>match color : ", info[1])
                                print(">>>>matched!!")
                                match_result.append(
                                [tosm["Symbol"]["type"],
                                tosm["Explicit"]["color"],
                                tosm["Explicit"]["pose"][:2]
                                ])
                    elif (info[0] != 'car') and (info[0] != 'truck'):
                        match_result.append(info)
            # print("match_result1 : ",match_result)
        unique_match_results = self.remove_duplicates(match_result)
        # print("match_result2 : ",unique_match_results)
        return unique_match_results
            # print("match_result : ",np.unique(match_result))

class SIP_Graph(object):
    def __init__(
        self
    ):
        self.graph = nx.DiGraph()
        self.plt_cnt = 0

        # self.danger = ["D1","D2","D3","D4"]
        # self.dan_num = [-1,0,0,0,3,1,2]
        print(">> SIP graph init..")
        
    def draw_graph(self,graph, match_list):
        print("match_results in draw_graph :", match_list)

        plt.clf()
        pos = {}
        labels = {}
        direct_list = []
        truck_num = 0
        convert_cnt = 0 
        for i, info in enumerate(match_list):
            node_id = i+1
            
            


            # if info[1] == None:
            #     info[1] = 'lightblue'
            graph.add_node(node_id, label=f'{info[0]} ({info[1]})')
            # pos[node_id] = (info[2][1], info[2][0])
            pos[node_id] = (-info[2][1], -info[2][0])
            # print(info[1])
            if info[1] == "None":
                labels[node_id] = f'{node_id} {info[0]}' #{self.danger[self.dan_num[node_id]]}'
            else:
                labels[node_id] = f'{node_id} {info[0]} ({info[1]})'# {self.danger[self.dan_num[node_id]]}'
        print("match_list : ",len(match_list))
        if len(match_list)>1:
            for i in range(1,len(match_list)):
                if convert_cnt ==0:
                    direct_list.append((1,i+1))
                if match_list[i][0] == 'truck':
                    if convert_cnt ==0:
                        truck_num = i+1
                        convert_cnt =1
                # print("truck num!!",truck_num)
                # print("match_list num!!",i+1)
                if truck_num !=0:
                    if truck_num < len(match_list) :
                        if truck_num< i+1:
                            direct_list.append((truck_num,i+1))
        graph.add_edges_from(direct_list)
        nx.draw(graph, pos, labels=labels, with_labels=True, node_color='lightblue', font_weight='bold', arrows=True)
        plt.pause(0.000001)

    def generate_graph(self,match_results):
        if self.plt_cnt ==0:
            plt.ion()
            self.plt_cnt +=1
        else:
            try:
                self.graph.clear()
                self.draw_graph(self.graph, match_results)
            except KeyboardInterrupt:
                print("KeyboardInterrupt at the SIP Graph!")
                plt.ioff()
                plt.show()
                
# if __name__ == '__main__':
#     cs = CAR_SIP(
#         vehicle_semantic_name = "vehicle1",
#         showthetosm = True
#     )

   