#!/usr/bin/python3

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovariance
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped
from geometry_msgs.msg import TwistWithCovariance
from geometry_msgs.msg import TwistWithCovarianceStamped

class TopicConverter:
    def __init__(self) -> None:
        pass

    class Odom:
        def __init__(self) -> None:
            self.__mapping_table = {}
            self.__mapping_table[Pose] = self.__toPose
            self.__mapping_table[PoseStamped] = self.__toPoseStamped
            self.__mapping_table[PoseWithCovariance] = self.__toPoseWithCovariance
            self.__mapping_table[PoseWithCovarianceStamped] = self.__toPoseWithCovarianceStamped
            self.__mapping_table[Twist] = self.__toTwist
            self.__mapping_table[TwistStamped] = self.__toTwistStamped
            self.__mapping_table[TwistWithCovariance] = self.__toTwistWithCovariance
            self.__mapping_table[TwistWithCovarianceStamped] = self.__toTwistWithCovarianceStamped
        
        def covert(self,type,odom):
            return self.__mapping_table[type](odom)

        def __toPose(self,odom):
            pose = Pose()
            pose = odom.pose.pose
            return pose

        def __toPoseStamped(self,odom):
            pose = PoseStamped()
            pose.header = odom.header
            pose.pose = odom.pose.pose
            return pose

        def __toPoseWithCovariance(self,odom):
            pose = PoseWithCovariance()
            pose.pose = odom.pose
            return pose

        def __toPoseWithCovarianceStamped(self,odom):
            pose = PoseWithCovarianceStamped()
            pose.header = odom.header
            pose.pose = odom.pose
            return pose

        def __toTwist(self,odom):
            twist = Twist()
            twist = odom.twist.twist
            return twist

        def __toTwistStamped(self,odom):
            twist = TwistStamped()
            twist.header = odom.header
            twist.twist = odom.twist.twist
            return twist

        def __toTwistWithCovariance(self,odom):
            twist = TwistWithCovariance()
            twist.twist = odom.twist
            return twist

        def __toTwistWithCovarianceStamped(self,odom):
            twist = TwistWithCovarianceStamped()
            twist.header = odom.header
            twist.twist = odom.twist
            return twist

if __name__ == '__main__':
    a = TopicConverter.Odom()
    odom = Odometry()
    print('---------------------------------------------')
    print(a.covert(Pose,odom))
    print('---------------------------------------------')
    print(a.covert(PoseStamped,odom))
    print('---------------------------------------------')
    print(a.covert(PoseWithCovariance,odom))
    print('---------------------------------------------')
    print(a.covert(PoseWithCovarianceStamped,odom))
    print('---------------------------------------------')
    print(a.covert(Twist,odom))
    print('---------------------------------------------')
    print(a.covert(TwistStamped,odom))
    print('---------------------------------------------')
    print(a.covert(TwistWithCovariance,odom))
    print('---------------------------------------------')
    print(a.covert(TwistWithCovarianceStamped,odom))
    print('---------------------------------------------')
