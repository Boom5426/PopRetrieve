# PopRetrieve Phase-II：Transition-to-Intervention Retrieval

## 0. 总原则：任务冻结，禁止漂移

### 唯一任务

给定：

\[
X_{\text{source}},\quad
X_{\text{target}},\quad
\mathcal D
\]

其中：

- \(X_{\text{source}}\)：目标 cellular context 的 untreated/control 单细胞 population；
- \(X_{\text{target}}\)：希望达到的 treated single-cell target population；
- \(\mathcal D=\{d_1,\ldots,d_N\}\)：固定 candidate drug library。

输出：

\[
R=(d_{(1)},d_{(2)},\ldots,d_{(N)})
\]

即：

> 哪一个 candidate drug 最可能把 source population 转变成 target population。

正式写成：

\[
d^*=
\arg\min_{d\in\mathcal D}
D\left(
\hat X_d,
X_{\text{target}}
\right),
\]

其中

\[
\hat X_d=f_\theta(X_{\text{source}},d)
\]

是 forward perturbation predictor 对 candidate drug \(d\) 的预测结果。

---

## 1. 严格禁止改变的内容

后续任何实验、模型或分析都不得修改以下定义。

### 输入冻结

输入永远是：

\[
X_{\text{source}}+
X_{\text{target}}+
\text{candidate drug IDs}
\]

不能偷偷改成：

- target response 单独作为 query；
- observed candidate response 直接作为 primary retrieval 输入；
- drug–drug response similarity；
- MoA label 作为 query；
- 已知 query drug identity。

### 输出冻结

唯一模型输出：

\[
\text{candidate drug ranking}
\]

不能把主任务改成：

- response prediction；
- clustering；
- drug classification；
- state classification；
- response similarity estimation。

这些只能作为 diagnostic。

### 泛化轴冻结

Primary generalization axis：

\[
\text{unseen cellular context, seen candidate drugs}
\]

即：

> candidate drugs 在训练 contexts 中可以出现，但 target cellular context 的所有 treated cells 必须完全 held out。

不要后续改成 unseen-drug prediction。

### Ground truth 冻结

对于 benchmark query \(q\)：

\[
X_{\text{target}}
=
X^{\text{observed}}_{q,c}
\]

算法不知道 \(q\) 的 identity。

真实 generating drug：

\[
q
\]

用于 exact retrieval evaluation。

所以 benchmark 是一个 controlled intervention-selection problem：

> 给 source + desired target，找回能够实现该 transition 的 intervention。

这和 Fig.2 最大的区别是：

> primary retrieval 阶段绝对不能看到 held-out context 中任何 candidate drug 的真实 treated response。

---

## 2. 数据集层级冻结

### Primary：Tahoe-100M plate 3

使用当前稿件相同版本：

- 50 cell lines；
- 93 compounds；
- DMSO_TF controls；
- released 2,304-gene log1p representation。

选择 Tahoe 作为 primary 的原因：

1. 完整 drug × cell-line grid；
2. 50 个独立 cellular contexts；
3. 当前 Fig.5 已经在使用它；
4. 当前稿件最大缺口就是 Tahoe 没真正跑 intervention retrieval。

### Secondary replication

SciPlex3。

但 **task definition、split、metrics 全部完全相同**。

不能为了 SciPlex3 重新定义另一套任务。

---

## 3. 数据冻结与 eligibility audit

第一步只允许做数据审计，不训练任何模型。

对 Tahoe：

固定 candidate library 为 plate 3 的 93 compounds。

Query eligibility：

\[
n_{\text{treated}}\ge100
\]

并要求该 cell line 有足够 DMSO control cells。

如果某个 query-condition 不满足 cell threshold：

> 只排除该 query，不允许因为 retrieval performance 排除 drug。

输出：

`TRANSITION_RETRIEVAL_TASK_FREEZE.md`

其中记录：

- 最终 50 cell lines；
- 93 candidate drugs；
- eligible query 数；
- 每个 context 的 cell counts；
- exclusion reasons；
- fixed random seeds。

完成后 candidate pool 和 query pool **永久冻结**。

---

## 4. Primary split：Leave-One-Cell-Line-Out

这是最关键的一条。

对于 target cell line \(c\)：

### Training

允许使用：

\[
\{X_{d,c'}:c'\neq c\}
\]

即其余 49 个 cell lines 的：

- controls；
- treated cells；
- 所有 candidate drugs。

### Test / inference

允许使用：

\[
X_{\text{source}}=X_{0,c}
\]

也就是 held-out cell line 的 untreated controls。

以及当前 query 的：

\[
X_{\text{target}}=X_{q,c}
\]

因为 desired target state 本来就是 task input。

但是：

> held-out cell line 中除 query target 本身之外的任何 treated response，都不允许进入 predictor、representation fitting 或 candidate ranking。

尤其禁止：

\[
X_{d,c}^{obs}
\rightarrow
retriever
\]

这是最重要的 leakage rule。

---

## 5. Target query construction

对每一个：

\[
(c,q)
\]

建立一个 query。

### Source

从：

\[
X_{0,c}
\]

固定抽取最多 200 control cells。

### Target

从：

\[
X_{q,c}
\]

固定抽取最多 200 treated cells。

做 5 个固定随机 seeds：

\[
\{13,29,47,71,101\}
\]

所有 mean 和 population 方法使用 **完全相同的 cell samples**。

---

## 6. Response definition 冻结

继续使用稿件现有定义，不创造新 normalization。

对 target：

\[
P_{\text{target}}
=
\{
x_i^{target}-\mu_{\text{source}}
\}
\]

其中：

\[
\mu_{\text{source}}
=
\operatorname{mean}(X_{\text{source}})
\]

对于 predictor 生成的 candidate：

\[
\hat P_d
=
\{
\hat x_{i,d}-\mu_{\text{source}}
\}
\]

因此 mean retrieval 和 population retrieval 比较的是 **同一个 transition**，区别只有保留多少 population information。

---

## 7. Phase A：Oracle Response-Bank Ceiling

这一步非常重要，但必须明确：

\[
\text{它不是 primary deployment task}
\]

它回答的是：

> 假设 virtual cell 能完美预测所有 candidate outcomes，population information 理论上有没有足够大的 decision value？

这是 retrieval ceiling。

### Oracle candidate responses

暂时用 held-out context 中真实 candidate responses：

\[
P_{d,c}^{obs}
\]

代替：

\[
\hat P_{d,c}
\]

但必须保证 query 与 oracle candidate bank **cell-disjoint**。

对于 generating drug \(q\)：

\[
X_{q,c}
=
X_{q,c}^{query}
\cup
X_{q,c}^{oracle}
\]

两个集合 cell ID 不重叠。

如果有 batch / replicate 标签，优先 batch-disjoint；

没有则固定 random split-half，并明确标记：

> oracle information ceiling, not deployment evaluation。

### Oracle Mean

\[
s_d^{mean}
=
\cos
\left(
\bar P_{\text{target}},
\bar P_{d,c}^{obs}
\right)
\]

### Oracle Population

Primary：

\[
s_d^{pop}
=
-\operatorname{Energy}
\left(
P_{\text{target}},
P_{d,c}^{obs}
\right)
\]

Secondary：

- MMD；
- sliced Wasserstein。

不要在这里继续开发十几个距离函数。

---

## 8. Phase A 的核心问题

必须回答：

\[
\text{With perfect candidate outcomes, does population information improve intervention selection?}
\]

这一步决定整个项目后续。

如果 oracle population 都不比 oracle mean 好：

> forward model 再强也无法创造 decision value。

如果 oracle population 明显优于 mean：

> 那么存在真正的 population-information ceiling，下一步才值得研究 predictor 是否把它保留下来。

---

## 9. Phase B：真正的 Predict-then-Retrieve

此时彻底移除 held-out context 的 observed candidate responses。

对于每个：

\[
d\in\mathcal D
\]

预测：

\[
\hat X_{d,c}
=
f_\theta(X_{0,c},d)
\]

得到：

\[
\hat P_{d,c}
\]

然后使用与 Phase A 完全相同的 retrieval rules。

### Mean

\[
s_d^{mean}
=
\cos
(
\bar P_{target},
\bar{\hat P}_{d,c}
)
\]

### Population

\[
s_d^{pop}
=
-
Energy
(
P_{target},
\hat P_{d,c}
)
\]

于是：

\[
R^{mean}
\quad vs \quad
R^{population}
\]

所有其他东西完全固定。

---

## 10. Predictor 集合冻结

这一步 **不是 predictor leaderboard**。

不要跑 20 个 foundation models。

第一轮只允许使用现稿已有、能够明确解释结构差异的 predictor family：

| Predictor | 作用 |
|---|---|
| Average-effect | additive lower baseline |
| Nearest-context transfer | simple context-transfer baseline |
| Linear-latent | latent additive baseline |
| OT mapping | cell-dependent / non-additive reference |

如果现有实现可以在严格 LOCO 下运行，就原样迁移。

不允许为了拿高分修改 task。

scGen 可以作为 secondary，但不是必须。

当前阶段的目的不是比较现代模型谁最好，而是判断：

> oracle ceiling 在 prediction 后损失在哪里？

---

## 11. Evaluation metrics 冻结

### Primary metric：MRR

真实 generating drug 的 rank：

\[
r_q
\]

定义：

\[
MRR=
\frac1N
\sum_q
\frac1{r_q}
\]

为什么用 MRR 做 primary：

> 不是只看第一名，而是直接反映整个 candidate ranking 中 true intervention 被推到多前。

### Secondary exact-retrieval metrics

固定：

\[
Hit@1
\]

\[
Hit@5
\]

\[
Hit@10
\]

### Secondary biological metric

固定：

\[
MoA\text{-}nDCG@10
\]

仅对 candidate pool 中存在 same-MoA candidates 的 query 计算。

### 必须报告 absolute performance

禁止只报：

\[
population-mean
\]

必须同时报告：

\[
MRR_{mean},\quad MRR_{population}
\]

以及：

\[
\Delta MRR
\]

否则容易出现“两边都很差但差值为正”的误导。

---

## 12. Phase C：把 Fig.5 三个 Gate 真正闭环

现稿提出：

\[
Differential\ response
\rightarrow
Recoverability
\rightarrow
Decision\ relevance
\]

这次直接在 **同一个 transition retrieval task** 上测。

### Gate 1：Differential response

沿用当前 Fig.5 的定义。

在 held-out context 的 controls 上预先定义两个 cellular states。

对于真实 response：

\[
r_{q,c,1},r_{q,c,2}
\]

计算：

\[
D_{q,c}
=
1-
\cos(r_{q,c,1},r_{q,c,2})
\]

越大：

> state-specific perturbation effect 越强。

同时对 predicted population 计算：

\[
\hat D_{q,c}
\]

得到：

\[
\text{differential-response fidelity}
\]

---

### Gate 2：Recoverability

沿用现有 supervised-vs-unsupervised framework。

记录：

\[
A_{sup}
\]

\[
A_{unsup}
\]

以及：

\[
G=A_{sup}-A_{unsup}
\]

并明确区分：

#### information-limited

\[
A_{sup}\text{ low}
\]

#### algorithm-limited

\[
A_{sup}\text{ high},\quad A_{unsup}\text{ low}
\]

---

### Gate 3：Decision relevance

这次不要再只用 state-ordering correlation。

直接使用真实 retrieval outcome。

对每个 query 定义：

\[
\Delta rank
=
rank_{mean}(q)
-
rank_{population}(q)
\]

如果：

\[
\Delta rank>0
\]

说明 population information 真正把正确 intervention 向前移动了。

再定义：

\[
Flip@1
=
\mathbf 1[
Top1_{mean}\neq Top1_{population}
]
\]

以及：

\[
CorrectedFlip@1
=
\mathbf 1[
Top1_{population}=q,\,
Top1_{mean}\neq q
]
\]

最后这个尤其重要：

> population information 是否真的把一个错误 decision 改成正确 decision？

这才是真正的 decision relevance。

---

## 13. 三 Gate 的最终联合分析

不要分别画完就结束。

必须回答：

> population gain 是否集中在 differential response 强且 recoverability 高的 query？

固定分析：

横轴：

\[
D=\text{differential response}
\]

纵轴：

\[
A_{sup}
\quad\text{or}\quad
G
\]

每个 query 的 outcome：

\[
\Delta MRR
\quad\text{or}\quad
CorrectedFlip@1
\]

先按预定义 quartiles 分层，不允许看结果后重新找 threshold。

最终形成一个二维 grid：

| | Low recoverability | High recoverability |
|---|---:|---:|
| Low differential response | population 不应有明显 gain | 不应有明显 gain |
| High differential response | information present but inaccessible | **population-benefit candidate regime** |

如果右下角仍然没有 retrieval gain：

> 三条件框架需要进一步修正，不能强行解释为 positive。

---

## 14. Oracle → Prediction decomposition

对于每个 query：

\[
\Delta MRR_{\text{oracle}}
\]

vs

\[
\Delta MRR_{\text{predicted}}
\]

分四种情况：

### I. Oracle 无 gain，Prediction 无 gain

→ **decision relevance 不足**

### II. Oracle 有 gain，Prediction 无 gain

→ **forward predictor bottleneck**

### III. Oracle 有 gain，Prediction 也有 gain

→ **真正成功的 population-aware intervention regime**

### IV. Oracle 无 gain，Prediction反而有 gain

→ 可疑，需要检查 noise / ranking artefact。

这样第一次能回答：

> population information 到底在哪一步丢掉？

---

## 15. 预注册式停止规则

AI 不允许无休止扩实验。

### Case A：Oracle population 没有实质 gain

如果在主数据上：

- \(\Delta MRR\) 很小；
- Hit@1/5/10 都无稳定提升；
- bootstrap CI 大部分覆盖 0；

则：

> **停止开发更复杂 predictor。**

结论：

\[
\text{decision relevance is the bottleneck}
\]

最多跑一个 additive predictor 做确认。

### Case B：Oracle 明显有 gain，但 predicted 没有

结论：

\[
\text{prediction is the bottleneck}
\]

此时才允许启动“更强 non-additive predictor”分支。

仍然不得改变 retrieval task。

### Case C：Oracle 和 predicted 都有 gain

进入机制分析：

> 哪些 contexts / drugs 满足 three-gate regime？

这才值得进一步扩展。

---

## 16. 严禁的行为

AI 执行中禁止：

1. 根据结果挑 drug；
2. 根据结果挑 cell line；
3. 重新调 candidate pool；
4. 改 primary metric；
5. 用 held-out treated cells fit PCA / encoder / scaler；
6. primary task 中读取 candidate observed target-context responses；
7. query drug identity 进入模型；
8. 把 Oracle 当成 deployable result；
9. 为了拿 positive result 改成 smaller candidate pool；
10. 用 MoA labels 训练 retrieval model；
11. 把 task 改回 response-response matching；
12. 如果结果 negative 就另造一个任务。

---

## 17. AI 必须输出的文件

```text
01_TRANSITION_TASK_FREEZE.md
02_DATA_ELIGIBILITY_AUDIT.md
03_ORACLE_RETRIEVAL_RESULTS.md
04_LOCO_PREDICTED_RETRIEVAL.md
05_DIFFERENTIAL_RESPONSE_AUDIT.md
06_RECOVERABILITY_AUDIT.md
07_DECISION_RELEVANCE_AUDIT.md
08_THREE_GATE_ANALYSIS.md
09_ORACLE_TO_PREDICTION_DECOMPOSITION.md
10_FINAL_VERDICT.md
```

其中 `10_FINAL_VERDICT.md` 只能回答四个问题：

1. 在 candidate outcomes 完美已知时，population information 是否改善 source→target intervention retrieval？
2. 在 leakage-safe forward prediction 后，这个优势还剩多少？
3. 丢失主要发生在 differential response、recoverability 还是 decision relevance？
4. 是否存在可重复的 real population-sensitive intervention regime？

---

## 18. 如果实验成功，Fig.5 应该怎么升级

### a
真实任务：

\[
Source + Target + Drugs
\rightarrow
Predict
\rightarrow
Rank
\]

### b
Oracle mean vs population：

> perfect outcome knowledge 下 population 有没有价值。

### c
Predicted mean vs population：

> virtual cell 后这个价值剩多少。

### d
Oracle → predicted gap：

> 定位 predictor bottleneck。

### e
Differential-response fidelity。

### f
Recoverability：

> information-limited vs algorithm-limited。

### g
Direct decision relevance：

\[
\Delta rank / CorrectedFlip@1
\]

### h
Three-gate regime。

### i
不同 context 的 Hit@1/5/10 / MRR。

### j
Tahoe large-scale summary。

最终 Fig.5 从：

> “我们提出三个必要条件”

升级为：

\[
\text{Source-to-target intervention retrieval}
\rightarrow
\text{oracle ceiling}
\rightarrow
\text{prediction bottleneck}
\rightarrow
\text{three measured gates}
\]

---

# 执行总指令

> **不要为了 positive result 改任务。Task 一旦按本文件冻结，后面允许变的只有 predictor；输入、输出、candidate pool、split 和 evaluation definitions 全部禁止修改。**
