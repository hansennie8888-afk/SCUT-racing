# ROS2基础作业

这次基础作业做的是让 turtlesim 里的小乌龟走一个 8 字形。我写了一个 C++ 节点，不断往 `/turtle1/cmd_vel` 发速度消息，再用 launch 文件把 turtlesim 和自己的节点一起启动。

环境：

Ubuntu 22.04

ROS2 Humble

## 文件

主要文件在下面几个位置：

```text
src/ros2_homework_basic_package/src/figure8_node.cpp
src/ros2_homework_basic_package/config/turtle_params.yaml
src/ros2_homework_basic_package/launch/turtle_figure8.launch.py
```

其中 `figure8_node.cpp` 是主要代码，`turtle_params.yaml` 放线速度、角速度和定时器周期，launch 文件负责一键启动。

## 运行

```bash
cd /data/projects/ROS2/ros2_homework_basic_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select ros2_homework_basic_package
source install/setup.bash
ros2 launch ros2_homework_basic_package turtle_figure8.launch.py
```

如果要看我发布的速度消息，可以另开终端：

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /turtle1/cmd_vel
```

## 思路

turtlesim 的控制话题是 `/turtle1/cmd_vel`，消息类型是 `geometry_msgs/msg/Twist`。这里主要用到了两个量：

`linear.x` 控制前进速度。

`angular.z` 控制转向。

如果线速度不变，角速度为正，小乌龟会往一个方向画圆；角速度改成负数，就会往反方向画圆。这里我没有直接用当前时间取余来切换方向，因为 timer 周期和一圈时间不一定刚好整除，跑久了可能会有一点角度误差。

```text
一圈时间 = 2 * pi / angular_speed
```

代码里先算出一圈大约需要多少次 timer 回调，然后让左圆和右圆都使用相同的回调次数。前半段发布正角速度，后半段发布负角速度，这样两个方向的运动更对称，8 字形不会越画越斜。

## 参数

参数写在 `turtle_params.yaml`：

```yaml
linear_speed: 1.5
angular_speed: 1.0
timer_period: 0.05
```

后面如果想让圆变大或变小，可以改线速度和角速度的比例。

## 问题记录

一开始 VSCode 提示找不到 `rclcpp` 和 `geometry_msgs`，后来发现不是包没装，而是 C++ 插件的 include path 没配置好。

还有一次运行 `ros2 run` 时提示 `No executable found`。原因是 `CMakeLists.txt` 里只写了依赖，没有把 `figure8_node.cpp` 加成可执行文件。加上 `add_executable`、`ament_target_dependencies` 和 `install(TARGETS ...)` 后就可以运行了。

调轨迹时还发现，如果单纯按时间切换方向，乌龟画久了 8 字会慢慢变斜。后来改成按固定步数切换，让左右两个圆发布的速度命令次数一样，轨迹稳定一些。

## AI使用情况

AI 主要用在几个比较卡的地方。刚开始不太清楚 ROS2 包里面 `src`、`config`、`launch`、`CMakeLists.txt` 分别管什么，所以让 AI 帮我按这个作业的结构解释了一遍。写 C++ 节点时，我也问了 `this`、`rclcpp::`、publisher 和 timer 的作用。

后面主要是让 AI 帮忙看报错。比如 VSCode 找不到 include path、`ros2 run` 提示 `No executable found`，这些问题我一开始分不清是代码错还是环境配置错，最后根据提示去检查了 `CMakeLists.txt` 和编译安装位置。8 字形的基本思路还是按 `/turtle1/cmd_vel` 的线速度和角速度来实现。
