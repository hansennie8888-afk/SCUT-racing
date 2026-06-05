# ros2_homework_advanced_package

这个包用于进阶作业的锥桶地图可视化。

主要节点：

```text
map_visualizer_node
```

它订阅 `/estimation/slam/map`，把 `fsd_common_msgs/msg/Map` 中的锥桶位置转换成 `MarkerArray`，再发布到 `/cone_markers`，供 RViz2 显示。

运行方法见工作空间根目录的 README。
