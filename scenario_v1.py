#public module
import carla
import numpy as np
import cv2

#custom module
from car_sim.car_generator import GenerateCar
from detection.object_detection import yolov8_detection
from utils.hdmap import map_express
from utils.semanticprocessing import CAR_SIP as cs

class Expansion():
    def __init__(
        self,
        multi_streaming = False,
        autopilot_option = False,
        show_map = True,
        streaming_id = 1
    ):  
        self.multi_streaming = multi_streaming
        self.show_map = show_map
        self.streaming_id = streaming_id

        self.gc1 = GenerateCar(
            model = 'vehicle.lincoln.mkz_2020',
            init_local = [-48.88, 11.74, -0.04660],
            camera_position = [0,0,2],
            sync = False,
            autopilot = autopilot_option#True
            )
        #semantic 1
        self.cs_car1 = cs(vehicle_semantic_name = "vehicle1",
                showthetosm = True)
        self.gc2 = GenerateCar(
            model = 'vehicle.tesla.model3',
            init_local = [-44.88, 5.74, -0.04660],
            camera_position = [0,0,2],
            sync = False,
            autopilot = autopilot_option#True
            )
        self.cs_car2 = cs(vehicle_semantic_name = "vehicle2",
                showthetosm = True)
        self.gc3 = GenerateCar(
            model = 'vehicle.bmw.grandtourer',
            init_local = [-41.88, -0.74, -0.04660],
            camera_position = [0,0,2],
            sync = False,
            autopilot = autopilot_option#True
            )
        
        self.cs_car3 = cs(vehicle_semantic_name = "vehicle3",
                showthetosm = True)
        # object detection
        self.detection = yolov8_detection()

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
            world  = client.get_world()

            gc1_vehicle, gc1_camera, gc1_depth_camera = self.gc1.setting(self.gc1.model,self.gc1.init_local,world)
            gc2_vehicle, gc2_camera, gc2_depth_camera = self.gc2.setting(self.gc2.model,self.gc2.init_local,world)
            gc3_vehicle, gc3_camera, gc3_depth_camera = self.gc3.setting(self.gc3.model,self.gc3.init_local,world)

            print(">>generate the vehicles...")


            gc1_image_queue,gc2_image_queue, gc3_image_queue= list(),list(),list()
            # 0 : RGB, 1 : depth
            gc1_image_queue=self.gc1.streaming_set(gc1_camera,gc1_depth_camera)
            gc2_image_queue=self.gc2.streaming_set(gc2_camera,gc2_depth_camera)
            gc3_image_queue=self.gc3.streaming_set(gc3_camera,gc3_depth_camera)


            gc_queue_id = [gc1_image_queue,gc2_image_queue,gc3_image_queue]
            while True:
                gcar_loc_xy = []
                world.tick()

                if not self.multi_streaming:
                    if self.streaming_id<4:
                        frame = gc_queue_id[self.streaming_id-1][0].get()
                        frame = np.reshape(np.copy(frame.raw_data), (frame.height, frame.width, 4))

                        #depth process
                        depth = gc_queue_id[self.streaming_id-1][1].get()
                        depth = np.reshape(np.copy(depth.raw_data), (depth.height, depth.width,4))
                        

                    else:
                        frame = np.zeros((600,800),np.int8)
                        depth = np.zeros((600,800),np.int8)

                    #object detection parts
                    frame=self.detection.make_box(frame,depth)
                    cv2.imshow('streaming car %d' % self.streaming_id,frame)
                    cv2.imshow('streaming car d %d' % self.streaming_id,depth)
                    
                else:
                    frame_car1 = gc_queue_id[0][0].get()
                    frame_car1 = np.reshape(np.copy(frame_car1.raw_data), (frame_car1.height, frame_car1.width, 4))

                    frame_car2 = gc_queue_id[1][0].get()
                    frame_car2 = np.reshape(np.copy(frame_car2.raw_data), (frame_car2.height, frame_car2.width, 4))

                    frame_car3 = gc_queue_id[2][0].get()
                    frame_car3 = np.reshape(np.copy(frame_car3.raw_data), (frame_car3.height, frame_car3.width, 4))

                    cv2.imshow('streaming car 1' ,frame_car1)
                    cv2.imshow('streaming car 2' ,frame_car2)
                    cv2.imshow('streaming car 3' ,frame_car3)
                    
                location_car1 = gc1_vehicle.get_location()

                location_car2 = gc2_vehicle.get_location()

                location_car3 = gc3_vehicle.get_location()

                # print('moved vehicle1 to 1',gcar_loc_xy)
                if self.show_map:
                    gcar_loc_xy.append([location_car1.x,location_car1.y])
                    gcar_loc_xy.append([location_car2.x,location_car2.y])
                    gcar_loc_xy.append([location_car3.x,location_car3.y])
                    
                    map_img = self.map_vi.draw_map(world,gcar_loc_xy)
                    cv2.imshow("CARLA Town01 Map", map_img)

                print('moved vehicle1 to %s' % location_car1)
                print('moved vehicle2 to %s' % location_car2)
                print('moved vehicle3 to %s' % location_car3)

                ## CV2
                if cv2.waitKey(1) == ord('q'):
                    break
            cv2.destroyAllWindows()

        except RuntimeError as e:
            print(f"RuntimeError: {e}")

        except Exception as e:
            print(f"Exception: {e}")

        finally:    
            print('destroying actors')
            cv2.destroyAllWindows()

            # client.apply_batch([carla.command.DestroyActor(x) for x in self.gc1.action_list])
            # client.apply_batch([carla.command.DestroyActor(x) for x in self.gc2.action_list])
            # client.apply_batch([carla.command.DestroyActor(x) for x in self.gc3.action_list])

            self.gc1.destroy()
            self.gc2.destroy()
            self.gc3.destroy()

            print('Actors cleaned up.')
if __name__== "__main__" :
    ex = Expansion(
        multi_streaming = False,
        autopilot_option = False,
        show_map = False,
        streaming_id = 3
    )