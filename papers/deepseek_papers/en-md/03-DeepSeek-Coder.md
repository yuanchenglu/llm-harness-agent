
<!-- Page 1 -->

DeepSeek-Coder:   When the Large Language Model Meets
Programming - The Rise of Code Intelligence
Daya Guo* 1 , Qihao Zhu ∗ 1,2 , Dejian Yang 1 , Zhenda Xie 1 , Kai Dong 1 , Wentao Zhang 1
Guanting Chen 1 , Xiao Bi   1 , Y. Wu 1 , Y.K. Li 1 , Fuli Luo 1 , Yingfei Xiong 2 , Wenfeng Liang 1
1 DeepSeek-AI
2 Key Lab of HCST (PKU), MOE; SCS, Peking University
{zhuqh,   guodaya}@deepseek.com
https://github.com/deepseek-ai/DeepSeek-Coder
Abstract
The   rapid   development   of   large   language   models   has   revolutionized   code   intelligence   in
software development.   However,   the predominance of closed-source models has restricted
extensive research and development.   To address this, we introduce the DeepSeek-Coder series,
a   range   of   open-source   code   models   with   sizes   from   1.3B   to   33B,   trained   from   scratch   on   2
trillion tokens.   These models are pre-trained on a high-quality project-level code corpus and
employ a fill-in-the-blank task with a 16K window to enhance code generation and infilling.
Our extensive evaluations demonstrate that DeepSeek-Coder not only achieves state-of-the-art
performance among open-source code models across multiple benchmarks but also surpasses
existing closed-source models like Codex and GPT-3.5.   Furthermore, DeepSeek-Coder models
are under a permissive license that allows for both research and unrestricted commercial use.
Figure 1  |  The Performance of DeepSeek-Coder
*Core contributors, ordered alphabetically by the name.
arXiv:2401.14196v2  [cs.SE]  26 Jan 2024

---


<!-- Page 2 -->

1.   Introduction
The field of software development has been significantly transformed by the swift advancement
of   large   language   models   (OpenAI,   2023;   Touvron   et   al.,   2023),   which   have   brought   about
a new era of code intelligence.   These models have the potential to automate and streamline
many aspects of coding, from bug detection to code generation, thereby enhancing productivity
and   reducing   the   likelihood   of   human   error.   However,   a   major   challenge   in   this   field   is   the
performance gap between open-source models   (Li et al., 2023; Nijkamp et al., 2022; Roziere
et al., 2023; Wang et al., 2021) and closed-source models   (Gemini Team, 2023; OpenAI, 2023).
The giant closed-source models, while powerful, are often inaccessible to many researchers and
developers due to their proprietary nature.
In response to this challenge, we present the DeepSeek-Coder series.   This series comprises
a   range   of   open-source   code   models,   varying   in   size   from   1.3B   to   33B,   including   the   base
version and instructed version for each size.   Each model in the series has been trained from
scratch on 2 trillion tokens sourced from 87 programming languages, ensuring a comprehensive
understanding   of   coding   languages   and   syntax.   Besides,   we   attempt   to   organize   the   pre-
training data at the repository level to enhance the pre-trained model’s understanding capability
within the context of cross-files within a repository.   In addition to employing the next token
prediction loss during pre-training, we have also incorporated the Fill-In-Middle (FIM) approach
(Bavarian et al., 2022; Li et al., 2023).   This approach is designed to further bolster the model’s
code   completion   capabilities.   To   meet   the   requirements   of   handling   longer   code   inputs,   we
have extended the context length to 16K. This adjustment allows our models to handle more
complex and extensive coding tasks, thereby increasing their versatility and applicability in
various coding scenarios.
We   have   carried   out   comprehensive   experiments   using   a   variety   of   public   code-related
benchmarks.   The findings reveal that among open-source models, DeepSeek-Coder-Base 33B
consistently   delivers   superior   performance   across   all   benchmarks.   Furthermore,   DeepSeek-
Coder-Instruct 33B surpasses  OpenAI GPT-3.5 Turbo  in the majority of the evaluation benchmarks,
significantly narrowing the performance gap between  OpenAI GPT-4  and open-source models.
Remarkably, despite having fewer parameters, DeepSeek-Coder-Base 7B demonstrates competi-
tive performance when compared to models that are five times larger, such as CodeLlama-33B
(Roziere et al., 2023).   To summarize, our main contributions are:
•   We   introduce   DeepSeek-Coder-Base   and   DeepSeek-Coder-Instruct,   our   advanced   code-
focused   large   language   models   (LLMs).   Developed   through   extensive   training   on   an
expansive code corpus, these models exhibit proficiency in understanding 87 programming
languages.   Additionally, they are available in various model scales to cater to a wide range
of computational and application needs.
•   We   make   the   first   attempt   to   incorporate   repository-level   data   construction   during   the
pre-training phase of our models.   We find that it can significantly boost the capability of
cross-file code generation.
•   Our analysis rigorously examines the impact of FIM training strategies on the pretraining
phase of code models. The outcomes of these comprehensive studies shed light on intriguing
aspects of FIM configurations, offering valuable insights that significantly contribute to the
enhancement and development of code pretrained models.
•   We conduct extensive evaluations of our code LLMs against a wide array of benchmarks en-
compassing numerous code-related tasks.   The findings demonstrate that DeepSeek-Coder-
Base surpasses all existing open-source code LLMs across these benchmarks.   Furthermore,
2

---


<!-- Page 3 -->

with meticulous fine-tuning using instructional data, DeepSeek-Coder-Instruct achieves
better performance compared to the  OpenAI GPT-3.5 Turbo  model in code-related tasks.
2.   Data Collection
The training dataset of DeepSeek-Coder is composed of 87% source code, 10% English code-
related natural language corpus, and 3% code-unrelated Chinese natural language corpus.   The
English corpus consists of materials from GitHub’s Markdown and StackExchange 1 , which are
used to enhance the model’s understanding of code-related concepts and improve its ability
to handle tasks like library usage and bug fixing.   Meanwhile, the Chinese corpus consists of
high-quality articles aimed at improving the model’s proficiency in understanding the Chinese
language.   In this section, we will provide an overview of how we construct the code training
data.   This process involves data crawling, rule-based filtering, dependency parsing, repository-
level deduplication, and quality screening, as illustrated in Figure 2.   In the following, we will
describe the data creation procedure step by step.
Rule 
Filtering
Dependency 
Parsing
Repo-level 
Deduplication
Quality 
Screening
Data 
Crawling
Figure 2  |  The Procedure of Dataset Creation
2.1.   GitHub Data Crawling and Filtering
We   collect   public   repositories   created   before   February   2023   on   GitHub   and   retain   only   87
programming languages, as listed in Table 1.   To reduce the amount of data to be processed, we
apply filtering rules similar to those used in the StarCoder project   (Li et al., 2023) to preliminarily
filter out lower-quality code.   By applying these filtering rules, we reduce the total amount of
data to only 32.8% of its original size.   To make the paper self-contained, we briefly describe the
filter rules used in the StarCoder Data project:
Firstly, we filter out files with an average line length exceeding 100 characters or a maximum
line   length   surpassing   1000   characters.   Additionally,   we   remove   files   with   fewer   than   25%
alphabetic characters.   Except for the XSLT programming language, we further filter out files
where the string  "<?xml   version="  appeared in the first 100 characters.   For HTML files, we
consider the ratio of visible text to HTML code.   We retain files where the visible text constitutes
at least 20% of the code and is no less than 100 characters.   For JSON and YAML files, which
typically contain more data, we only keep files that have a character count ranging from 50 to
5000 characters.   This effectively removes most data-heavy files.
2.2.   Dependency Parsing
In previous works   (Chen et al., 2021; Li et al., 2023; Nijkamp et al., 2022; Roziere et al., 2023),
large language models for code are mainly pre-trained on file-level source code, which ignores
the dependencies between different files in a project.   However, in practical applications, such
models struggle to effectively scale to handle entire project-level code scenarios.   Therefore, we
1 https://stackexchange.com
3

---


<!-- Page 4 -->

Algorithm 1  Topological Sort for Dependency Analysis
1:   procedure   T  O P O L O G I C A L S  O R T (  𝑓𝑖𝑙𝑒𝑠 )
2:
𝑔𝑟𝑎𝑝ℎ𝑠 ←{}
⊲ Initialize an empty adjacency list
3:
𝑖𝑛𝐷𝑒𝑔𝑟𝑒𝑒 ←{}
⊲ Initialize an empty dictionary for in-degrees
4:
for each   𝑓𝑖𝑙𝑒 in   𝑓𝑖𝑙𝑒𝑠 do
5:
𝑔𝑟𝑎𝑝ℎ𝑠 [  𝑓𝑖𝑙𝑒 ]   ←[]
6:
𝑖𝑛𝐷𝑒𝑔𝑟𝑒𝑒 [  𝑓𝑖𝑙𝑒 ]   ← 0
7:
end for
8:
9:
for each   𝑓𝑖𝑙𝑒𝐴 in   𝑓𝑖𝑙𝑒𝑠 do
10:
for each   𝑓𝑖𝑙𝑒𝐵 in   𝑓𝑖𝑙𝑒𝑠 do
11:
if   H  A S D  E P E N D E N C Y (  𝑓𝑖𝑙𝑒𝐴 ,   𝑓𝑖𝑙𝑒𝐵 )  then
⊲ If fileA depends on fileB
12:
𝑔𝑟𝑎𝑝ℎ𝑠 [  𝑓𝑖𝑙𝑒𝐵 ] .append (  𝑓𝑖𝑙𝑒𝐴 )
⊲ Add edge from B to A
13:
𝑖𝑛𝐷𝑒𝑔𝑟𝑒𝑒 [  𝑓𝑖𝑙𝑒𝐴 ]   ← 𝑖𝑛𝐷𝑒𝑔𝑟𝑒𝑒 [  𝑓𝑖𝑙𝑒𝐴 ] +  1
⊲ Increment in-degree of A
14:
end if
15:
end for
16:
end for
17:
18:
𝑠𝑢𝑏𝑔𝑟𝑎𝑝ℎ𝑠 ← getDisconnectedSubgraphs ( 𝑔𝑟𝑎𝑝ℎ𝑠 )
⊲ Identify disconnected subgraphs
19:
𝑎𝑙𝑙𝑅𝑒𝑠𝑢𝑙𝑡𝑠 ←[]
20:
for each  𝑠𝑢𝑏𝑔𝑟𝑎𝑝ℎ in  𝑠𝑢𝑏𝑔𝑟𝑎𝑝ℎ𝑠 do
21:
𝑟𝑒𝑠𝑢𝑙𝑡𝑠 ←[]
22:
while  length ( 𝑟𝑒𝑠𝑢𝑙𝑡𝑠 )   ≠ NumberOfNodes ( 𝑠𝑢𝑏𝑔𝑟𝑎𝑝ℎ )  do
23:
𝑓𝑖𝑙𝑒 ← argmin ({ 𝑖𝑛𝐷𝑒𝑔𝑟𝑒𝑒 [  𝑓𝑖𝑙𝑒 ]   |   𝑓𝑖𝑙𝑒 ∈ 𝑠𝑢𝑏𝑔𝑟𝑎𝑝ℎ and   𝑓𝑖𝑙𝑒 ∉ 𝑟𝑒𝑠𝑢𝑙𝑡𝑠 })
24:
for each  𝑛𝑜𝑑𝑒 in  𝑔𝑟𝑎𝑝ℎ𝑠 [  𝑓𝑖𝑙𝑒 ]   do
25:
𝑖𝑛𝐷𝑒𝑔𝑟𝑒𝑒 [ 𝑛𝑜𝑑𝑒 ]   ← 𝑖𝑛𝐷𝑒𝑔𝑟𝑒𝑒 [ 𝑛𝑜𝑑𝑒 ] − 1
26:
end for
27:
𝑟𝑒𝑠𝑢𝑙𝑡𝑠 .append (  𝑓𝑖𝑙𝑒 )
28:
end while
29:
𝑎𝑙𝑙𝑅𝑒𝑠𝑢𝑙𝑡𝑠 .append ( 𝑟𝑒𝑠𝑢𝑙𝑡𝑠 )
30:
end for
31:
32:
return  𝑎𝑙𝑙𝑅𝑒𝑠𝑢𝑙𝑡𝑠
33:   end procedure
will consider how to leverage the dependencies between files within the same repository in
this   step.   Specifically,   we   first   parse   the   dependencies   between   files   and   then   arrange   these
files   in   an   order   that   ensures   the   context   each   file   relies   on   is   placed   before   that   file   in   the
input sequence.   By aligning the files in accordance with their dependencies, our dataset more
accurately represents real coding practices and structures.   This enhanced alignment not only
makes our dataset more relevant but also potentially increases the practicality and applicability
of the model in handling project-level code scenarios.   It’s worth noting that we only consider
the invocation relationships between files and use regular expressions to extract them, such as
"import"  in Python,  "using"  in C#, and  "include"  in C.
The algorithm 1 describes a topological sort for dependency analysis on a list of files within
the same project.   Initially, it sets up two data structures: an empty adjacency list named  "graphs"
to represent dependencies between files and an empty dictionary called  "inDegree"  for storing
the in-degrees of each file.   The algorithm then iterates over each file pair to identify depen-
4

---


<!-- Page 5 -->

dencies, updating  "graphs"  and  "inDegree"  accordingly.   Next, it identifies any disconnected
subgraphs within the overall dependency graph.   For each subgraph, the algorithm employs a
modified topological sort.   Unlike the standard approach that selects nodes with zero in-degrees,
this algorithm selects nodes with minimal in-degrees, which allows it to handle cycles within
the graph.   Selected nodes are added to a  "results"  list, and the in-degrees of their connected
nodes are decreased.   This process continues until a topologically sorted sequence is generated
for each subgraph.   The algorithm concludes by returning a list of these sorted sequences, and
each sequence’s files are concatenated to form a single training sample.   To incorporate file path
information, a comment indicating the file’s path is added at the beginning of each file.   This
method ensures that the path information is preserved in the training data.
2.3.   Repo-Level Deduplication
Recent   studies   have   demonstrated   the   significant   performance   improvements   that   can   be
achieved by deduplicating training datasets for Large Language Models (LLMs).   Lee et al. (2022)
have shown that language model training corpora often contain numerous near-duplicates, and
the performance of LLMs can be enhanced by removing long repetitive substrings.   Kocetkov
et al. (2022) have applied a near-deduplication method to training data, resulting in dramatic
improvements, and they emphasize that near-deduplication is a crucial preprocessing step for
achieving   competitive   performance   on   code   benchmark   tasks.   In   our   dataset,   we   have   also
employed near-deduplication.   However, there is a distinction in our approach compared to
previous works.   We perform deduplication at the repository level of code, rather than at the file
level, as the latter approach may filter out certain files within a repository, potentially disrupting
the structure of the repository.   Specifically, we treat the concatenated code from the repository
level as a single sample and apply the same near-deduplication algorithm to ensure the integrity
of the repository structure.
2.4.   Quality Screening and Decontamination
In addition to applying the filtering rules mentioned in Section 2.1, we also employ a compiler
and a quality model, combined with heuristic rules, to further filter out low-quality data.   This
includes code with syntax errors, poor readability, and low modularity.   We provide the statistical
summary of source code in Table 1, which includes a total of 87 languages, detailing the disk
size, number of files, and percentage for each language.   The total data volume is 798 GB with
603   million   files.   To   ensure   that   our   code   training   data   is   not   contaminated   by   information
from the test set,   which may be present on GitHub,   we’ve implemented an n-gram filtering
process.   This process involves the removal of any code segments that match specific criteria.
Specifically, we filter out files containing docstrings, questions, and solutions from sources such
as HumanEval   (Chen et al., 2021), MBPP   (Austin et al., 2021), GSM8K (Cobbe et al., 2021) and
MATH   (Hendrycks   et   al.,   2021).   For   the   filtering   criteria,   we   apply   the   following   rules:   if   a
piece of code includes a 10-gram string identical to any in the test data, it is excluded from our
training data.   In cases where the test data comprises strings that are shorter than 10-grams but
no less than 3-grams, we use an exact match approach for filtering.
5

---


<!-- Page 6 -->

Language
Size (GB)
Files (k)
Prop.   (%)
Language
Size (GB)
Files (k)
Prop.   (%)
Table 1  |  A summary of the cleaned training data for the selected programming languages.
3.   Training Policy
3.1.   Training Strategy
3.1.1.   Next Token Prediction
The   first   training   objective   for   our   model   is   known   as   next   token   prediction .   In   this   process,
various files are concatenated to form a fixed-length entry.   Then, these entries are used to train
the model, enabling it to predict the subsequent token based on the provided context.
6


| Ada Agda Alloy ANTLR AppleScript Assembly Augeas AWK Batchfile Bluespec C C# Clojure CMake CoffeeScript Common Lisp C++ CSS CUDA Dart Dockerfile Elixir Elm Emacs Lisp Erlang F# Fortran GLSL Go Groovy Haskell HTML Idris Isabelle Java Java Server Pages JavaScript JSON Julia Jupyter Notebook Kotlin Lean Literate Agda Literate CoffeeScript | 0.91 0.26 0.07 0.19 0.03 0.91 0.00 0.09 0.92 0.10 28.64 58.56 0.90 0.90 0.92 0.92 90.87 5.63 0.91 0.89 0.04 0.91 0.92 0.91 0.92 0.91 1.67 0.92 2.58 0.89 0.87 30.05 0.11 0.74 148.66 0.86 53.84 4.61 0.92 14.38 6.00 0.52 0.05 0.01 | 126 59 24 38 17 794 1 53 859 15 27,111 53,739 295 359 361 105 36,006 11,638 115 264 48 549 232 148 145 340 654 296 1,365 340 213 14,998 32 39 134,367 1072 71,895 11956 202 2,555 3,121 68 4 3 | 0.11 0.03 0.01 0.02 0.00 0.11 0.00 0.01 0.12 0.01 3.59 7.34 0.11 0.11 0.12 0.11 11.39 0.71 0.11 0.11 0.00 0.11 0.12 0.11 0.12 0.11 0.21 0.11 0.32 0.11 0.11 3.77 0.01 0.09 18.63 0.11 6.75 0.58 0.12 1.80 0.75 0.07 0.01 0.00 | Literate Haskell Lua Makeflie Maple Mathematica MATLAB OCaml Pascal Perl PHP PowerShell Prolog Protocol Buffer Python R Racket RMarkdown Ruby Rust SAS Scala Scheme Shell Smalltalk Solidity Sparql SQL Stan Standard ML Stata SystemVerilog TCL Tcsh Tex Thrift TypeScript Verilog VHDL Visual Basic XSLT Yacc YAML Zig Total | 0.16 0.82 0.92 0.03 0.82 0.01 0.91 0.79 0.81 58.92 0.91 0.03 0.92 120.68 0.92 0.09 6.83 15.01 0.61 0.92 0.81 0.92 13.92 0.92 0.85 0.10 15.14 0.20 0.74 0.91 0.91 0.90 0.17 20.46 0.05 60.62 0.01 0.85 0.75 0.36 0.72 0.74 0.81 797.92 | 20 138 460 6 10 1 139 470 148 40,627 236 5 391 75,188 158 13 1,606 18,526 692 70 971 216 10,890 880 83 88 7,009 41 117 122 165 110 53 2,867 21 62,432 1 392 73 48 67 890 70 603,173 | 0.02 0.10 0.12 0.00 0.10 0.00 0.11 0.10 0.10 7.38 0.11 0.00 0.12 15.12 0.11 0.01 0.86 1.88 0.08 0.11 0.10 0.12 1.74 0.12 0.11 0.01 1.90 0.03 0.09 0.11 0.11 0.11 0.02 2.56 0.01 7.60 0.00 0.11 0.09 0.04 0.09 0.09 0.10 100.00 |
| --- | --- | --- | --- | --- | --- | --- | --- |


---


<!-- Page 7 -->

3.1.2.   Fill-in-the-Middle
The second training objective for our model is known as  fill-in-the-middle.  In the code pre-training
scenario, it is often necessary to generate corresponding inserted content based on the given
context and subsequent text.   Due to specific dependencies in a programming language, relying
solely on next token prediction is insufficient to learn this fill-in-the-middle capability.   Therefore,
several approaches   (Bavarian et al., 2022; Li et al., 2023) propose the pretraining method of
Fill-in-the-Midlle (FIM). This approach involves randomly dividing the text into three parts,
then shuffling the order of these parts and connecting them with special characters.   This method
aims to incorporate a fill-in-the-blank pretraining task during the training process.   Within the
FIM   methodology,   two   distinct   modes   are   employed:   PSM   (Prefix-Suffix-Middle)   and   SPM
(Suffix-Prefix-Middle).   In   the   PSM   mode,   the   training   corpus   is   organized   in   the   sequence
of   𝑃𝑟𝑒𝑓𝑖𝑥 ,  𝑆𝑢𝑓𝑓𝑖𝑥 ,  𝑀𝑖𝑑𝑑𝑙𝑒 , aligning the text in a way that the middle segment is flanked by the
prefix and suffix.   Conversely, the SPM mode arranges the segments as  𝑆𝑢𝑓𝑓𝑖𝑥 ,  𝑃𝑟𝑒𝑓𝑖𝑥 ,  𝑀𝑖𝑑𝑑𝑙𝑒 ,
presenting   a   different   structural   challenge.   These   modes   are   instrumental   in   enhancing   the
model’s capability to handle various structural arrangements in code, providing a robust training
framework for advanced code prediction tasks.
0
2000
4000
6000
8000
Steps
0.000
0.025
0.050
0.075
0.100
0.125
0.150
0.175
0.200
Value
Benchmark/HumanEval-Pass@1
0
2000
4000
6000
8000
Steps
0.0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
Value
Benchmark/HumanFIM-Pass@1
0
2000
4000
6000
8000
Steps
0.00
0.05
0.10
0.15
0.20
0.25
Value
Benchmark/MBPP-Pass@1
fim_0
fim_0.5
fim_1.0
msp_0.5
Figure 3  |  The effectiveness of using FIM objective.
To determine the effectiveness of various hyperparameters within the FIM approach, we
conducted a series of ablation experiments.
Experiment Settings:   In this experiment, we employ DeepSeek-Coder-Base 1.3B as our model
architecture.   We   focused   on   a   Python   subset   from   our   training   dataset   to   streamline   the   ex-
perimental process.   Our primary objective was to assess the efficacy of the Fill-in-the-Middle
(FIM) technique, utilizing the HumanEval-FIM benchmark (Fried et al., 2022).   This benchmark
specializes in a single-line FIM task for Python, in which one line of code from a HumanEval
solution is randomly obscured, testing the model’s proficiency in predicting the missing line.
We hypothesize that the PSM mode may exhibit subtle differences compared to the traditional
next-token prediction objective.   This is primarily because PSM involves rearranging the order
of the original text, potentially impacting the learning dynamics of the model.   Therefore, we
implement the PSM mode for FIM across four distinct configurations:   0% FIM rate, 50% FIM
rate, 100% FIM rate, and 50% MSP rate.   The Masked Span Prediction (MSP) strategy, initially
introduced in T5 (Raffel et al., 2023), conceals multiple text spans and trains the model to recon-
struct these segments.   According to CodeGen2.5 (Nijkamp et al., 2023), MSP may enhance FIM
performance compared to PSM. Thus, we include this method in our comparative analysis.
Results:   The outcomes of our experiment are illustrated in Figure 3.   While the model demon-
strates peak performance on the HumanEval-FIM with a 100% FIM rate, this configuration also
results in the weakest code completion capability.   This indicates a trade-off between FIM and
7

---


<!-- Page 8 -->

code completion abilities.   Moreover, we observe that with a 50% PSM rate, the model outper-
forms   the   MSP   strategy.   To   achieve   a   balance   between   FIM   efficiency   and   code   completion
proficiency, we ultimately choose the 50% PSM rate as our preferred training policy.
In our implementation, we have introduced three sentinel tokens specifically for this task.
For each code file, we initially divide its content into three segments, denoted as   𝑓 𝑝𝑟𝑒 ,   𝑓 𝑚𝑖𝑑𝑑𝑙𝑒 , and
𝑓 𝑠𝑢𝑓 .   Using the PSM mode, we construct the training example as follows:
< ｜ fim_start ｜ >  𝑓 𝑝𝑟𝑒 < ｜ fim_hole ｜ >  𝑓 𝑠𝑢𝑓 < ｜ fim_end ｜ >  𝑓 𝑚𝑖𝑑𝑑𝑙𝑒 <|eos_token|>
We implement the Fill-in-the-Middle (FIM) method at the document level before the packing
process, as proposed in the original work by   Bavarian et al. (2022).   This is done with an FIM
rate of 0.5, following the PSM mode.
3.2.   Tokenizer
For the tokenization process, we employ the HuggingFace Tokenizer library 2   to train Byte Pair
Encoding   (BPE)   tokenizers,   as   outlined   in   Sennrich   et   al.   (2015)   (Sennrich   et   al.,   2015),   on   a
subset of our training corpus.   Ultimately, we utilize a tokenizer configured with a vocabulary
size of 32,000.
3.3.   Model Architecture
We develop a range of models with varying parameters to cater to diverse applications, including
models with 1.3B, 6.7B, and 33B parameters.   These models are built upon the same framework
as the DeepSeek Large Language Model (LLM) outlined by DeepSeek-AI (2024).   Each model is a
decoder-only Transformer, incorporating Rotary Position Embedding (RoPE) as described by Su
et al. (2023).   Notably, the DeepSeek 33B model integrates Grouped-Query-Attention (GQA) with
a group size of 8, enhancing both training and inference efficiency.   Additionally, we employ
FlashAttention v2 (Dao, 2023) to expedite the computation involved in the attention mechanism.
The architectural details of our models are summarized in Table 2.
3.4.   Optimization
Following DeepSeek LLM   (DeepSeek-AI, 2024), we use AdamW   (Loshchilov and Hutter, 2019)
as the optimizer with   𝛽 1  and   𝛽 2  values of 0.9 and 0.95.   We adapt batch sizes and learning rates by
the scaling laws suggested in DeepSeek LLM. For the learning rate scheduling, we implement a
three-stage policy, which includes 2000 warm-up steps, and set the final learning rate to 10% of
the initial rate.   Notably, the learning rate at each stage is scaled down to
√︃
1
10   of the preceding
stage’s rate, following the guidelines established in DeepSeek LLM (DeepSeek-AI, 2024).
3.5.   Environments
Our experiments are conducted using the HAI-LLM (High-Flyer, 2023) framework, known for
its   efficiency   and   lightweight   approach   in   training   large   language   models.   This   framework
incorporates a variety of parallelism strategies to optimize computational efficiency.   These in-
clude tensor parallelism (Korthikanti et al., 2023), alongside ZeRO data parallelism (Rajbhandari
et   al.,   2020)   and   PipeDream   pipeline   parallelism   (Narayanan   et   al.,   2019).   Our   experiments
2 https://github.com/huggingface/tokenizers
8

---


<!-- Page 9 -->

Hyperparameter
DeepSeek-Coder 1.3B
DeepSeek-Coder 6.7B
DeepSeek-Coder 33B
Table 2  |  Hyperparameters of DeepSeek-Coder.
utilize clusters outfitted with NVIDIA A100 and H800 GPUs.   In the A100 cluster, each node
is configured with 8 GPUs, interconnected in pairs using NVLink bridges.   The H800 cluster is
similarly arranged, with each node containing 8 GPUs.   These GPUs are interconnected using
a combination of NVLink and NVSwitch technologies, ensuring efficient data transfer within
nodes.   To facilitate seamless communication between nodes in both A100 and H800 clusters, we
employ InfiniBand interconnects, known for their high throughput and low latency.   This setup
provides a robust and efficient infrastructure for our computational experiments.
3.6.   Long Context
To enhance the capabilities of DeepSeek-Coder in handling extended contexts, particularly for
scenarios like repository-level code processing, we have reconfigured the RoPE (Su et al., 2023)
parameters to extend the default context window.   Following previous practices (Chen et al.,
2023; kaiokendev, 2023), we employed a linear scaling strategy, increasing the scaling factor from
1 to 4 and altering the base frequency from 10000 to 100000.   The model underwent an additional
1000 steps of training, using a batch size of 512 and a sequence length of 16K. The learning rate
was maintained as in the final pre-training phase.   Theoretically, these modifications enable our
model to process up to 64K tokens in context.   However, empirical observations suggest that
the   model   delivers   its   most   reliable   outputs   within   a   16K   token   range.   Future   research   will
continue to refine and evaluate the long-context adaptation methodology,   aiming to further
enhance DeepSeek-Coder’s efficiency and user-friendliness in processing extended contexts.
3.7.   Instruction Tuning
We develop DeepSeek-Coder-Instruct by enhancing the DeepSeek-Coder-Base through instruction-
based fine-tuning using high-quality data.   This data comprises helpful and impartial human
instructions, structured by the Alpaca Instruction format   (Taori et al., 2023).   To demarcate each
dialogue turn, we employed a unique delimiter token  <|EOT|>  to signify the conclusion of each
segment.   For training, we use a cosine schedule with 100 warm-up steps and an initial learning
rate 1e-5.   We also use a batch size of 4M tokens and 2B tokens in total.
An example of using DeepSeek-Coder-Instruct 34B is depicted in Figure 4.   This example is
a multi-turn dialogue scenario for building a snake game.   Initially, we ask the model to write
a game snake using pygame.   The model successfully creates a basic snake game that can run
without bugs.   To improve the game, we further request adding a scoring system in the top left
corner.   The model then introduces a  "score"  variable and a  "display_score"  function, along with
an explanation of how to integrate these features.   This example illustrates DeepSeek-Coder-
Instruct’s ability to provide complete solutions in multi-turn dialogue settings.   More cases can
be found in the Appendix A.
9


| Hidden Activation Hidden size Intermediate size Hidden layers number Attention heads number Attention Batch Size Max Learning Rate | SwiGLU 2048 5504 24 16 Multi-head 1024 5.3e-4 | SwiGLU 4096 11008 32 32 Multi-head 2304 4.2e-4 | SwiGLU 7168 19200 62 56 Grouped-query (8) 3840 3.5e-4 |
| --- | --- | --- | --- |


---


<!-- Page 10 -->

Q1: Write a game snake using pygame
Sure, here is a simple implementation of the classic Snake 
game using Pygame. This code will create a window with a 
snake that can be controlled using the arrow keys. The snake 
will grow in length each time it eats the food. The game will 
end if the snake hits the edge of the window or its own tail.
```python
import pygame 
import random
…
running = True
While running:
…
# Draw everything 
screen.fill(BLACK) 
snake.draw() 
food.draw() 
pygame.display.flip() 
# Cap the frame rate 
clock.tick(SPEED) 
# Quit Pygame 
pygame.quit()
```
This code sets up a basic game loop where the snake moves in 
response to key presses, and the game ends if the snake hits the 
edge of the window or its own tail. The snake grows in length 
each time it eats the food. The game continues until the player 
closes the window.
Run Code
Q2: Add a scoring system in the top left corner
To add a scoring system to the top left corner of the game 
window, you can create a function to display the score and 
increment it each time the snake eats the food. Here's how you 
can modify the code to include a scoring system:
```python
…
running = True
While running:
…
# Draw everything 
screen.fill(BLACK) 
snake.draw() 
food.draw()
display_score(score)  # Display the score
pygame.display.flip() 
# Cap the frame rate 
clock.tick(SPEED) 
# Quit Pygame 
pygame.quit()
```
In this updated code, we've added a  `score`  variable to keep 
track of the player's score, which is incremented each time the 
snake eats the food. The  `display_score`  function is used to 
render the score text and display it in the top left corner of the 
window. The  `display_score`  function is called after the snake 
has moved and the screen has been filled with the black color, 
but before the  `pygame.display.flip()`  call, so that the score is 
drawn on top of everything else.
Run Code
Figure 4  |  An example of responses from DeepSeek-Coder-Instruct 33B in a multi-turn setting.
4.   Experimental Results
In this section, we evaluate DeepSeek-Coder on four tasks, including code generation (§4.1), FIM
code completion (§4.2), cross-file code completion (§4.3) and program-based math reasoning
(§4.4).   We compare DeepSeek-Coder with the previous state-of-the-art large language models:
•   CodeGeeX2   (Zheng   et   al.,   2023)   represents   the   second   generation   of   the   multilingual
code generation model CodeGeeX. It is developed using the ChatGLM2 (Du et al., 2022)
architecture and is enhanced with an extensive dataset of coding examples.
•   StarCoder  (Li et al., 2023) is a publicly accessible model with a substantial parameter count
of 15 billion.   It is specifically trained on a meticulously curated subset of the Stack dataset
(Kocetkov   et   al.,   2022),   covering   86   programming   languages,   ensuring   its   proficiency
across a wide range of coding tasks.
•   CodeLlama  (Roziere et al., 2023) encompasses a series of code-centric Large Language
Models (LLMs) that are derivatives of LLaMA2 (Touvron et al., 2023).   Available in three
sizes — 7B, 13B, and 34B — these models undergo continued training on a vast 500 billion
token code corpus, building upon the foundational LLaMA2 architecture.
•   code-cushman-001  Chen et al. (2021) is a 12 billion parameter model developed by OpenAI
and served as the initial model for Github Copilot.
•   GPT-3.5 and GPT-4  (OpenAI, 2023) are   advanced generative AI models developed by
OpenAI. While they are not explicitly trained for code generation, they also demonstrate
10

---


<!-- Page 11 -->

notable performance in this domain.   Their effectiveness in handling code generation tasks
is largely attributed to their massive scale in terms of parameter count.
4.1.   Code Generation
HumanEval and MBPP Benchmarks
The HumanEval   (Chen et al., 2021) and MBPP   (Austin
et al., 2021) benchmarks are widely used for evaluating code LLMs.   HumanEval consists of 164
hand-written Python problems that are validated using test cases to assess the code generated
by   a   Code   LLM   in   a   zero-shot   setting,   while   the   MBPP   benchmark   includes   500   problems
in   a   few-shot   setting.   To   evaluate   the   model’s   multilingual   capabilities,   we   expanded   the
Python problems of Humaneval Benchmark to seven additional commonly used programming
languages, namely C++, Java, PHP, TypeScript (TS), C#, Bash, and JavaScript (JS) (Cassano et al.,
2023).   For both benchmarks, We adopted a greedy search approach and re-implemented the
baseline results using the same script and environment for fair comparison.
Multilingual Base Models
Instruction-Tuned Models
Table 3  |  Performance of approaches on the Multilingual HumanEval and MBPP Benchmarks.
The results are presented in Table 3.   As we can see, DeepSeek-Coder-Base achieves state-
of-the-art performance with an average accuracy of 50.3% on HumanEval and 66.0% on MBPP.
In comparison to the similarly sized open-source model CodeLlama-Base 34B, our model has
demonstrated   a   notable   improvement   of   9%   and   11%   in   accuracy,   respectively.   It’s   worth
noting that   even our   smaller model,   DeepSeek-Coder-Base 6.7B,   surpasses the   performance
of CodeLlama-Base 34B. After instruction fine-tuning, our model surpasses the closed-source
GPT-3.5-Turbo model in HumanEval benchmark, significantly reducing the performance gap
between OpenAI GPT-4 and open-source models.
DS-1000 Benchmark
HumanEval and MBPP have a significant drawback in that they rely
heavily on straightforward programming tasks that may not accurately represent the kind of
code most programmers typically write.   In contrast, the DS-1000 benchmark, as introduced in
the work by   Lai et al. (2023), offers a comprehensive collection of 1,000 practical and realistic data
science workflows across seven different libraries.   This benchmark evaluates code generation by
executing it against specific test cases.   What sets DS-1000 apart is its categorization of problems
based on the libraries involved, which encompass Matplotlib, NumPy, Pandas, SciPy, Scikit-
11


| Model Size | Python | C++ | Java | PHP | TS | C# | Bash | JS | Avg | MBPP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |



| code-cushman-001 12B CodeGeeX2 6B StarCoderBase 16B CodeLlama 7B CodeLlama 13B CodeLlama 34B | 33.5% 36.0% 31.7% 31.7% 36.0% 48.2% | 31.9% 29.2% 31.1% 29.8% 37.9% 44.7% | 30.6% 25.9% 28.5% 34.2% 38.0% 44.9% | 28.9% 23.6% 25.4% 23.6% 34.2% 41.0% | 31.3% 20.8% 34.0% 36.5% 45.2% 42.1% | 22.1% 29.7% 34.8% 36.7% 43.0% 48.7% | 11.7% 6.3% 8.9% 12.0% 16.5% 15.8% | - 24.8% 29.8% 29.2% 32.3% 42.2% | - 24.5% 28.0% 29.2% 35.4% 41.0% | - 36.2% 42.8% 38.6% 48.4% 55.2% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-Coder-Base 1.3B DeepSeek-Coder-Base 6.7B DeepSeek-Coder-Base 33B | 34.8% 49.4% 56.1% | 31.1% 50.3% 58.4% | 32.3% 43.0% 51.9% | 24.2% 38.5% 44.1% | 28.9% 49.7% 52.8% | 36.7% 50.0% 51.3% | 10.1% 28.5% 32.3% | 28.6% 48.4% 55.3% | 28.3% 44.7% 50.3% | 46.2% 60.6% 66.0% |



| GPT-3.5-Turbo - GPT-4 - | 76.2% 84.1% | 63.4% 76.4% | 69.2% 81.6% | 60.9% 77.2% | 69.1% 77.4% | 70.8% 79.1% | 42.4% 58.2% | 67.1% 78.0% | 64.9% 76.5% | 70.8% 80.0% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-Coder-Instruct 1.3B DeepSeek-Coder-Instruct 6.7B DeepSeek-Coder-Instruct 33B | 65.2% 78.6% 79.3% | 45.3% 63.4% 68.9% | 51.9% 68.4% 73.4% | 45.3% 68.9% 72.7% | 59.7% 67.2% 67.9% | 55.1% 72.8% 74.1% | 12.7% 36.7% 43.0% | 52.2% 72.7% 73.9% | 48.4% 66.1% 69.2% | 49.4% 65.4% 70.0% |


---


<!-- Page 12 -->

Learn, PyTorch, and TensorFlow.   The benchmark assesses the performance of base models in the
code completion setting and we provide pass@1 results for each library, as well as overall score.
The results of DS-1000 benchmark are shown in Table 4.   As can be seen from the table, the
DeepSeek-Coder model achieves relatively high accuracy in all libraries, demonstrating that our
model is not only capable of generating good code but also of using libraries more accurately in
real data science workflows.
Table 4  |  Performance of different approaches on the DS-1000-Tasks.
LeetCode Contest Benchmark
To further validate the model’s capability in real-world pro-
gramming   problems,   we   construct   the   LeetCode   Contest   benchmark 3 .   LeetCode 4   presents
competition-level problems, offering significant challenges that test the model’s problem under-
standing and code generation skills.   We collected the latest problems from LeetCode Contests to
prevent the appearance of both the problems or their solutions in our pre-training data.   A total
of 180 problems were collected from July 2023 to January 2024.   For each problem, we collected
100 test cases to ensure the test coverage.   We use the template "{problem_description}\nPlease
complete the code below to solve the above problem:\n ``` python\n{code_template}\n ``` " to
build the instruction prompt.
The evaluation results are shown in Table 5.   In our evaluation, the DeepSeek-Coder models
demonstrate remarkable performance over current open-source coding models.   Specifically, the
DeepSeek-Coder-Instruct 6.7B and 33B achieve Pass@1 scores of 19.4% and 27.8% respectively
in this benchmark.   This performance notably surpasses existing open-sourced models such as
Code-Llama-33B. The DeepSeek-Coder-Instruct 33B is the only open-sourced model that outper-
forms OpenAI’s GPT-3.5-Turbo in this task.   However, there remains a substantial performance
gap when compared to the more advanced GPT-4-Turbo.
Our analysis indicates that the implementation of Chain-of-Thought (CoT) prompting no-
tably enhances the capabilities of DeepSeek-Coder-Instruct models.   This improvement becomes
particularly   evident   in   the   more   challenging   subsets   of   tasks.   By   adding   the   directive,   "You
need first to write a step-by-step outline and then write the code." following the initial prompt,
we have observed enhancements in performance.   This observation leads us to believe that the
process of first crafting detailed code descriptions assists the model in more effectively under-
standing and addressing the intricacies of logic and dependencies in coding tasks, particularly
those of higher complexity. Therefore, we strongly recommend employing CoT prompting strate-
gies when utilizing DeepSeek-Coder-Instruct models for complex coding challenges.   Such an
approach promotes a more methodical and logical framework for problem-solving, potentially
resulting in more precise and efficient outcomes in code generation tasks.
3 We have published this benchmark in  https://github.com/deepseek-ai/DeepSeek-Coder/tree/main
/Evaluation/LeetCode .
4 https://leetcode.com/
12


| Model Size | Matplotlib | Numpy | Pandas | Pytorch | Scipy | Scikit-Learn | Tensorflow | Avg |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CodeGeeX2 6B StarCoder-Base 16B CodeLlama-Base 7B CodeLlama-Base 13B CodeLlama-Base 34B | 38.7% 43.2% 41.9% 46.5% 50.3% | 26.8% 29.1% 24.6% 28.6% 42.7% | 14.4% 11.0% 14.8% 18.2% 23.0% | 11.8% 20.6% 16.2% 19.1% 25.0% | 19.8% 23.6% 18.9% 18.9% 28.3% | 27.0% 32.2% 17.4% 27.8% 33.9% | 17.8% 15.6% 17.8% 33.3% 40.0% | 22.9% 24.6% 22.1% 26.8% 34.3% |
| DeepSeek-Coder-Base 1.3B DeepSeek-Coder-Base 6.7B DeepSeek-Coder-Base 33B | 32.3% 48.4% 56.1% | 21.4% 35.5% 49.6% | 9.3% 20.6% 25.8% | 8.8% 19.1% 36.8% | 8.5% 22.6% 36.8% | 16.5% 38.3% 40.0% | 8.9% 24.4% 46.7% | 16.2% 30.5% 40.2% |


---


<!-- Page 13 -->

Model
Size
Easy (45)
Medium (91)
Hard (44)
Overall(180)
Table 5  |  Performance of different models on the LeetCode Contest Benchmark.
It is important to acknowledge that despite our diligent efforts to gather the most recent
code questions for model testing, the possibility of data contamination cannot be entirely ruled
out.   We observed that the GPT-4-Turbo and DeepSeek-Coder models achieved higher scores
in the LeetCode Contest held in July and August.   We encourage the research community to
consider the potential issue of data contamination when evaluating models in future studies
using our released LeetCode data.
4.2.   Fill-in-the-Middle Code Completion
DeepSeek-Coder models are trained with a 0.5 FIM (Fill-In-the-Middle) rate during their pre-
training phase.   This specialized training strategy empowers the model to proficiently generate
code by filling in blanks based on the surrounding context, both prefix and suffix, of the given
code   snippet.   This   capability   is   particularly   advantageous   in   the   realm   of   code   completion
tools.   Several open-source models have emerged with similar capabilities.   Notable among these
are SantaCoder (Allal et al., 2023), StarCoder (Li et al., 2023), and CodeLlama (Roziere et al.,
2023).   These models have set a precedent in the field of code generation and completion.   In
evaluating the performance DeepSeek-Coder models, we conducted a comparative analysis with
the aforementioned models.   The benchmark for this comparison was the Single-Line Infilling
benchmarks, encompassing three different programming languages, as proposed by Allal et al.
(2023).   This benchmark uses the line exact match accuracy as the evaluation metric.
Model
Size
python
java
javascript
Mean
Table 6  |  Performance of different approaches on the FIM-Tasks.
The evaluation results are shown in Table 6.   Despite being the smallest model with a capacity
13


| WizardCoder-V1.0 15B CodeLlama-Instruct 34B Phind-CodeLlama-V2 34B | 17.8% 24.4% 26.7% | 1.1% 4.4% 8.8% | 0.0% 4.5% 9.1% | 5.0% 9.4% 13.3% |
| --- | --- | --- | --- | --- |



| GPT-3.5-Turbo - GPT-3.5-Turbo + CoT - GPT-4-Turbo - GPT-4-Turbo + CoT - | 46.7% 42.2% 73.3% 71.1% | 15.4 % 15.4% 31.9% 35.2% | 15.9% 20.5% 25.0% 25.0% | 23.3% 23.3% 40.6% 41.8% |
| --- | --- | --- | --- | --- |



| DeepSeek-Coder-Instruct 1.3B DeepSeek-Coder-Instruct + CoT 1.3B DeepSeek-Coder-Instruct 6.7B DeepSeek-Coder-Instruct + CoT 6.7B DeepSeek-Coder-Instruct 33B DeepSeek-Coder-Instruct + CoT 33B | 22.2% 22.2% 44.4% 44.4% 57.8% 53.3% | 1.1% 2.2% 12.1% 17.6% 22.0% 25.3% | 4.5% 2.3% 9.1% 4.5% 9.1% 11.4% | 7.2% 7.2% 19.4% 21.1% 27.8% 28.9% |
| --- | --- | --- | --- | --- |



| SantaCoder 1.1B StarCoder 16B CodeLlama-Base 7B CodeLlama-Base 13B | 44.0% 62.0% 67.6% 68.3% | 62.0% 73.0% 74.3% 77.6% | 74.0% 74.0% 80.2% 80.7% | 69.0% 69.7% 69.7% 75.5% |
| --- | --- | --- | --- | --- |



| DeepSeek-Coder-Base 1B DeepSeek-Coder-Base 7B DeepSeek-Coder-Base 33B | 57.4% 66.6% 65.4% | 82.2% 88.1% 86.6% | 71.7% 79.7% 82.5% | 70.4% 80.7% 81.2% |
| --- | --- | --- | --- | --- |


---


<!-- Page 14 -->

of 1.3 billion parameters, DeepSeek-Coder outperforms its larger counterparts, StarCoder and
CodeLlama,   in   these   benchmarks.   This   superior   performance   can   be   attributed   to   the   high
quality   of   the   pre-trained   data   utilized   by   DeepSeek-Coder.   Furthermore,   a   notable   trend
observed is the correlation between the size of the model and its performance.   As the model
size   increases,   there   is   a   corresponding   and   responsible   enhancement   in   performance.   This
trend   underscores   the   importance   of   model   capacity   in   achieving   higher   accuracy   in   code
completion tasks.   Based on these findings, we recommend the deployment of the DeepSeek-
Coder-Base   6.7B   model   in   code   completion   tools.   This   recommendation   is   grounded   in   the
model’s demonstrated balance between efficiency and accuracy.   The DeepSeek-Coder-Base 6.7B
model, with its substantial parameter size, has proven to be highly effective in the context of
code completion, making it an ideal choice for integrating advanced computational capabilities
into coding environments.
4.3.   Cross-File Code Completion
In this section, we will evaluate the performance of existing open-source models in cross-file
code completion tasks.   Unlike code generation discussed in the previous section, cross-file code
completion requires the model to access and understand repositories that span multiple files
with numerous cross-file dependencies.   We use CrossCodeEval (Ding et al., 2023) to evaluate the
capabilities of currently available open-source code models of 7B scale in cross-file completion
tasks.   This dataset is constructed on a diverse set of real-world, open-sourced, permissively
licensed repositories in four popular programming languages:   Python, Java, TypeScript, and C#.
The dataset is specifically designed to strictly require cross-file context for accurate completion.
Notably, this dataset was constructed from repositories created between March and June 2023,
while our pre-training data only includes code created before February 2023, which ensures that
this dataset was not present in our pre-training data, thus avoiding data leakage.
Model
Size
Python
Java
TypeScript
C#
EM
ES
EM
ES
EM
ES
EM
ES
CodeGeex2
6B
8.11%
59.55%
7.34%
59.60%
6.14%
55.50%
1.70%
51.66%
+ Retrieval
10.73%
61.76%
10.10%
59.56%
7.72%
55.17%
4.64%
52.30%
StarCoder-Base
7B
6.68%
59.55%
8.65%
62.57%
5.01%
48.83%
4.75%
59.53%
+ Retrieval
13.06%
64.24%
15.61%
64.78%
7.54%
42.06%
14.20%
65.03%
CodeLlama-Base
7B
7.32%
59.66%
9.68%
62.64%
8.19%
58.50%
4.07%
59.19%
+ Retrieval
13.02%
64.30%
16.41%
64.64%
12.34%
60.64%
13.19%
63.04%
DeepSeek-Coder-Base
6.7B
9.53%
61.65%
10.80%
61.77%
9.59%
60.17%
5.26%
61.32%
+ Retrieval
16.14%
66.51%
17.72%
63.18%
14.03%
61.77%
16.23%
63.42%
+ Retrieval w/o Repo Pre-training
16.02%
66.65%
16.64%
61.88%
13.23%
60.92%
14.48%
62.38%
Table 7  |  Performance of different models on cross-file code completion.
In our evaluation of various models, we set the maximum sequence length to 2048 tokens,
the maximum output length to 50 tokens, and a limit of 512 tokens for the cross-file context.   For
the cross-file context, we utilize the official BM25 search results provided by   Ding et al. (2023).
Evaluation metrics include exact match and edit similarity.   The results, presented in Table 7,
demonstrate that DeepSeek-Coder consistently outperforms other models in cross-file comple-
tion tasks across multiple languages, showcasing its superior practical application capabilities.
When only utilizing file-level code corpus ( w/o Repo Pre-training ) to pre-train DeepSeek-Coder,
we observe a decrease in performance in the Java, TypeScript, and C# languages, indicating the
effectiveness of the repository-level pre-training.
14

---


<!-- Page 15 -->

4.4.   Program-based Math Reasoning
Program-based math reasoning involves evaluating a model’s ability to understand and solve
mathematical   problems   through   programming.   This   type   of   reasoning   is   critical   in   fields
such   as   data   analysis   and   scientific   computing.   To   conduct   this   assessment,   we   utilize   the
Program-Aided Math Reasoning (PAL) method as outlined in Gao et al. (2023).   This approach
is   applied   across   seven   distinct   benchmarks,   each   offering   unique   challenges   and   contexts.
These benchmarks includes GSM8K (Cobbe et al., 2021), MATH (Hendrycks et al., 2021), GSM-
Hard   (Gao   et   al.,   2023),   SVAMP   (Patel   et   al.,   2021),   TabMWP   (Lu   et   al.,   2022),   ASDiv   (Miao
et al., 2020) and MAWPS (Gou et al., 2023).   In each of these benchmarks, the model is prompted
to   alternately   describe   a   solution   step   in   natural   language   and   then   execute   that   step   with
code.   As seen in Table 8, DeepSeek-Coder models achieve a remarkable performance across all
benchmarks, especially the 33B variant, which demonstrates the potential of using such models
in applications that require complex mathematical computations and problem-solving abilities.
Model
Size
GSM8k
MATH
GSM-Hard
SVAMP
TabMWP
ASDiv
MAWPS
Avg
Multilingual Base Models
Table 8  |  Performance of different approaches on the program-aid math reasoning tasks.
5.   Continue Pre-Training From General LLM
To further enhance the natural language understanding and mathematical reasoning abilities
of the DeepSeek-Coder model, we perform additional pre-training from the general language
model DeepSeek-LLM-7B Base (DeepSeek-AI, 2024) on 2 trillion tokens, resulting in DeepSeek-
Coder-v1.5 7B. For this pre-training, we specifically use the data sources listed in Table 9.   Unlike
DeepSeek-Coder, DeepSeek-Coder-v1.5 employs solely a next token prediction objective with a
4K context length during its pre-training phase.
Data Source
Percentage
Table 9  |  Data sources for DeepSeek-Coder-v1.5 7B pre-training
We conduct a comparison between DeepSeek-Coder-v1.5 7B and DeepSeek-Coder 6.7B, and
re-run all benchmarks using our evaluation pipeline to ensure a fair comparison.   We evaluate
performance across a wide range of tasks, which can be categorized as follows:
15


| CodeGeex-2 7B StarCoder-Base 16B CodeLlama-Base 7B CodeLlama-Base 13B CodeLlama-Base 34B | 22.2% 23.4% 31.2% 43.1% 58.2% | 9.7% 10.3% 12.1% 14.4% 21.2% | 23.6% 23.0% 30.2% 40.2% 51.8% | 39.0% 42.4% 54.2% 59.2% 70.3% | 44.6% 45.0% 52.9% 60.3% 69.8% | 48.5% 54.9% 59.6% 63.6% 70.7% | 66.0% 81.1% 82.6% 85.3% 91.8% | 36.2% 40.0% 46.1% 52.3% 62.0% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-Coder-Base 1.3B DeepSeek-Coder-Base 6.7B DeepSeek-Coder-Base 33B | 14.6% 43.2% 60.7% | 16.8% 19.2% 29.1% | 14.5% 40.3% 54.1% | 36.7% 58.4% 71.6% | 30.0% 67.9% 75.3% | 48.2% 67.2% 76.7% | 62.3% 87.0% 93.3% | 31.9% 54.7% 65.8% |



| Source Code Markdown and StackExchange Natural language related to code Natural language related to math Bilingual (Chinese-English) natural language | 70% 10% 7% 7% 6% |
| --- | --- |


---


<!-- Page 16 -->

•   Programming :   This   category   includes   evaluations   in   a   multilingual   setting   using   the
HumanEval dataset by Chen et al. (2021), as well as evaluations in a Python setting using
the MBPP dataset by Austin et al. (2021)
•   Math   Reasoning :   We   assess   performance   on   math   reasoning   tasks   using   the   GSM8K
benchmark   (Cobbe et al., 2021) and the MATH   (Hendrycks et al., 2021) benchmark [4].
These tasks involve solving math problems by generating programs.
•   Natural Language  Our evaluation in natural language tasks includes MMLU (Hendrycks
et al., 2020), BBH (Suzgun et al., 2022), HellaSwag (Zellers et al., 2019), Winogrande (Sak-
aguchi et al., 2021), and ARC-Challenge (Clark et al., 2018) benchmarks.
The   results   for   the   Base   and   Instruct   models   are   presented   in   Table   10.   It   is   observed
that   the   DeepSeek-Coder-Base-v1.5   model,   despite   a   slight   decrease   in   coding   performance,
shows marked improvements across most tasks when compared to the DeepSeek-Coder-Base
model.   In   particular,   in   the   Math   Reasoning   and   Natural   Language   categories,   DeepSeek-
Coder-Base-v1.5 significantly outperforms its predecessor across all benchmarks, which also
demonstrates significant improvements in its mathematical reasoning and natural language
processing capabilities.
Programming
Math Reasoning
Natural Language
Models
Size   HumanEval   MBPP   GSM8K   MATH   MMLU
BBH
HellaSwag   WinoG   ARC-C
DeepSeek-Coder-Base
6.7B
44.7%
60.6%
43.2%
19.2%
36.6%
44.3%
53.8%
57.1%
32.5%
DeepSeek-Coder-Base-v1.5
6.9B
43.2%
60.4%
62.4%
24.7%
49.1%
55.2%
69.9%
63.8%
47.2%
DeepSeek-Coder-Instruct
6.7B
66.1%
65.4%
62.8%
28.6%
37.2%
46.9%
55.0%
57.6%
37.4%
DeepSeek-Coder-Instruct-v1.5   6.9B
64.1%
64.6%
72.6%
34.1%
49.5%
53.3%
72.2%
63.4%
48.1%
Table 10  |  Comparative analysis of performance between DeepSeek-Coder-Base and
DeepSeek-Coder-Base-v1.5.   Math tasks are solved through programming.
6.   Conclusion
In this technical report, we introduce a series of specialized Large Language Models (LLMs) for
coding, named DeepSeek-Coder, available in three distinct scales: 1.3B, 6.7B, and 33B parameters.
These models are uniquely trained on a meticulously curated project-level code corpus, utilizing
a "fill-in-the-blank" pre-training objective to enhance code infilling capabilities.   A significant
advancement is the extension of the models’ context window to 16,384 tokens, thereby greatly
improving   their   effectiveness   in   handling   extensive   code   generation   tasks.   Our   evaluations
reveal that the most advanced model in our series, DeepSeek-Coder-Base 33B surpasses existing
open-source code models across a variety of standard tests.   Impressively, the DeepSeek-Coder-
Base 6.7B model, despite its smaller scale, delivers performance on par with the 34B parameter
CodeLlama, a testament to the high quality of our pretraining corpus.
To augment the zero-shot instruction capabilities of the DeepSeek-Coder-Base models, we
have fine-tuned them with high-quality instructional data.   This has led to the DeepSeek-Coder-
Instruct 33B model outperforming OpenAI’s GPT-3.5 Turbo in a range of coding-related tasks,
showcasing its exceptional proficiency in code generation and understanding.
To further improve the natural language understanding capabilities of the DeepSeek-Coder-
Base models, we have conducted additional pretraining based on the DeepSeek-LLM 7B check-
point.   This additional training involved processing a diverse dataset comprising 2 billion tokens,
including natural language, code, and mathematical data.   The result is the creation of a new
16

---


<!-- Page 17 -->

and improved code model, DeepSeek-Coder-v1.5.   Our observations indicate that DeepSeek-
Coder-v1.5 not only maintains its predecessor’s high-level coding performance but also exhibits
enhanced natural language comprehension.   This advancement underscores our belief that the
most effective code-focused Large Language Models (LLMs) are those built upon robust general
LLMs.   The reason is evident:   to effectively interpret and execute coding tasks, these models
must also possess a deep understanding of human instructions, which often come in various
forms of natural language.   Looking ahead, our commitment is to develop and openly share
even more powerful code-focused LLMs based on larger-scale general LLMs.
Acknowledgements
We   would   like   to   express   our   gratitude   to   Bo   Liu,   Chengqi   Deng,   Chong   Ruan,   Damai   Dai,
Jiashi Li, Kang Guan, Mingchuan Zhang, Panpan Huang, Shuiping Yu, Shirong Ma, Yaofeng
Sun, Yishi Piao, Zhihong Shao, and Zhewen Hao for their invaluable discussions and assistance
during training DeepSeek-Coder models.
References
L. B. Allal, R. Li, D. Kocetkov, C. Mou, C. Akiki, C. M. Ferrandis, N. Muennighoff, M. Mishra,
A. Gu, M. Dey, et al.   Santacoder:   don’t reach for the stars!   arXiv preprint arXiv:2301.03988 ,
2023.
J. Austin, A. Odena, M. Nye, M. Bosma, H. Michalewski, D. Dohan, E. Jiang, C. Cai, M. Terry,
Q. Le, and C. Sutton.   Program synthesis with large language models, 2021.
M. Bavarian, H. Jun, N. Tezak, J. Schulman, C. McLeavey, J. Tworek, and M. Chen.   Efficient
training of language models to fill in the middle.   arXiv preprint arXiv:2207.14255, 2022.
F.   Cassano,   J.   Gouwar,   D.   Nguyen,   S.   Nguyen,   L.   Phipps-Costin,   D.   Pinckney,   M.-H.   Yee,
Y. Zi, C. J. Anderson, M. Q. Feldman, et al.   Multipl-e:   a scalable and polyglot approach to
benchmarking neural code generation.   IEEE Transactions on Software Engineering, 2023.
M.   Chen,   J.   Tworek,   H.   Jun,   Q.   Yuan,   H.   P.   d.   O.   Pinto,   J.   Kaplan,   H.   Edwards,   Y.   Burda,
N.   Joseph,   G.   Brockman,   et   al.   Evaluating   large   language   models   trained   on   code.   arXiv
preprint arXiv:2107.03374, 2021.
S. Chen, S. Wong, L. Chen, and Y. Tian.   Extending context window of large language models via
positional interpolation.   arXiv preprint arXiv:2306.15595, 2023.
P.   Clark,   I.   Cowhey,   O.   Etzioni,   T.   Khot,   A.   Sabharwal,   C.   Schoenick,   and   O.   Tafjord.   Think
you have solved question answering?   try arc,   the ai2 reasoning challenge.   arXiv preprint
arXiv:1803.05457, 2018.
K.   Cobbe,   V.   Kosaraju,   M.   Bavarian,   M.   Chen,   H.   Jun,   L.   Kaiser,   M.   Plappert,   J.   Tworek,
J. Hilton, R. Nakano, et al.   Training verifiers to solve math word problems.   arXiv preprint
arXiv:2110.14168, 2021.
T. Dao.   Flashattention-2:   Faster attention with better parallelism and work partitioning, 2023.
DeepSeek-AI.   Deepseek llm:   Scaling open-source language models with longtermism.   arXiv
preprint arXiv:2401.02954, 2024.
17

---


<!-- Page 18 -->

Y.   Ding,   Z.   Wang,   W. U. Ahmad,   H. Ding,   M. Tan,   N. Jain,   M. K. Ramanathan,   R. Nallapati,
P. Bhatia, D. Roth, et al.   Crosscodeeval:   A diverse and multilingual benchmark for cross-file
code completion.   In  Thirty-seventh Conference on Neural Information Processing Systems
Datasets and Benchmarks Track, 2023.
Z. Du,   Y. Qian,   X. Liu,   M. Ding,   J. Qiu,   Z. Yang,   and J. Tang.   Glm:   General language model
pretraining with autoregressive blank infilling.   In  Proceedings of the 60th Annual Meeting
of   the   Association   for   Computational   Linguistics   (Volume   1:   Long   Papers) ,   pages   320–335,
2022.
D. Fried, A. Aghajanyan, J. Lin, S. Wang, E. Wallace, F. Shi, R. Zhong, W.-t. Yih, L. Zettlemoyer,
and M. Lewis.   Incoder:   A generative model for code infilling and synthesis.   arXiv preprint
arXiv:2204.05999, 2022.
L. Gao, A. Madaan, S. Zhou, U. Alon, P. Liu, Y. Yang, J. Callan, and G. Neubig.   Pal:   Program-
aided   language   models.   In   International   Conference   on   Machine   Learning ,   pages   10764–
10799. PMLR, 2023.
G. Gemini Team.   Gemini:   A family of highly capable multimodal models, 2023.   URL  https:
//goo.gle/GeminiPaper .
Z. Gou, Z. Shao, Y. Gong, Y. Yang, M. Huang, N. Duan, W. Chen, et al.   Tora:   A tool-integrated
reasoning agent for mathematical problem solving.   arXiv preprint arXiv:2309.17452, 2023.
D. Hendrycks,   C. Burns,   S. Basart,   A. Zou,   M. Mazeika,   D. Song,   and J. Steinhardt.   Measur-
ing   massive   multitask   language   understanding.   In   International   Conference   on   Learning
Representations, 2020.
D. Hendrycks, C. Burns, S. Kadavath, A. Arora, S. Basart, E. Tang, D. Song, and J. Steinhardt. Mea-
suring mathematical problem solving with the math dataset.   arXiv preprint arXiv:2103.03874 ,
2021.
High-Flyer.   Hai-llm:   An efficient and lightweight tool for training large models.   2023.   URL
https://www.high-flyer.cn/en/blog/hai-llm .
kaiokendev.   Things i’m learning while training superhot.   https://kaiokendev.github.io
/til#extending-context-to-8k , 2023.
D. Kocetkov, R. Li, L. Jia, C. Mou, Y. Jernite, M. Mitchell, C. M. Ferrandis, S. Hughes, T. Wolf,
D. Bahdanau,   et al.   The stack:   3 tb of permissively licensed source code.   Transactions   on
Machine Learning Research, 2022.
V. A. Korthikanti, J. Casper, S. Lym, L. McAfee, M. Andersch, M. Shoeybi, and B. Catanzaro.
Reducing   activation   recomputation   in   large   transformer   models.   Proceedings   of   Machine
Learning and Systems, 5, 2023.
Y. Lai, C. Li, Y. Wang, T. Zhang, R. Zhong, L. Zettlemoyer, W.-t. Yih, D. Fried, S. Wang, and T. Yu.
Ds-1000:   A natural and reliable benchmark for data science code generation.   In  International
Conference on Machine Learning, pages 18319–18345. PMLR, 2023.
K. Lee, D. Ippolito, A. Nystrom, C. Zhang, D. Eck, C. Callison-Burch, and N. Carlini.   Deduplicat-
ing training data makes language models better.   In  Proceedings of the 60th Annual Meeting
of the Association for Computational Linguistics (Volume 1:   Long Papers) , pages 8424–8445,
2022.
18

---


<!-- Page 19 -->

R. Li, L. B. Allal, Y. Zi, N. Muennighoff, D. Kocetkov, C. Mou, M. Marone, C. Akiki, J. Li, J. Chim,
et al.   Starcoder:   may the source be with you!   arXiv preprint arXiv:2305.06161, 2023.
I. Loshchilov and F. Hutter.   Decoupled weight decay regularization, 2019.
P. Lu, L. Qiu, K.-W. Chang, Y. N. Wu, S.-C. Zhu, T. Rajpurohit, P. Clark, and A. Kalyan.   Dynamic
prompt   learning   via   policy   gradient   for   semi-structured   mathematical   reasoning.   In   The
Eleventh International Conference on Learning Representations, 2022.
S.-Y. Miao, C.-C. Liang, and K.-Y. Su.   A diverse corpus for evaluating and developing english
math word problem solvers.   In  Proceedings of the 58th Annual Meeting of the Association
for Computational Linguistics, pages 975–984, 2020.
D.   Narayanan,   A.   Harlap,   A.   Phanishayee,   V.   Seshadri,   N.   R.   Devanur,   G.   R.   Ganger,   P.   B.
Gibbons,   and   M.   Zaharia.   Pipedream:   Generalized   pipeline   parallelism   for   dnn   training.
In   Proceedings   of   the   27th   ACM   Symposium   on   Operating   Systems   Principles ,   pages 1–15,
2019.
E. Nijkamp, B. Pang, H. Hayashi, L. Tu, H. Wang, Y. Zhou, S. Savarese, and C. Xiong.   Codegen:
An open large language model for code with multi-turn program synthesis.   arXiv preprint
arXiv:2203.13474, 2022.
E. Nijkamp, H. Hayashi, C. Xiong, S. Savarese, and Y. Zhou.   Codegen2:   Lessons for training
llms on programming and natural languages, 2023.
OpenAI.   Gpt-4 technical report, 2023.
A.   Patel,   S.   Bhattamishra,   and   N.   Goyal.   Are   nlp   models   really   able   to   solve   simple   math
word problems?   In  Proceedings of the 2021 Conference of the North American Chapter of
the Association for Computational Linguistics:   Human Language Technologies , pages 2080–
2094, 2021.
C. Raffel, N. Shazeer, A. Roberts, K. Lee, S. Narang, M. Matena, Y. Zhou, W. Li, and P. J. Liu.
Exploring the limits of transfer learning with a unified text-to-text transformer, 2023.
S. Rajbhandari, J. Rasley, O. Ruwase, and Y. He. Zero: Memory optimizations toward training tril-
lion parameter models.   In  SC20:   International Conference for High Performance Computing,
Networking, Storage and Analysis, pages 1–16. IEEE, 2020.
B. Roziere, J. Gehring, F. Gloeckle, S. Sootla, I. Gat, X. E. Tan, Y. Adi, J. Liu, T. Remez, J. Rapin,
et al.   Code llama:   Open foundation models for code.   arXiv preprint arXiv:2308.12950, 2023.
K. Sakaguchi, R. L. Bras, C. Bhagavatula, and Y. Choi.   Winogrande:   An adversarial winograd
schema challenge at scale.   Communications of the ACM, 64(9):99–106, 2021.
R. Sennrich, B. Haddow, and A. Birch.   Neural machine translation of rare words with subword
units.   arXiv preprint arXiv:1508.07909, 2015.
J. Su, Y. Lu, S. Pan, A. Murtadha, B. Wen, and Y. Liu.   Roformer:   Enhanced transformer with
rotary position embedding, 2023.
M. Suzgun, N. Scales, N. Schärli, S. Gehrmann, Y. Tay, H. W. Chung, A. Chowdhery, Q. V. Le,
E. H. Chi, D. Zhou, , and J. Wei.   Challenging big-bench tasks and whether chain-of-thought
can solve them.   arXiv preprint arXiv:2210.09261, 2022.
19

---


<!-- Page 20 -->

R.   Taori,   I.   Gulrajani,   T.   Zhang,   Y.   Dubois,   X. Li,   C.   Guestrin,   P.   Liang,   and T.   B. Hashimoto.
Stanford alpaca:   An instruction-following llama model.   https://github.com/tatsu-lab
/stanford_alpaca , 2023.
H.   Touvron,   L.   Martin,   K.   Stone,   P.   Albert,   A.   Almahairi,   Y.   Babaei,   N.   Bashlykov,   S.   Batra,
P. Bhargava, S. Bhosale, et al.   Llama 2:   Open foundation and fine-tuned chat models.   arXiv
preprint arXiv:2307.09288, 2023.
Y. Wang, W. Wang, S. Joty, and S. C. Hoi.   Codet5:   Identifier-aware unified pre-trained encoder-
decoder   models   for   code   understanding   and   generation.   arXiv   preprint   arXiv:2109.00859 ,
2021.
R. Zellers,   A. Holtzman,   Y. Bisk,   A. Farhadi,   and   Y. Choi.   Hellaswag:   Can   a machine   really
finish   your   sentence?
In   Proceedings   of   the   57th   Annual   Meeting   of   the   Association   for
Computational Linguistics, pages 4791–4800, 2019.
Q.   Zheng,   X.   Xia,   X.   Zou,   Y.   Dong,   S.   Wang,   Y.   Xue,   L.   Shen,   Z.   Wang,   A.   Wang,   Y.   Li,   et   al.
Codegeex:   A   pre-trained   model   for   code   generation   with   multilingual   benchmarking   on
humaneval-x. In  Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery
and Data Mining, pages 5673–5684, 2023.
20

---


<!-- Page 21 -->

A.   Cases of Chatting with DeepSeek-Coder-Instruct
We will present two cases of interactions with DeepSeek-Coder-Instruct, with one involving a
multi-turn conversation about creating a database and performing data analysis, and the other
centered around using a model to solve a sample problem from LeetCode.
In the first scenario, depicted in Figure 5, we instruct the model to build a student database
using Python and randomly insert 10 pieces of information.   Subsequently, in the second round
of   the   conversation,   we   continue   to   ask   the   model   by   analyzing   the   age   distribution   of   the
students.   From Figure 5, it’s evident that the model can generate bug-free and comprehensive
code, accompanied by explanatory details.   In the second scenario, as illustrated in Figure 6,
we further assess the model’s capabilities by testing it on an out-of-domain LeetCode contest
problem.   This particular problem was released in November 2023, after our data collection, and
thus, isn’t part of our model’s training data.   The results show that our model excels at solving
problems that extend beyond its training distribution.
Q1: Build a database in Python that includes 
various pieces of information about students, 
insert ten random records and display.
Sure, here is a simple example of how you can do this using 
SQLite in Python.
```python
import sqlite3
import random
# Connect to SQLite database
conn = sqlite3.connect(' students.db ')
# Create a cursor object
cur = conn.cursor()
…
# Create table
cur.execute(''’
CREATE TABLE IF NOT EXISTS students (
id INTEGER PRIMARY KEY,
name TEXT,
age INTEGER,
grade TEXT)  ''')
…
# Display all records
cur.execute( 'SELECT * FROM students ')
…
```
This script will create a SQLite database named 'students.db' 
and a table named 'students' with four columns: 'id', 'name', 'age', 
and 'grade'. It will then insert 10 random records into the table 
and display all records.  …
Run Code
Q2: create a graph depicting the age distribution.
To create a graph depicting the age distribution of the students, you 
can use the matplotlib library in Python. Here's how you can do it:
```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
# Connect to SQLite database
conn = sqlite3.connect(' students.db ')
# Read the data from the database into a pandas DataFrame
df = pd.read_sql_query(" SELECT * from students ", conn)
# Create a histogram of the age distribution
plt.hist(df['age'], bins=range(10, 30, 2), edgecolor='black')
plt.title(' Age Distribution of Students ')
plt.xlabel(' Age ')
plt.ylabel( 'Number of Students ')
plt.show()
# Close the connection
conn.close()
```
This script will connect to the SQLite database, read the data into a 
pandas DataFrame, then create a histogram of the age distribution. 
The histogram will show the number of students in each age range.
Run Code
Figure 5  |  An example of building database and data analysis.
21

---


<!-- Page 22 -->

Q:  There are n teams numbered from 0 to n - 1 in a tournament; each team is 
also a node in a  DAG .
You are given the integer n and a  0-indexed  2D integer array edges of 
length m representing the  DAG , where edges[i] = [u i , v i ] indicates that there is a 
directed edge from team u i  to team v i  in the graph.
A directed edge from a to b in the graph means that team a is  stronger  than 
team b and team b is  weaker  than team a.
Team a will be the  champion  of the tournament if there is no team b that 
is  stronger  than team a.
Return  the team that will be the  champion  of the tournament if there is 
a  unique  champion, otherwise, return  -1 .
Notes
• A  cycle  is a series of nodes a 1 , a 2 , ..., a n , a n+1  such that node a 1  is the same node 
as node a n+1 , the nodes a 1 , a 2 , ..., a n  are distinct, and there is a directed edge from 
the node a i  to node a i+1  for every i in the range [1, n].
• A  DAG  is a directed graph that does not have any  cycle .
• Example 1:
…
• Example 2:
…
Constraints:
…
Please follow the template below to solve the problem:
```python
class Solution:
def findChampion(self, n: int, edges: List[List[int]]) -> int: 
```
To solve this problem, we can use a topological sorting algorithm. The idea is to …
```python
from typing import List
class Solution:
def findChampion(self, n: int, edges: List[List[int]]) -> int:
# Create an adjacency list to represent the DAG
adj_list = {i: [] for i in range(n)}
for u, v in edges:
adj_list[u].append(v)
# Initialize a list to keep track of the number of …
in_degree = [0] * n
# Calculate the in-degree for each team
for u in adj_list:
for v in adj_list[u]:
in_degree[v] += 1
# Initialize a list to keep track of the teams with no incoming edges
no_incoming_edges = [i for i in range(n) if in_degree[i] == 0]
# If there is more than one team with no incoming edges, there is no unique 
champion
if len(no_incoming_edges) != 1:
return -1
# Return the team with no incoming edges, which is the champion
return no_incoming_edges[0]
```
This code first creates an adjacency list to represent the DAG. Then, …
Submit Code
Figure 6  |  An example of solving LeetCode Problem.
B.   Benchmark curves during training of DeepSeek-Coder-Base
In Figure 7, we present the benchmark curves illustrating the performance of DeepSeek-Coder-
Base models during their training phase.   For validation, a carefully curated subset of the training
corpus was employed,   consisting of 8,000 code files.   This subset was deliberately chosen to
ensure a diverse and representative sample, critical for an accurate assessment of the models’
capabilities.   The performance metrics of these models are specifically detailed in the final two
sub-figures of Figure 7, offering a clear visual representation of their efficacy throughout the
training process.
22

---


<!-- Page 23 -->

0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.0
0.1
0.2
0.3
0.4
0.5
Value
HumanEval-Pass@1
0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.0
0.1
0.2
0.3
0.4
0.5
0.6
Value
HumanEval-cpp-Pass@1
0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.0
0.1
0.2
0.3
0.4
0.5
0.6
Value
HumanEval-java-Pass@1
0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.50
0.55
0.60
0.65
0.70
0.75
0.80
0.85
Value
HumanEvalFIM-EM
0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.0
0.2
0.4
0.6
Value
MBPP-Pass@1
0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.0
0.1
0.2
0.3
0.4
0.5
Value
MeanHumanEval
0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.0
0.1
0.2
0.3
0.4
Value
Validation-Completion-EM
0
250
500
750
1000
1250
1500
1750
2000
Tokens (Billions)
0.0
0.1
0.2
0.3
0.4
0.5
Value
Validation-CompletionFIM-EM
DeepSeek-Coder-Base-1.3B
DeepSeek-Coder-Base-6.7B
DeepSeek-Coder-Base-33B
Figure 7  |  Benchmark curves during training of DeepSeek-Coder-Base.
23

---
