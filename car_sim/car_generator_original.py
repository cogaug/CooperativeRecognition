import carla
import numpy as np
import queue
# import time

class GenerateCar(object):
    def __init__(
        self,
        model = 'vehicle.lincoln.mkz_2020',
        init_local = [-48.88, 12.74, -0.04660],
        camera_position = [0,0,2],
        sync = False,
        autopilot = False
    ):  
        self.action_list = []

        self.model = model
        self.init_local = init_local
        self.sync = sync
        self.autopilot = autopilot        
        # self.temp_test()

        self.camera_position=camera_position
        
        # camera attribute
        self.image_w = None
        self.image_h = None
        self.image_fov = None
        self.K = None
        self.K_b = None

    def setting(self,model,init_local, world):

        bp_lib = world.get_blueprint_library()

        vehicle_bp = bp_lib.find(model)

        transform = world.get_map().get_spawn_points()[0]
        # print("transform : ", transform)
        transform.location.x += init_local[0]
        transform.location.y += init_local[1]
        transform.location.z += init_local[2]
        transform.rotation.yaw += 90

        vehicle = world.try_spawn_actor(vehicle_bp, transform)
        self.action_list.append(vehicle)
        print('created %s' % vehicle.type_id)
        
        vehicle.set_autopilot(self.autopilot)

        camera, depth_camera=self.camera_setting(bp_lib,vehicle,world)
        self.action_list.append(camera)
        self.action_list.append(depth_camera)

        return vehicle,camera,depth_camera

    # camera setting
    def camera_setting(self,bp_lib,vehicle,world):

        rgb_camera_bp = bp_lib.find('sensor.camera.rgb')
        # rgb_camera_bp.set_attribute('image_size_x', '800')
        # rgb_camera_bp.set_attribute('image_size_y', '600')
        # rgb_camera_bp.set_attribute('fov', '90')

        camera_init_trans = carla.Transform(carla.Location(
            x=self.camera_position[0],
            y=self.camera_position[1],
            z=self.camera_position[2]
        ))

        camera = world.spawn_actor(rgb_camera_bp, camera_init_trans, attach_to=vehicle)

        depth_camera_bp = bp_lib.find('sensor.camera.depth')
        # depth_camera_bp.set_attribute('image_size_x', '800')
        # depth_camera_bp.set_attribute('image_size_y', '600')
        # depth_camera_bp.set_attribute('fov', '90')

        depth_camera = world.spawn_actor(depth_camera_bp, camera_init_trans, attach_to=vehicle)


        image_w = rgb_camera_bp.get_attribute("image_size_x").as_int()
        image_h = rgb_camera_bp.get_attribute("image_size_y").as_int()
        fov = rgb_camera_bp.get_attribute("fov").as_float()

        print('created %s' % camera.type_id)
        print('created %s' % depth_camera.type_id)
        print('-*'*10)

        # getting the camera matrix
        # Get the attributes from the camera
        self.image_w = rgb_camera_bp.get_attribute("image_size_x").as_int()
        self.image_h = rgb_camera_bp.get_attribute("image_size_y").as_int()
        self.image_fov = rgb_camera_bp.get_attribute("fov").as_float()

        self.K = self.build_projection_matrix(self.image_w, self.image_h, self.image_fov)
        self.K_b = self.build_projection_matrix(self.image_w, self.image_h, self.image_fov, is_behind_camera=True)


        return camera, depth_camera

    def streaming_set(self,camera,depth_cam):
        self.image_queue = queue.Queue(maxsize=10)
        camera.listen(self.image_queue.put)

        self.image_depth_queue = queue.Queue(maxsize=10)
        depth_cam.listen(self.image_depth_queue.put)

        return [self.image_queue,self.image_depth_queue]

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

    def stop_listeners(self):
        if self.image_queue and self.camera:
            self.camera.stop()
        if self.image_depth_queue and self.depth_cam:
            self.depth_cam.stop()

    def destroy(self):
        print('Destroying actors')
        # self.stop_listeners()
        for actor in self.action_list:
            if actor is not None:
                actor.destroy()
        self.action_list = []
        print('All actors destroyed.')

    def __del__(self):
        self.destroy()

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