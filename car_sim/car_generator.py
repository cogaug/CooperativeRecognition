import carla
import numpy as np
import queue
import random as rd
# import time

class GenerateCar(object):
    def __init__(
        self,
        model = 'vehicle.lincoln.mkz_2020',
        init_local = [-48.88, 12.74, -0.04660],
        camera_position = [0,0,2],
        sync = False,
        autopilot = False,
        isCamera  = True

    ):  
        self.action_list = []

        self.model = model
        self.init_local = init_local
        self.sync = sync
        self.autopilot = autopilot        
        self.isCamera = isCamera        
        # self.temp_test()

        self.camera_position=camera_position
        
        # camera attribute
        self.image_w = None
        self.image_h = None
        self.image_fov = None
        self.K = None
        self.K_b = None

    def vehicle_for_detect(self,model,init_local, world):
        bp_lib = world.get_blueprint_library()

        vehicle_bp = bp_lib.find(model)

        transform = world.get_map().get_spawn_points()[0]
        print("transform 1: ", transform)
        transform.location.x += init_local[0]-586.805603
        transform.location.y += init_local[1]+10.063208
        transform.location.z += init_local[2]
        transform.rotation.yaw += init_local[3] # default 0
        print("transform 2: ", transform)
        vehicle = world.try_spawn_actor(vehicle_bp, transform)
        bounding_box = vehicle.bounding_box
        self.action_list.append(vehicle)
        print('created side car')

        print('created %s' % vehicle.type_id)
        # print(bounding_box.extent.x)
        # print(bounding_box.extent.y)
        # print(bounding_box.extent.z)
        vehicle.set_autopilot(self.autopilot)
        
        return vehicle, bounding_box

    def setting(self,model,init_local, world):

        bp_lib = world.get_blueprint_library()

        vehicle_bp = bp_lib.find(model)

      

        # transform = carla.Transform(
        #         carla.Location(x=init_local[0], y=init_local[1], z=init_local[2]), 
        #         carla.Rotation(yaw=init_local[3]))

        transform = world.get_map().get_spawn_points()[0]
        print("transform 1: ", transform)
        transform.location.x += init_local[0]-586.805603
        transform.location.y += init_local[1]+10.063208
        transform.location.z += init_local[2]
        transform.rotation.yaw += init_local[3] # default 0
        print("transform 2: ", transform)
        vehicle = world.try_spawn_actor(vehicle_bp, transform)
        bounding_box = vehicle.bounding_box
        print("bounding_box : ",bounding_box)
        # print("bounding_box extent: ",bounding_box.extent)
        self.action_list.append(vehicle)
        print('created %s' % vehicle.type_id)
        # print(bounding_box.extent.x)
        # print(bounding_box.extent.y)
        # print(bounding_box.extent.z)
        vehicle.set_autopilot(self.autopilot)

        camera, depth_camera=self.camera_setting(bp_lib,vehicle,world)

        self.action_list.append(camera)
        self.action_list.append(depth_camera)
        
        ## walker add 




        return vehicle,camera, depth_camera, bounding_box

    # walker setting
    def walker_setting(self,world,num_walker_pose,iswalk=False):
        bp_lib = world.get_blueprint_library()
        for pose in num_walker_pose:
            # walker_spawn_point = carla.Transform(carla.Location(x=-106.52, y=28.2, z=1.0), carla.Rotation())
            walker_spawn_point = carla.Transform(
                carla.Location(x=pose[0], y=pose[1], z=1.0), carla.Rotation(yaw=pose[2]))
            walker_bp = bp_lib.filter('walker.pedestrian.000*')[rd.randrange(1,5)] 
        
            walker = world.spawn_actor(walker_bp, walker_spawn_point)
            bounding_box = walker.bounding_box

            if iswalk:
                walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
                controller = world.spawn_actor(walker_controller_bp, carla.Transform(), walker)
                dest_location = carla.Location(x=pose[0]-100, y=pose[1], z=0.5)

                controller.start()

                controller.go_to_location(dest_location)
                controller.set_max_speed(1.3)

            self.action_list.append(walker)

        return walker, bounding_box
            

    # def walker_walking(self, world,walker_list):
    #         bp_lib = world.get_blueprint_library()
    #         walker_controller_bp = bp_lib.find('controller.ai.walker')

    #         for walker in walker_list[:1]:
    #             walker_controller = world.spawn_actor(walker_controller_bp, walker.get_transform(), walker)

    #             # # # Walker 속도 설정 (느린 속도)
    #             walker_speed = 1.0  # 느린 속도로 걷기 (m/s)
    #             walker_controller.set_max_speed(walker_speed)

    #             walker_controller.start()
    #             target_location = walker.get_location()
    #             target_location.x += 10  
                
    #             if world.get_map().get_waypoint(target_location):
    #                 walker_controller.go_to_location(target_location)
    #             else:
    #                 print(f"Invalid target location for walker {walker.id}")

    #             print("check:",walker)

    #             # walker_controller.go_to_location(world.get_random_location_from_navigation())
    #         # walker_controller.set_max_speed(walker_speed)
        
    def walker_walking(self, world, walker_list):
        bp_lib = world.get_blueprint_library()
        walker_controller_bp = bp_lib.find('controller.ai.walker')
        for walker in walker_list:
            try:
                walker_controller = world.spawn_actor(walker_controller_bp, walker.get_transform(), walker)
                if walker_controller is None:
                    print(f"Controller not found for walker {walker.id}")
                    continue

                walker_controller.start()

                current_location = walker.get_location()
                waypoint = world.get_map().get_waypoint(current_location, project_to_road=True, lane_type=carla.LaneType.Any)
                print("waypoint : ",waypoint)
                if waypoint:
                    target_waypoint = waypoint.next(10.0)[0] 
                    target_location = target_waypoint.transform.location
                    walker_controller.go_to_location(target_location)

                else:
                    print(f"Invalid target location for walker {walker.id}")

            except Exception as e:
                print(f"Exception occurred: {e}")   
    # camera setting
    def camera_setting(self,bp_lib,vehicle,world):

        camera_bp = bp_lib.find('sensor.camera.rgb')
        camera_init_trans = carla.Transform(carla.Location(
            x=self.camera_position[0],
            y=self.camera_position[1],
            z=self.camera_position[2]
        ))

        camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=vehicle)

        depth_camera_bp = bp_lib.find('sensor.camera.depth')
        depth_camera_bp.set_attribute('sensor_tick', '0.05') 
        depth_camera = world.spawn_actor(depth_camera_bp, camera_init_trans, attach_to=vehicle)



        image_w = camera_bp.get_attribute("image_size_x").as_int()
        image_h = camera_bp.get_attribute("image_size_y").as_int()
        fov = camera_bp.get_attribute("fov").as_float()

        print('camera created %s' % camera.type_id)
        print('depth created %s' % depth_camera.type_id)

        # getting the camera matrix
        # Get the attributes from the camera
        self.image_w = camera_bp.get_attribute("image_size_x").as_int()
        self.image_h = camera_bp.get_attribute("image_size_y").as_int()
        self.image_fov = camera_bp.get_attribute("fov").as_float()

        self.K = self.build_projection_matrix(self.image_w, self.image_h, self.image_fov)
        self.K_b = self.build_projection_matrix(self.image_w, self.image_h, self.image_fov, is_behind_camera=True)


        return camera, depth_camera

    def streaming_set(self,camera, depth_camera):
        image_queue = queue.Queue()
        # camera.listen(image_queue.put)
        camera.listen(lambda image: self.rgb_camera_callback(image, image_queue))

        depth_queue = queue.Queue()
        # image.convert(carla.ColorConverter.LogarithmicDepth)
        depth_camera.listen(lambda depth: self.depth_camera_callback(depth, depth_queue))

        return image_queue, depth_queue
    def rgb_camera_callback(self,image,rgb_image_queue):
        # rgb_image_queue.put(np.reshape(np.copy(image.raw_data), (image.height, image.width, 4)))
        rgb_image_queue.put(np.reshape(image.raw_data, (image.height, image.width, 4)))

    def depth_camera_callback(self,depth, depth_image_queue):
        # image.convert(carla.ColorConverter.LogarithmicDepth)
        # depth_image_queue.put(np.reshape(np.copy(depth.raw_data), (depth.height, depth.width, 4)))
        depth_image_queue.put(np.reshape(depth.raw_data, (depth.height, depth.width, 4)))
    def build_projection_matrix(self,w, h, fov, is_behind_camera=False):
        focal = w / (2.0 * np.tan(fov * np.pi / 360.0))
        K = np.identity(3)

        if is_behind_camera:
            K[0, 0] = K[1, 1] = -focal
        else:
            K[0, 0] = K[1, 1] = focal

        K[0, 2] = w / 2.0
        K[1, 2] = h / 2.0

        return K

    # def temp_test(self):
    #     try:
    #         client = carla.Client('localhost', 2000)
    #         client.set_timeout(2.0)
    #         world  = client.get_world()
    #         self.setting(self.model,self.init_local, world)

    #         # while True:
    #         #     time.sleep(0.1)  
    #     finally:
    #         print('destroying actors')
    #         # camera.destroy()
    #         client.apply_batch([carla.command.DestroyActor(x) for x in self.action_list])
    #         print('done.')



# if __name__ == '__main__':
#     gc1 = GenerateCar(
#     model = 'vehicle.lincoln.mkz_2020',
#     init_local = [-48.88, 12.74, -0.04660],
#     sync = False,
#     autopilot = False
#     )

#     gc2 = GenerateCar(
#     model = 'vehicle.tesla.model3',
#     init_local = [-40.88, 15.74, -0.04660],
#     sync = False,
#     autopilot = True
#     )