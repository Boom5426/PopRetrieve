# 引言 (v5 审计透镜稿, 中文)

版本 2026-07-12。相对 v4 的改动: P1/P2 从"我们的方法"重构为"领域正在涌入 distributional 方法且几乎都用 distributional 度量自评"这个 timely 张力 (点名 CellOT 一类); 新增一段 related work 划清与两篇威胁论文的界线 (retrieval-vs-generative + circularity 两条轴)。定位: 审计透镜, 不是 first method。全文无 em dash。定稿后译回英文进手稿。

---

[P1 立场与赌注]
单细胞技术改变了我们对"一个药物的效果"的理解: 它不是一个数字, 而是一个分布。在一群被处理的细胞里, 不同亚群的响应可以截然不同, 而决定治疗结局的往往正是那个少数派状态, 一个持留细胞 (persister)、一个耐药克隆。正是这个前提, 驱动了当前一轮对 virtual cell、单细胞基础模型和扰动响应预测器的巨大投入: 如果我们能在单细胞分辨率上刻画响应, 我们就应该能比那些把群体抹平成均值的方法, 比如 Connectivity Map, 更好地对候选药物排序。

[P2 领域涌入 + 循环自评, 新钩子]
这个前提正在快速转化成方法。近两年, 一批工作把群体到群体的 distributional 距离 (optimal transport、maximum-mean-discrepancy、energy distance、Wasserstein) 引入单细胞扰动建模, 以刻画均值之外的响应结构。它们几乎无一例外地报告, 相对均值方法有可观的提升。但这里有一个很少被正面追问的问题: 这些方法几乎总是被 distributional 的度量所评测。一个 distributional 的模型, 被一个 distributional 的标尺打分, 然后赢, 这个"赢"到底有多少是真实的决策改善, 有多少只是方法与标尺共享了同一个数学目标, 这个问题被系统性地少问了。

[P3 循环性, 知识内核]
我们指出这为什么要紧: 单细胞扰动检索的评测里存在一个结构性的循环。当一个 distributional 检索方法被一个本身就是 distributional 的度量评判时, 一个 energy-distance 的 regret、一个基于 discrepancy 的 welfare proxy, 评测和方法共享同一个数学目标, 于是"提升"几乎是被保证的。这不是某一篇论文的疏忽, 它是"让目标和标尺对齐"这件事的固有性质。后果是: "distributional 方法更好"这句话, 可以在领域自己的度量下为真, 同时在任何一个外部 oracle 会真正在意的判据下为假, 比如机制回收 (mechanism recovery)、真实的细胞活性 (viability)。

[P4 仪器 + 统一]
为了严格地探查这一点, 我们引入 DART, 一族群体到群体的 distributional 检索打分 (energy、maximum-mean-discrepancy、sliced-Wasserstein、subpopulation-coverage)。关键在于, 我们证明 mean-signature 检索, 包括 CMap cosine, 不是一个竞争者, 而是同一族在零方差处的塌缩成员: 在实现所用的核下, 两者数值恒等 (Hit@1 三位一致)。这个统一让比较变得精确 (mean 是 DART 自己的退化极限, 不是一个稻草人), 也让我们可以把 DART 当作一个受控探针来用: 拧动方差, 拧动度量类别, 观察结论如何随之变化。

[P5 发现: 崩塌 + 机制/正面载荷]
在 SciPlex3、Frangieh、CD34+ 数据上, distributional 检索在 objective-aligned 度量下看起来很强 (energy Hit@1 0.837 对 0.389), 但这个优势不迁移: 机制回收是平的 (MoA-nDCG −0.013), 没有一个真实任务是 distributional 占优的 (0/37), 一个为集中优势而构建的 gate 也失败了。随后我们从机制上解释这个塌缩, 而这正是本文的 affirmative 载荷: distributional 信息在今天不可用, 有两个彼此独立的原因。当前的扰动预测器把候选群体塌缩向它们的均值 (亚群方差损失约五倍), 而即便在真实数据里, 这些亚群本身也无法被可靠地识别 (没有任何无监督方法能回收已知的双峰结构, ARI < 0.15)。我们把这形式化为一个双门判据: 结构必须先被保留, 而且必须可识别, 单细胞分辨率才可能开始有回报。

[P6 与已有评测工作的区分, 防御段]
我们的角度与两条相邻的工作线不同。一条线为 distributional 单细胞扰动建模提供预测方法 (基于 optimal transport 或 Schrödinger bridge 的响应预测), 但它们研究如何更好地预测扰动结果, 而非如何检索/排序候选药物, 也不检验评测本身是否循环。另一条线为生成式单细胞模型比较 distributional 评测度量, 但它们问的是"哪个度量更好地衡量一个生成分布是否匹配真实分布", 而我们问的是一个正交的问题: 当检索 score 与评测 metric 是同一个 distributional 对象时, 报告出来的提升在多大程度上是自我实现的。据我们所知, 这个循环性, 以及 mean-signature 是 distributional 检索零方差塌缩极限这一恒等式, 此前都没有被陈述过。

[P7 读者拿走什么 / 为什么出版]
这些发现给了这个快速增长的领域三样它当前没有的东西。一个检验: 一个探针 (以及一个合成基准, HIR-Bench), 用来判断一个 distributional 的收益是真实的还是循环的。一个诊断: 一个被命名的失败模式 (evaluation circularity), 它很可能在远超药物检索的范围内高估结果。一张路线图: 两个具体的、可测量的门, 它们告诉一个 virtual-cell 建模者, 在声称"单细胞分辨率改善了决策"之前, 需要先修好什么。DART 最好被理解为一件仪器, 用来知道 distributional 信息何时可信, 而不是一个被验证的治疗推荐器; 而随着单细胞基础模型的扩散, 这个问题只会变得更紧迫, 不会更不重要。
