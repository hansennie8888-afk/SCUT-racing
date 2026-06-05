#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <memory>

class Figure8Node : public rclcpp::Node
{
public:
    Figure8Node() : Node("figure8_node")
    {
        // 先声明参数，如果 launch 没有加载 yaml，就使用这里的默认值。
        this->declare_parameter<double>("linear_speed", 1.5);
        this->declare_parameter<double>("angular_speed", 1.0);
        this->declare_parameter<double>("timer_period", 0.05);

        // 从参数服务器读取实际使用的速度和定时器周期。
        linear_speed_ = this->get_parameter("linear_speed").as_double();
        angular_speed_ = this->get_parameter("angular_speed").as_double();
        timer_period_ = this->get_parameter("timer_period").as_double();

        steps_per_circle_ = std::max(
            1, static_cast<int>(std::round(2.0 * M_PI / (std::abs(angular_speed_) * timer_period_))));
        angular_speed_ = 2.0 * M_PI / (steps_per_circle_ * timer_period_);

        // turtlesim 通过 /turtle1/cmd_vel 话题接收速度指令。
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>(
            "/turtle1/cmd_vel", 10);

        // 定时发布速度消息，让乌龟持续运动。
        timer_ = this->create_wall_timer(
            std::chrono::duration<double>(timer_period_),
            std::bind(&Figure8Node::publish_velocity, this));

        RCLCPP_INFO(this->get_logger(), "steps per circle: %d", steps_per_circle_);
    }

private:
    double linear_speed_;
    double angular_speed_;
    double timer_period_;
    int steps_per_circle_;
    int step_count_ = 0;

    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;

    void publish_velocity()
    {
        geometry_msgs::msg::Twist msg;

        msg.linear.x = linear_speed_;

        // 每个圆固定发布相同次数的速度命令，减少长时间运行后的角度累计误差。
        int phase = (step_count_ / steps_per_circle_) % 2;
        if (phase == 0)
        {
            msg.angular.z = angular_speed_;
        }
        else
        {
            msg.angular.z = -angular_speed_;
        }

        publisher_->publish(msg);

        step_count_++;
        if (step_count_ >= 2 * steps_per_circle_)
        {
            step_count_ = 0;
        }
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<Figure8Node>();
    rclcpp::spin(node);

    rclcpp::shutdown();
    return 0;
}
