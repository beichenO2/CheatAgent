# intellichain

> 来源：`intellichain.pdf`（AutoOffice to-markdown）

IntelliChain:
An Integrated Framework for Enhanced Socratic
Method Dialogue with LLMs and Knowledge Graphs ∗

arXiv:2502.00010v1 [cs.CY] 7 Jan 2025

Changyong Qi1,2,3 , Linzhao Jia1,2,3 , Yuang Wei1,2,3 , Yuan-Hao Jiang1,2,3 Xiaoqing Gu4 †
2

1
Lab of Artificial Intelligence for Education, East China Normal University
Shanghai Institute of Artificial Intelligence for Education, East China Normal University
3
School of Computer Science and Technology, East China Normal University
4
Department of Educational Information Technology, East China Normal University

Abstract
With the continuous advancement of educational technology, the demand for
Large Language Models (LLMs) as intelligent educational agents in providing
personalized learning experiences is rapidly increasing. This study aims to explore
how to optimize the design and collaboration of a multi-agent system tailored
for Socratic teaching through the integration of LLMs and knowledge graphs
in a chain-of-thought dialogue approach, thereby enhancing the accuracy and
reliability of educational applications. By incorporating knowledge graphs, this
research has bolstered the capability of LLMs to handle specific educational content,
ensuring the accuracy and relevance of the information provided. Concurrently,
we have focused on developing an effective multi-agent collaboration mechanism
to facilitate efficient information exchange and chain dialogues among intelligent
agents, significantly improving the quality of educational interaction and learning
outcomes. In empirical research within the domain of mathematics education,
this framework has demonstrated notable advantages in enhancing the accuracy
and credibility of educational interactions. This study not only showcases the
potential application of LLMs and knowledge graphs in mathematics teaching but
also provides valuable insights and methodologies for the development of future
AI-driven educational solutions.

1

Introduction

The advancement of artificial intelligence technology, particularly the development of Large Language
Models (LLMs), is propelling educational innovation forward. These models demonstrate significant
potential in complex interactions, natural language understanding, and generation, paving the way
for new possibilities in creating intelligent educational agents [1]. In the realm of education, LLMs
support more personalized and interactive learning experiences, which are crucial for meeting diverse
learning needs and enhancing the quality of education [2]. However, despite LLMs’ remarkable
capabilities in enhancing the intelligence of educational applications, they still face challenges
regarding accuracy, reliability, and relevance to specific educational content [3].
∗

Qi, C., Jia L., Wei, Y., Jiang Y.-H., Gu, X. (2024). IntelliChain: An Integrated Framework for Enhanced
Socratic Method Dialogue with LLMs and Knowledge Graphs. Conference Proceedings of the 28th Global
Chinese Conference on Computers in Education (GCCCE 2024), 116–121. Chongqing, China: Global Chinese
Conference on Computers in Education.
†
Corresponding Author: xqgu@ses.ecnu.edu.cn
Conference Proceedings of the 28th Global Chinese Conference on Computers in Education (GCCCE 2024).

This study is dedicated to optimizing the information exchange and collaboration mechanisms among
intelligent agents through the chain-of-thought dialogue approach, combining LLMs and knowledge
graphs, to enhance teaching effectiveness and the learning experience. The chain-of-thought dialogue,
an interaction mode that simulates the human thought process, can promote a deeper understanding
and response among intelligent agents, offering learners richer and more targeted learning content
[4]. However, achieving this goal requires addressing the inherent shortcomings of relying on LLMs,
including improving the accuracy of interactions and ensuring the credibility of educational content
[5].
To overcome these challenges, this research proposes an innovative solution: integrating knowledge
graphs to enhance the credibility of LLMs’ application in educational settings, while optimizing
the design and collaboration of the multi-agent system. As an effective tool for organizing and
representing information, knowledge graphs provide rich, structured background knowledge for
LLMs, aiding intelligent agents in more accurately understanding and responding to educational
content [6]. Furthermore, by optimizing the design of the multi-agent system, this study aims to
achieve more effective collaboration and information sharing among intelligent agents, thereby
enhancing the educational outcomes based on the chain-of-thought dialogue approach. The goal of
this research is to develop a reliable and effective educational multi-agent system that can leverage
LLMs and knowledge graphs to provide personalized learning experiences and promote efficient
collaboration among intelligent agents through the chain-of-thought dialogue method. In this way, we
aim to offer a new and effective AI application mode in the field of educational technology, especially
in supporting complex teaching tasks and facilitating students’ learning processes.

2

Related Work

Amidst the rapid advancements in artificial intelligence, LLMs have unveiled unprecedented potential
in the field of education. Generative models have been demonstrated to effectively support adaptive
learning systems, automated content generation, and intelligent assessment mechanisms [7]. Their
capacity to understand and generate complex natural language offers robust support for personalized
educational pathways. However, the academic community has extensively discussed the limitations
and accuracy challenges of LLMs when dealing with domain-specific knowledge [8]. Despite their
revolutionary capabilities in language processing, how to effectively leverage these capabilities to
enhance learning efficiency and outcomes remains an open question in educational applications.
2.1

Chain-of-Thought Dialogues in Educational Technology

Chain-of-thought dialogue, as a method simulating human thought processes, has gained considerable
attention in educational technology research in recent years. By facilitating deeper and more coherent
exchanges, this approach aims to promote critical thinking and deep understanding among learners.
Research has highlighted that the implementation of chain-of-thought dialogue significantly enhances
learning motivation and engagement in online learning environments [9]. The integration of LLMs in
chain-of-thought dialogue represents a significant leap forward in educational technology research.
These models, when applied to simulate and generate chain-of-thought dialogues, offer the potential
to facilitate more nuanced and deep learning interactions [10]. Recent studies have explored how
LLMs like GPT-3.5 can be fine-tuned to produce sequential reasoning steps in problem-solving
tasks, effectively mimicking the human thought process [11]. This application not only enhances the
dialogue’s relevance and depth but also promotes a more engaging and interactive learning experience.
However, despite these advancements, challenges persist in ensuring the dialogues’ consistency with
factual accuracy and pedagogical objectives, indicating a fertile area for future research.
2.2

Leveraging Knowledge Graphs and Multi-Agent Systems to Transform Educational
Interactions

Knowledge graphs, as a structured representation of knowledge, play a critical role in enhancing the
knowledge base and reasoning capabilities of LLMs. By integrating rich domain knowledge in the
form of graphs, LLMs can achieve more accurate contextual understanding and reasoning within
educational settings, significantly improving the quality and accuracy of responses [1]. Additionally,
knowledge graphs provide detailed entity relationships and attribute information, effectively aiding
LLMs in avoiding the generation of hallucinations—content that appears plausible but is factually
2

Q: Roger has 5 tennis balls. He buys 2 more
cans oftennis balls. Each can have 3 tennis balls.
How many tennis balls does he have now?
A: Roger started with 5 balls. 2 cans of 3 tennis
ballseach is 6 tennis balls.5 +6= 11.The answer
is 11.
Q: The cafeteria had 23 apples. If they used 20
tomake lunch and bought 6 more, how many
applesdo they have?

Reward

State

IntelliChain
The optimization of the multi-agent system
Action

Prompt chain

The cafeteria had 23 apples originally. They used
20 to make lunch. So, they had 23 -20 =3. They
bought 6 more apples, so they have 3 + 6 = 9.
The answer is 9.

LLM Agent

e1

Dep(e1,e2)

e3

Aff(e2,e3)

e2

Dep(e3,e4)

Knowledge Graph

Math-KG

Concept

e4

Theorem

Search

Chain-of-Thought

The construction and integration of knowledge graphs

Figure 1: The Framework of IntelliChain.
incorrect [12]. This capability is especially important for educational applications, as it directly relates
to the reliability of learning content and the quality of education. Simultaneously, the development of
multi-agent systems based on LLMs represents a new zenith in intelligent teaching and interactive
learning within the field of educational technology. Agents within these systems leverage the
computational power and advanced language processing abilities of LLMs to facilitate efficient
communication and collaboration amongst themselves. More importantly, they can continuously
learn from interactions with learners, thereby dynamically adapting to learners’ needs and providing
personalized learning support. Furthermore, by simulating complex interactions of the real world,
multi-agent systems offer learners a more rich and immersive learning experience. The flexibility and
dynamism of these systems are unparalleled by traditional educational methods.
Integrating knowledge graphs and multi-agent systems based on LLMs, especially in supporting chainof-thought dialogues based on LLMs, not only enhances the accuracy and relevance of educational
content but also greatly increases the personalization and interactivity of educational interactions.
This transforms the educational process from a one-way transmission of knowledge into a dynamic,
bidirectional, and interactive learning experience.

3

Framework

In this study, we introduce IntelliChain, a comprehensive educational support architecture that
synergistically integrates LLMs, knowledge graphs, and a multi-agent system to facilitate an efficient
chain-of-thought dialogue mechanism, as shown in Figure 1. Specifically, IntelliChain is built upon
modular principles with a focus on optimizing the collaborative efficiency of intelligent agents in
three main areas: the strategy design of chain-of-thought dialogue, the construction and integration
of knowledge graphs, and the optimization of the multi-agent system. This framework not only aims
to enhance the accuracy and relevance of educational content but also leverages the unique strengths
of each component to support nuanced educational dialogues, thereby setting a new standard for
interactive learning environments.
Within the IntelliChain framework, an innovative dialogue strategy is articulated, leveraging a sophisticated chain-of-thought approach to enhance the pedagogical efficacy of educational dialogues. This
methodology is underpinned by an integration of advanced pedagogical principles, encompassing
strategies such as guided questioning, sequential analytical reasoning, iterative feedback mechanisms,
and the facilitation of exploratory inquiry. The design premise of IntelliChain advocates for a structured dialogue progression, where learners are methodically navigated through complex cognitive
tasks, thereby augmenting their analytical acumen and fostering critical thinking capacities. The
framework introduces a novel role-based interaction schema, wherein agents designated as "instructors" and "learners" partake in a reciprocal exchange of investigative queries and insights. This
3

- Initiate exploration with guided questioning about the
total of 35 heads, what it implies about the number of
animals.
- Establish mathematical equations for heads (H = 35))
and legs (2C + 4R = 94).
- Emphasize step-by-step reasoning to form two
equations based on the given information, focusing on
understanding how each piece of information contributes
to the overall picture rather than rushing to an answer.

- Clearly present the problem, leading students to set up
equations based on the given information.
- Highlight the importance of representing the number of
chickens and rabbits with variables, resulting in two
equations: for heads (C + R = 35)) and for legs (2C + 4R
= 94).
- Discuss methods for solving these equations,
demonstrating the elimination process, and encouraging
critical thinking to independently reach conclusions.

- Clarify the problem, encouraging students to reflect on
what the counts of heads and legs imply about the
animals' distribution.
- Guide students to mathematically represent the
problem, leading to formulating two equations: for heads
(c + r = 35) and for legs (2c + 4r = 94).
- Introduce solving a system of equations, guiding
towards the elimination method, verifying strategies
through calculation steps, and reflecting on the process
and its value for solving other problems.

Without Agent

With Agent but Without
Knowledge Graph
Integration

With Agent and
Knowledge Graph
Integration

Figure 2: Differential Teaching Outcomes Using the IntelliChain Framework Across Three System
Configurations.
orchestrated educational dialogue not only promotes active learner engagement through sustained
cognitive involvement but also ensures pedagogical alignment via continuous feedback loops.
The construction and integration of the knowledge graph represent a cornerstone in facilitating
enriched educational dialogues, specifically tailored to the domain of mathematics education. This
process is undergirded by a meticulous amalgamation of domain expertise and high-caliber educational resources, culminating in the development of a knowledge graph that meticulously catalogues
key mathematical concepts, principles, and illustrative examples. The resultant knowledge base
serves as a robust and comprehensive repository, furnishing LLMs with precise and extensive domainspecific information. To achieve an efficacious integration of the knowledge graph with LLMs,
this study introduces an advanced querying mechanism designed to harness the knowledge graph’s
potential fully. Prior to each dialogue iteration, the system autonomously conducts a query within
the knowledge graph based on the specific knowledge points implicated in the dialogue content.
This procedure extracts pertinent information to serve as prompts for dialogue generation, thereby
ensuring the educational content’s relevance and accuracy.
The optimization of the multi-agent system represents a strategic deployment of intelligent agents,
precisely tailored to the specific demands of educational tasks. This strategy is designed to fully
leverage the unique expertise of each agent, thereby enhancing the quality of instructional content
and the efficiency of the learning process. At the heart of system optimization lies the adoption
of advanced reinforcement learning algorithms, establishing a learning and adaptation mechanism.
This mechanism enables intelligent agents to iteratively adjust their behaviors and strategies based
on feedback received from interactions with learners. This adaptive process allows the system to
self-modulate based on the correlation between the agents’ actions and learners’ responses, ensuring
that educational interventions are optimally aligned with the learners’ evolving needs and preferences.

4

Results

In the present study, the IntelliChain framework was utilized to examine the differential outputs
of teacher agents employing the Socratic method in solving the classical chicken-rabbit problem
under three distinct system configurations: without agents, with agents but without knowledge
graph integration, and with agents integrated with a knowledge graph, as shown in Figure 2. This
comparative analysis aimed to elucidate the impact of knowledge graph integration and multi-agent
system optimization on the quality of pedagogical dialogue and teaching efficacy.
Without Agent Configuration: In the absence of agent intervention, the teaching dialogue primarily
relied on open-ended questioning and step-by-step reasoning to stimulate learner exploration. While
this approach facilitated learner engagement, it lacked the specificity and efficiency that could
be achieved through the utilization of specific algorithms or educational resources, rendering the
teaching process somewhat generic and less targeted. With Agents but Without Knowledge Graph:
The configuration of employing teaching agents without knowledge graph integration showed a
marked improvement in teaching dialogue by adhering to the Socratic method, characterized by
structured problem presentation and algebraic problem-solving guidance. Despite the potential of
4

agents in enhancing the learning process, the absence of knowledge graph support limited the depth
and breadth of instructional content, underutilizing the potential benefits of agent involvement in
teaching. With Agents Integrated with Knowledge Graph: The integration of teaching agents with a
knowledge graph significantly enhanced the quality of teaching dialogue. This configuration not only
enabled agents to guide the problem-solving process through algebraic methods effectively but also
deepened the discussion on problem context and related concepts utilizing the rich information from
the knowledge graph. Such an integrated approach not only deepened learners’ understanding of the
problem but also promoted personalized learning and active learner participation by dynamically
adjusting teaching strategies and methods.

5

Discussion

The IntelliChain framework constitutes a pivotal technological advancement in the realm of educational technology, particularly in augmenting Socratic method through the integration of chain-ofthought dialogues, knowledge graphs, and an optimized multi-agent system. This comprehensive
strategy not only facilitates a deeper and structured inquiry, akin to the Socratic method, but also
pioneers a personalized educational pathway via adaptive learning strategies. Despite the framework’s
promising capabilities, challenges such as its applicability across diverse learning scenarios and
the imperative for maintaining up-to-date, unbiased knowledge graphs warrant further investigation.
Future research directions might include refining the framework’s dialogue strategies to accommodate
various learning styles and broadening the scope of knowledge graphs to cover a wider spectrum of
disciplines. Additionally, the potential integration of emergent technologies presents an exciting frontier for creating more immersive and interactive learning environments, underscoring IntelliChain’s
transformative potential in educational methodologies.

6

Conclusion

This study introduced the IntelliChain framework, an innovative approach that enhances educational
dialogues through the integration of LLMs, knowledge graphs, and a multi-agent system, optimized
for the Socratic method. It demonstrated the framework’s capability to improve the precision and
relevance of educational content while facilitating personalized learning experiences. Comparative
analysis across different configurations underscored the significance of knowledge graph integration
and multi-agent system optimization in augmenting teaching efficacy. Despite promising outcomes,
challenges such as adaptability across diverse learning scenarios and maintaining unbiased knowledge
graphs remain. Future efforts will focus on refining dialogue strategies and exploring emerging
technologies to further enhance the learning environment. IntelliChain represents a significant
stride towards advancing AI-driven personalized education, promising to elevate the quality and
effectiveness of teaching and learning methodologies.

References
[1] W. Gan, Z. Qi, J. Wu, and J. C.-W. Lin, “Large language models in education: Vision and
opportunities,” in 2023 IEEE international conference on big data (BigData). IEEE, 2023, pp.
4776–4785.
[2] S. Wang, T. Xu, H. Li, C. Zhang, J. Liang, J. Tang, P. S. Yu, and Q. Wen, “Large language
models for education: A survey and outlook,” arXiv preprint arXiv:2403.18105, 2024.
[3] J. Kaddour, J. Harris, M. Mozes, H. Bradley, R. Raileanu, and R. McHardy, “Challenges and
applications of large language models,” arXiv preprint arXiv:2307.10169, 2023.
[4] H. Chae, Y. Song, K. Ong, T. Kwon, M. Kim, Y. Yu, D. Lee, D. Kang, and J. Yeo, “Dialogue
chain-of-thought distillation for commonsense-aware conversational agents,” in Proceedings of
the 2023 Conference on Empirical Methods in Natural Language Processing, H. Bouamor,
J. Pino, and K. Bali, Eds. Singapore: Association for Computational Linguistics, Dec. 2023,
pp. 5606–5632. [Online]. Available: https://aclanthology.org/2023.emnlp-main.342/
[5] J. Bai, S. Bai, Y. Chu, Z. Cui, K. Dang, X. Deng, Y. Fan, W. Ge, Y. Han, F. Huang et al., “Qwen
technical report,” arXiv preprint arXiv:2309.16609, 2023.
5

[6] T. Bui, O. Tran, P. Nguyen, B. Ho, L. Nguyen, T. Bui, and T. Quan, “Cross-data knowledge
graph construction for llm-enabled educational question-answering system: A case study at
hcmut,” in Proceedings of the 1st ACM Workshop on AI-Powered Q&A Systems for Multimedia,
ser. AIQAM ’24. New York, NY, USA: Association for Computing Machinery, 2024, p.
36–43. [Online]. Available: https://doi.org/10.1145/3643479.3662055
[7] Z. Bahroun, C. Anane, V. Ahmed, and A. Zacca, “Transforming education: A comprehensive
review of generative artificial intelligence in educational settings through bibliometric and
content analysis,” Sustainability, vol. 15, no. 17, p. 12983, 2023.
[8] J. Yao, W. Xu, J. Lian, X. Wang, X. Yi, and X. Xie, “Knowledge plugins: Enhancing large
language models for domain-specific recommendations,” arXiv preprint arXiv:2311.10779,
2023.
[9] H. Wang, R. Wang, F. Mi, Y. Deng, Z. Wang, B. Liang, R. Xu, and K.-F. Wong, “Cue-cot:
Chain-of-thought prompting for responding to in-depth dialogue questions with llms,” arXiv
preprint arXiv:2305.11792, 2023.
[10] Z. Yin, Q. Sun, C. Chang, Q. Guo, J. Dai, X. Huang, and X. Qiu, “Exchange-of-thought:
Enhancing large language model capabilities through cross-model communication,” arXiv
preprint arXiv:2312.01823, 2023.
[11] Y. Liu, A. Singh, C. D. Freeman, J. D. Co-Reyes, and P. J. Liu, “Improving large language
model fine-tuning for solving math problems,” arXiv preprint arXiv:2310.10047, 2023.
[12] G. Agrawal, T. Kumarage, Z. Alghamdi, and H. Liu, “Can knowledge graphs reduce hallucinations in llms?: A survey,” arXiv preprint arXiv:2311.07914, 2023.

6
