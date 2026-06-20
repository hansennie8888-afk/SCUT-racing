# 第五次作业说明

本目录保存第五次作业的代码、推导和运行结果。

## 文件结构

- `作业1/bicycle_models_problem.m`：Kinematic Bicycle Model（运动学自行车模型）的开环仿真。
- `作业1/lane_follower.m`：用 Pure Pursuit（纯跟踪）方法跟踪正弦参考轨迹。
- `作业1/result/`：MATLAB 运行后保存的轨迹图和误差图。
- `作业2/dog_optimization.cpp`：机器狗寻优问题，包含 Gradient Descent（梯度下降）、KKT 条件和 QP 矩阵。
- `作业2/机器狗寻优问题.pdf`：题目原文件。

## 作业 1：自行车模型和轨迹跟踪

### 1.1 运动学自行车模型

代码中采用以后轴中心为参考点的 Kinematic Bicycle Model（运动学自行车模型）：

```text
X_dot = v cos(phi)
Y_dot = v sin(phi)
phi_dot = v / L * tan(sigma)
```

其中 `L = lf + lr` 是轴距，`sigma` 是前轮转角，`phi` 是车身航向角。程序里用显式欧拉法离散化，也就是每个小步长 `dt` 内认为速度和转角不变：

```text
X = X + X_dot * dt
Y = Y + Y_dot * dt
phi = phi + phi_dot * dt
```

固定转角下，`phi_dot` 为常数，因此车辆会沿圆弧行驶。运行图中的蓝色轨迹与这个结论一致。

运行：

```matlab
cd 作业1
bicycle_models_problem
```

运行后会生成：

```text
作业1/result/bicycle_kinematic_trajectory.png
```

### 1.2 Pure Pursuit 跟踪正弦轨迹

第二问采用 Pure Pursuit（纯跟踪）。前视点查找、转向角计算和车辆状态更新都放在同一个仿真循环中。

每一步控制分三步：

1. 先在参考轨迹上找距离车辆最近的点，判断车辆大概走到哪里。
2. 再往前找距离约为 `Ld` 的目标点，而不是追最近点。
3. 把目标点方向转换到车身坐标系，用夹角 `alpha` 计算前轮转角：

```text
sigma = atan2(2 L sin(alpha), Ld_now)
```

这里 `Ld` 是前视距离。本次取 `Ld = 8 m`，并把前轮转角限制在 `25 deg` 内。`Ld` 太小时修正较快，容易有抖动；`Ld` 太大时轨迹会更平滑，但弯道误差会增加。

运行：

```matlab
cd 作业1
lane_follower
```

运行后会生成：

```text
作业1/result/lane_follower_pure_pursuit.png
作业1/result/lane_follower_error.png
```

本次结果中，车辆从相对参考线约 `3 m` 的初始偏移开始，随后红色轨迹与参考轨迹接近重合。正弦轨迹的转弯段仍有小误差，误差图中可以看到周期性的波动。

## 作业 2：机器狗寻优

题目目标函数是：

```text
f(x, y) = 1/2 (x - 3)^2 + 10/2 (y - 3)^2
```

梯度为：

```text
grad f = [x - 3, 10(y - 3)]^T
```

### Q1 梯度下降

迭代公式：

```text
X_{k+1} = X_k - eta * grad f(X_k)
```

本机运行记录如下：`eta = 0.01` 时迭代 797 次，`0.05` 时 157 次，`0.10` 和 `0.19` 都是 76 次；`eta = 0.21` 不收敛。原因是 y 方向的更新系数为 `1 - 10 eta`，当 `eta = 0.21` 时其绝对值大于 1。

### Q2 KKT 条件

加入约束：

```text
x + y <= 4
```

无约束最优点是 `(3, 3)`，但它不满足 `x + y <= 4`，所以最优点会落在边界 `x + y = 4` 上。

拉格朗日函数：

```text
L(x, y, mu) = 1/2 (x - 3)^2 + 10/2 (y - 3)^2 + mu (x + y - 4)
```

KKT 条件：

```text
x - 3 + mu = 0
10(y - 3) + mu = 0
x + y - 4 <= 0
mu >= 0
mu(x + y - 4) = 0
```

无约束最优点 `(3, 3)` 不满足约束，所以取活动约束 `x + y = 4`。解得：

```text
mu = 20 / 11
x = 13 / 11 = 1.1818
y = 31 / 11 = 2.8182
```

y 方向的代价权重较大，因此受约束后 y 的变化较小，主要通过减小 x 来满足 `x + y <= 4`。

### Q3 QP 标准型

OSQP 使用的形式是：

```text
min 1/2 X^T P X + q^T X
s.t. l <= A X <= u
```

本题展开后常数项可以省略，所以：

```text
P = [1  0
     0 10]

q = [-3
     -30]

A = [1 1]
l = -inf
u = 4
```

实际运行 OSQP 得到：

```text
x = 1.181814
y = 2.818189
iteration = 25
```

## C++ 编译说明（Windows + Visual Studio + vcpkg）

本次在 Windows 下使用 MSVC、Eigen3 和 OSQP 运行。先在 VS Code 终端进入 Visual Studio Developer Command Prompt，再进入作业目录：

```bat
cd /d "C:\Users\ASUS8848\Downloads\最优化与控制\2026培训\Control\作业2"
```

只运行 Eigen 部分：

```bat
cl /nologo /std:c++17 /EHsc /utf-8 /O2 /I C:\dev\vcpkg\installed\x64-windows\include\eigen3 dog_optimization.cpp /Fe:dog_optimization_eigen.exe
dog_optimization_eigen.exe
```

`/utf-8` 用来保证源代码里的中文注释按 UTF-8 读取，否则 MSVC 可能给出代码页警告。

运行 OSQP 部分：

```bat
cl /nologo /std:c++17 /EHsc /utf-8 /O2 /DUSE_OSQP /I C:\dev\vcpkg\installed\x64-windows\include\eigen3 /I C:\dev\vcpkg\installed\x64-windows\include dog_optimization.cpp /Fe:dog_optimization_osqp.exe /link /LIBPATH:C:\dev\vcpkg\installed\x64-windows\lib osqp.lib

set PATH=C:\dev\vcpkg\installed\x64-windows\bin;%PATH%
dog_optimization_osqp.exe
```

第二条 `set PATH` 是为了让系统在运行时找到 `osqp.dll`。本次运行结果与 KKT 手算解一致。
