# 作业1：启发式算法 — 遗传算法 (Genetic Algorithm)

## 参考资料

- GitHub: https://github.com/guofei9987/scikit-opt (优秀的启发式算法 Python 库，含遗传算法、粒子群、模拟退火等)
- CSDN: https://blog.csdn.net/u010835747/article/details/80038372 (遗传算法原理与Python实现详解)
- 博客园: https://www.cnblogs.com/LoganChen/p/12597272.html (遗传算法入门教程)
- 维基百科: https://en.wikipedia.org/wiki/Genetic_algorithm

## 参考文献

[1] Holland, J.H. (1975). Adaptation in Natural and Artificial Systems. University of Michigan Press.
[2] Goldberg, D.E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning. Addison-Wesley.
[3] scikit-opt 开源项目: https://github.com/guofei9987/scikit-opt

## 文件说明

| 文件 | 说明 |
|------|------|
| `genetic_algorithm.py` | 遗传算法核心实现，包含 `GeneticAlgorithm` 类和测试函数 |
| `test_ga.py` | 测试与可视化程序，依赖 `genetic_algorithm.py` |
| `README.md` | 本文件 |

## 文件依赖关系

```
test_ga.py ──→ genetic_algorithm.py
```

`test_ga.py` 导入 `genetic_algorithm.py` 中的 `GeneticAlgorithm` 类、`rastrigin_func` 和 `ackley_func` 函数。

## 运行方法

```bash
cd 作业1
python3 test_ga.py
```

## 算法简介

遗传算法 (Genetic Algorithm, GA) 是一种模拟自然界"物竞天择，适者生存"进化规律的启发式搜索算法。基本流程：

1. **编码**：将问题的解编码为"染色体"（DNA），本实现使用二进制编码
2. **初始化种群**：随机生成一组候选解
3. **计算适应度**：用目标函数评价每个个体的优劣
4. **选择**：按适应度比例选出优良个体作为父代（轮盘赌法）
5. **交叉**：父代基因片段交换产生子代（单点交叉）
6. **变异**：子代基因以一定概率随机改变（位翻转变异）
7. **迭代**：重复步骤3-6，直到满足终止条件

## 测试函数

- **Rastrigin 函数**：f(x) = 10 + x^2 - 10cos(2πx)，全局最小值 f(0)=0，有大量局部最小值
- **Ackley 函数**：有多个局部最小值，全局最小值 f(0)=0
