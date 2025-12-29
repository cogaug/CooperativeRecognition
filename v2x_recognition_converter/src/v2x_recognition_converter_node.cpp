#include <rclcpp/rclcpp.hpp>

#include <autoware_perception_msgs/msg/detected_objects.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>
#include <geometry_msgs/msg/quaternion_stamped.hpp>

#include <v2x_intf_msg/msg/recognition.hpp>
#include <v2x_intf_msg/msg/object.hpp>

#include <tf2/utils.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

using autoware_perception_msgs::msg::DetectedObjects;

class ObjectConverterNode : public rclcpp::Node
{
public:
  ObjectConverterNode() : Node("v2x_object_converter")
  {
    vehicle_id_ = declare_parameter<int>("vehicle_id", 1);

    sub_objects_ = create_subscription<DetectedObjects>(
      "/detected_objects", 10,
      std::bind(&ObjectConverterNode::objectsCallback, this, std::placeholders::_1));

    sub_fix_ = create_subscription<sensor_msgs::msg::NavSatFix>(
      "/fix", 10,
      std::bind(&ObjectConverterNode::fixCallback, this, std::placeholders::_1));

    sub_heading_ =
      create_subscription<geometry_msgs::msg::QuaternionStamped>(
        "/heading", 10,
        std::bind(&ObjectConverterNode::headingCallback, this, std::placeholders::_1));

    pub_ = create_publisher<v2x_intf_msg::msg::Recognition>(
      "/v2x/recognition", 10);
  }

private:
  void fixCallback(const sensor_msgs::msg::NavSatFix::SharedPtr msg)
  {
    last_fix_ = msg;
  }

  void headingCallback(
    const geometry_msgs::msg::QuaternionStamped::SharedPtr msg)
  {
    last_heading_ = msg;
  }

  void objectsCallback(const DetectedObjects::SharedPtr msg)
  {
    if (!last_fix_ || !last_heading_)
    {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 2000,
        "Waiting for /fix and /heading");
      return;
    }

    RCLCPP_WARN_ONCE(
      get_logger(),
      "Get Object Information");

    v2x_intf_msg::msg::Recognition out;
    out.vehicle_id = vehicle_id_;

    /* ---------- vehicle time ---------- */
    auto t = msg->header.stamp;
    std::time_t tt = t.sec;
    tm tm{};
    gmtime_r(&tt, &tm);

    out.vehicle_time = {
      tm.tm_year + 1900,
      tm.tm_mon + 1,
      tm.tm_mday,
      tm.tm_hour,
      tm.tm_min,
      tm.tm_sec,
      static_cast<int32_t>(t.nanosec / 1000)
    };

    /* ---------- vehicle position ---------- */
    out.vehicle_position = {
      static_cast<float>(last_fix_->latitude),
      static_cast<float>(last_fix_->longitude)
    };

    /* ---------- ego heading ---------- */
    tf2::Quaternion q_ego;
    tf2::fromMsg(last_heading_->quaternion, q_ego);
    double ego_yaw = tf2::getYaw(q_ego);

    /* ---------- objects ---------- */
    for (const auto & obj : msg->objects)
    {
      if (out.object_data.size() >= 256) break;

      v2x_intf_msg::msg::Object o;

      /* detection time */
      o.detection_time = out.vehicle_time;

      /* relative position */
      const auto & p = obj.kinematics.pose_with_covariance.pose.position;
      o.object_position = {
        static_cast<float>(p.x),
        static_cast<float>(p.y)
      };

      /* velocity */
      const auto & v = obj.kinematics.twist_with_covariance.twist.linear;
      o.object_velocity = std::hypot(v.x, v.y);

      /* heading */
      tf2::Quaternion q_obj;
      tf2::fromMsg(
        obj.kinematics.pose_with_covariance.pose.orientation, q_obj);

      double rel_heading = tf2::getYaw(q_obj) - ego_yaw;
      if (rel_heading < 0) rel_heading += 2 * M_PI;

      o.object_heading = rel_heading * 180.0 / M_PI;

      /* classification */
      if (!obj.classification.empty())
      {
        o.object_class = obj.classification[0].label;
        o.recognition_accuracy =
          static_cast<int32_t>(obj.classification[0].probability * 100.0);
      }
      else
      {
        o.object_class = 0;
        o.recognition_accuracy = 0;
      }

      out.object_data.push_back(o);
    }

    pub_->publish(out);
  }

  int vehicle_id_;

  rclcpp::Subscription<DetectedObjects>::SharedPtr sub_objects_;
  rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr sub_fix_;
  rclcpp::Subscription<geometry_msgs::msg::QuaternionStamped>::SharedPtr sub_heading_;
  rclcpp::Publisher<v2x_intf_msg::msg::Recognition>::SharedPtr pub_;

  sensor_msgs::msg::NavSatFix::SharedPtr last_fix_;
  geometry_msgs::msg::QuaternionStamped::SharedPtr last_heading_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ObjectConverterNode>());
  rclcpp::shutdown();
  return 0;
}
