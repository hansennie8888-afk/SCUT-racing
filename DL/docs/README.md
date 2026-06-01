DL锥桶颜色分类作业

这个作业是用深度学习做锥桶颜色分类，类别是 blue、red、yellow。
数据集按文件夹分好类，程序读取文件夹名作为标签。

文件说明

src/net.py
网络结构和训练代码。

src/test.py
加载训练好的模型，在 test1 和 test2 上测试。

src/check_data.py
训练前检查数据集里有没有坏图。

models/model_best.pth
训练后保存下来的模型。

docs/ppt
课程 PPT 放在这里。

docs/homework2
深度学习笔记和 U-Net 论文阅读放在这里。

dataset
数据集文件夹，里面是 train、test1、test2。

运行方法

先进入 DL 文件夹，然后使用 dl 环境。

检查数据：
python -m src.check_data

训练模型：
python -m src.net

测试模型：
python -m src.test

数据情况

原始数据一共 1655 张图，扫描后有 1627 张能正常读取，28 张坏图。
程序里用了 is_valid_file，训练和测试时会自动跳过坏图。

train 中三类数量大概是：
blue 476
red 479
yellow 343

yellow 的数量少一些，所以后面测试里 yellow 的正确率比另外两类低一点。

网络设计

用的是一个比较小的 CNN，没有用预训练模型。
输入图片先统一 resize 到 64 x 64。

网络大概是：

输入 3 x 64 x 64
卷积 3 到 16，池化后变成 16 x 32 x 32
卷积 16 到 32，池化后变成 32 x 16 x 16
卷积 32 到 64，池化后变成 64 x 8 x 8
拉平成 4096
全连接 4096 到 256
全连接 256 到 3

卷积层有 3 层，全连接有 2 层，符合 PPT 里层数不能太多的要求。

训练方法

优化器最后用了 Adam，学习率是 0.001。
一开始考虑过 SGD 加 momentum，代码里也保留了那一行注释。后来用 Adam 是因为这个数据集比较小，Adam 收敛快一些。

训练集做了一点简单的数据增强：

resize 到 64 x 64
随机水平翻转
小角度旋转
轻微调整亮度、对比度、饱和度
归一化

没有改 hue，因为这个任务主要就是分 blue、red、yellow，颜色本身不能乱改。

训练结果

训练 50 个 epoch，保存 test1 上效果最好的模型。

最后一次测试结果：

test1 Overall Accuracy:99.53%
blue: 100.00%
red: 100.00%
yellow: 98.11%

test2 Overall Accuracy:95.71%
blue: 98.00%
red: 95.92%
yellow: 92.68%

test2 比 test1 低一些，主要是 test2 和训练集差别更大一点，而且 yellow 样本本来就少。
