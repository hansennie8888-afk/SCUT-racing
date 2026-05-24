**搜索算法与机器学习 — 作业记录**  
**作业 1：遗传算法 (Genetic Algorithm)**  
**为什么选 GA**  
启发式算法很多——模拟退火、粒子群、蚁群、差分进化……选 GA 是因为它的"适者生存"隐喻特别直观，而且其二进制编码、选择、交叉、变异每一步都能可视化，很适合理解启发式搜索的核心思想。  
**实现过程**  
参考了 scikit-opt 的源码风格和网上的几篇博客（见文末链接），写了一个 GeneticAlgorithm 类。用二进制编码，轮盘赌选择，单点交叉，位翻转变异，加上精英保留。  
**运行结果分析**  
测试函数选了 Rastrigin 和 Ackley：  
- **Rastrigin**：几乎每次都能收敛到全局最优 (x≈0, f(x)≈0)。这个函数虽然有大量局部极小值，但它们分布均匀，GA 的种群多样性加上变异操作能有效跳出局部陷阱。  
- **Ackley**：也找到了全局最优，但比 Rastrigin 慢一些。我猜是因为 Ackley 外部非常平坦（梯度信息弱），初期种群在平坦区域时适应度差异小，选择压力不够强。  
参数实验的发现：  
- **种群规模**：Pop=100 明显比 50 好，但 200 和 100 差距不大——边际收益递减  
- **变异率**：0.001 太低，容易早熟；0.05 太高，变成随机搜索；0.01 左右是个甜点  
- **精英保留**：有精英保留时收敛曲线平滑很多，否则最优解会振荡——这很直观，保证最好的基因不会因为交叉变异被破坏  
   
   
   
**作业 2：多元线性回归 + 正则化**  
**正规方程 vs 梯度下降**  
结果和 sklearn 完全一致（R²=0.5871）。梯度下降在 5000 轮后也收敛到了几乎相同的结果。十分有趣的是数据标准化后梯度下降收敛很快，但如果不标准化，代价函数会震荡——因为各特征尺度差异太大，等高线变成狭长的椭圆。  
**正则化实验**  
| | | | |  
|-|-|-|-|  
| **方法** | **最佳 R²** | **最佳 λ** | **备注** |   
| 无正则化 | 0.5871 | - | 基准 |   
| Ridge (L2) | 0.5888 | 0.001 | λ 增大后性能下降明显 |   
| Lasso (L1) | 0.5890 | 0.001 | 理论上应做特征选择 |   
| ElasticNet | 0.5016 | 0.1 | 混合效果不如预期 |   
   
一个意外的发现：Lasso 没有像预期那样把很多特征压缩到零。反思了一下，简单次梯度下降对于 L1 的精确稀疏化确实力不从心——实际工程中通常用坐标下降或 proximal gradient（如 sklearn 的 Lasso）。不过在小 λ 下确实有一个特征权重趋近于零，方向是对的。  
**数据问题**  
sklearn 的 fetch_california_housing 死活下不下来（HTTP 403/504），最后从 GitHub 上 ageron/handson-ml2 的仓库找到了 housing.csv。而且数据里有 207 行 total_bedrooms 缺失，一开始忘了 dropna()，MSE 直接 NaN，debug 了好久。  
   
   
   
   
   
   
   
**作业 3：** **用** **SVM 对 Iris 分类**  
**三种核函数**  
| | | |  
|-|-|-|  
| **Kernel** | **准确率** | **感受** |   
| Linear | 91.11% | 简单直接，Iris 数据线性可分性不错 |   
| RBF | 91.11% | 和 Linear 持平，说明非线性边界在这里提升有限 |   
| Poly | 86.67% | 反而更差，可能 degree=3 过拟合或参数不够好 |   
   
GridSearchCV 最优参数是 C=0.1, kernel='linear'，说明 Iris 这个数据集本身线性可分性就很好，不需要复杂核函数。  
**PCA 可视化**  
即使降到 2 维后 RBF SVM 仍然有很好的分类效果。Setosa 和其他两类几乎完美分离，Versicolor 和 Virginica 有少量重叠——这和实际数据特点一致。  
   
   
   
   
   
   
   
   
   
   
   
   
   
   
**作业 4：K-Means 聚类**  
**补全过程**  
notebook 框架搭好了，需要补全 6 个函数。整体逻辑很清晰：  
初始化中心 → 簇分配 → 计算代价 → 更新中心 → 检查停机 → 循环  
   
需要注意的细节：  
- init_centers 用 np.random.choice 保证不重复  
- center_update 里用 np.allclose 判断中心是否变化（浮点数不能用 ==）  
- cost_function 要处理空簇的情况  
**K 值选择**  
从散点图观察估计 k=3，k-cost 曲线也在 k=3 出现明显的肘部。最终代价函数值约 3.89。  
**K-Means 的问题**  
K-Means 对初始中心敏感——初始中心选得不好可能收敛到局部最优。运行多次会发现代价有小波动。另外它假设簇是球形的，如果数据有细长形状的簇就分不好。这些问题在看散点图时能直观感受到。  
**总体学习体会**  
1. **"手搓一遍"真的很重要**：调包时觉得简单的算法，自己写才会发现各种细节（矩阵可逆性、梯度符号、浮点比较、空簇处理……）  
2. **可视化是调试利器**：GA 的种群分布图、K-Means 的迭代过程图、回归的残差分布图，比单纯看数字直观太多了  
3. **正则化不是万能的**：L1/L2 对加州房价数据提升有限，说明数据集本身没有严重的过拟合问题  
4. **数据清洗永远是大头**：缺失值、标准化、特征工程，这些比模型选型更耗时  
   
   
**环境配置踩坑记录**  
环境是一台没有 pip、没有 Jupyter、部分包版本冲突的 Ubuntu 机器，配置过程堪称经典：  
**第一关：没有 pip**  
$ pip3 install seaborn  
 bash: pip3: command not found  
   
ensurepip 也没装，apt 需要 sudo 又没有密码。最后靠 curl 下载 get-pip.py，用 python3 get-pip.py --user 装上 pip。  
**第二关：numpy 版本冲突**  
pip 默认装了 numpy 2.2.6，但系统的 matplotlib 和 scipy 是用 numpy 1.x 编译的。导入 matplotlib 直接报：  
AttributeError: _ARRAY_API not found  
 ImportError: numpy.core.multiarray failed to import  
   
解决办法是把 numpy 降回 1.x（pip install "numpy<2"），但这又引发了连锁反应——sklearn 1.7 要求 numpy ≥2，于是 sklearn 也要降级到 1.5。scipy 虽然能跑但全程 Warning："A NumPy version >=1.17.3 and <1.25.0 is required"。属于能用但有精神污染的水平。  
**第三关：加州房价数据集下不下来**  
fetch_california_housing() 背后是从 figshare 下载数据，试了 N 次：  
直连 → HTTP 403 Forbidden  
原始网站 (dcc.fc.up.pt) → 504 Gateway Timeout  
手动 curl 加 User-Agent → 也不行  
最后在 GitHub 上 ageron/handson-ml2 仓库找到了 housing.csv（实际是一个 399KB 的 tgz，里面就一个 housing.csv）。下载后还要解压放到 ~/scikit_learn_data/，但 sklearn 还是会尝试先联网下载再 fallback 到缓存……最后干脆跳过 sklearn 的 fetcher，直接 pd.read_csv 手动读。  
**第四关：缺失值**  
housing.csv 有 207 行 total_bedrooms 是 NaN。一开始没注意，跑回归时 mean_squared_error 直接报 ValueError: Input contains NaN，R² 只能全变成 nan。dropna() 。  
**第五关：Jupyter nbconvert 不兼容**  
装完 Jupyter 想执行 notebook 验证，nbconvert --execute 报了 AttributeError: 'RcParams' object has no attribute '_get'。原因是系统 matplotlib 版本太老，和 pip 装的 matplotlib-inline 不兼容。升级 matplotlib 到 3.10 解决，但旧的 scipy 又开始报警告（上面第二关那个）.......  
**总结**  
这套环境的核心矛盾是：**系统 apt 装的包（matplotlib、scipy）和 pip 装的包（numpy、sklearn）版本互相不对付**。如果重来一次，最优解可能是全部用 pip 装或者全部用 apt 装，不要混用。或者直接用 conda 。  
   
**参考资料**  
- 遗传算法：https://github.com/guofei9987/scikit-opt | [https://blog.csdn.net/u010835747/article/details/80038372](https://blog.csdn.net/u010835747/article/details/80038372 "https://blog.csdn.net/u010835747/article/details/80038372")  
- 线性回归：sklearn 官方文档 | CS229 线性回归讲义  
- SVM：https://scikit-learn.org/stable/modules/svm.html  
- K-Means：https://scikit-learn.org/stable/modules/clustering.html#k-means  
- 加州房价数据集：https://github.com/ageron/handson-ml2 (housing.csv)  
- Holland, J.H. (1975). *Adaptation in Natural and Artificial Systems*  
- Goldberg, D.E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*  
   
