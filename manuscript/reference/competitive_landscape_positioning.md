# PopRetrieve 竞争 landscape 与定位 memo

版本 2026-07-12。目的: 回答"我们是不是第一个做 distributional drug retrieval"这个定位问题, 并据此给出可辩护的高度定位。
全文无 em dash。所有外部工作均来自 2026-07-12 文献检索, 引用见文末。

## 0. 一句话结论

"第一个做 distributional drug retrieval" 这个主张站不住, distributional 单细胞扰动是一个 2023 至 2025 高度拥挤、还在爆发的领域。
但有一个比"第一个方法"更高、且真实可辩护的定位: **第一个揭示 distributional 单细胞检索里的评测循环性, 并给出判断 distributional 收益何时可信的框架 (统一定理 + 探针 + 双门判据)。** 这是站在拥挤领域之上做评测透镜, 不是声称领先于它。

## 1. 已被占领的地盘 (naked "first" 会被打的点)

| 主张 | 谁已经做了 | 证据 |
|---|---|---|
| distributional distance (energy/MMD/Wasserstein) 用于单细胞扰动 | CellOT (Bunne et al., Nat Methods 2023, 用 MMD); Departures (2025, Schrödinger Bridge OT); StateXDiff (2025, Wasserstein); Meta Flow Matching (2024); RAG-perturbation (2026, energy distance 作 primary objective) | 高度占领, prediction 任务 |
| mean/bulk signature 丢失亚群分辨率的批判 | scRNA CMap mTOR 论文明确说 "averaged signatures from bulk lack the resolution to identify effective agents" | 已被陈述 |
| 比较 distributional 距离度量用于单细胞评测 | "Optimal distance metrics for scRNA-seq populations" (biorxiv 2023); "Standardized Framework for Evaluating Gene Expression Generative Models" (2026) | 已被占领, 但针对 generative model 评测 |
| CMap 可复现性/可靠性批判 | "Evaluation of connectivity map shows limited reproducibility" (Sci Rep 2021) | 已被占领 |
| 单细胞药物 repurposing | ASGARD (Nat Commun 2023, per-cluster DEG + CLUE) | 已被占领, signature-based |
| 样本级/群体到群体 Wasserstein 比较 | PILOT (patient-level OT, 2024) | 已被占领 |

结论: distributional 工具、mean 批判、metric 比较、CMap 批判、单细胞 repurposing, 五条线全部有人。

## 2. 真正还开着的地盘 (PopRetrieve 的真实新意)

1. **统一定理**: mean-signature/CMap cosine 是 distributional 家族在零方差处的塌缩成员, 在实现核下数值恒等 (Hit@1 三位一致 0.389)。我没有检索到任何工作陈述过这个代数恒等式。这是让"公平比较"成立的地基。
2. **检索任务的循环性审计**: 现有 metric-comparison 论文比较度量在 generative model 评测里的表现, 但没有把它框成"当检索 SCORE 和评测 METRIC 是同一个 distributional 对象时, 提升是自我实现的"这个循环性问题。PopRetrieve 的 knife 在这里, 且针对 retrieval/ranking 任务, 不是 prediction。
3. **双门信息条件**: 结构保留 (predictor 塌缩 5x) + 结构可识别 (真实亚群 ARI<0.15), 作为 distributional 分辨率何时可能有回报的判据。未见先例。

## 3. 两篇必须正面区分的威胁论文 (否则会被当 prior art 引)

- **"Optimal distance metrics for single-cell RNA-seq populations" (biorxiv 2023.12.26)**: 比较 distributional 距离度量。区分点: 它评的是 generative model 的 distribution 是否 match true; PopRetrieve 评的是 retrieval 排序, 且核心是 score 与 metric 同源导致的循环性, 不是"哪个度量更好"。
- **"Standardized Framework for Evaluating Gene Expression Generative Models" (2026)**: distributional metric (OT/MMD/energy) 评 generative model。区分点同上: 它是 generative eval 的标准化, PopRetrieve 是 retrieval 评测的循环性诊断。

手稿 related work 必须显式点名这两篇并划清 retrieval-vs-generative + circularity 这两条界线, 否则审稿人会说"metric comparison 已有人做"。

## 4. 可辩护的高度定位 (推荐)

不要说: "我们发明了 distributional drug retrieval。" (假, 会被打)
要说: "distributional 方法正在涌入单细胞扰动 (CellOT/Departures/StateXDiff/RAG-perturbation, 都用 energy/MMD/Wasserstein), 且几乎总被 distributional 度量评测。我们提供第一个原则性框架, 把真实的 distributional 收益与评测 artifact 分开。" (真, 高度更高, 且 timely)

这个定位的三个好处:
1. 可辩护: 不在新意上送人头。
2. 高度更高: 它是整个 distributional 扰动子领域的评测透镜, 而非又一个方法。
3. timely: 领域 2025 正在爆发, editor 会觉得"领域正需要这个"。

代价: 这是一个 evaluation/audit overview, 不是 method-invention overview。用户想要的"overview 高度"可以拿到, 但方式是"审计透镜", 不是"我们最先做的"。

## 5. 对引言与图的影响

- 引言 P1/P2 应显式挂到"distributional 方法正在涌入 + 都用 distributional 度量自评"这个 timely 张力上 (点名 CellOT 一类), 让 editor 第一段就看到领域热度 + 我们的独特角度。
- 引言 related-work 段必须区分两篇威胁论文 (retrieval-vs-generative, circularity)。
- Figure 1 的钩子可以强化为"领域在涌入 distributional, 但没人检验收益真假", 把 PopRetrieve 定位成透镜。
- 其余图不受影响, 证据链不变。

## 参考 (2026-07-12 检索)

- Bunne et al. Learning single-cell perturbation responses using neural optimal transport (CellOT). Nature Methods 2023. (MMD distributional distance, prediction)
- Departures: Distributional Transport for Single-Cell Perturbation Prediction with Neural Schrödinger Bridges. arXiv 2511.13124, 2025.
- StateXDiff: Cell State-Contextualized Multimodal Diffusion for Single-Cell Perturbation Prediction. arXiv 2605.16104, 2025.
- Retrieval-Augmented Generation for Predicting Cellular Responses to Gene Perturbation. arXiv 2603.07233, 2026. (energy distance primary objective)
- Optimal distance metrics for single-cell RNA-seq populations. bioRxiv 2023.12.26.572833.
- A Standardized Framework For Evaluating Gene Expression Generative Models. arXiv 2603.11244, 2026.
- ASGARD: A Single-cell Guided Pipeline to Aid Repurposing of Drugs. Nature Communications 2023.
- Evaluation of connectivity map shows limited reproducibility in drug repositioning. Scientific Reports 2021.
- Connectivity Map Analysis of a scRNA-seq-Derived Transcriptional Signature of mTOR Signaling. PMC8122562. (states bulk-averaging loses subpopulation resolution)
- PILOT: patient-level distances from single-cell data with optimal transport. 2024.
