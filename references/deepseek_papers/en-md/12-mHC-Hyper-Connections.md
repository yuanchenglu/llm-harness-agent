
<!-- Page 1 -->

m HC: Manifold-Constrained Hyper-Connections
Zhenda Xie* † , Yixuan Wei*, Huanqi Cao*,
Chenggang Zhao, Chengqi Deng, Jiashi Li, Damai Dai, Huazuo Gao, Jiang Chang,
Kuai Yu, Liang Zhao, Shangyan Zhou, Zhean Xu, Zhengyan Zhang, Wangding Zeng,
Shengding Hu, Yuqing Wang, Jingyang Yuan, Lean Wang, Wenfeng Liang
DeepSeek-AI
Abstract
Recently, studies exemplified by Hyper-Connections (HC) have extended the ubiquitous resid-
ual connection paradigm established over the past decade by expanding the residual stream
width and diversifying connectivity patterns.   While yielding substantial performance gains,
this   diversification   fundamentally   compromises   the   identity   mapping   property   intrinsic   to
the residual connection, which causes severe training instability and restricted scalability, and
additionally   incurs   notable   memory   access   overhead.   To   address   these   challenges,   we   pro-
pose  Manifold-Constrained Hyper-Connections  ( m HC ), a general framework that projects
the residual connection space of HC onto a specific manifold to restore the identity mapping
property,   while incorporating rigorous infrastructure optimization to ensure efficiency.   Em-
pirical experiments demonstrate that  m HC is effective for training at scale, offering tangible
performance improvements and superior scalability.   We anticipate that  m HC, as a flexible and
practical extension of HC, will contribute to a deeper understanding of topological architecture
design and suggest promising directions for the evolution of foundational models.
(a) Residual Connection
(b) Hyper-Connections (HC)
(c) Manifold-Constrained HC ( m HC)
Layer  ℱ
x !
x !"#
Res Mapping
ℋ !
$%&
Pre Mapping
ℋ !
'$%
Post Mapping
ℋ !
'(&)
Layer  ℱ
h !
$%&
h !
*+
h !
(,)
Res Mapping
𝒫 ℳ !"# (ℋ !
$%& )
Pre Mapping
𝒫 ℳ $!" (ℋ !
'$% )
Post Mapping
𝒫 ℳ $%#& (ℋ !
'(&) )
Layer  ℱ
h !
$%&
h !
*+
h !
(,)
Figure 1  |  Illustrations of Residual Connection Paradigms.   This figure compares the structural
design of (a) standard Residual Connection, (b) Hyper-Connections (HC), and (c) our proposed
Manifold-Constrained Hyper-Connections  ( m HC ). Unlike the unconstrained HC,  m HC focuses
on   optimizing   the   residual   connection   space   by   projecting   the   matrices   onto   a   constrained
manifold to ensure stability.
*Core contributors.   † Corresponding author:   xie.zhenda@deepseek.com
arXiv:2512.24880v2  [cs.CL]  5 Jan 2026


|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
| x !"# | x !"# |  |  |  |
|  |  |  |  |  |



|  |  |  |  |  |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
| x !"# | x !"# |  |  |  |
|  |  |  |  |  |



| h'(&) ! | h'(&) |  |
| --- | --- | --- |



| h'(&) ! | h'(&) |  |
| --- | --- | --- |



|  |  |  |
| --- | --- | --- |
| x ! |  |  |



|  |  |  |
| --- | --- | --- |
| x ! |  |  |


---


<!-- Page 2 -->

Contents
1
Introduction
3
2
Related Works
4
2.1
Micro Design
.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
4
2.2
Macro Design   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
5
3
Preliminary
5
3.1
Numerical Instability   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
6
3.2
System Overhead   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
7
4
Method
8
4.1
Manifold-Constrained Hyper-Connections
.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
8
4.2
Parameterization and Manifold Projection   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
9
4.3
Efficient Infrastructure Design   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
9
4.3.1
Kernel Fusion   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
9
4.3.2
Recomputing   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
10
4.3.3
Overlapping Communication in DualPipe
.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
11
5
Experiments
12
5.1
Experimental Setup   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
12
5.2
Main Results   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
12
5.3
Scaling Experiments
.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
13
5.4
Stability Analysis   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
14
6
Conclusion and Outlook
15
A   Appendix
19
A.1   Detailed Model Specifications and Hyper-parameters.   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .
19
2

---


<!-- Page 3 -->

1.   Introduction
Deep neural network architectures have undergone rapid evolution since the introduction of
ResNets   (He   et   al.,   2016a).   As   illustrated   in   Fig.   1(a),   the   structure   of   a   single-layer   can   be
formulated as follows:
x 𝑙 + 1   =  x 𝑙 + F ( x 𝑙 ,  W 𝑙 ) ,
(1)
where   x 𝑙 and   x 𝑙 + 1   denote   the   𝐶 -dimensional   input   and   output   of   the   𝑙 -th   layer,   respectively,
and   F   represents the residual function.   Although the residual function   F   has evolved over
the past decade to include various operations such as convolution, attention mechanisms, and
feed forward networks, the paradigm of the residual connection has maintained its original
form.   Accompanying the progression of Transformer (Vaswani et al., 2017) architecture, this
paradigm has currently established itself as a fundamental design element in large language
models (LLMs) (Brown et al., 2020; Liu et al., 2024b; Touvron et al., 2023).
This success is primarily attributed to the concise form of the residual connection.   More
importantly, early research (He et al., 2016b) revealed that the identity mapping property of the
residual connection maintains stability and efficiency during large-scale training.   By recursively
extending the residual connection across multiple layers, Eq. (1) yields:
x 𝐿 =  x 𝑙 +
𝐿 − 1
∑︁
𝑖 = 𝑙
F ( x 𝑖 ,  W 𝑖 ) ,
(2)
where   𝐿 and   𝑙 correspond   to   deeper   and   shallower   layers,   respectively.   The   term   identity
mapping refers to the component  x 𝑙 itself, which emphasizes the property that the signal from
the shallower layer maps directly to the deeper layer without any modification.
Recently, studies exemplified by Hyper-Connections (HC) (Zhu et al., 2024) have introduced
a   new   dimension   to   the   residual   connection   and   empirically   demonstrated   its   performance
potential. The single-layer architecture of HC is illustrated in Fig. 1(b). By expanding the width of
the residual stream and enhancing connection complexity, HC significantly increases topological
complexity without altering the computational overhead of individual units regarding FLOPs.
Formally, single-layer propagation in HC is defined as:
x 𝑙 + 1   =  H res
𝑙
x 𝑙 + H post  ⊤
𝑙
F (H pre
𝑙
x 𝑙 ,  W 𝑙 ) ,
(3)
where  x 𝑙 and  x 𝑙 + 1  denote the input and output of the  𝑙 -th layer, respectively.   Unlike the formu-
lation in Eq.  (1) , the feature dimension of  x 𝑙 and  x 𝑙 + 1   is expanded from   𝐶 to   𝑛 ×  𝐶 , where   𝑛 is
the expansion rate.   The term  H res
𝑙
∈ R 𝑛 × 𝑛 represents a learnable mapping that mixes features
within the residual stream.   Also as a learnable mapping,  H pre
𝑙
∈ R 1 × 𝑛 aggregates features from
the  𝑛𝐶 -dim stream into a  𝐶 -dim layer input, and conversely,  H post
𝑙
∈ R 1 × 𝑛 maps the layer output
back onto the stream.
However, as the training scale increases, HC introduces potential risks of instability.   The
primary concern is that the unconstrained nature of HC compromises the identity mapping
property   when   the   architecture   extends   across   multiple   layers.   In   architectures   comprising
multiple parallel streams, an ideal identity mapping serves as a conservation mechanism.   It
ensures that the average signal intensity across streams remains invariant during both forward
and backward propagation.   Recursively extending HC to multiple layers via Eq. (3) yields:
x 𝐿 =
� 𝐿 − 𝑙
�
𝑖 = 1
H res
𝐿 − 𝑖
�
x 𝑙 +
𝐿 − 1
∑︁
𝑖 = 𝑙
��
�
𝐿 − 1 − 𝑖
�
𝑗 = 1
H res
𝐿 − 𝑗
��
�
H post  ⊤
𝑖
F (H pre
𝑖
x 𝑖 ,  W 𝑖 ) ,
(4)
3

---


<!-- Page 4 -->

where   𝐿 and  𝑙 represent a deeper layer and a shallower layer, respectively.   In contrast to Eq.  (2) ,
the composite mapping   � 𝐿 − 𝑙
𝑖 = 1   H res
𝐿 − 𝑖 in HC fails to preserve the global mean of the features.   This
discrepancy   leads   to   unbounded   signal   amplification   or   attenuation,   resulting   in   instability
during large-scale training.   A further consideration is that, while HC preserves computational
efficiency in terms of FLOPs, the hardware efficiency concerning memory access costs for the
widened residual stream remains unaddressed in the original design.   These factors collectively
restrict the practical scalability of HC and hinder its application in large-scale training.
To address these challenges, we propose  Manifold-Constrained Hyper-Connections  ( m HC ),
as shown in Fig. 1(c), a general framework that projects the residual connection space of HC
onto a specific manifold to restore the identity mapping property, while incorporating rigorous
infrastructure optimization to ensure efficiency.   Specifically,  m HC utilizes the Sinkhorn-Knopp
algorithm (Sinkhorn and Knopp, 1967) to entropically project  H res
𝑙
onto the Birkhoff polytope.
This   operation   effectively   constrains   the   residual   connection   matrices   within   the   manifold
that   is   constituted   by   doubly   stochastic   matrices.   Since   the   row   and   column   sums   of   these
matrices equal to 1, the operation  H res
𝑙
x 𝑙 functions as a convex combination of the input features.
This   characteristic   facilitates   a   well-conditioned   signal   propagation   where   the   feature   mean
is   conserved,   and   the   signal   norm   is   strictly   regularized,   effectively   mitigating   the   risk   of
vanishing or exploding signals.   Furthermore, due to the closure of matrix multiplication for
doubly stochastic matrices, the composite mapping   � 𝐿 − 𝑙
𝑖 = 1   H res
𝐿 − 𝑖 retains this conservation property.
Consequently,  m HC effectively maintains the stability of identity mappings between arbitrary
depths.   To ensure efficiency,   we employ kernel fusion and develop mixed precision kernels
utilizing TileLang (Wang et al., 2025).   Furthermore, we mitigate the memory footprint through
selective recomputing and carefully overlap communication within the DualPipe schedule (Liu
et al., 2024b).
Extensive   experiments   on   language   model   pretraining   demonstrate   that   m HC   exhibits
exceptional stability and scalability while maintaining the performance advantages of HC. In-
house large-scale training indicates that  m HC supports training at scale and introduces only a
6.7% additional time overhead when expansion rate  𝑛 =  4.
2.   Related Works
Architectural advancements in deep learning can be primarily classified into  micro-design  and
macro-design . Micro-design concerns the internal architecture of computational blocks, specifying
how   features   are   processed   across   spatial,   temporal,   and   channel   dimensions.   In   contrast,
macro-design establishes the inter-block topological structure, thereby dictating how feature
representations are propagated, routed, and merged across distinct layers.
2.1.   Micro Design
Driven by parameter sharing and translation invariance, convolution initially dominated the pro-
cessing of structured signals.   While subsequent variations such as depthwise separable (Chollet,
2017)   and   grouped   convolutions   (Xie   et   al.,   2017)   optimized   efficiency,   the   advent   of   Trans-
formers (Vaswani et al., 2017) established Attention and Feed-Forward Networks (FFNs) as
the   fundamental   building   blocks   of   modern   architecture.   Attention   mechanisms   facilitate
global information propagation, while FFNs enhance the representational capacity of individual
features.   To balance performance with the computational demands of LLMs, attention mecha-
nisms have evolved towards efficient variants such as Multi-Query Attention (MQA) (Shazeer,
2019), Grouped-Query Attention (GQA) (Ainslie et al., 2023), and Multi-Head Latent Attention
4

---


<!-- Page 5 -->

(MLA) (Liu et al., 2024a).   Simultaneously, FFNs have been generalized into sparse computing
paradigms via Mixture-of-Experts (MoE) (Fedus et al., 2022; Lepikhin et al., 2020; Shazeer et al.,
2017), allowing for massive parameter scaling without proportional computational costs.
2.2.   Macro Design
Macro-design governs the global topology of the network (Srivastava et al., 2015).   Following
ResNet   (He   et   al.,   2016a),   architectures   such   as   DenseNet   (Huang   et   al.,   2017)   and   Fractal-
Net (Larsson et al., 2016) aimed to enhance performance by increasing topological complexity
through dense connectivity and multi-path structures, respectively.   Deep Layer Aggregation
(DLA) (Yu et al., 2018) further extended this paradigm by recursively aggregating features across
various depths and resolutions.
More recently,   the focus of macro-design has shifted toward expanding the width of the
residual   stream   (Chai   et   al.,   2020;   Fang   et   al.,   2023;   Heddes   et   al.,   2025;   Mak   and   Flanigan,
2025; Menghani et al., 2025; Pagliardini et al., 2024; Xiao et al., 2025; Xie et al., 2023; Zhu et al.,
2024).   Hyper-Connections (HC) (Zhu et al., 2024) introduced learnable matrices to modulate
connection strengths among features at varying depths, while the Residual Matrix Transformer
(RMT) (Mak and Flanigan, 2025) replaced the standard residual stream with an outer-product
memory matrix to facilitate feature storage.   Similarly, MUDDFormer (Xiao et al., 2025) employs
multiway dynamic dense connections to optimize cross-layer information flow.   Despite their
potential, these approaches compromise the inherent identity mapping property of the residual
connection, thereby introducing instability and hindering scalability.   Furthermore, they incur
significant   memory   access   overhead   due   to   expanded   feature   widths.   Building   upon   HC,
the proposed  m HC restricts the residual connection space onto a specific manifold to restore
the identity mapping property, while also incorporating rigorous infrastructure optimizations
to   ensure   efficiency.   This   approach   enhances   stability   and   scalability   while   maintaining   the
topological benefits of expanded connections.
3.   Preliminary
We first establish the notation used in this work. In the HC formulation, the input to the  𝑙 -th layer,
x 𝑙 ∈ R 1 × 𝐶 , is expanded by a factor of  𝑛 to construct a hidden matrix  x 𝑙 =  ( x ⊤
𝑙 ,0 ,  . . .  ,  x ⊤
𝑙 , 𝑛 − 1 ) ⊤ ∈ R 𝑛 × 𝐶
which can be viewed as   𝑛 -stream residual.   This operation effectively broadens the width of
the residual stream.   To govern the read-out, write-in, and updating processes of this stream,
HC introduces three learnable linear mappings— H pre
𝑙
,  H post
𝑙
∈ R 1 × 𝑛 , and  H res
𝑙
∈ R 𝑛 × 𝑛 .   These
mappings modify the standard residual connection shown in Eq.  (1) , resulting in the formulation
given in Eq. (3).
In the HC formulation, learnable mappings are composed of two parts of coefficients:   the
input-dependent one and the global one, referred to as dynamic mappings and static mappings,
respectively.   Formally, HC computes the coefficients as follows:


˜ x 𝑙 =  RMSNorm ( x 𝑙 )
H pre
𝑙
=  𝛼 pre
𝑙
·  tanh ( 𝜃 pre
𝑙
˜ x ⊤
𝑙 ) +  b pre
𝑙
H post
𝑙
=  𝛼 post
𝑙
·  tanh ( 𝜃 post
𝑙
˜ x ⊤
𝑙 ) +  b post
𝑙
H res
𝑙
=  𝛼 res
𝑙
·  tanh ( 𝜃 res
𝑙
˜ x ⊤
𝑙 ) +  b res
𝑙 ,
(5)
where  RMSNorm (·)  (Zhang and Sennrich, 2019) is applied to the last dimension, and the scalars
𝛼 pre
𝑙
,  𝛼 post
𝑙
and   𝛼 res
𝑙
∈ R   are   learnable   gating   factors   initialized   to   small   values.   The   dynamic
5

---


<!-- Page 6 -->

mappings are derived via linear projections parameterized by  𝜃 pre
𝑙
,  𝜃 post
𝑙
∈ R 1 × 𝐶 and  𝜃 res
𝑙
∈ R 𝑛 × 𝐶 ,
while the static mappings are represented by learnable biases  b pre
𝑙
,  b post
𝑙
∈ R 1 × 𝑛 and  b res
𝑙
∈ R 𝑛 × 𝑛 .
It is worth noting that the introduction of these mappings— H pre
𝑙
,  H post
𝑙
, and  H res
𝑙
—incurs
negligible computational overhead, as the typical expansion rate  𝑛 , e.g.   4, is much smaller than
the input dimension   𝐶 .   With this design,   HC effectively decouples the information capacity
of the residual stream from the layer’s input dimension, which is strongly correlated with the
model’s computational complexity (FLOPs).   Consequently, HC offers a new avenue for scaling
by adjusting the residual stream width, complementing the traditional scaling dimensions of
model FLOPs and training data size discussed in pre-training scaling laws (Hoffmann et al.,
2022).
Although HC necessitates three mappings to manage the dimensional mismatch between
the residual stream and the layer input, preliminary experiments presented in Tab. 1 indicate
that   the   residual   mapping   H res
𝑙
yields   the   most   significant   performance   gain.   This   finding
underscores the critical importance of effective information exchange within the residual stream.
Table 1  |  Ablation Study of HC Components.   When a specific mapping ( H pre
𝑙
,  H post
𝑙
, or  H res
𝑙
) is
disabled, we employ a fixed mapping to maintain dimensional consistency:   uniform weights of
1 / 𝑛 for  H pre
𝑙
, uniform weights of ones for  H post
𝑙
, and the identity matrix for  H res
𝑙
.
H res
𝑙
H pre
𝑙
H post
𝑙
Absolute Loss Gap
3.1.   Numerical Instability
While the residual mapping  H res
𝑙
is instrumental for performance, its sequential application
poses a significant risk to numerical stability.   As detailed in Eq.  (4) , when HC is extended across
multiple layers, the effective signal propagation from layer  𝑙 to   𝐿 is governed by the composite
mapping   � 𝐿 − 𝑙
𝑖 = 1   H res
𝐿 − 𝑖 .   Since the learnable mapping  H res
𝑙
is unconstrained, this composite mapping
inevitably deviates from the identity mapping.   Consequently, the signal magnitude is prone to
explosion or vanishing during both the forward pass and backpropagation.   This phenomenon
undermines the fundamental premise of residual learning, which relies on unimpeded signal
flow, thereby destabilizing the training process in deeper or larger-scale models.
Empirical evidence supports this analysis.   We observe unstable loss behavior in large-scale
experiments, as illustrated in Fig. 2.   Taking  m HC as the baseline, HC exhibits an unexpected
loss surge around the 12k step, which is highly correlated with the instability in the gradient
norm.   Furthermore, the analysis on  H res
𝑙
validates the mechanism of this instability.   To quantify
how the composite mapping   � 𝐿 − 𝑙
𝑖 = 1   H res
𝐿 − 𝑖 amplifies signals along the residual stream, we utilize
two metrics.   The first, based on the maximum absolute value of the row sums of the composite
mapping,   captures the worst-case expansion in the forward pass.   The second,   based on the
maximum absolute column sum, corresponds to the backward pass.   We refer to these metrics
as the  Amax Gain Magnitude  of the composite mapping.   As shown in Fig. 3 (b), the Amax Gain
Magnitude yields extreme values with peaks of 3000, a stark divergence from 1 that confirms
the presence of exploding residual streams.
6


| ✓ ✓ ✓ ✓ ✓ ✓ | 0.0 −0.022 −0.025 −0.027 |
| --- | --- |


---


<!-- Page 7 -->

0
10000
20000
30000
40000
50000
Steps
-0.002
0.000
0.002
0.004
0.006
0.008
0.010
0.012
Absolute Loss Gap
(a) Absolute Training Loss Gap  vs.   Training Steps
m HC
HC
0
10000
20000
30000
40000
50000
Steps
0.00
0.05
0.10
0.15
0.20
0.25
Grad Norm
(b) Gradient Norm  vs.   Training Steps
m HC
HC
Figure 2  |  Training Instability of Hyper-Connections (HC).  This figure illustrates (a) the absolute
loss gap of HC relative to  m HC, and (b) the comparisons of gradient norms.   All results are based
on 27B models.
0
10
20
30
40
50
60
Layer Index  l
10 0
10 1
Amax Gain Magnitude
(a) Single-Layer Mapping
0
10
20
30
40
50
60
Layer Index  l
10 1
10 2
10 3
10 4
10 5
Amax Gain Magnitude
(b) Composite Mapping
Figure   3   |   Propagation   Instability   of   Hyper-Connections   (HC).   This   figure   illustrates   the
propagation   dynamics   of   (a)   the   single-layer   mapping   H res
𝑙
and   (b)   the   composite   mapping
� 𝐿 − 𝑙
𝑖 = 1   H res
𝐿 − 𝑖 within the 27B model.   The layer index  𝑙 (x-axis) unrolls each standard Transformer
block into two independent layers (Attention and FFN). The Amax Gain Magnitude (y-axis) is
calculated as the maximum absolute row sum (for the forward signal) and column sum (for the
backward gradient), averaged over all tokens in a selected sequence.
3.2.   System Overhead
While   the   computational   complexity   of   HC   remains   manageable   due   to   the   linearity   of   the
additional mappings, the system-level overhead prevents a non-negligible challenge. Specifically,
memory access (I/O) costs often constitute one of the primary bottlenecks in modern model
architectures, which is widely referred to as the “memory wall” (Dao et al., 2022). This bottleneck
is frequently overlooked in architectural design, yet it decisively impacts runtime efficiency.
Focusing on the widely adopted pre-norm Transformer (Vaswani et al., 2017) architecture,
we analyze the I/O patterns inherent to HC. Tab. 2 summarizes the per token memory access
overhead in a single residual layer introduced by the   𝑛 -stream residual design.   The analysis
reveals that HC increases the memory access cost by a factor approximately proportional to  𝑛 .
This excessive I/O demand significantly degrades training throughput without the mitigation of
fused kernels.   Besides, since  H pre
𝑙
,  H post
𝑙
, and  H res
𝑙
involve learnable parameters, their interme-
diate activations are required for backpropagation.   This results in a substantial increase in the
GPU memory footprint, often necessitating gradient checkpointing to maintain feasible memory
usage.   Furthermore, HC requires  𝑛 -fold more communication cost in pipeline parallelism (Qi
et al., 2024), leading to larger bubbles and decreasing the training throughput.
7


|  |  |
| --- | --- |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
| 10000 20000 30000 Steps (a) Absolute Training Loss Gap vs. Train |  |



|  |  | Signal Gain d Gradient Gain |  |
| --- | --- | --- | --- |
|  | Hr es Forward l Hr es Backwar l |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |



|  |  |  | Gain |
| --- | --- | --- | --- |
|  |  | Yl 1Hr e +s Forward Signal i = l 1 −i Y | Gain |
|  |  | 6 i 1 = − 1 l Hr 6e 1s −i Backward Gradi | ent Gain |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |


---


<!-- Page 8 -->

Table   2   |   Comparison   of   Memory   Access   Costs   Per   Token.   This   analysis   accounts   for   the
overhead introduced by the residual stream maintenance in the forward pass, excluding the
internal I/O of the layer function  F  .
Method
Operation
Read (Elements)
Write (Elements)
Residual
Connection
Residual Merge
2 𝐶
𝐶
Hyper-
Connections
Calculate  H pre
𝑙
,  H post
𝑙
,  H res
𝑙
𝑛𝐶
𝑛 2   +  2 𝑛
H pre
𝑙
𝑛𝐶 +  𝑛
𝐶
H post
𝑙
𝐶 +  𝑛
𝑛𝐶
H res
𝑙
𝑛𝐶 +  𝑛 2
𝑛𝐶
Residual Merge
2 𝑛𝐶
𝑛𝐶
Total I/O
( 5n  +  1 ) C  +  n 2   +  2n
( 3n  +  1 ) C  +  n 2   +  2n
4.   Method
4.1.   Manifold-Constrained Hyper-Connections
Drawing inspiration from the identity mapping principle (He et al., 2016b), the core premise
of  m HC is to constrain the residual mapping  H res
𝑙
onto a specific manifold.   While the original
identity mapping ensures stability by enforcing  H res
𝑙
=  I , it fundamentally precludes information
exchange within the residual stream,   which is critical for maximizing the potential of multi-
stream architectures.   Therefore, we propose projecting the residual mapping onto a manifold
that simultaneously maintains the stability of signal propagation across layers and facilitates
mutual interaction among residual streams to preserve the model’s expressivity.   To this end,
we restrict  H res
𝑙
to be a doubly stochastic matrix, which has non-negative entries where both
the rows and columns sum to 1.   Formally, let  M res   denote the manifold of doubly stochastic
matrices (also known as the Birkhoff polytope).   We constrain  H res
𝑙
to  P M res (H res
𝑙
) , defined as:
P M res (H res
𝑙
)   ≔
�
H res
𝑙
∈ R 𝑛 × 𝑛 |   H res
𝑙
1 𝑛 =  1 𝑛 ,   1 ⊤
𝑛 H res
𝑙
=  1 ⊤
𝑛 ,   H res
𝑙
⩾ 0
�
,
(6)
where  1 𝑛 represents the  𝑛 -dimensional vector of all ones.
It is worth noting that when  𝑛 =  1, the doubly stochastic condition degenerates to the scalar
1, thereby recovering the original identity mapping.   The choice of double stochasticity confers
several rigorous theoretical properties beneficial for large-scale model training:
1.   Norm   Preservation:   The   spectral   norm   of   a   doubly   stochastic   matrix   is   bounded   by   1
(i.e.,   ∥H res
𝑙
∥ 2   ≤ 1).   This implies that the learnable mapping is non-expansive, effectively
mitigating the gradient explosion problem.
2.   Compositional   Closure:   The   set   of   doubly   stochastic   matrices   is   closed   under   matrix
multiplication.   This ensures that the composite residual mapping across multiple layers,
� 𝐿 − 𝑙
𝑖 = 1   H res
𝐿 − 𝑖 , remains doubly stochastic, thereby preserving stability throughout the entire
depth of the model.
3.   Geometric   Interpretation   via   the   Birkhoff   Polytope:   The   set   M res   forms   the   Birkhoff
polytope,   which is the convex hull of the set of permutation matrices.   This provides a
clear   geometric   interpretation:   the   residual   mapping   acts   as   a   convex   combination   of
permutations.   Mathematically, the repeated application of such matrices tends to increase
8


| Connection | Total I/O 2C C |
| --- | --- |


---


<!-- Page 9 -->

the mixing of information across streams monotonically, effectively functioning as a robust
feature fusion mechanism.
Additionally, we impose non-negativity constraints on the input mappings  H pre
𝑙
and output
mappings  H post
𝑙
.   This constrain prevents signal cancellation arising from the composition of
positive and negative coefficients, which can also be considered as a special manifold projection.
4.2.   Parameterization and Manifold Projection
In   this   section,   we   detail   the   calculation   process   of   H pre
𝑙
,  H post
𝑙
,  and  H res
𝑙
in   m HC.   Given   the
input hidden matrix  x 𝑙 ∈ R 𝑛 × 𝐶 at the  𝑙 -th layer, we first flatten it into a vector  � x 𝑙 =  vec ( x 𝑙 )   ∈ R 1 × 𝑛𝐶
to preserve full context information.   Then, we follow the original HC formulation to get the
dynamic mappings and the static mappings as follows:


� x ′
𝑙 =  RMSNorm (� x 𝑙 )
˜ H pre
𝑙
=  𝛼 pre
𝑙
· (� x ′
𝑙 𝜑 pre
𝑙
) +  b pre
𝑙
˜ H post
𝑙
=  𝛼 post
𝑙
· (� x ′
𝑙 𝜑 post
𝑙
) +  b post
𝑙
˜ H res
𝑙
=  𝛼 res
𝑙
·  mat (� x ′
𝑙 𝜑 res
𝑙 ) +  b res
𝑙 ,
(7)
where   𝜑 pre
𝑙
,  𝜑 post
𝑙
∈ R 𝑛𝐶 × 𝑛 and   𝜑 res
𝑙
∈ R 𝑛𝐶 × 𝑛 2   are linear projections for dynamic mappings and
mat (·)  is a reshape function from  R 1 × 𝑛 2   to  R 𝑛 × 𝑛 .
Then, the final constrained mappings are obtained via:


H pre
𝑙
=  𝜎 (   ˜ H pre
𝑙
)
H post
𝑙
=  2 𝜎 (   ˜ H post
𝑙
)
H res
𝑙
=  Sinkhorn-Knopp (   ˜ H res
𝑙
) ,
(8)
where   𝜎 (·)   denotes   the   Sigmoid   function.   The   Sinkhorn-Knopp (·)   operator   firstly   makes   all
elements to be positive via an exponent operator and then conducts iterative normalization
process that alternately rescales rows and columns to sum to 1.   Specifically, given a positive
matrix  M ( 0 )   =  exp (   ˜ H res
𝑙
)   as the start point, the normalization iteration proceeds as:
M ( 𝑡 )   =  T 𝑟
�
T 𝑐 ( M ( 𝑡 − 1 ) )
�
,
(9)
where  T 𝑟 and  T 𝑐 denote row and column normalization, respectively.   This process converges to a
doubly stochastic matrix  H res
𝑙
=  M ( 𝑡 max )   as  𝑡 max   →∞ .   We choose  𝑡 max   =  20 as a practical value in
our experiments.
4.3.   Efficient Infrastructure Design
In this section, we detail the infrastructure design tailored for  m HC. Through rigorous optimiza-
tion, we implement  m HC (with  𝑛 =  4) in large-scale models with a marginal training overhead
of only 6.7%.
4.3.1.   Kernel Fusion
Observing that RMSNorm in  m HC imposes significant latency when operating on the high-
dimensional hidden state  � x 𝑙 ∈ R 1 × 𝑛𝐶 , we reorder the dividing-by-norm operation to follow the
9

---


<!-- Page 10 -->

matrix multiplication.   This optimization maintains mathematical equivalence while improving
efficiency.   Furthermore, we employ mixed-precision strategies to maximize numerical accuracy
without compromising speed, and fuse multiple operations with shared memory access into
unified compute kernels to reduce memory bandwidth bottlenecks.   Based on the inputs and
parameters detailed in Eq.  (10)  to   (13) , we implement three specialized  m HC kernels to compute
H pre
𝑙
,  H post
𝑙
, and  H res
𝑙
.   In these kernels, the biases and linear projections are consolidated into  b 𝑙
and   𝜑 𝑙 , and the RMSNorm weight is also absorbed in   𝜑 𝑙 .
•   Eq.  (14)  to  (15) :   We develop a unified kernel that fuses two scans on   � x 𝑙 , leveraging ma-
trix   multiplication   units   to   maximize   memory   bandwidth   utilization.   The   backward
pass—comprising two matrix multiplications—is similarly consolidated into a single ker-
nel, eliminating redundant reloading of  � x 𝑙 .   Both kernels feature a finely tuned pipeline
(load, cast, compute, store) to efficiently handle mixed-precision processing.
•   Eq.  (16)  to   (18) :   These lightweight operations on small coefficients are opportunistically
fused into a single kernel, significantly reducing kernel launch overhead.
•   Eq.   (19) :   We   implement   the   Sinkhorn-Knopp   iteration   within   a   single   kernel.   For   the
backward pass, we derive a custom backward kernel that recomputes the intermediate
results on-chip and traverses the entire iteration.
𝜑 𝑙 : tfloat32
[ 𝑛𝐶 ,  𝑛 2   +  2 𝑛 ]
(10)
� x 𝑙 : bfloat16
[ 1,  𝑛𝐶 ]
(11)
𝛼 pre
𝑙
,  𝛼 post
𝑙
,  𝛼 res
𝑙
: float32
Scalars
(12)
b 𝑙 : float32
[ 1,  𝑛 2   +  2 𝑛 ]
(13)
� ˜˜ H pre
𝑙
,   ˜˜ H post
𝑙
,   ˜˜ H res
𝑙
�
: float32
=  � x 𝑙 𝜑 𝑙
(14)
𝑟 : float32
=
�� � x 𝑙
��
2   /
√
𝑛𝐶
(15)
�
˜ H pre
𝑙
,   ˜ H post
𝑙
,   ˜ H res
𝑙
�
: float32
=  1 / 𝑟
�
𝛼 pre
𝑙
˜˜ H pre
𝑙
,  𝛼 post
𝑙
˜˜ H post
𝑙
,  𝛼 res
𝑙
˜˜ H res
𝑙
�
+  b 𝑙
(16)
H pre
𝑙
: float32
=  𝜎
�
˜ H pre
𝑙
�
(17)
H post
𝑙
: float32
=  2 𝜎
�
˜ H post
𝑙
�
(18)
H res
𝑙
: float32
=  Sinkhorn-Knopp   � ˜ H res
𝑙
�
(19)
Using   the   coefficients   derived   from   the   aforementioned   kernels,   we   introduce   two   addi-
tional   kernels   to   apply   these   mappings:   one   for   F pre   ≔ H pre
𝑙
x 𝑙 and   another   for   F post,res   ≔
H res
𝑙
x 𝑙 + H post  ⊤
𝑙
F (· ,  ·) .   Through fusing the application of  H post
𝑙
and  H res
𝑙
with residual merging,
we reduce the number of elements read from  ( 3 𝑛 +  1 ) 𝐶 to  ( 𝑛 +  1 ) 𝐶 and the number of elements
written   from   3 𝑛𝐶 to   𝑛𝐶 for   this   kernel.   We   efficiently   implement   the   majority   of   kernels   (ex-
cluding Eq.  (14)  to   (15) ) using TileLang (Wang et al., 2025).   This framework streamlines the
implementation of kernels with complex calculation process and allows us to fully utilize the
memory bandwidth with minimal engineering effort.
4.3.2.   Recomputing
The   𝑛 -stream   residual   design   introduces   substantial   memory   overhead   during   training.   To
mitigate this, we discard the intermediate activations of the  m HC kernels after the forward pass
and recompute them on-the-fly in the backward pass, through re-executing the  m HC kernels
10

---


<!-- Page 11 -->

without the heavy layer function  F  .   Consequently, for a block of   𝐿 𝑟 consecutive layers, we need
only store the input  x 𝑙 0   to the first layer.   Excluding lightweight coefficients while accounting
for the pre-norm with in  F  , Tab.   3 summarizes the intermediate activations preserved for the
backward pass.
Table 3   |   Stored and Recomputed Intermediate Activations  We list per token activation pre-
served for the backward pass and the transient activation recomputed in   𝐿 𝑟 consecutive layers.
Layer  𝑙 0  represents the first layer in   𝐿 𝑟 layers and layer  𝑙 is in   [ 𝑙 0 ,  𝑙 0  +  𝐿 𝑟 − 1 ] .
Activations
x 𝑙 0
F (H pre
𝑙
x 𝑙 ,  W 𝑙 )
x 𝑙
H pre
𝑙
x 𝑙
RMSNorm (H pre
𝑙
x 𝑙 )
Size (Elements)
𝑛𝐶
𝐶
𝑛𝐶
𝐶
𝐶
Stored Method
Every   𝐿 𝑟 layers
Every layer
Transient inside   𝐿 𝑟 layers
Since  m HC kernels recomputation is performed for blocks of   𝐿 𝑟 consecutive layers, given
a total of   𝐿 layers, we must persistently store the first layer input  x 𝑙 0   for all   ⌈ 𝐿
𝐿 𝑟 ⌉ blocks for the
backward pass.   In addition to this resident memory, the recomputation process introduces a
transient memory overhead of  ( 𝑛 +  2 ) 𝐶 ×  𝐿 𝑟 elements for the active block, which determines the
peak memory usage during backpropagation.   Consequently, we determine the optimal block
size   𝐿 ∗
𝑟 by minimizing the total memory footprint corresponded to   𝐿 𝑟 :
𝐿 ∗
𝑟 =  arg min
𝐿 𝑟
�
𝑛𝐶 ×
� 𝐿
𝐿 𝑟
�
+ ( 𝑛 +  2 ) 𝐶 ×  𝐿 𝑟
�
≈
√︂
𝑛𝐿
𝑛 +  2 .
(20)
Furthermore, pipeline parallelism in large-scale training imposes a constraint: recomputation
blocks must not cross pipeline stage boundaries.   Observing that the theoretical optimum   𝐿 ∗
𝑟
typically   aligns   with   the   number   of   layers   per   pipeline   stage,   we   choose   to   synchronize   the
recomputation boundaries with the pipeline stages.
4.3.3.   Overlapping Communication in DualPipe
In large-scale training, pipeline parallelism is the standard practice for mitigating parameter and
gradient memory footprints.   Specifically, we adopt the DualPipe schedule (Liu et al., 2024b),
which   effectively   overlaps   scale-out   interconnected   communication   traffic,   such   as   those   in
expert and pipeline parallelism.   However, compared to the single-stream design, the proposed
𝑛 -stream   residual   in   m HC   incurs   substantial   communication   latency   across   pipeline   stages.
Furthermore, at stage boundaries, the recomputation of  m HC kernels for all   𝐿 𝑟 layers introduces
non-negligible computational overhead.   To address these bottlenecks, we extend the DualPipe
schedule (see Fig. 4) to facilitate improved overlapping of communication and computation at
pipeline stage boundaries.
Notably,   to   prevent   blocking   the   communication   stream,   we   execute   the   F post,res   kernels
of   MLP   (i.e.   FFN)   layers   on   a   dedicated   high-priority   compute   stream.   We   further   refrain
from   employing   persistent   kernels   for   long-running   operations   in   attention   layers,   thereby
preventing extended stalls.   This design enables the preemption of overlapped attention com-
putations, allowing for flexible scheduling while maintaining high utilization of the compute
device’s processing units.   Furthermore, the recomputation process is decoupled from pipeline
communication dependencies, as the initial activation of each stage  x 𝑙 0   is already cached locally.
11


| Size (Elements) Stored Method | 𝑛𝐶 Every 𝐿 𝑟 layers | 𝐶 Every layer | 𝑛𝐶 𝐶 𝐶 Transient inside 𝐿 𝑟 layers |
| --- | --- | --- | --- |


---


<!-- Page 12 -->

MLP (B)
DISPATCH (B)
DISPATCH (F)
MLP (W)
MLP (F)
ATTN (B)
COMBINE (F)
COMBINE (B)
PP Send Recv (F)
PP Send Recv (B)
ℱ !"#$, '(#
)
(F)
ℱ !"#$, '(#
)
(B)
ℱ !"#$, '(#
*
(B)
ℱ !'(
)   (B)
ATTN (W)
ATTN (F)
Whole Stage 
Recompute (B)
ℱ !'(
*   (B)
ℱ !'(
*   (F)
ℱ !"#$, '(#
*
(F)
ℱ !'(
)   (F)
Normal Compute Stream
Communication Stream
High Priority Compute Stream
Figure   4   |   Communication-Computation   Overlapping   for   m HC.   We   extend   the   DualPipe
schedule to handle the overhead introduced by  m HC. Lengths of each block are illustrative only
and do not represent actual duration.   (F), (B), (W) refers to forward pass, backward pass, weight
gradient computation, respectively.   F   A   and  F   M   represents kernels corresponded to Attention
and MLP, respectively.
5.   Experiments
5.1.   Experimental Setup
We validate the proposed method via language model pre-training, conducting a comparative
analysis between the baseline, HC, and our proposed  m HC. Utilizing MoE architectures inspired
by   DeepSeek-V3   (Liu   et   al.,   2024b),   we   train   four   distinct   model   variants   to   cover   different
evaluation regimes.   Specifically, the expansion rate   𝑛 for both HC and  m HC is set to 4.   Our
primary focus is a 27B model trained with a dataset size proportional to its parameters, which
serves   as   the   subject   for   our   system-level   main   results.   Expanding   on   this,   we   analyze   the
compute scaling behavior by incorporating smaller 3B and 9B models trained with proportional
data, which allows us to observe performance trends across varying compute.   Additionally,
to specifically investigate the token scaling behavior, we train a separate 3B model on a fixed
corpus of 1 trillion tokens.   Detailed model configurations and training hyper-parameters are
provided in Appendix A.1.
5.2.   Main Results
10000
20000
30000
40000
50000
Steps
-0.06
-0.04
-0.02
0.00
Absolute Loss Gap
10000
20000
30000
40000
50000
Steps
0.00
0.05
0.10
0.15
0.20
Grad Norm
(b) Gradient Norm  vs.   Training Steps
Baseline
HC
m HC
Figure 5  |  Training Stability of Manifold-Constrained Hyper-Connections ( m HC).  This figure
illustrates (a) the absolute training loss gap of  m HC and HC relative to the baseline,   and (b)
the gradient norm of the three methods.   All experiments utilize the 27B model.   The results
demonstrate that  m HC exhibits improved stability in terms of both loss and gradient norm.
We   begin   by   examining   the   training   stability   and   convergence   of   the   27B   models.   As
illustrated   in   Fig.   5   (a),   m HC   effectively   mitigates   the   training   instability   observed   in   HC,
achieving a final loss reduction of 0.021 compared to the baseline.   This improved stability is
further corroborated by the gradient norm analysis in Fig. 5 (b), where  m HC exhibits significantly
better behavior than HC, maintaining a stable profile comparable to the baseline.
12


| DISPATCH (B) | COMBINE (F) PP Send Recv (F) PP Send |
| --- | --- |



|  |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  | Baseline |
|  |  |  | HC mHC |
| 10000 20000 30000 40000 50 Steps (a) Absolute Training Loss Gap vs. Training Steps |  |  |  |


---


<!-- Page 13 -->

Table   4   |   System-level   Benchmark   Results   for   27B   Models.   This   table   compares   the   zero-
shot and few-shot performance of the Baseline, HC, and  m HC across 8 diverse downstream
benchmarks.   m HC consistently outperforms the Baseline and surpasses HC on the majority of
benchmarks, demonstrating its effectiveness in large-scale pre-training.
# Shots
3-shot
3-shot
8-shot
10-shot
4-shot
5-shot
0-shot
5-shot
Tab. 4 presents the downstream performance across a diverse set of benchmarks (Bisk et al.,
2020; Cobbe et al., 2021; Hendrycks et al., 2020, 2021; Joshi et al., 2017; Zellers et al., 2019).   m HC
yields comprehensive improvements, consistently outperforming the baseline and surpassing
HC   on   the   majority   of   tasks.   Notably,   compared   to   HC,   m HC   further   enhances   the   model’s
reasoning capabilities, delivering performance gains of 2.1% on BBH (Suzgun et al., 2022) and
2.3% on DROP (Dua et al., 2019).
5.3.   Scaling Experiments
10 21
10 22
FLOPs
-0.04
-0.03
-0.02
-0.01
0.00
0.01
0.02
Absolute Loss Gap
10 21
10 22
FLOPs
98.0%
99.0%
100.0%
101.0%
Relative Loss Ratio
2
4
FLOPs
× 10 21
-0.03
-0.02
-0.01
0.00
0.01
Absolute Loss Gap
2
4
FLOPs
× 10 21
98.0%
99.0%
100.0%
101.0%
Relative Loss Ratio
(a) Compute Scaling Curve
(b) Token Scaling Curve
Figure 6  |  Scaling properties of  m HC compared to the Baseline.   (a) Compute Scaling Curve.
Solid lines depict the performance gap across different compute budgets.   Each point represents
a specific compute-optimal configuration of model size and dataset size, scaling from 3B and 9B
to 27B parameters.   (b) Token Scaling Curve.   Trajectory of the 3B model during training.   Each
point represents the model’s performance at different training tokens.   Detailed architectures
and training configurations are provided in Appendix A.1.
To assess the scalability of our approach, we report the relative loss improvement of  m HC
against   the   baseline   across   different   scales.   In   Fig.   6   (a),   we   plot   the   compute   scaling   curve
spanning 3B, 9B, and 27B parameters.   The trajectory indicates that the performance advantage is
robustly maintained even at higher computational budgets, showing only marginal attenuation.
Furthermore,   we   examine   the   within-run   dynamics   in   Fig.   6   (b),   which   presents   the   token
scaling curve for the 3B model.   Collectively, these findings validate the effectiveness of  m HC
in   large-scale   scenarios.   This   conclusion   is   further   corroborated   by   our   in-house   large-scale
training experiments.
13


| Benchmark (Metric) | BBH DROP GSM8K HellaSwag MATH MMLU PIQA TriviaQA (EM) (F1) (EM) (Acc.) (EM) (Acc.) (Acc.) (EM) |
| --- | --- |



| 27B Baseline 27B w/ HC | 43.8 47.0 46.7 73.7 22.0 59.0 78.5 54.3 48.9 51.6 53.2 74.3 26.4 63.0 79.9 56.3 |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 27B w/ mHC | 51.0 | 53.9 | 53.8 | 74.7 | 26.0 | 63.4 | 80.5 | 57.6 |



|  |  |  |  |
| --- | --- | --- | --- |
|  |  | Baseline |  |
|  |  |  |  |
|  |  | mHC |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |



|  |  |  |  |
| --- | --- | --- | --- |
|  |  | Baseline mHC |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |



|  |  |  |
| --- | --- | --- |
|  |  |  |
|  | Basel mHC | ine |
|  |  |  |
|  |  |  |
|  |  |  |



|  |  | ine |
| --- | --- | --- |
|  | Basel mHC |  |
|  |  |  |
|  |  |  |


---


<!-- Page 14 -->

0
10
20
30
40
50
60
Layer Index  l
0.0
0.5
1.0
1.5
2.0
Amax Gain Magnitude
(a) Single-Layer Mapping
0
10
20
30
40
50
60
Layer Index  l
0.0
0.5
1.0
1.5
2.0
Amax Gain Magnitude
(b) Composite Mapping
Y
l
i  = 1 P M res ( H res
l  + 1  − i )  Forward Signal Gain
Y
61  − l
i  = 1   P M res ( H res
61  − i )  Backward Gradient Gain
Figure 7  |  Propagation Stability of Manifold-Constrained Hyper-Connections ( m HC).  This
figure illustrates the propagation dynamics of (a) the single-layer mapping  P M res (H res
𝑙
)   and (b)
the composite mapping   � 𝐿 − 𝑙
𝑖 = 1   P M res (H res
𝐿 − 𝑖 )  within the 27B model.   The results demonstrate that
m HC significantly enhances propagation stability compared to HC.
-6.81   -6.81   -6.81   -6.81
18.73
-15.29
-14.79
-15.88
5.43
4.43
4.43
4.43
-4.07   -3.07   -4.07   -4.07
-3.95   -3.95   -2.95   -3.95
-4.22   -4.22   -4.22   -3.22
HC
H res
1
0.83
0.73
0.66
0.75
0.84
0.67
0.49
0.96
0.94   -0.07   -0.05   0.02
-0.08   0.89   -0.07   -0.07
-0.10   -0.14   0.81   -0.07
0.06
0.05   -0.03   0.87
H res
30
-11.97 -6.86 -10.23-11.89
-21.64
-20.22
22.50
-21.59
-5.58   -3.74   -5.71   -6.60
-6.06   -2.27   -5.33   -6.57
6.08
3.12
6.53
6.77
-6.41   -3.97   -5.72   -5.49
H res
60
1.22
1.04
1.06
1.02
-1.35
6.47
0.03
-0.81
-0.38   -0.33   -0.34   -0.31
1.81
1.56
1.58
1.51
0.01   -0.00   0.01
0.01
-0.23   -0.19   -0.20   -0.19
Y
30
i  = 1 H res
31  − i
-135.4-133.4-489.0273.3
-251.4
-243.0
264.6
-254.8
-69.9   -68.3 -255.3 142.1
-69.1   -66.1 -247.4 139.6
74.8
72.7   268.9 -151.8
-71.2   -71.8 -255.2 143.3
Y
30
i  = 1 H res
61  − i
-259.2-219.1-228.2-221.0
-475.3
-462.8
509.1
-498.5
-132.8-112.2-117.0-113.3
-129.3-109.3-113.9-110.3
142.3 120.2 125.3 121.3
-139.3-117.8-122.6-118.7
Y
60
i  = 1 H res
61  − i
0.98
1.00
0.98
1.04
1.00
1.00
1.00
1.00
0.67
0.09
0.03
0.22
0.26
0.48
0.26
0.00
0.03
0.24
0.00
0.73
0.03
0.20
0.69
0.09
m HC
P M res ( H res
1   )
0.96
1.02
1.04
0.99
1.00
1.00
1.00
1.00
0.96
0.01
0.00
0.04
0.00
0.97
0.03
0.00
0.00
0.00
1.00
0.00
0.00
0.04
0.01
0.95
P M res ( H res
30   )
1.00
1.01
0.99
1.00
1.00
1.00
1.00
1.00
0.92
0.06
0.01
0.01
0.05
0.81
0.01
0.13
0.00
0.01
0.97
0.02
0.03
0.13
0.00
0.84
P M res ( H res
60   )
0.90
1.06
0.93
1.11
1.00
1.00
1.00
1.00
0.30
0.25
0.22
0.24
0.24
0.25
0.25
0.26
0.20
0.24
0.28
0.28
0.17
0.32
0.18
0.34
Y
30
i  = 1 P M res ( H res
31  − i )
0.41
1.50
1.50
0.60
1.00
1.00
1.00
1.00
0.35
0.28
0.17
0.20
0.03
0.62
0.29
0.07
0.01
0.17
0.80
0.02
0.02
0.42
0.25
0.31
Y
30
i  = 1 P M res ( H res
61  − i )
0.88
1.03
1.00
1.11
1.00
1.01
1.01
1.00
0.24
0.26
0.23
0.27
0.23
0.25
0.26
0.27
0.21
0.25
0.27
0.28
0.21
0.27
0.24
0.29
Y
60
i  = 1 P M res ( H res
61  − i )
Figure 8  |  Visualizations of Learnable Mappings.   This figure displays representative single-
layer   and   composite   mappings   for   HC   (first   row)   and   m HC   (second   row).   Each   matrix   is
computed by averaging over all tokens within a selected sequence.   The labels annotated along
the y-axis and x-axis indicate the forward signal gain (row sum) and the backward gradient gain
(column sum), respectively.
5.4.   Stability Analysis
Similar   to   Fig.   3,   Fig.   7   illustrates   the   propagation   stability   of   m HC.   Ideally,   the   single-layer
mapping satisfies the doubly stochastic constraint, implying that both the forward signal gain
and the backward gradient gain should equal to 1.   However, practice implementations utilizing
the Sinkhorn-Knopp algorithm must limit the number of iterations to achieve computational
efficiency.   In our settings, we use 20 iterations to obtain an approximate solution.   Consequently,
as shown in Fig. 7(a), the backward gradient gain deviates slightly from 1.   In the composite case
shown in Fig. 7(b), the deviation increases but remains bounded, reaching a maximum value
of approximately 1.6.   Notably, compared to the maximum gain magnitude of nearly 3000 in
HC,  m HC significantly reduces it by three orders of magnitude.   These results demonstrate that
m HC significantly enhances propagation stability compared to HC, ensuring stable forward
signal and backward gradient flows.   Additionally, Fig. 8 displays representative mappings.   We
observe that for HC, when the maximum gain is large, other values also tend to be significant,
which indicates general instability across all propagation paths.   In contrast,  m HC consistently
yields stable results.
14


|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  | PM PM | res(Hr es) Fo l res(Hr es) Ba l | rward Sig ckward Gr | nal Gain adient Gai | n |
|  |  |  |  |  |  |  |  |



|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |
|  |  | Y |  |  |  |  |  |  |
|  |  |  | Y | l | res |  |  |  |
|  |  | Y | Y | 1PMres( i = 6 i 1 = − 1 l PMres | Hl + 1 −i) Fo (Hr 6e 1s −i) Ba | rward Sig ckward Gr | nal Gain adient Gai | n |
|  |  |  |  |  |  |  |  |  |


---


<!-- Page 15 -->

6.   Conclusion and Outlook
In this paper, we identify that while expanding the width of residual stream and diversifying
connections   yields   performance   gains   as   proposed   in   Hyper-Connections   (HC),   the   uncon-
strained nature of these connections leads to signal divergence.   This disruption compromises
the conservation of signal energy across layers, inducing training instability and hindering the
scalability of deep networks.   To address these challenges, we introduce  Manifold-Constrained
Hyper-Connections  ( m HC ), a generalized framework that projects the residual connection space
onto   a   specific   manifold.   By   employing   the   Sinkhorn-Knopp   algorithm   to   enforce   a   doubly
stochastic constraint on residual mappings,  m HC transforms signal propagation into a convex
combination of features.   Empirical results confirm that  m HC effectively restores the identity
mapping property, enabling stable large-scale training with superior scalability compared to
conventional HC. Crucially, through efficient infrastructure-level optimizations,  m HC delivers
these improvements with negligible computational overhead.
As a generalized extension of the HC paradigm,  m HC opens several promising avenues for
future research.   Although this work utilizes doubly stochastic matrices to ensure stability, the
framework accommodates the exploration of diverse manifold constraints tailored to specific
learning objectives.   We anticipate that further investigation into distinct geometric constraints
could yield novel methods that better optimize the trade-off between plasticity and stability.
Furthermore,   we   hope   m HC   rejuvenates   community   interest   in   macro-architecture   design.
By   deepening   the   understanding   of   how   topological   structures   influence   optimization   and
representation learning,  m HC will help address current limitations and potentially illuminate
new pathways for the evolution of next-generation foundational architectures.
References
J. Ainslie, J. Lee-Thorp, M. De Jong, Y. Zemlyanskiy, F. Lebrón, and S. Sanghai.   Gqa:   Training
generalized multi-query transformer models from multi-head checkpoints.   arXiv preprint
arXiv:2305.13245, 2023.
Y. Bisk, R. Zellers, R. L. Bras, J. Gao, and Y. Choi.   PIQA: reasoning about physical commonsense
in natural language.   In  The Thirty-Fourth AAAI Conference on Artificial Intelligence, AAAI
2020, The Thirty-Second Innovative Applications of Artificial Intelligence Conference, IAAI
2020, The Tenth AAAI Symposium on Educational Advances in Artificial Intelligence, EAAI
2020,   New   York,   NY,   USA,   February   7-12,   2020 ,   pages   7432–7439.   AAAI   Press,   2020.   doi:
10.1609/aaai.v34i05.6239.   URL  https://doi.org/10.1609/aaai.v34i05.6239 .
T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam,
G.   Sastry,   A.   Askell,   et   al.   Language   models   are   few-shot   learners.   Advances   in   neural
information processing systems, 33:1877–1901, 2020.
Y. Chai, S. Jin, and X. Hou.   Highway transformer:   Self-gating enhanced self-attentive networks.
In D. Jurafsky, J. Chai, N. Schluter, and J. Tetreault, editors,  Proceedings of the 58th Annual
Meeting   of   the   Association   for   Computational   Linguistics ,   pages   6887–6900,   Online,   July
2020. Association for Computational Linguistics.   doi:   10.18653/v1/2020.acl-main.616.   URL
https://aclanthology.org/2020.acl-main.616/ .
F. Chollet.   Xception:   Deep learning with depthwise separable convolutions.   In  Proceedings of
the IEEE conference on computer vision and pattern recognition, pages 1251–1258, 2017.
15

---


<!-- Page 16 -->

K.   Cobbe,   V.   Kosaraju,   M.   Bavarian,   M.   Chen,   H.   Jun,   L.   Kaiser,   M.   Plappert,   J.   Tworek,
J. Hilton, R. Nakano, et al.   Training verifiers to solve math word problems.   arXiv preprint
arXiv:2110.14168, 2021.
T. Dao, D. Y. Fu, S. Ermon, A. Rudra, and C. Ré.   FlashAttention:   Fast and memory-efficient
exact attention with IO-awareness.   In  Advances in Neural Information Processing Systems
(NeurIPS), 2022.
D. Dua, Y. Wang, P. Dasigi, G. Stanovsky, S. Singh, and M. Gardner.   DROP: A reading compre-
hension benchmark requiring discrete reasoning over paragraphs. In J. Burstein, C. Doran, and
T. Solorio, editors,  Proceedings of the 2019 Conference of the North American Chapter of the
Association   for   Computational   Linguistics:   Human   Language   Technologies,   NAACL-HLT
2019, Minneapolis, MN, USA, June 2-7, 2019, Volume 1 (Long and Short Papers) , pages 2368–
2378. Association for Computational Linguistics, 2019.   doi:   10.18653/V1/N19-1246.   URL
https://doi.org/10.18653/v1/n19-1246 .
Y. Fang, Y. CAI, J. Chen, J. Zhao, G. Tian, and G. Li.   Cross-layer retrospective retrieving via layer
attention.   In  The Eleventh International Conference on Learning Representations , 2023.   URL
https://openreview.net/forum?id=pvgEL1yS3Ql .
W. Fedus, B. Zoph, and N. Shazeer.   Switch transformers:   Scaling to trillion parameter models
with simple and efficient sparsity.   Journal of Machine Learning Research, 23(120):1–39, 2022.
K. He, X. Zhang, S. Ren, and J. Sun. Deep residual learning for image recognition. In  Proceedings
of the IEEE conference on computer vision and pattern recognition, pages 770–778, 2016a.
K. He, X. Zhang, S. Ren, and J. Sun.   Identity mappings in deep residual networks.   In  European
conference on computer vision, pages 630–645. Springer, 2016b.
M. Heddes, A. Javanmard, K. Axiotis, G. Fu, M. Bateni, and V. Mirrokni.   Deepcrossattention:
Supercharging transformer residual connections.   In  Forty-second International Conference
on Machine Learning, 2025.   URL  https://openreview.net/forum?id=j3JBfFnGYh .
D. Hendrycks, C. Burns, S. Basart, A. Zou, M. Mazeika, D. Song, and J. Steinhardt.   Measuring
massive multitask language understanding.   arXiv preprint arXiv:2009.03300, 2020.
D. Hendrycks, C. Burns, S. Kadavath, A. Arora, S. Basart, E. Tang, D. Song, and J. Steinhardt. Mea-
suring mathematical problem solving with the math dataset.   arXiv preprint arXiv:2103.03874 ,
2021.
J. Hoffmann, S. Borgeaud, A. Mensch, E. Buchatskaya, T. Cai, E. Rutherford, D. de Las Casas,
L. A. Hendricks, J. Welbl, A. Clark, T. Hennigan, E. Noland, K. Millican, G. van den Driessche,
B.   Damoc,   A.   Guy,   S.   Osindero,   K.   Simonyan,   E.   Elsen,   O.   Vinyals,   J.   Rae,   and   L.   Sifre.
An   empirical   analysis   of   compute-optimal   large   language   model   training.   In   S.   Koyejo,
S.   Mohamed,   A.   Agarwal,   D.   Belgrave,   K.   Cho,   and   A.   Oh,   editors,   Advances   in   Neural
Information Processing Systems , volume 35, pages 30016–30030. Curran Associates, Inc., 2022.
URL  https://proceedings.neurips.cc/paper_files/paper/2022/file/c1e2faf
f6f588870935f114ebe04a3e5-Paper-Conference.pdf .
G. Huang, Z. Liu, L. Van Der Maaten, and K. Q. Weinberger.   Densely connected convolutional
networks. In  Proceedings of the IEEE conference on computer vision and pattern recognition ,
pages 4700–4708, 2017.
16

---


<!-- Page 17 -->

M. Joshi, E. Choi, D. Weld, and L. Zettlemoyer.   TriviaQA: A large scale distantly supervised chal-
lenge dataset for reading comprehension. In R. Barzilay and M.-Y. Kan, editors,  Proceedings of
the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1:   Long
Papers) ,   pages   1601–1611,   Vancouver,   Canada,   July   2017.   Association   for   Computational
Linguistics.   doi:   10.18653/v1/P17-1147.   URL  https://aclanthology.org/P17-1147 .
G. Larsson, M. Maire, and G. Shakhnarovich.   Fractalnet:   Ultra-deep neural networks without
residuals.   arXiv preprint arXiv:1605.07648, 2016.
D. Lepikhin, H. Lee, Y. Xu, D. Chen, O. Firat, Y. Huang, M. Krikun, N. Shazeer, and Z. Chen.
Gshard:   Scaling giant models with conditional computation and automatic sharding.   arXiv
preprint arXiv:2006.16668, 2020.
A. Liu, B. Feng, B. Wang, B. Wang, B. Liu, C. Zhao, C. Dengr, C. Ruan, D. Dai, D. Guo, et al.
Deepseek-v2:   A strong, economical, and efficient mixture-of-experts language model.   arXiv
preprint arXiv:2405.04434, 2024a.
A.   Liu,   B.   Feng,   B.   Xue,   B.   Wang,   B.   Wu,   C.   Lu,   C.   Zhao,   C.   Deng,   C.   Zhang,   C.   Ruan,   et   al.
Deepseek-v3 technical report.   arXiv preprint arXiv:2412.19437, 2024b.
I.   Loshchilov   and   F.   Hutter.
Decoupled   weight   decay   regularization.
arXiv   preprint
arXiv:1711.05101, 2017.
B. Mak and J. Flanigan.   Residual matrix transformers:   Scaling the size of the residual stream.
arXiv preprint arXiv:2506.22696, 2025.
G.   Menghani,   R.   Kumar,   and   S.   Kumar.
LAurel:   Learned   augmented   residual   layer.
In
Forty-second   International   Conference   on   Machine   Learning ,   2025.   URL   https://open
review.net/forum?id=rUDRWP9WvZ .
M. Pagliardini, A. Mohtashami, F. Fleuret, and M. Jaggi.   Denseformer:   Enhancing information
flow in transformers via depth weighted averaging.   In  The Thirty-eighth Annual Conference
on Neural Information Processing Systems , 2024.   URL  https://openreview.net/forum
?id=kMnoh7CXrq .
P. Qi, X. Wan, G. Huang, and M. Lin.   Zero bubble (almost) pipeline parallelism.   In  The Twelfth
International Conference on Learning Representations ,   2024.   URL  https://openreview
.net/forum?id=tuzTN0eIO5 .
N.   Shazeer.
Fast   transformer   decoding:   One   write-head   is   all   you   need.
arXiv   preprint
arXiv:1911.02150, 2019.
N.   Shazeer,   A.   Mirhoseini,   K.   Maziarz,   A.   Davis,   Q.   Le,   G.   Hinton,   and   J.   Dean.
Outra-
geously large neural networks:   The sparsely-gated mixture-of-experts layer.   arXiv preprint
arXiv:1701.06538, 2017.
R. Sinkhorn and P. Knopp.   Concerning nonnegative matrices and doubly stochastic matrices.
Pacific Journal of Mathematics, 21(2):343–348, 1967.
R.   K.   Srivastava,   K.   Greff,   and   J.   Schmidhuber.   Training   very   deep   networks.   In   C.   Cortes,
N. Lawrence, D. Lee, M. Sugiyama, and R. Garnett, editors,  Advances in Neural Information
Processing Systems , volume 28. Curran Associates, Inc., 2015.   URL  https://proceedings.
neurips.cc/paper_files/paper/2015/file/215a71a12769b056c3c32e7299f1c5e
d-Paper.pdf .
17

---


<!-- Page 18 -->

J. Su, M. Ahmed, Y. Lu, S. Pan, W. Bo, and Y. Liu.   Roformer:   Enhanced transformer with rotary
position embedding.   Neurocomputing, 568:127063, 2024.
M. Suzgun, N. Scales, N. Schärli, S. Gehrmann, Y. Tay, H. W. Chung, A. Chowdhery, Q. V. Le,
E. H. Chi, D. Zhou, et al.   Challenging big-bench tasks and whether chain-of-thought can solve
them.   arXiv preprint arXiv:2210.09261, 2022.
H. Touvron, T. Lavril, G. Izacard, X. Martinet, M.-A. Lachaux, T. Lacroix, B. Rozière, N. Goyal,
E. Hambro, F. Azhar, et al.   Llama:   Open and efficient foundation language models.   arXiv
preprint arXiv:2302.13971, 2023.
A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polo-
sukhin.   Attention is all you need.   Advances in neural information processing systems , 30,
2017.
L. Wang, H. Gao, C. Zhao, X. Sun, and D. Dai.   Auxiliary-loss-free load balancing strategy for
mixture-of-experts.   arXiv preprint arXiv:2408.15664, 2024.
L. Wang, Y. Cheng, Y. Shi, Z. Tang, Z. Mo, W. Xie, L. Ma, Y. Xia, J. Xue, F. Yang, et al.   Tilelang:   A
composable tiled programming model for ai systems.   arXiv preprint arXiv:2504.17577, 2025.
D. Xiao, Q. Meng, S. Li, and X. Yuan. Muddformer: Breaking residual bottlenecks in transformers
via multiway dynamic dense connections.   arXiv preprint arXiv:2502.12170, 2025.
S. Xie, R. Girshick, P. Dollár, Z. Tu, and K. He.   Aggregated residual transformations for deep
neural   networks.   In   Proceedings   of   the   IEEE   conference   on   computer   vision   and   pattern
recognition, pages 1492–1500, 2017.
S. Xie, H. Zhang, J. Guo, X. Tan, J. Bian, H. H. Awadalla, A. Menezes, T. Qin, and R. Yan. Residual:
Transformer with dual residual connections, 2023.   URL  https://arxiv.org/abs/2304.1
4802 .
F. Yu, D. Wang, E. Shelhamer, and T. Darrell.   Deep layer aggregation.   In  Proceedings of the
IEEE conference on computer vision and pattern recognition, pages 2403–2412, 2018.
R. Zellers, A. Holtzman, Y. Bisk, A. Farhadi, and Y. Choi.   HellaSwag:   Can a machine really finish
your sentence?   In A. Korhonen, D. R. Traum, and L. Màrquez, editors,  Proceedings of the 57th
Conference of the Association for Computational Linguistics, ACL 2019, Florence, Italy, July
28- August 2, 2019, Volume 1:   Long Papers , pages 4791–4800. Association for Computational
Linguistics, 2019.   doi:   10.18653/v1/p19-1472.   URL  https://doi.org/10.18653/v1/p1
9-1472 .
B.   Zhang   and   R.   Sennrich.
Root   mean   square   layer   normalization.
Advances   in   neural
information processing systems, 32, 2019.
D. Zhu, H. Huang, Z. Huang, Y. Zeng, Y. Mao, B. Wu, Q. Min, and X. Zhou.   Hyper-connections.
arXiv preprint arXiv:2409.19606, 2024.
18

---


<!-- Page 19 -->

A.   Appendix
A.1.   Detailed Model Specifications and Hyper-parameters.
Table 5  |  Detailed Model Specifications and Hyper-parameters.   This table presents the architec-
tural configurations for the 3B, 9B, and 27B models based on the DeepSeek-V3 (Liu et al., 2024b)
architecture.   It outlines the specific hyper-parameters for  m HC and HC, including the residual
stream expansion and Sinkhorn-Knopp settings, alongside the optimization and training proto-
cols used in the experiments.
m HC/HC Expansion Rate  𝑛
4
4
m HC/HC Gating Factor Init  𝛼
0.01
0.01
m HC Sinkhorn-Knopp  𝑡 max
20
20
19


| Attribute | 3B 9B 27B | 3B 1T Tokens |
| --- | --- | --- |



| Vocab Params Active Params Total Params | 331M 496M 662M 612M 1.66B 4.14B 2.97B 9.18B 27.0B | 331M 612M 2.97B |
| --- | --- | --- |



| Layers Leading Dense Layers Routed Experts Active Experts Shared Experts Dimension FFN Dimension Load Balancing Method Attention Heads Attention Dimension Attention Variant KV Rank Position Embedding RoPE Dimension RoPE 𝜃 Layer Norm Type Layer Norm 𝜀 | 12 18 30 1 64 64 72 6 2 1280 1920 2560 896 1280 1536 Loss-Free (Wang et al., 2024) 16 24 32 128 MLA (Liu et al., 2024a) 512 RoPE (Su et al., 2024) 64 10000 RMSNorm (Zhang and Sennrich, 2019) 1e-20 | 12 1 64 6 2 1280 896 Loss-Free 16 128 MLA 512 RoPE 64 10000 RMSNorm 1e-20 |
| --- | --- | --- |



| mHC/HC Expansion Rate 𝑛 mHC/HC Gating Factor Init 𝛼 mHC Sinkhorn-Knopp 𝑡 max | 4 0.01 20 | 4 0.01 20 |
| --- | --- | --- |



| Sequence Length Vocab Size Batch Size Training Steps Training Tokens Warmup Steps Optimizer AdamW Betas AdamW 𝜀 Base Learning Rate Lr Scheduler Lr Decay Step Ratio Lr Decay Rate Weight Decay | 4096 129280 320 512 1280 30000 50000 50000 39.3B 105B 262B 2000 AdamW (Loshchilov and Hutter, 2017) (0.9, 0.95) 1e-20 8.6e-4 5.9e-4 4.0e-4 Step [0.8 ×, 0.9 ×] [0.316, 0.1] 0.1 | 4096 129280 2560 100000 1.05T 2000 AdamW (0.9, 0.95) 1e-20 9.0e-4 Step [0.8 ×, 0.9 ×] [0.316, 0.1] 0.1 |
| --- | --- | --- |


---
