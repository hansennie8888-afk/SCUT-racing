"""
================================================================================
 test_ga.py — 遗传算法测试与可视化
================================================================================

 依赖关系：
 - 依赖 genetic_algorithm.py（提供 GeneticAlgorithm 类和测试函数）
 - 用法：python3 test_ga.py

 功能：
 1. 在 Rastrigin 函数上运行遗传算法
 2. 在 Ackley 函数上运行遗传算法
 3. 对比不同参数的收敛效果
 4. 生成收敛曲线图和种群进化分布图
================================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 无 GUI 后端，直接保存图片
import matplotlib.pyplot as plt
from matplotlib import cm
import os

# 导入遗传算法核心模块
from genetic_algorithm import GeneticAlgorithm, rastrigin_func, ackley_func

# ============================================================================
# 输出目录
# ============================================================================
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_rastrigin():
    """
    ----------------------------------------------------------------------------
    测试1：遗传算法求解 Rastrigin 函数最小值

    运作流程：
    1. 创建 GeneticAlgorithm 实例，配置参数
    2. 调用 run() 执行进化
    3. 绘制并保存收敛曲线和种群进化图

    预期结果：
    - 最优解 x ≈ 0, f(x) ≈ 0
    - 收敛曲线逐渐下降并趋于平稳
    - 种群从分散状态聚集到 x=0 附近
    ----------------------------------------------------------------------------
    """
    print("=" * 60)
    print("测试1: Rastrigin 函数最小值求解")
    print("f(x) = 10 + x^2 - 10*cos(2*pi*x)")
    print("理论最优: x=0, f(x)=0")
    print("=" * 60)

    ga = GeneticAlgorithm(
        dna_size=24,           # DNA长度=24，编码精度约 (10.24/(2^24-1)) ≈ 6.1e-7
        pop_size=100,          # 种群规模=100
        cross_rate=0.8,        # 交叉概率=0.8
        mutation_rate=0.01,    # 变异概率=0.01
        n_generations=100,     # 进化100代
        x_bound=[-5.12, 5.12],# Rastrigin 推荐搜索范围
        func=rastrigin_func,   # 目标函数
        maximize=False,        # 最小化问题
        elitism=True           # 启用精英保留
    )

    best_x, best_y = ga.run(verbose=True)

    # 保存收敛曲线
    fig1 = ga.plot_convergence()
    fig1.savefig(os.path.join(OUTPUT_DIR, 'rastrigin_convergence.png'), dpi=150)
    plt.close(fig1)
    print(f"\n收敛曲线已保存至: {OUTPUT_DIR}/rastrigin_convergence.png")

    # 保存种群进化图
    fig2 = ga.plot_evolution(resolution=300)
    fig2.savefig(os.path.join(OUTPUT_DIR, 'rastrigin_evolution.png'), dpi=150)
    plt.close(fig2)
    print(f"种群进化图已保存至: {OUTPUT_DIR}/rastrigin_evolution.png")

    return ga


def test_ackley():
    """
    ----------------------------------------------------------------------------
    测试2：遗传算法求解 Ackley 函数最小值

    运作流程：同 test_rastrigin()

    预期结果：
    - 最优解 x ≈ 0, f(x) ≈ 0
    - Ackley 函数外围平坦、中心有深谷，对算法收敛有挑战
    ----------------------------------------------------------------------------
    """
    print("\n" + "=" * 60)
    print("测试2: Ackley 函数最小值求解")
    print("理论最优: x=0, f(x)=0")
    print("=" * 60)

    ga = GeneticAlgorithm(
        dna_size=24,
        pop_size=100,
        cross_rate=0.8,
        mutation_rate=0.01,
        n_generations=100,
        x_bound=[-5, 5],
        func=ackley_func,
        maximize=False,
        elitism=True
    )

    best_x, best_y = ga.run(verbose=True)

    fig1 = ga.plot_convergence()
    fig1.savefig(os.path.join(OUTPUT_DIR, 'ackley_convergence.png'), dpi=150)
    plt.close(fig1)
    print(f"\n收敛曲线已保存至: {OUTPUT_DIR}/ackley_convergence.png")

    fig2 = ga.plot_evolution(resolution=300)
    fig2.savefig(os.path.join(OUTPUT_DIR, 'ackley_evolution.png'), dpi=150)
    plt.close(fig2)
    print(f"种群进化图已保存至: {OUTPUT_DIR}/ackley_evolution.png")

    return ga


def test_parameter_comparison():
    """
    ----------------------------------------------------------------------------
    测试3：对比不同参数对遗传算法收敛的影响

    分别测试：
    - 不同种群规模（pop_size=50, 100, 200）
    - 不同变异概率（mutation_rate=0.001, 0.01, 0.1）
    - 有/无精英保留

    运作流程：
    1. 对每种参数配置分别运行遗传算法
    2. 收集收敛曲线
    3. 绘制对比图

    此函数展示了遗传算法参数调优的基本方法
    ----------------------------------------------------------------------------
    """
    print("\n" + "=" * 60)
    print("测试3: 参数对比实验")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # --- 对比不同种群规模 ---
    print("\n[对比种群规模]")
    ax = axes[0, 0]
    colors = ['#2196F3', '#FF5722', '#4CAF50']
    for idx, pop_size in enumerate([50, 100, 200]):
        ga = GeneticAlgorithm(
            dna_size=24, pop_size=pop_size, cross_rate=0.8,
            mutation_rate=0.01, n_generations=100,
            x_bound=[-5.12, 5.12], func=rastrigin_func,
            maximize=False, elitism=True
        )
        ga.run(verbose=False)
        ax.plot(ga.best_fitness_hist, color=colors[idx],
                linewidth=1.5, label=f'Pop={pop_size}')
        print(f"  Pop={pop_size}: best={ga.best_x:.6f}, f(x)={rastrigin_func(np.array([[ga.best_x]])).flatten()[0]:.6f}")
    ax.set_xlabel('Generation')
    ax.set_ylabel('Best Fitness')
    ax.set_title('Effect of Population Size')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- 对比不同变异概率 ---
    print("\n[对比变异概率]")
    ax = axes[0, 1]
    colors = ['#2196F3', '#FF5722', '#4CAF50']
    for idx, mut_rate in enumerate([0.001, 0.01, 0.05]):
        ga = GeneticAlgorithm(
            dna_size=24, pop_size=100, cross_rate=0.8,
            mutation_rate=mut_rate, n_generations=100,
            x_bound=[-5.12, 5.12], func=rastrigin_func,
            maximize=False, elitism=True
        )
        ga.run(verbose=False)
        ax.plot(ga.best_fitness_hist, color=colors[idx],
                linewidth=1.5, label=f'Mut={mut_rate}')
        print(f"  Mut={mut_rate}: best={ga.best_x:.6f}, f(x)={rastrigin_func(np.array([[ga.best_x]])).flatten()[0]:.6f}")
    ax.set_xlabel('Generation')
    ax.set_ylabel('Best Fitness')
    ax.set_title('Effect of Mutation Rate')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- 对比精英保留 ---
    print("\n[对比精英保留]")
    ax = axes[1, 0]
    for label, use_elite, color in [('With Elitism', True, '#2196F3'),
                                      ('Without Elitism', False, '#FF5722')]:
        ga = GeneticAlgorithm(
            dna_size=24, pop_size=100, cross_rate=0.8,
            mutation_rate=0.01, n_generations=100,
            x_bound=[-5.12, 5.12], func=rastrigin_func,
            maximize=False, elitism=use_elite
        )
        ga.run(verbose=False)
        ax.plot(ga.best_fitness_hist, color=color, linewidth=1.5, label=label)
        print(f"  {label}: best={ga.best_x:.6f}, f(x)={rastrigin_func(np.array([[ga.best_x]])).flatten()[0]:.6f}")
    ax.set_xlabel('Generation')
    ax.set_ylabel('Best Fitness')
    ax.set_title('Effect of Elitism')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- 函数曲面对比 ---
    print("\n[函数曲面展示]")
    ax = axes[1, 1]
    x_plot = np.linspace(-5.12, 5.12, 500)
    y_rastrigin = rastrigin_func(x_plot.reshape(-1, 1)).flatten()
    y_ackley = ackley_func(x_plot.reshape(-1, 1)).flatten()

    ax.plot(x_plot, y_rastrigin, 'b-', linewidth=1.5, label='Rastrigin')
    ax.plot(x_plot, y_ackley, 'r-', linewidth=1.5, label='Ackley')
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title('Test Functions Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'parameter_comparison.png'), dpi=150)
    plt.close(fig)
    print(f"\n参数对比图已保存至: {OUTPUT_DIR}/parameter_comparison.png")


def plot_search_space_3d():
    """
    ----------------------------------------------------------------------------
    绘制 Rastrigin 函数的 3D 曲面展示搜索空间

    此图直观展示遗传算法面临的搜索环境：
    - 多个"山峰"和"山谷"（局部最优）
    - 中心的全局最优解 (x=0, f(x)=0)
    ----------------------------------------------------------------------------
    """
    fig = plt.figure(figsize=(12, 5))

    # 2D 详细视图
    ax1 = fig.add_subplot(1, 2, 1)
    x_plot = np.linspace(-5.12, 5.12, 1000)
    y_plot = rastrigin_func(x_plot.reshape(-1, 1)).flatten()
    ax1.plot(x_plot, y_plot, 'b-', linewidth=1)
    ax1.scatter([0], [0], c='r', s=100, marker='*', zorder=5, label='Global Minimum')
    # 标记一些局部最小值
    for k in range(-5, 6):
        if k != 0:
            y_local = rastrigin_func(np.array([[k]]))[0, 0]
            ax1.scatter([k], [y_local], c='orange', s=30, zorder=4)
    ax1.set_xlabel('x')
    ax1.set_ylabel('f(x)')
    ax1.set_title('Rastrigin Function: 1D View\nMultiple Local Minima (orange), Global Minimum (red star)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 初始种群 vs 最终种群示意
    ax2 = fig.add_subplot(1, 2, 2)

    # 模拟初始种群（均匀分布）
    np.random.seed(42)
    init_pop = np.random.uniform(-5.12, 5.12, 50)
    init_fit = rastrigin_func(init_pop.reshape(-1, 1)).flatten()

    # 模拟收敛后的种群（集中在最优解附近）
    final_pop = np.random.normal(0, 0.5, 50)
    final_fit = rastrigin_func(final_pop.reshape(-1, 1)).flatten()

    ax2.plot(x_plot, y_plot, 'k-', linewidth=0.5, alpha=0.5)
    ax2.scatter(init_pop, init_fit, c='blue', s=30, alpha=0.6, label='Initial Population')
    ax2.scatter(final_pop, final_fit, c='red', s=30, alpha=0.8, label='Final Population')
    ax2.scatter([0], [0], c='yellow', s=150, marker='*', zorder=5, edgecolors='k', label='Global Optimum')
    ax2.set_xlabel('x')
    ax2.set_ylabel('f(x)')
    ax2.set_title('GA Search Visualization\nBlue=Initial, Red=Converged')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'search_space.png'), dpi=150)
    plt.close(fig)
    print(f"搜索空间图已保存至: {OUTPUT_DIR}/search_space.png")


# ============================================================================
# 主程序入口
# ============================================================================
if __name__ == '__main__':
    print("遗传算法 (Genetic Algorithm) 演示程序")
    print("=" * 60)
    print(f"输出图片目录: {OUTPUT_DIR}")
    print()

    # 运行各项测试
    test_rastrigin()
    test_ackley()
    test_parameter_comparison()
    plot_search_space_3d()

    print(f"\n所有测试完成！生成的结果图片在: {OUTPUT_DIR}/")
    print("文件列表：")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        print(f"  - {f}")
