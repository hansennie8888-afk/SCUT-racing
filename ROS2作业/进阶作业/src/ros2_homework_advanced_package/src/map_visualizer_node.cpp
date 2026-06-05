#include "rclcpp/rclcpp.hpp"
#include "fsd_common_msgs/msg/map.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"

#include <functional>
#include <memory>
#include <string>

class MapVisualizerNode : public rclcpp::Node
{
public:
    MapVisualizerNode() : Node("map_visualizer_node")
    {
        this->declare_parameter<double>("marker_scale", 0.35);
        marker_scale_ = this->get_parameter("marker_scale").as_double();

        marker_pub_ = this->create_publisher<visualization_msgs::msg::MarkerArray>(
            "/cone_markers", 10);

        map_sub_ = this->create_subscription<fsd_common_msgs::msg::Map>(
            "/estimation/slam/map", 10,
            std::bind(&MapVisualizerNode::map_callback, this, std::placeholders::_1));

        RCLCPP_INFO(this->get_logger(), "map_visualizer_node started");
    }

private:
    double marker_scale_;

    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;
    rclcpp::Subscription<fsd_common_msgs::msg::Map>::SharedPtr map_sub_;

    void map_callback(const fsd_common_msgs::msg::Map::SharedPtr msg)
    {
        visualization_msgs::msg::MarkerArray marker_array;

        // 先清除旧 marker，避免 RViz 中残留上一次发布的锥桶。
        visualization_msgs::msg::Marker clear_marker;
        clear_marker.header = msg->header;
        if (clear_marker.header.frame_id.empty())
        {
            clear_marker.header.frame_id = "world";
        }
        clear_marker.action = visualization_msgs::msg::Marker::DELETEALL;
        marker_array.markers.push_back(clear_marker);

        int marker_id = 0;

        auto add_cones = [&](const auto &cones,
                             const std::string &ns,
                             float r, float g, float b)
        {
            for (const auto &cone : cones)
            {
                visualization_msgs::msg::Marker marker;
                marker.header = msg->header;
                if (marker.header.frame_id.empty())
                {
                    marker.header.frame_id = "world";
                }
                marker.header.stamp = this->now();

                marker.ns = ns;
                marker.id = marker_id++;
                marker.type = visualization_msgs::msg::Marker::SPHERE;
                marker.action = visualization_msgs::msg::Marker::ADD;

                marker.pose.position = cone.position;
                marker.pose.orientation.w = 1.0;

                marker.scale.x = marker_scale_;
                marker.scale.y = marker_scale_;
                marker.scale.z = marker_scale_;

                marker.color.r = r;
                marker.color.g = g;
                marker.color.b = b;
                marker.color.a = 1.0;

                marker_array.markers.push_back(marker);
            }
        };

        add_cones(msg->cone_yellow, "yellow_cones", 1.0f, 0.85f, 0.0f);
        add_cones(msg->cone_blue, "blue_cones", 0.0f, 0.25f, 1.0f);
        add_cones(msg->cone_red, "red_cones", 1.0f, 0.0f, 0.0f);
        add_cones(msg->cone_unknown, "unknown_cones", 0.6f, 0.6f, 0.6f);

        marker_pub_->publish(marker_array);
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<MapVisualizerNode>();
    rclcpp::spin(node);

    rclcpp::shutdown();
    return 0;
}
