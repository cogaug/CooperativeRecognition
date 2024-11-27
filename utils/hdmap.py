import numpy as np
import cv2

# show the map
class map_express(object):
    def __init__(
        self,
        model=[]
    ):
        self.window_size = 500 
        self.lw = max(round(sum((self.window_size,self.window_size,1)) / 2 * 0.003), 2) 
        self.tf = max(   self.lw - 1, 1) 
        self.txt_color=(0, 0, 0)

        self.vehicle_color = [(255, 0, 0),(0, 255, 0),(0, 0, 255),(0, 255, 255),(255, 0, 255)]
        self.model_list = model
        # print(self.model_list)
    def draw_map(self, world,gc_position):

        map = world.get_map()
        waypoints = map.generate_waypoints(1.0)  


        x_vals = [wp.transform.location.x for wp in waypoints]
        y_vals = [wp.transform.location.y for wp in waypoints]

        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)

        x_range = x_max - x_min
        y_range = y_max - y_min
        scale_x = (self.window_size - 20) / x_range  
        scale_y = (self.window_size - 20) / y_range
        scale = min(scale_x, scale_y) 

        img = np.ones((self.window_size, self.window_size, 3), dtype=np.uint8) * 255

        for x, y in zip(x_vals, y_vals):

            px = int((x_max - x) * scale + 10) 
            py = int((y_max-y) * scale + 10) 
 
            cv2.circle(img, (px, py), 1, (0, 0, 255), -1)

        for i,pose in enumerate(gc_position):
            px_origin = int((x_max - pose[0]) * scale + 10)
            py_origin = int((y_max-pose[1]) * scale + 10)

            outside = py_origin- self.window_size >= 3
            label = '%d: %s' % (i+1, self.model_list[i].split('.')[2])
            print("vehicle label:",label)

            cv2.circle(img, (px_origin, py_origin), 5, self.vehicle_color[i], -1)
            cv2.putText(img,
                        label, 
                        (px_origin + 2, py_origin + 2),
                        2,
                        self.lw / 5,
                        self.txt_color,
                        thickness=self.tf,
                        lineType=cv2.LINE_AA)
        return img
        # cv2.imshow("CARLA Town01 Map", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

# def main():
#     client = carla.Client('localhost', 2000)
#     client.set_timeout(10.0)

#     world = client.get_world()

#     # 맵 그리기 함수 호출
#     draw_map(world)

# if __name__ == '__main__':
#     main()
