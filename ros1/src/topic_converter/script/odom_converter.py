import os
import sys
import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovariance
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped
from geometry_msgs.msg import TwistWithCovariance
from geometry_msgs.msg import TwistWithCovarianceStamped
from tools import TopicConverter

class OdomConverterNode:
    def __init__(self) -> None:
        self.__odom_topic = rospy.get_param('odom_topic','/zedx/zed_node/odom')
        self.__convert_topic_list = rospy.get_param('convert_topic_list',['Pose',
                                                                          'PoseStamped',
                                                                          'PoseWithCovariance',
                                                                          'PoseWithCovarianceStamped',
                                                                          'Twist',
                                                                          'TwistStamped',
                                                                          'TwistWithCovariance',
                                                                          'TwistWithCovarianceStamped'])
        self.__topic_table = {}
        self.__topic_table['Pose'] = Pose 
        self.__topic_table['PoseStamped'] = PoseStamped 
        self.__topic_table['PoseWithCovariance'] = PoseWithCovariance 
        self.__topic_table['PoseWithCovarianceStamped'] = PoseWithCovarianceStamped 
        self.__topic_table['Twist'] = Twist 
        self.__topic_table['TwistStamped'] = TwistStamped 
        self.__topic_table['TwistWithCovariance'] = TwistWithCovariance 
        self.__topic_table['TwistWithCovarianceStamped'] = TwistWithCovarianceStamped

        self.__publisher = {}
        self.__publisher['Pose'] = rospy.Publisher(self.__odom_topic+'/Pose',Pose, queue_size = 10)
        self.__publisher['PoseStamped'] = rospy.Publisher(self.__odom_topic+'/PoseStamped',PoseStamped, queue_size = 10)
        self.__publisher['PoseWithCovariance'] = rospy.Publisher(self.__odom_topic+'/PoseWithCovariance',PoseWithCovariance, queue_size = 10)
        self.__publisher['PoseWithCovarianceStamped'] = rospy.Publisher(self.__odom_topic+'/PoseWithCovarianceStamped',PoseWithCovarianceStamped, queue_size = 10)
        self.__publisher['Twist'] = rospy.Publisher(self.__odom_topic+'/Twist',Twist, queue_size = 10)
        self.__publisher['TwistStamped'] = rospy.Publisher(self.__odom_topic+'/TwistStamped',TwistStamped, queue_size = 10)
        self.__publisher['TwistWithCovariance'] = rospy.Publisher(self.__odom_topic+'/TwistWithCovariance',TwistWithCovariance, queue_size = 10)
        self.__publisher['TwistWithCovarianceStamped'] = rospy.Publisher(self.__odom_topic+'/TwistWithCovarianceStamped',TwistWithCovarianceStamped, queue_size = 10)

        self.__sub = rospy.Subscriber(self.__odom_topic,Odometry,self.__callback)
        self.__converter = TopicConverter.Odom()

    def __callback(self,msgs):
        for topic in self.__convert_topic_list:
            converted_msg = self.__converter.covert(self.__topic_table[topic],msgs)
            self.__publisher[topic].publish(converted_msg)

if __name__ == '__main__':
    rospy.init_node('odom_converter')
    node = OdomConverterNode()
    rospy.spin()