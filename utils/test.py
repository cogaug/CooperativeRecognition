import numpy as np
from math import cos, sin, radians
# target car GT = (x=-109.524841, y=30.211012, z=0.001674)


width = 800
height = 600
fov = 90

fx = (width/2) / np.tan(np.deg2rad(fov /2 ))
fy = fx#*height/width

cx = width /2  
cy = height /2

k = np.array([
[fx, 0, cx],
[0, fy, cy],
[0,  0,  1]
])

print(k[0][0])

u_bbox = 618
v_bbox = 400

depth = 6.269
xc = (u_bbox - k[0][2])*depth / k[0][0]
yc = (v_bbox- k[1][2])*depth / k[1][1]
zc = depth

print("camera coodinate :", xc,yc,zc)

# R_map = np.array([
# [0,1,0],
# [0,0,-1],
# [1,0,0] 
# ])

R_map = np.array([
[0,0,1],
[1,0,0],
[0,-1,0] 
])
degree = 90
# theta = degree *(np.pi/180)
yaw = radians(degree)
cos = np.cos(yaw)
sin = np.sin(yaw)

R_head = np.array([
[cos, -sin,0],
[sin, cos,0],
[0,0,1] 
])
print("R_head : ",R_head)
R_t =R_head @ R_map
print("R_t : ",R_t)



camera_coords = np.array([xc, yc, zc]).reshape((3, 1))

camera_world_coords = R_t@camera_coords
print(camera_world_coords)

T = np.array([[-106.524780], [23.730978], [1.9994]])
print("T : ",T)

vehicle_coord =camera_world_coords + T

print(vehicle_coord)