clear; clc; close all
%% 第一问：运动学自行车模型 (开环测试 - 必做)
% 车辆基础参数
lf = 2.168;
lr = 1.907;
lfr = lf + lr; % 轴距 L
sigma = 5 / 180 * pi; % 恒定前轮转角 5度
dt = 0.01; % 仿真步长
v = 30; % 恒定纵向车速 30 m/s

X = 1; Y = 10; phi = 0; % 初始状态
phi_vec = []; X_vec = []; Y_vec = [];

for ii = 1:5000
    phi_vec = [phi_vec, phi];
    X_vec = [X_vec, X + lr*cos(phi)]; % 记录质心位置
    Y_vec = [Y_vec, Y + lr*sin(phi)];

    % ================= 1.1: 运动学模型状态更新 =================
    % 提示: 根据车辆运动学方程，计算横摆角速度 phi_dot，
    % 然后利用 dt 更新航向角 phi 和全局坐标 X, Y。

    % 这里把车辆简化成以后轴中心为参考点的运动学自行车模型。
    % v 是车身前进方向速度，sigma 是前轮转角，转角越大横摆角速度越大。
    phi_dot = v / lfr * tan(sigma);

    % 用显式欧拉法积分：先用当前航向更新位置，再更新航向角。
    % dt 取得比较小，所以这种离散近似已经能看出车辆转弯轨迹。
    X = X + v * cos(phi) * dt;
    Y = Y + v * sin(phi) * dt;
    phi = phi + phi_dot * dt;
    % ===============================================================
end

figure(1); hold on; plot(X_vec, Y_vec, 'b.');
axis equal; title("Kinematic Bicycle Model");
xlabel("X [m]"); ylabel("Y [m]");
grid on;
ax = gca;
ax.Toolbar.Visible = 'off';

result_dir = fullfile(fileparts(mfilename('fullpath')), 'result');
if ~exist(result_dir, 'dir')
    mkdir(result_dir);
end
saveas(gcf, fullfile(result_dir, 'bicycle_kinematic_trajectory.png'));
disp("第一问完成：轨迹图已保存到 result/bicycle_kinematic_trajectory.png");


% %% =================================================================
% %% 拓展问题：动力学模型 (Dynamic Model - 选做)
% %% =================================================================
% % 如果你对车辆底盘动力学感兴趣，可以全选以下行，ctrl+T 取消注释。
%
%
% Iz = 5633.44; % 横摆转动惯量
% Cf = 100000;  % 前轮侧偏刚度
% Cr = 100000;  % 后轮侧偏刚度
% m = 1500;     % 车辆质量
%
% X = 1; Y = 10; phi = 0; % 重置初始状态
% x_dot = v; y_dot = 0; phi_dot = 0; % 初始速度状态
% phi_vec = []; X_vec_dyn = []; Y_vec_dyn = [];
%
% for ii = 1:5000
%     phi_vec = [phi_vec, phi];
%     X_vec_dyn = [X_vec_dyn, X];
%     Y_vec_dyn = [Y_vec_dyn, Y];
%
%     % 计算前后轮侧偏角
%     alpha_f = sigma - (y_dot + lf * phi_dot) / x_dot;
%     alpha_r = - (y_dot - lr * phi_dot) / x_dot;
%
%     % ================= 拓展: 动力学模型状态更新 =================
%     % 提示:
%     % 1. 根据侧偏刚度计算横向轮胎力 Fyf, Fyr
%     % 2. 根据牛顿第二定律计算横向加速度 y_ddot 和横摆角加速度 phi_ddot
%     % 3. 积分更新速度 y_dot, phi_dot
%     % 4. 将车体坐标系下的速度转换到全局坐标系下，更新 X, Y, phi
%
%     % 线性轮胎模型：侧偏角越大，轮胎提供的横向力越大。
%     % Fyf = Cf * alpha_f;
%     % Fyr = Cr * alpha_r;
%     %
%     % 车体坐标系下的横向动力学：
%     % m * (y_ddot + x_dot * phi_dot) = Fyf + Fyr
%     % Iz * phi_ddot = lf * Fyf - lr * Fyr
%     % y_ddot = (Fyf + Fyr) / m - x_dot * phi_dot;
%     % phi_ddot = (lf * Fyf - lr * Fyr) / Iz;
%     %
%     % y_dot = y_dot + y_ddot * dt;
%     % phi_dot = phi_dot + phi_ddot * dt;
%     %
%     % phi = phi + phi_dot * dt;
%     % X = X + (x_dot * cos(phi) - y_dot * sin(phi)) * dt;
%     % Y = Y + (x_dot * sin(phi) + y_dot * cos(phi)) * dt;
%
%     % ===============================================================
% end
% figure(1); hold on;
% plot(X_vec_dyn, Y_vec_dyn, 'r.');
% legend('Kinematic (运动学)', 'Dynamic (动力学)');
% title("Kinematic vs Dynamic Bicycle Model (v = 30m/s)");
