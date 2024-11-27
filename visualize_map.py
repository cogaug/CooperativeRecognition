import carla
import numpy as np
import cv2
import time
from utils.hdmap import map_express

class Show_the_map(object):
    def __init__(
    self,
    car_EA =3
    ):
        self.client = carla.Client('localhost', 2000)

        self.client.set_timeout(30.0)
        self.world = self.client.get_world()

        # print(len(self.world.get_actors().filter('vehicle.*')))
        if len(self.world.get_actors().filter('vehicle.*'))>=car_EA:
            self.vehicles = self.world.get_actors().filter('vehicle.*')
            self.vehicle_list = []
            for namei in self.vehicles:
                self.vehicle_list.append(namei.type_id)
            # print(self.vehicle_list)
            self.map_vi = map_express(self.vehicle_list)
            self.show_window()
        else:
            print("No show the map")
    def show_window(self):
        print("show window")

        try:
            while True:
                vehicle_locations = []
                for vehicle in self.vehicles:
                    transform = vehicle.get_transform()
                    location = transform.location
                    vehicle_locations.append((location.x, location.y))
                    map_img = self.map_vi.draw_map(self.world,vehicle_locations)
                cv2.imshow("CARLA Town01 Map", map_img)
                if cv2.waitKey(1) == ord('q'):
                    break   
        finally:
            cv2.destroyAllWindows()
if __name__== "__main__" :
    sm = Show_the_map(
        car_EA=3
    )