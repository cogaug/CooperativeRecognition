"""
pedestrian walking the street and generating the 
graph for augmenting the occlusion
"""

#public module
import carla
import numpy as np
import cv2
import gc
#custom module
from car_sim.car_generator import GenerateCar
from detection.object_detection import yolov8_detection
from utils.hdmap import map_express
from utils.semanticprocessing import CAR_SIP as cs, SIP_Graph as sg

class Expansion():
    def __init__(
        self,
        multi_streaming = False,
        autopilot_option = False,
        show_map = True,
        show_graph = True,
        spectator_view = False,
        streaming_id = 1
    ):  
        self.multi_streaming = multi_streaming
        self.show_map = show_map
        self.show_graph = show_graph
        self.spectator_view=spectator_view
        self.streaming_id = streaming_id
        # danger car
        self.gc1 = GenerateCar(
            model = 'vehicle.lincoln.mkz_2020',
            init_local = [23.5, -20.5, -0.04660,0],
            camera_position = [0,0,2],
            sync = False,
            autopilot = autopilot_option#True
            )
        # occlusion car
        self.cs_car1 = cs(vehicle_semantic_name = "vehicle1",
                showthetosm = True,
                detect_dist_margin = 2)
        
        self.gc2 = GenerateCar(
            model = 'vehicle.carlamotors.carlacola',
            init_local = [28.9,  -16.9, -0.04660,0],
            camera_position = [0.5,0,3],
            sync = False,
            autopilot = autopilot_option#True
            )
        self.cs_car2 = cs(vehicle_semantic_name = "vehicle2",
                showthetosm = True,
                detect_dist_margin = 2)

        # ego car
        self.gc3 = GenerateCar(
            model = 'vehicle.bmw.grandtourer',
            init_local = [31.9, -12.9, -0.04660,0],
            camera_position = [0,0,2.0],
            sync = False,
            autopilot = autopilot_option#True
            )
        self.cs_car3 = cs(vehicle_semantic_name = "vehicle3",
                showthetosm = True,
                detect_dist_margin = 2)
        
        # smf information integrated
        print(">> smf information integrated")
        self.cs_car2.info_integrated([self.cs_car1.tosm, self.cs_car3.tosm])
        
        self.cs_car3.info_integrated([self.cs_car1.tosm, self.cs_car2.tosm])
        # object detection
        self.detection = yolov8_detection()

        #walker addition and position
        self.num_walker_pose = [[23.8,-10.7,0], [20.8,-16.9,90], [20.0,-20.4,90]]

        # Graph generation
        self.sg  = sg()
        # map visualization
        if self.show_map:
            print("visualize the map")
            self.map_vi = map_express([self.gc1.model,self.gc2.model,self.gc3.model])

        print(">> initialize...")

        self.run_loop()

    def run_loop(self):
        try:
            client = carla.Client('localhost', 2000)
            client.set_timeout(20.0)
            world = client.load_world('Town06')
            world  = client.get_world()
            spectator = world.get_spectator() 

            gc1_vehicle, gc1_camera, gc1_depth_camera = self.gc1.setting(self.gc1.model,self.gc1.init_local,world)
            gc2_vehicle, gc2_camera, gc2_depth_camera = self.gc2.setting(self.gc2.model,self.gc2.init_local,world)
            gc3_vehicle, gc3_camera, gc3_depth_camera = self.gc3.setting(self.gc3.model,self.gc3.init_local,world)

            print(">>generate the vehicles...")


            gc1_image_queue, gc1_depth_queue=self.gc1.streaming_set(gc1_camera,gc1_depth_camera)
            gc2_image_queue, gc2_depth_queue=self.gc2.streaming_set(gc2_camera,gc2_depth_camera)
            gc3_image_queue, gc3_depth_queue=self.gc3.streaming_set(gc3_camera,gc3_depth_camera)
            
            # #walker setting
            self.gc1.walker_setting(world,self.num_walker_pose)


            
            gc_queue_id = [gc1_image_queue,gc2_image_queue,gc3_image_queue]
            gc_depth_queue_id = [gc1_depth_queue,gc2_depth_queue,gc3_depth_queue]

            gc_camera = [gc1_camera,gc2_camera,gc3_camera]

            # while True:
            #     print("check!!")
            while True:
                gcar_loc_xy = []
                

                world.tick()

                # self.gc1.walker_walking(world,self.walker_list)


                location_car1 = gc1_vehicle.get_location()
                
                # print("camera position: ",gc1_camera.get_location())
                location_car2 = gc2_vehicle.get_location()

                location_car3 = gc3_vehicle.get_location()

                if not self.multi_streaming:
                    if self.streaming_id<4:
                        frame_v2 = gc_queue_id[1].get()
                        frame_v3 = gc_queue_id[2].get()
                        # frame_v2 = np.reshape(np.copy(frame_v2.raw_data), (frame_v2.height, frame_v2.width, 4))
                        # frame_v3 = np.reshape(np.copy(frame_v3.raw_data), (frame_v3.height, frame_v3.width, 4))

                        depth_frame_v2 = gc_depth_queue_id[1].get()
                        depth_frame_v3 = gc_depth_queue_id[2].get()
                        # depth_frame = np.reshape(np.copy(depth_frame.raw_data), (depth_frame.height, depth_frame.width, 4))

                    else:
                        frame = np.zeros((600,800),np.int8)
                        depth_frame = np.zeros((600,800),np.int8)

                    # camera_transform = gc1_camera.get_transform()
                    # vehicle_transform = gc1_vehicle.get_transform()
                    # camera_to_world = camera_transform.get_matrix()
                    # world_to_vehicle = vehicle_transform.get_inverse_matrix()

                    # print("transform :")
                    # print("camera_transform : ",camera_transform)
                    # print("vehicle_transform : ",vehicle_transform)
                    # print("camera_to_world : ",camera_to_world)
                    # print("world_to_vehicle : ",world_to_vehicle)

                    frame_v2,detect_info_v2=self.detection.make_box(frame_v2, depth_frame_v2,gc_camera[1].get_transform())
                    frame_v3,detect_info_v3=self.detection.make_box(frame_v3, depth_frame_v3,gc_camera[2].get_transform())

                    match_results2 = self.cs_car2.matching(detected_info=detect_info_v2,other_car = [location_car1,location_car3])
                    # # print("seperate!!!")
                    match_results3 = self.cs_car3.matching(detected_info=detect_info_v3,other_car = [location_car1,location_car2])

                    combined_frame = np.hstack((frame_v3, frame_v2))
                    # cv2.imshow('streaming car %d' % 2,frame_v2)
                    # cv2.imshow('streaming car %d' % 3,frame_v3)


                    cv2.imshow('streaming car',combined_frame)
                    del combined_frame
                    del frame_v2
                    del frame_v3
                    # cv2.imshow('streaming car %d depth' % self.streaming_id,depth_frame[:,:,:3])
                    
                else:
                    frame_car1 = gc_queue_id[0].get()
                    frame_car1 = np.reshape(np.copy(frame_car1.raw_data), (frame_car1.height, frame_car1.width, 4))

                    frame_car2 = gc_queue_id[1].get()
                    frame_car2 = np.reshape(np.copy(frame_car2.raw_data), (frame_car2.height, frame_car2.width, 4))

                    frame_car3 = gc_queue_id[2].get()
                    frame_car3 = np.reshape(np.copy(frame_car3.raw_data), (frame_car3.height, frame_car3.width, 4))

                    cv2.imshow('streaming car 1' ,frame_car1)
                    cv2.imshow('streaming car 2' ,frame_car2)
                    cv2.imshow('streaming car 3' ,frame_car3)
                    
                
                if self.spectator_view:
                    transform = carla.Transform(gc2_vehicle.get_transform().transform(carla.Location(x=0,z=20)), carla.Rotation(yaw=0, pitch=-90,roll=90)) 
                    spectator.set_transform(transform) 
                # print('moved vehicle1 to 1',gcar_loc_xy)
                if self.show_map:
                    gcar_loc_xy.append([location_car1.x,location_car1.y])
                    gcar_loc_xy.append([location_car2.x,location_car2.y])
                    gcar_loc_xy.append([location_car3.x,location_car3.y])
                    
                    map_img = self.map_vi.draw_map(world,gcar_loc_xy)
                    cv2.imshow("CARLA Town06 Map", map_img)

                if self.show_graph:
                    # self.cs_car3.own_info+[[location_car3.x,location_car3.y]]+match_results
                    # print(self.cs_car3.own_info+[[location_car3.x,location_car3.y]]+match_results)
                    self.sg.generate_graph([self.cs_car3.own_info+[[location_car3.x,location_car3.y]]]+match_results3+match_results2)
                # print('moved vehicle1 to %s' % location_car1)
                # print('moved vehicle2 to %s' % location_car2)
                # print('moved vehicle3 to %s' % location_car3)
               
                ## CV2
                if cv2.waitKey(1) == ord('q'):
                    cv2.destroyAllWindows()

                    break
                
                # gc.collect()


        except RuntimeError as e:
            print(f"RuntimeError: {e}")

        finally:
            print('destroying actors')
            client.apply_batch([carla.command.DestroyActor(x) for x in self.gc1.action_list])
            client.apply_batch([carla.command.DestroyActor(x) for x in self.gc2.action_list])
            client.apply_batch([carla.command.DestroyActor(x) for x in self.gc3.action_list])




if __name__== "__main__" :
    ex = Expansion(
        multi_streaming = False,
        autopilot_option = False,
        show_map = False,
        show_graph = True,
        spectator_view = True,
        streaming_id = 2
    )