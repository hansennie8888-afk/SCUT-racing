# ROS2进阶作业

进阶作业是把老师给的 ros2 bag 里的锥桶地图显示到 RViz2 里。这里没有做 YOLO 或其他检测算法，因为 bag 里已经有地图消息了，作业重点是把已有的 `Map` 消息转成 RViz 能显示的 marker。

环境：

Ubuntu 22.04

ROS2 Humble

## 文件

```text
map_to_visualize/
src/fsd_common_msgs/
src/ros2_homework_advanced_package/src/map_visualizer_node.cpp
src/ros2_homework_advanced_package/launch/map_visualizer.launch.py
```

`fsd_common_msgs` 是老师给的消息包，里面有 `Map.msg` 和 `Cone.msg`。我自己的代码主要在 `map_visualizer_node.cpp`。

## 运行

先编译：

```bash
cd /data/projects/ROS2/ros2_homework_advanced_ws
source /opt/ros/humble/setup.bash
colcon build --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
```

终端 1 播放 bag：

```bash
cd /data/projects/ROS2/ros2_homework_advanced_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 bag play map_to_visualize --loop
```

终端 2 启动可视化节点和 RViz2：

```bash
cd /data/projects/ROS2/ros2_homework_advanced_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ros2_homework_advanced_package map_visualizer.launch.py
```

RViz2 中设置：

```text
Fixed Frame: world
Add -> By topic -> /cone_markers -> MarkerArray
```

## 思路

bag 里要看的话题是：

```text
/estimation/slam/map
```

消息类型是：

```text
fsd_common_msgs/msg/Map
```

`Map.msg` 里分了四类锥桶：

```text
cone_yellow
cone_blue
cone_red
cone_unknown
```

每个锥桶都有 `position`，所以我的节点订阅 `/estimation/slam/map` 后，遍历这四个数组，把每个锥桶变成一个球形 marker，再放进 `MarkerArray` 发布到 `/cone_markers`。

颜色对应关系：

```text
yellow -> 黄色
blue -> 蓝色
red -> 红色
unknown -> 灰色
```

我查看过 bag 消息头，坐标系是 `world`，所以 RViz2 里 Fixed Frame 也设成 `world`。

## 问题记录

编译 `fsd_common_msgs` 时遇到过 Python 环境问题。因为终端在 conda base 环境下时，`colcon` 可能会调用 conda 的 Python，导致 ROS2 生成消息时找不到 `em` 模块。后面编译时指定 `/usr/bin/python3` 就解决了。

RViz2 里如果一开始看不到锥桶，需要检查两点：Fixed Frame 是不是 `world`，以及有没有添加 `/cone_markers` 的 `MarkerArray` 显示项。

## AI使用情况

AI 主要用在读懂进阶作业数据和排查环境问题上。一开始我不确定这个作业需不需要 YOLO，后来通过查看 bag 里的话题和 `Map.msg` 字段，确认数据里已经有锥桶位置，所以这里只需要做可视化。

实现时比较难的是 `MarkerArray` 和 RViz2 的坐标系设置。我让 AI 帮我梳理了 `fsd_common_msgs/msg/Map` 里四类锥桶数组的结构，以及 marker 的颜色、大小、frame_id 应该怎么设置。编译 `fsd_common_msgs` 时还遇到了 conda Python 导致缺少 `em` 模块的问题，这部分也是根据 AI 的提示去定位到 Python 环境并改用 `/usr/bin/python3` 的。
