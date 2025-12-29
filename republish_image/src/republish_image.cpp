#include <rclcpp/rclcpp.hpp>
#include <rclcpp/qos.hpp>
#include <sensor_msgs/msg/compressed_image.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

#include <yaml-cpp/yaml.h>
#include <optional>
#include <string>
#include <mutex>

using rclcpp::SensorDataQoS;

class FastRepublishYamlNode : public rclcpp::Node {
public:
  FastRepublishYamlNode(const rclcpp::NodeOptions & opts)
  : Node("fast_republish_yaml_node", opts)
  {
    // ---- Parameters
    in_image_compressed_ = declare_parameter<std::string>("in_image_compressed", "/camera_fl/image_raw/compressed");
    out_image_raw_       = declare_parameter<std::string>("out_image_raw",       "/left/image_raw");
    out_camera_info_     = declare_parameter<std::string>("out_camera_info",     "/left/camera_info");
    resize_width_        = declare_parameter<int>("resize_width", 0);
    resize_height_       = declare_parameter<int>("resize_height", 0);

    yaml_path_           = declare_parameter<std::string>("yaml_path", "/path/to/cameras.yaml");
    yaml_camera_key_     = declare_parameter<std::string>("yaml_camera_key", "LeftFront"); // 예: LeftFront, RightFront, MiddleLeft ...

    // frame_id 강제 지정(빈 문자열이면 이미지 헤더 frame_id 사용)
    frame_id_override_   = declare_parameter<std::string>("frame_id_override", "");

    RCLCPP_INFO(get_logger(),
      "Republish (YAML):\n  %s -> %s\n  CameraInfo -> %s (from %s:%s)\n  resize=%dx%d, frame_id_override='%s'",
      in_image_compressed_.c_str(), out_image_raw_.c_str(),
      out_camera_info_.c_str(), yaml_path_.c_str(), yaml_camera_key_.c_str(),
      resize_width_, resize_height_, frame_id_override_.c_str());

    // ---- Load YAML → CameraInfo prototype
    if (!loadYamlCameraInfo(yaml_path_, yaml_camera_key_, proto_info_)) {
      RCLCPP_FATAL(get_logger(), "Failed to load CameraInfo from YAML: %s (key=%s)",
                   yaml_path_.c_str(), yaml_camera_key_.c_str());
      throw std::runtime_error("YAML load failed");
    }

    auto sub_qos = SensorDataQoS(); // BestEffort/Volatile/저지연
    auto pub_qos = rclcpp::QoS(rclcpp::KeepLast(10));
    pub_qos.best_effort();
    pub_qos.durability_volatile();

    pub_image_ = create_publisher<sensor_msgs::msg::Image>(out_image_raw_, pub_qos);
    pub_info_  = create_publisher<sensor_msgs::msg::CameraInfo>(out_camera_info_, pub_qos);

    sub_image_ = create_subscription<sensor_msgs::msg::CompressedImage>(
      in_image_compressed_, sub_qos,
      std::bind(&FastRepublishYamlNode::onCompressedImage, this, std::placeholders::_1));
  }

private:
  // YAML → proto CameraInfo
  bool loadYamlCameraInfo(const std::string& path,
                          const std::string& cam_key,
                          sensor_msgs::msg::CameraInfo& out)
  {
    YAML::Node root = YAML::LoadFile(path);
    if (!root["cameras"]) {
      RCLCPP_ERROR(get_logger(), "YAML: 'cameras' root key not found.");
      return false;
    }
    YAML::Node cam = root["cameras"][cam_key];
    if (!cam) {
      RCLCPP_ERROR(get_logger(), "YAML: camera key '%s' not found under 'cameras'.", cam_key.c_str());
      return false;
    }

    auto intr = cam["intrinsic"];
    auto dist = cam["distortion"];
    if (!intr || !dist) {
      RCLCPP_ERROR(get_logger(), "YAML: missing 'intrinsic' or 'distortion' under '%s'.", cam_key.c_str());
      return false;
    }

    double fx = intr["fx"].as<double>();
    double fy = intr["fy"].as<double>();
    double cx = intr["cx"].as<double>();
    double cy = intr["cy"].as<double>();

    double k1 = dist["k1"] ? dist["k1"].as<double>() : 0.0;
    double k2 = dist["k2"] ? dist["k2"].as<double>() : 0.0;
    double p1 = dist["p1"] ? dist["p1"].as<double>() : 0.0;
    double p2 = dist["p2"] ? dist["p2"].as<double>() : 0.0;

    out = sensor_msgs::msg::CameraInfo();
    out.distortion_model = "plumb_bob";
    out.d = {k1, k2, p1, p2, 0.0};

    // K
    out.k = {fx, 0.0, cx,
             0.0, fy, cy,
             0.0, 0.0, 1.0};

    // R = identity
    out.r = {1.0, 0.0, 0.0,
             0.0, 1.0, 0.0,
             0.0, 0.0, 1.0};

    
    // P (Tx=0)
    double Tx = 0.0;

    out.p = {fx, 0.0, cx, Tx,
             0.0, fy, cy, 0.0,
             0.0, 0.0, 1.0, 0.0};

    if (cam["width"])  out.width  = cam["width"].as<int>();
    if (cam["height"]) out.height = cam["height"].as<int>();

    out.header.frame_id = cam_key;

    return true;
  }

  void scaleIntrinsics(sensor_msgs::msg::CameraInfo& info, int out_w, int out_h)
  {
    if (out_w <= 0 || out_h <= 0) return;

    if (info.width == 0 || info.height == 0) {
      info.width = out_w;
      info.height = out_h;
      return;
    }
    const double sx = out_w / static_cast<double>(info.width);
    const double sy = out_h / static_cast<double>(info.height);

    auto & K = info.k; // [fx,0,cx, 0,fy,cy, 0,0,1]
    auto & P = info.p; // [fx,0,cx,0, 0,fy,cy,0, 0,0,1,0]

    K[0] *= sx;  K[2] *= sx;
    K[4] *= sy;  K[5] *= sy;

    P[0] *= sx;  P[2] *= sx;
    P[5] *= sy;  P[6] *= sy;

    info.width  = out_w;
    info.height = out_h;
  }

  void onCompressedImage(const sensor_msgs::msg::CompressedImage::SharedPtr msg)
  {

    cv::Mat buf(1, static_cast<int>(msg->data.size()), CV_8UC1,
                const_cast<uint8_t*>(msg->data.data()));
    cv::Mat bgr = cv::imdecode(buf, cv::IMREAD_COLOR);
    if (bgr.empty()) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "imdecode failed.");
      return;
    }

    int out_w = bgr.cols;
    int out_h = bgr.rows;
    if (resize_width_ > 0 && resize_height_ > 0 &&
        (resize_width_ != out_w || resize_height_ != out_h))
    {
      cv::Mat tmp;
      cv::resize(bgr, tmp, cv::Size(resize_width_, resize_height_), 0, 0, cv::INTER_LINEAR);
      bgr = std::move(tmp);
      out_w = bgr.cols;
      out_h = bgr.rows;
    }

    sensor_msgs::msg::Image out_img;
    out_img.header = msg->header;
    const auto now = msg->header.stamp;
    out_img.header.stamp = now;
      
    if (!frame_id_override_.empty())
      out_img.header.frame_id = frame_id_override_;
    else if (out_img.header.frame_id.empty())
      out_img.header.frame_id = "camera_frame";
      
    out_img.height   = static_cast<uint32_t>(out_h);
    out_img.width    = static_cast<uint32_t>(out_w);
    out_img.encoding = "bgr8";
    out_img.is_bigendian = false;
    out_img.step = static_cast<uint32_t>(out_w * 3);
    out_img.data.assign(bgr.data, bgr.data + (out_img.step * out_img.height));
      
    pub_image_->publish(out_img);
      
    sensor_msgs::msg::CameraInfo info = proto_info_;
    scaleIntrinsics(info, out_w, out_h);
    info.header.frame_id = out_img.header.frame_id;
    info.header.stamp    = now; 
      
    pub_info_->publish(info);
  }

  // Params
  std::string in_image_compressed_;
  std::string out_image_raw_;
  std::string out_camera_info_;
  int resize_width_{0}, resize_height_{0};

  std::string yaml_path_;
  std::string yaml_camera_key_;
  std::string frame_id_override_;

  // Publishers/Subscribers
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_image_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr pub_info_;
  rclcpp::Subscription<sensor_msgs::msg::CompressedImage>::SharedPtr sub_image_;

  // YAML prototype
  sensor_msgs::msg::CameraInfo proto_info_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::executors::MultiThreadedExecutor exec;
  auto node = std::make_shared<FastRepublishYamlNode>(rclcpp::NodeOptions{});
  exec.add_node(node);
  exec.spin();
  rclcpp::shutdown();
  return 0;
}
