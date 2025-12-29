cmake_minimum_required(VERSION 3.8)
project(republish_image)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(OpenCV REQUIRED)
find_package(yaml-cpp REQUIRED)

add_executable(fast_republish_yaml_node src/republish_image.cpp)
ament_target_dependencies(fast_republish_yaml_node rclcpp sensor_msgs)
target_link_libraries(fast_republish_yaml_node ${OpenCV_LIBS} yaml-cpp)

target_include_directories(fast_republish_yaml_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)

install(TARGETS fast_republish_yaml_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME})

ament_package()
