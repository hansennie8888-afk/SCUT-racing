"""
================================================================================
 遗传算法 (Genetic Algorithm, GA) — 求解函数最小值问题
================================================================================

 算法来源参考：
 - GitHub: https://github.com/guofei9987/scikit-opt (遗传算法库)
 - CSDN:   https://blog.csdn.net/u010835747/article/details/80038372
 - 博客园: https://www.cnblogs.com/LoganChen/p/12597272.html

 本实现参考文献：
 [1] Holland, J.H. (1975). Adaptation in Natural and Artificial Systems.
 [2] Goldberg, D.E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning.
 [3] scikit-opt 开源项目: https://github.com/guofei9987/scikit-opt

================================================================================
 文件结构：
 - genetic_algorithm.py :  遗传算法完整实现（本文件）
 - test_ga.py           :  运行示例与可视化

 依赖关系：
 - genetic_algorithm.py 是核心模块，包含 GA 类和所有遗传操作
 - test_ga.py 依赖 genetic_algorithm.py，用于演示和可视化
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import random
import time


# ============================================================================
# 全局变量说明
# ============================================================================
# DNA_SIZE       : 每个个体的 DNA（染色体）长度，即编码精度
# POP_SIZE       : 种群规模，每一代有多少个体
# CROSS_RATE     : 交叉概率，个体发生交叉的概率
# MUTATION_RATE  : 变异概率，每个基因位发生变异的概率
# N_GENERATIONS  : 最大进化代数
# X_BOUND        : 自变量的取值范围 [min, max]


class GeneticAlgorithm:
    """
    ============================================================================
    遗传算法类

    算法整体流程：
    1. 初始化种群：随机生成 POP_SIZE 个个体（DNA）
    2. 计算适应度：将每个个体的 DNA 解码为十进制，代入目标函数计算适应度
    3. 选择（Selection）：根据适应度按轮盘赌/锦标赛方式选出父代
    4. 交叉（Crossover）：父代个体以一定概率交换部分 DNA 片段
    5. 变异（Mutation）：以一定概率随机改变 DNA 的某些基因位
    6. 重复步骤 2-5，直到满足终止条件（达到最大代数或收敛）

    关键局部变量：
    - pop : ndarray (POP_SIZE, DNA_SIZE) — 种群矩阵，每行是一个个体的二进制DNA
    - fitness : ndarray (POP_SIZE,) — 每个个体的适应度值
    - best_fitness_history : list — 记录每代最优适应度，用于绘制收敛曲线
    ============================================================================
    """

    def __init__(self, dna_size, pop_size, cross_rate, mutation_rate,
                 n_generations, x_bound, func, maximize=True, elitism=True):
        """
        ------------------------------------------------------------------------
        初始化遗传算法参数

        参数：
        dna_size      : DNA长度，决定编码精度。值越大精度越高
        pop_size      : 种群规模，越大搜索越全面但计算量也越大
        cross_rate    : 交叉概率，通常取值 0.6~0.9
        mutation_rate : 变异概率，通常取值 0.001~0.1
        n_generations : 最大进化代数
        x_bound       : 搜索空间边界 [lower, upper]
        func          : 目标函数（适应度函数）
        maximize      : True=最大化, False=最小化
        elitism       : 是否保留精英个体

        内部状态变量（实例变量）：
        - self.pop             : 当前种群 (ndarray)
        - self.best_dna        : 历史最优个体的DNA
        - self.best_fitness    : 历史最优适应度
        - self.best_x          : 历史最优个体的解码值
        - self.best_fitness_hist : 每代最优适应度记录
        - self.avg_fitness_hist  : 每代平均适应度记录
        ------------------------------------------------------------------------
        """
        self.DNA_SIZE = dna_size
        self.POP_SIZE = pop_size
        self.CROSS_RATE = cross_rate
        self.MUTATION_RATE = mutation_rate
        self.N_GENERATIONS = n_generations
        self.X_BOUND = x_bound
        self.func = func
        self.maximize = maximize
        self.elitism = elitism

        # 内部状态
        self.pop = None                     # 种群矩阵
        self.best_dna = None                # 历史最优DNA
        self.best_fitness = None            # 历史最优适应度
        self.best_x = None                  # 历史最优解
        self.best_fitness_hist = []         # 记录每代最优
        self.avg_fitness_hist = []          # 记录每代平均
        self.all_pop_history = []           # 记录部分代种群（用于可视化）
        self.x_values = None                # 解码后的种群值

    # ========================== 核心遗传操作 ==========================

    def dna_to_decimal(self, pop):
        """
        ------------------------------------------------------------------------
        将二进制 DNA 解码为十进制数值

        运作流程：
        1. 将二进制 DNA 转换为整数
        2. 将整数映射到 [X_BOUND[0], X_BOUND[1]] 区间

        变量变化：
        - 输入 pop : (POP_SIZE, DNA_SIZE) — 保持不变（只读）
        - 返回 x   : (POP_SIZE, 1)         — 解码后的十进制值

        解码公式：
        x = lower + (upper - lower) * int_value / (2^DNA_SIZE - 1)
        ------------------------------------------------------------------------
        """
        lower, upper = self.X_BOUND
        # 二进制 → 十进制整数：将每行视为二进制数求和
        # 例如 [1,0,1] → 1*4 + 0*2 + 1*1 = 5
        decimal_values = pop.dot(2 ** np.arange(self.DNA_SIZE)[::-1])
        # 映射到搜索空间
        x = lower + decimal_values * (upper - lower) / (2 ** self.DNA_SIZE - 1)
        return x.reshape(-1, 1)

    def get_fitness(self, pop):
        """
        ------------------------------------------------------------------------
        计算种群中每个个体的适应度

        运作流程：
        1. 调用 dna_to_decimal() 解码 DNA → x
        2. 代入目标函数 func(x) 计算函数值
        3. 处理最大化/最小化：最大化直接用函数值；最小化取负
        4. 保证适应度为非负数（减去最小值，加上小常数防止除零）

        与其他函数依赖：
        - 依赖 dna_to_decimal() 进行 DNA 解码
        - 被 select(), run() 调用
        ------------------------------------------------------------------------
        """
        x = self.dna_to_decimal(pop)
        raw = self.func(x).flatten()

        if not self.maximize:
            raw = -raw  # 最小化问题取负

        # 保证适应度非负
        min_val = np.min(raw)
        if min_val < 0:
            raw = raw - min_val + 1e-10
        return raw + 1e-10

    def select(self, fitness):
        """
        ------------------------------------------------------------------------
        选择操作：轮盘赌选择法 (Roulette Wheel Selection)

        运作流程：
        1. 将适应度归一化为选择概率（适应度越高，被选中概率越大）
        2. 生成累加概率分布
        3. 用均匀随机数进行轮盘赌采样，选出 POP_SIZE 个父代

        变量变化：
        - 输入 fitness : (POP_SIZE,)      — 只读
        - 返回 idx     : array             — 被选中个体的索引数组
        - 局部变量 probs : 选择概率分布
        - 局部变量 cumsum : 累加概率

        注意：此处采用放回抽样，同一个体会被多次选中
        ------------------------------------------------------------------------
        """
        # 归一化适应度为选择概率
        probs = fitness / np.sum(fitness)
        # 累加概率：用于轮盘赌
        cumsum = np.cumsum(probs)

        # 轮盘赌：生成 POP_SIZE 个均匀随机数，落在哪个区间就选哪个
        idx = np.zeros(self.POP_SIZE, dtype=int)
        for i in range(self.POP_SIZE):
            r = np.random.rand()
            # np.where 返回所有 cumsum > r 的位置，取第一个即为选中索引
            idx[i] = np.where(cumsum > r)[0][0]
        return idx

    def crossover(self, parent, pop):
        """
        ------------------------------------------------------------------------
        交叉操作：单点交叉 (Single Point Crossover)

        运作流程：
        1. 判断是否发生交叉（按 CROSS_RATE 概率）
        2. 若不交叉，直接返回父代之一
        3. 若交叉，随机选一个交叉点，交换两个父代在交叉点后的 DNA 片段

        变量变化：
        - 输入 parent : (1, DNA_SIZE)         — 父代
        - 输入 pop    : (POP_SIZE, DNA_SIZE)  — 交叉对象
        - 返回        : (1, DNA_SIZE)         — 子代
        ------------------------------------------------------------------------
        """
        if np.random.rand() < self.CROSS_RATE:
            # 随机选择另一个父代
            other = pop[np.random.randint(0, self.POP_SIZE)]
            # 随机选交叉点 (1 到 DNA_SIZE-1，确保有交换)
            cross_point = np.random.randint(1, self.DNA_SIZE)
            # 拼接：前半来自 parent, 后半来自 other
            child = np.hstack((parent[0, :cross_point], other[cross_point:]))
            return child.reshape(1, -1)
        else:
            return parent.copy()

    def mutate(self, child):
        """
        ------------------------------------------------------------------------
        变异操作：位翻转变异 (Bit Flip Mutation)

        运作流程：
        1. 遍历子代 DNA 的每一位
        2. 以 MUTATION_RATE 概率翻转该位 (0→1, 1→0)

        变量变化：
        - 输入 child : (1, DNA_SIZE) — 子代DNA（原地修改）

        注意：此函数直接修改传入的数组而非返回新数组
        ------------------------------------------------------------------------
        """
        for point in range(self.DNA_SIZE):
            if np.random.rand() < self.MUTATION_RATE:
                child[0, point] = not child[0, point]  # 翻转位

    # ========================== 主循环 ==========================

    def run(self, verbose=True):
        """
        ============================================================================
        遗传算法主循环

        运作流程：
        1. 初始化种群：随机生成 POP_SIZE 个二进制 DNA 个体
        2. 进入进化循环（N_GENERATIONS 代）：
           a. 计算适应度：调用 get_fitness(pop) 获取每个个体的适应度
           b. 记录最优：更新全局最优个体记录
           c. 精英保留：若启用，保留适应度最高的个体直接进入下一代
           d. 生成下一代：
              - 重复 POP_SIZE（减去精英数）次：
                * 选择：调用 select() 选出父代索引
                * 交叉：调用 crossover() 生成子代
                * 变异：调用 mutate() 对子代进行变异
              - 将精英个体放回种群
           e. 记录历史数据用于可视化
        3. 输出最优结果

        关键变量变化过程（以最小化为例）：
        - 第0代: pop随机, fitness随机, best_fitness=较大值
        - 第N代: pop趋向最优, fitness逐渐降低, best_fitness逐渐收敛

        与其他函数依赖：
        - 调用 get_fitness()  → 计算适应度
        - 调用 select()      → 选择父代
        - 调用 crossover()   → 交叉产生子代
        - 调用 mutate()      → 变异子代
        - 调用 dna_to_decimal() → 最终解码最优解
        ============================================================================
        """

        # ========== 步骤1：初始化种群 ==========
        # 随机生成二进制 DNA: 0 或 1
        self.pop = np.random.randint(0, 2, size=(self.POP_SIZE, self.DNA_SIZE))

        # 记录迭代开始时间
        start_time = time.time()

        # ========== 步骤2：进化循环 ==========
        for generation in range(self.N_GENERATIONS):

            # ------ 步骤2a：计算适应度 ------
            fitness = self.get_fitness(self.pop)

            # ------ 步骤2b：记录本代最优 ------
            best_idx = np.argmax(fitness)
            gen_best_fitness = fitness[best_idx]
            gen_best_dna = self.pop[best_idx].copy()

            # 更新全局最优
            if self.best_fitness is None or gen_best_fitness > self.best_fitness:
                self.best_fitness = gen_best_fitness
                self.best_dna = gen_best_dna.copy()

            # ------ 步骤2c：记录统计信息 ------
            self.best_fitness_hist.append(gen_best_fitness)
            self.avg_fitness_hist.append(np.mean(fitness))

            # 每隔一定的代数记录完整种群（用于后期可视化）
            if generation % max(1, self.N_GENERATIONS // 20) == 0:
                self.all_pop_history.append((
                    generation,
                    self.dna_to_decimal(self.pop).flatten().copy(),
                    fitness.copy()
                ))

            if verbose and generation % max(1, self.N_GENERATIONS // 10) == 0:
                best_x_val = self.dna_to_decimal(gen_best_dna.reshape(1, -1))[0, 0]
                best_y_val = self.func(np.array([[best_x_val]])).flatten()[0]
                print(f"Gen {generation:4d}/{self.N_GENERATIONS} | "
                      f"Best Fitness: {gen_best_fitness:.6f} | "
                      f"x={best_x_val:.6f} | f(x)={best_y_val:.6f}")

            # ------ 步骤2d：生成下一代 ------
            new_pop = []

            # 精英保留：直接保留最优个体
            elite_count = 1 if self.elitism else 0
            if self.elitism:
                new_pop.append(self.pop[best_idx].copy())

            # 选择、交叉、变异 产生 (POP_SIZE - elite_count) 个子代
            while len(new_pop) < self.POP_SIZE:
                # 轮盘赌选择父代
                parent_idx = self.select(fitness)
                # 选其中一个父代
                chosen = self.pop[parent_idx[np.random.randint(0, len(parent_idx))]]
                # 交叉
                child = self.crossover(chosen.reshape(1, -1), self.pop)
                # 变异
                self.mutate(child)
                # 加入新种群
                new_pop.append(child.flatten())

            # 更新种群
            self.pop = np.array(new_pop[:self.POP_SIZE])

        # ========== 步骤3：输出结果 ==========
        elapsed = time.time() - start_time
        self.best_x = self.dna_to_decimal(self.best_dna.reshape(1, -1))[0, 0]
        best_func_value = self.func(np.array([[self.best_x]])).flatten()[0]

        if verbose:
            print(f"\n{'='*60}")
            print(f"遗传算法完成！耗时: {elapsed:.3f}s")
            print(f"最优解: x = {self.best_x:.6f}")
            print(f"最优函数值: f(x) = {best_func_value:.6f}")
            print(f"DNA = {self.best_dna}")
            print(f"{'='*60}")

        return self.best_x, best_func_value

    # ========================== 可视化 ==========================

    def plot_convergence(self):
        """
        ------------------------------------------------------------------------
        绘制收敛曲线：展示每代最优适应度和平均适应度的变化

        依赖：需要在 run() 之后调用，使用 best_fitness_hist 和 avg_fitness_hist
        ------------------------------------------------------------------------
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 最优适应度曲线
        axes[0].plot(self.best_fitness_hist, 'b-', linewidth=1.5, label='Best Fitness')
        axes[0].set_xlabel('Generation')
        axes[0].set_ylabel('Fitness')
        axes[0].set_title('Best Fitness Convergence Curve')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # 同时画最优和平均
        axes[1].plot(self.best_fitness_hist, 'b-', linewidth=1, label='Best Fitness')
        axes[1].plot(self.avg_fitness_hist, 'r--', linewidth=1, label='Average Fitness')
        axes[1].set_xlabel('Generation')
        axes[1].set_ylabel('Fitness')
        axes[1].set_title('Population Fitness Evolution')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_evolution(self, resolution=200):
        """
        ------------------------------------------------------------------------
        绘制种群在搜索空间中的进化分布图

        展示种群如何从分散的随机初始值，逐渐聚集到全局最优解附近。
        依赖：需要在 run() 之后调用，使用 all_pop_history
        ------------------------------------------------------------------------
        """
        lower, upper = self.X_BOUND
        x_plot = np.linspace(lower, upper, resolution)
        y_plot = self.func(x_plot.reshape(-1, 1)).flatten()

        n_snapshots = len(self.all_pop_history)
        cols = min(4, n_snapshots)
        rows = (n_snapshots + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows))
        if rows * cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        for idx, (gen, pop_x, fitness) in enumerate(self.all_pop_history):
            ax = axes[idx]
            ax.plot(x_plot, y_plot, 'k-', linewidth=0.5, alpha=0.5)
            # 适应度越高，点越大
            sizes = (fitness - fitness.min()) / (fitness.max() - fitness.min() + 1e-10) * 80 + 10
            ax.scatter(pop_x, self.func(pop_x.reshape(-1, 1)).flatten(),
                       c=fitness, cmap='viridis', s=sizes, alpha=0.8, edgecolors='k', linewidth=0.3)
            ax.set_title(f'Generation {gen}')
            ax.set_xlabel('x')
            ax.set_ylabel('f(x)')
            ax.grid(True, alpha=0.3)

        # 隐藏多余的 subplot
        for idx in range(n_snapshots, len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()
        return fig


# ============================================================================
# 预定义测试函数
# ============================================================================

def rastrigin_func(x):
    """
    ----------------------------------------------------------------------------
    Rastrigin 函数：经典的多峰优化测试函数

    f(x) = 10*n + sum(x_i^2 - 10*cos(2*pi*x_i))
    对于 n=1: f(x) = 10 + x^2 - 10*cos(2*pi*x)

    特点：
    - 全局最小值在 x=0 处，f(0)=0
    - 有大量局部最小值，容易陷入局部最优
    - 是测试遗传算法全局搜索能力的理想函数

    搜索范围推荐：[-5.12, 5.12]
    ----------------------------------------------------------------------------
    """
    return 10 + x**2 - 10 * np.cos(2 * np.pi * x)


def ackley_func(x):
    """
    ----------------------------------------------------------------------------
    Ackley 函数：另一个经典多峰测试函数

    特点：
    - 全局最小值在 x=0 处，f(0)=0
    - 外部平坦，中心有一个深谷
    - 有许多局部最小值

    搜索范围推荐：[-5, 5]
    ----------------------------------------------------------------------------
    """
    n = 1
    sum1 = x**2
    sum2 = np.cos(2 * np.pi * x)
    term1 = -20 * np.exp(-0.2 * np.sqrt(sum1 / n))
    term2 = -np.exp(sum2 / n)
    return term1 + term2 + 20 + np.e
