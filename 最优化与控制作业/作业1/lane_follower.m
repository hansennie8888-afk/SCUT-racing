%% 第二问：轨迹跟踪
clear; clc; close all

% 车辆参数
lfr = 2.168 + 1.907; % 轴距 L
dt = 0.01;
v = 15;
sim_steps = 2000;
Ld = 8;                 % Pure Pursuit 的前视距离，太小会抖，太大会切弯
max_sigma = 25*pi/180;  % 简单限制前轮转角，避免仿真中出现不现实的大转角

% 参考轨迹 (正弦曲线)
X_ref = 0:0.1:200;
Y_ref = 10 * sin(X_ref / 15);

% 初始车辆状态
X = X_ref(1); Y = Y_ref(1) + 3; phi = 0;
X_vec = zeros(1, sim_steps); Y_vec = zeros(1, sim_steps);
e_vec = zeros(1, sim_steps);


for ii = 1:sim_steps
    X_vec(ii) = X; Y_vec(ii) = Y;


    % ===============================================================

    % ================= 2.1: Pure Pursuit 跟踪算法 =================

    % Pure Pursuit 的思路是：不直接追最近点，而是追前方 Ld 附近的点。
    % 最近点用于判断车辆现在走到轨迹哪一段，目标点负责给出转向方向。
    dist_to_ref = hypot(X_ref - X, Y_ref - Y);
    [e_vec(ii), nearest_idx] = min(dist_to_ref);

    target_idx = nearest_idx;
    while target_idx < numel(X_ref) && ...
            hypot(X_ref(target_idx) - X, Y_ref(target_idx) - Y) < Ld
        target_idx = target_idx + 1;
    end

    target_x = X_ref(target_idx);
    target_y = Y_ref(target_idx);

    % alpha 是目标点方向和车身当前航向之间的夹角。
    % 用 atan2(sin, cos) 归一化角度，避免角度跳到 2*pi 附近。
    dx = target_x - X;
    dy = target_y - Y;
    alpha = atan2(dy, dx) - phi;
    alpha = atan2(sin(alpha), cos(alpha));

    Ld_now = hypot(dx, dy);
    sigma = atan2(2 * lfr * sin(alpha), Ld_now);
    sigma = max(min(sigma, max_sigma), -max_sigma);

    % ===============================================================

    % ================= 2.2: 车辆状态更新 =================
    % 提示: 将刚才求得的转向角 sigma 代入运动学模型（复用第一问代码），更新 X, Y, phi。

    phi_dot = v / lfr * tan(sigma);
    X = X + v * cos(phi) * dt;
    Y = Y + v * sin(phi) * dt;
    phi = phi + phi_dot * dt;
    phi = atan2(sin(phi), cos(phi));

    % ===============================================================

    % 到达终点提前结束
    if X >= X_ref(end), break; end
end

% 绘图对比
figure; hold on; grid on;
plot(X_ref, Y_ref, 'k--', 'LineWidth', 2);
plot(X_vec(1:ii), Y_vec(1:ii), 'r-', 'LineWidth', 2);
legend('参考规划轨迹', '实际行驶轨迹');
title(['Pure Pursuit 跟踪 (Ld = ', num2str(Ld), 'm)']);
xlabel('X [m]'); ylabel('Y [m]');
xlim([X_ref(1), X_ref(end)]);
ylim([min(Y_ref) - 5, max(Y_ref) + 5]);
ax = gca;
ax.Toolbar.Visible = 'off';

result_dir = fullfile(fileparts(mfilename('fullpath')), 'result');
if ~exist(result_dir, 'dir')
    mkdir(result_dir);
end
saveas(gcf, fullfile(result_dir, 'lane_follower_pure_pursuit.png'));

figure; hold on; grid on;
plot((0:ii-1) * dt, e_vec(1:ii), 'b-', 'LineWidth', 1.5);
title('Pure Pursuit 横向误差变化');
xlabel('t [s]'); ylabel('nearest path error [m]');
ax = gca;
ax.Toolbar.Visible = 'off';
saveas(gcf, fullfile(result_dir, 'lane_follower_error.png'));
disp("第二问完成：轨迹图和误差图已保存到 result 文件夹");
