# user-intent-slreview

> 来源：`user-intent-slreview.pdf`（AutoOffice to-markdown）

arXiv:2308.08496v1 [cs.IR] 5 Aug 2023

Understanding User Intent Modeling for
Conversational Recommender Systems: A
Systematic Literature Review
Siamak Farshidi1*, Kiyan Rezaee2† , Sara Mazaheri2† , Amir Hossein
Rahimi2† , Ali Dadashzadeh2 , Morteza Ziabakhsh2 , Sadegh Eskandari2*†

and Slinger Jansen1,3*
1* Department of Information and Computer Science, Utrecht University,

Utrecht, The Netherlands.

2 Department of Computer Science, University of Guilan, Rasht,Iran.
3 Lappeenranta University of Technology,Lappeenranta, Finland.

*Corresponding author(s). E-mail(s): s.farshidi@uu.nl;
eskandari@guilan.ac.ir; slinger.jansen@uu.nl;
† These authors contributed equally to this work.

Abstract
Context: User intent modeling is a crucial process in Natural
Language Processing that aims to identify the underlying purpose behind a user’s request, enabling personalized responses. With
a vast array of approaches introduced in the literature (over
13,000 papers in the last decade), understanding the related concepts and commonly used models in AI-based systems is essential.
Method: We conducted a systematic literature review to gather
data on models typically employed in designing conversational recommender systems. From the collected data, we developed a decision model to assist researchers in selecting the most suitable models for their systems. Additionally, we performed two case studies to evaluate the effectiveness of our proposed decision model.
Results: Our study analyzed 59 distinct models and identified 74 commonly used features. We provided insights into potential model combinations, trends in model selection, quality concerns, evaluation measures,
and frequently used datasets for training and evaluating these models.

1

2

Understanding User Intent Modeling for CRS: An SLR
Contribution: Our study contributes practical insights and a
comprehensive understanding of user intent modeling, empowering the development of more effective and personalized conversational recommender systems. With the Conversational Recommender System, researchers can perform a more systematic
and efficient assessment of fitting intent modeling frameworks.
Keywords: user intent modeling, user behavior, query intent, conversational
recommender systems, personalized recommendation, machine learning models

1 Introduction
User intent modeling is a fundamental process in Natural Language Processing (NLP) that aims to discern the underlying purpose or objective of a
user’s request [1]. By leveraging machine learning algorithms to analyze various aspects of user input, such as words, phrases, and context, user intent
modeling enables accurate identification of desired outcomes in conversational
recommender systems [2]. Consequently, this approach leads to the delivery of
personalized and precise responses [3].
Understanding and predicting user goals and motivations through user
intent modeling play a vital role in optimizing search engines and recommender
systems [4]. Aligning the user experience and search results with users’ preferences and needs allows designers and developers to enhance user satisfaction
and engagement [5]. This personalized approach results in providing relevant
and tailored results [6, 7]. For example, ChatGPT is a state-of-the-art generative language model that has garnered substantial interest for its potential
applications in search engines and recommender systems [8]. It can comprehend
user intentions and engage in meaningful interactions with them.
User intent modeling finds diverse practical applications in several domains,
from e-commerce and healthcare to education, social media, and virtual
assistants. In e-commerce, it plays a pivotal role in delivering personalized
product recommendations, thereby enhancing the overall shopping experience
for users [9–11]. Moreover, user intent modeling contributes to the detection
of fake product reviews, which is a critical issue in e-commerce platforms [12].
By identifying and filtering out fraudulent reviews, it helps build trust among
customers and ensures more reliable product evaluations, ultimately benefiting both consumers and businesses. The healthcare domain benefits from
user intent modeling by utilizing it to provide personalized health recommendations and interventions based on individual patients’ health goals and
motivations [13, 14].
Similarly, in education, user intent modeling supports personalized learning
experiences tailored to the specific goals and preferences of students [15, 16].
In the realm of social media, it enables a comprehensive understanding of

Understanding User Intent Modeling for CRS: An SLR

3

user interests, preferences, and behaviors, which, in turn, drives the delivery
of personalized content and advertising [17, 18].
User intent modeling proves to be a valuable asset for virtual assistants
as it assists them in comprehending user queries and providing relevant and
personalized responses [19, 20]. Moreover, its application extends to advertising
targeting and personalization across various domains, benefiting businesses
and users alike [21–23].
User intent modeling finds utility in other contexts, such as chatbots, where
it enhances the user experience by providing more human-like interactions [24].
Recommender systems rely on user intent modeling to make more accurate
and personalized suggestions [25]. In software applications, it contributes to
a better understanding of user behavior and improving user interfaces [26].
Additionally, user intent modeling significantly optimizes web services and
enhances user interactions [27].
The field of user intent modeling encompasses various machine learning
models, including Support Vector Machines (SVM) [28, 29], Latent Dirichlet
Allocation (LDA) [30, 31], Naive Bayes [32, 33], and deep learning models
like Bidirectional Encoder Representations from Transformers (BERT) [34],
Word2vec [35, 36], and Multilayer Perceptron (MLP) [37, 38]. A thorough
examination of these models and their characteristics provides a comprehensive
understanding of their advantages and limitations, offering valuable insights
for future research and development.
The process of selecting the most suitable machine learning model for user
intent modeling in recommender systems can be challenging due to the wide
array of models and approaches available [4, 39]. The lack of a clear classification scheme further complicates the model selection process [40]. Researchers
and developers often struggle to navigate the multitude of available models,
leading to uncertainty and a lack of confidence in selecting the optimal model
for their specific requirements [41, 42]. Overcoming these challenges is crucial
for developing effective solutions in user intent modeling and recommendation
tasks, underscoring the need for continued research to enhance model selection
and development processes.
While user intent modeling and its application in conversational recommender systems have gained significant attention, existing research in this field
is often scattered across diverse sources, hindering comprehensive understanding. Moreover, the multitude of machine learning models, concepts, datasets,
and evaluation measures utilized in this research can be overwhelming. To
address these issues, we conducted a systematic literature review following
the guidelines of Kitchenham [43], Xiao [44], and Okoli [45] to consolidate
and analyze the information, providing a more comprehensive understanding
of the field. Additionally, we developed a decision model based on the data
collected from the literature review, serving as a valuable tool for selecting
intent modeling approaches. To evaluate the effectiveness of the decision model,
we conducted two academic case studies following the guidelines outlined by
Yin [46].

4

Understanding User Intent Modeling for CRS: An SLR

This study presents a Systematic Literature Review (SLR) on user intent
modeling within conversational recommender systems. Additionally, it proposes a decision model based on the collected data to guide research modelers
in making informed decisions. Section 2 defines the problem statement and
research questions and outlines the research methods employed, including
systematic literature study and case study research. Section 3 outlines the
methodology used in the SLR, covering the review protocol, paper collection
procedures, inclusion/exclusion criteria, quality assessment techniques, data
extraction methods, synthesis processes, and systematic search approach. In
Section 4, the findings and analysis of the SLR are presented, exploring various aspects of user intent modeling, such as models and their characteristics,
feature engineering techniques, model combinations, emerging trends, quality
evaluation measures, and available datasets. Section 5 focuses on the practical
utilization of the collected data, addressing project-specific concerns through
the introduced decision model. This meta-model serves as a framework for
effective decision-making, particularly in model selection. Section 6 includes
insightful academic case studies that provide practical insights and validate
the conducted research to enrich the evaluation of findings. Section 7 critically
examines the outcomes of the SLR, discussing lessons learned, implications of
the findings, and addressing potential threats to the study’s validity. Section 8
situates our study and the decision model within the broader landscape of
related research studies, establishing their unique contributions and relevance.
Finally, in Section 9, the paper summarizes the study’s contributions and highlights avenues for future research, providing a cohesive closure to the research
on user intent modeling in conversational recommender systems.

2 Research Approach
This study adopted a systematic research approach, combining SLR and Case
Study Research to investigate user intent modeling approaches. The SLR
enabled us to gather and analyze relevant information from existing literature,
while the case studies allowed us to assess the practical applicability of our
findings.

2.1 Problem Statement
Developing effective search engines and recommendation systems relies on
accurately identifying and understanding user intent [47, 48]. However, user
intent modeling lacks consensus and comprehensive analysis of optimal
approaches [40]. This scattered knowledge makes it challenging for researchers
to choose suitable models for specific scenarios [49]. Additionally, combining
models to enhance conversational recommender systems’ accuracy presents
a formidable challenge [50]. Understanding prevailing trends, emerging patterns, and appropriate evaluation measures for intent modeling approaches
further complicate the development of effective systems [51–54]. Furthermore,

Understanding User Intent Modeling for CRS: An SLR

5

selecting representative datasets for training and evaluation is not straightforward [55]. Consequently, in the realm of intent modeling approaches, the
following research challenges have been identified:
Scattered knowledge: The concepts, models, and characteristics of intent
modeling approaches are dispersed across diverse academic literature [40], hindering informed decision-making for developing conversational recommender
systems. Systematically consolidating and categorizing existing approaches is
demanding. Researchers need a comprehensive landscape of intent modeling
techniques to make better choices.
Model combinations and integration: Combining and integrating models
in user intent modeling is challenging [56]. Finding effective model combinations to improve conversational recommender systems’ accuracy requires
investigating compatibility and synergy between models.
Trends and emerging patterns: Understanding prevailing trends and
emerging patterns in user intent modeling approaches is crucial. Researchers
need to analyze a large volume of research papers to identify such patterns
and tailor their efforts accordingly [51, 52].
Selecting assessment criteria: Choosing appropriate evaluation measures
and quality attributes for assessing intent modeling approaches is challenging.
Researchers must identify measures tailored to each approach to evaluate their
performance accurately [53, 54].
Selecting datasets: Selecting suitable datasets for training and evaluating
intent modeling approaches is complex. Researchers must analyze and choose
representative datasets encompassing various intents and user behaviors to
develop robust intent models [57].
Decision-making process: A comprehensive decision model encompassing various intent modeling concepts and guidelines for selecting model
combinations and conducting systematic evaluations is missing from the existing literature [58, 59]. Such a model would aid researchers in navigating
the complexities of intent modeling and streamlining their decision-making
processes.

2.2 Research Questions
Based on the identified research challenges in intent modeling approaches, the
following research questions are formulated:
RQ1 : What types and categories of models have researchers commonly used
in the literature, following best practices, for developing decision-making in
conversational recommender systems?
RQ2 : What are the essential features that models in the context of conversational recommender systems must possess to address the requirements of
researchers effectively?
RQ3 : Are there any discernible trends in using models to develop conversational recommender systems?
RQ4 : What evaluation measures and quality attributes are most suitable for
accurately assessing the performance of user intent modeling approaches?

6

Understanding User Intent Modeling for CRS: An SLR

RQ5 : How can researchers identify and select representative datasets that accurately depict real-world scenarios, enabling effective training and evaluation of
intent modeling approaches?
RQ6 : How can we develop a comprehensive decision model to guide
researchers in making informed decisions while developing user intent modeling
approaches?

2.3 Research Methods
We utilized a mixed research method [60, 61] to tackle the research questions,
combining SLR and Case Study Research. The SLR allowed us to gain a comprehensive understanding of user intent modeling approaches, and the case
studies assessed the practical applicability of the proposed decision model in
real-world scenarios.
The SLR followed guidelines by Kitchenham [43], Xiao [44], and Okoli [45]
to identify models, their definitions, model combinations, supported features,
potential evaluation measures, and relevant concepts from existing literature.
Based on the SLR findings, we developed a decision model, drawing from our
previous studies on multi-criteria decision-making in software engineering [59].
To evaluate the practical applicability of the decision model, we conducted
two case studies, following the guidelines of Yin [62]. These case studies
assessed if the proposed decision model effectively assisted research modelers
in selecting models for their projects.
We addressed the research questions by employing this mixed research
method, including SLR and case studies, contributing meaningful insights and
practical solutions to advance intent modeling and improve conversational
recommender systems.

3 Systematic Literature Review Methodology
In this study, we followed the procedures and guidelines outlined by Kitchenham [43], Xiao [44], and Okoli [45] to address the research question highlighted
in Section 2.2. Accordingly, we adopted the following review protocol (see
Figure 1) to systematically collect and extract data from relevant studies. The
following steps were taken to conduct the SLR:
(1) Problem formulation: In this research phase, we followed the prescribed
procedures and guidelines of Xiao [44] to define the problem statement and
research questions. By identifying the research methods, including using an
SLR, we ensured that our study addressed a subset of research questions suitable for an SLR. This systematic approach allowed us to conduct a rigorous
investigation.
(2) Initial hypotheses: During the initial stage, we considered a set of keywords to search for primary studies that could address our research questions.
These keywords formed the basis for identifying potential seed papers, which
served as the starting point for our literature review. This method enabled us
to explore relevant publications systematically.

process

process

synthesizing

Knowledge
base

Pool of
publications

Understanding User Intent Modeling for CRS: An SLR

7

Problem formulation

Initial hypotheses

Iinitial data
collection

Query string
definition

Digital library
exploration

Relevancy
evaluation

Defining problem
statement

Querying
digital
libraries

Extacting primary
studies information

Building a dataset of
relevant studies

Selecting digital
libraries

Extacting publication
information

Indicating relevancies

Extracting frequent
terms (NLP tools)

Quering DL by the
search term

Indicating relevancies

Formulating research
questions

Selecting
primary
studies

Selecting research
methods
1

Identifying
keywords
Finding venue
qualities

2

Pool of
publications

Building a search
term

3

4

Publication pruning
process

Quality assessment
process

Data extraction and
synthesizing

Indicating the inclusion
criteria

Indicating the quality
assessment criteria

Quantitative synthesis

Indicating the exclusion
criteria

Skimming and screening
of the pruned publications

applying inclusion/exlusion
criteria

Judging publications
qualities

6

Snowballing process

Looking at the references
of publications

Qualitative synthesis

7

8

9

Structured synthesis
Narrative synthesis
10

Finding venue
qualities

Extracting identified
publications
5

Knowledge
base

Selecting potential
publications

11

12

Fig. 1 illustrates the review protocol employed in this study, following the prescribed
procedures and guidelines outlined by Kitchenham [43], Xiao [44], and Okoli [45]. The review
protocol consists of 12 elements systematically executed to collect and extract data from
relevant studies. These steps ensure a rigorous investigation and adherence to scientific
standards in the research process.

(3) Initial data collection: We manually collected a comprehensive set of
characteristics for primary studies, including source, URL, title, keywords,
abstract, venue, venue quality, type of publication, number of citations,
publication year, relevancy level. This meticulous process ensured that our
review focused on essential information and facilitated the establishment of
inclusion/exclusion criteria.
(4) Query string definition: By analyzing primary studies’ keywords,
abstracts, and titles, we constructed a search query based on frequent terms
found in highly relevant and high-quality papers. This approach helped refine
our search and ensure the inclusion of relevant publications.
(5) Digital library exploration: We thoroughly explored digital libraries
such as ACM, ScienceDirect, and Elsevier, using the generated search query
to query these databases. This systematic exploration of reputable sources
ensured the comprehensive coverage of relevant publications.
(6) Relevancy Evaluation: We assessed the characteristics of the resulting
publications and added them to our collection while estimating their relevancy
based on their alignment with our research questions and challenges. This
evaluation process ensured the inclusion of highly relevant publications in our
review.
(7) The pool of publications: The collected papers and their associated
characteristics formed the pool of publications that served as the foundation
for our subsequent review. This pool was continuously expanded during the
snowballing process, ensuring a comprehensive examination of the literature.
(8) Publication pruning process: We rigorously applied inclusion/exclusion criteria to evaluate the pool of publications, eliminating irrelevant material

8

Understanding User Intent Modeling for CRS: An SLR

and refining the selection to include the most relevant and high-quality studies.
This process enhanced the quality and focus of our review.
(9) Quality assessment process: We assessed the quality of the remaining
publications based on established criteria, including the clarity of research
questions and findings. This evaluation ensured that only high-quality studies
were included in our review, enhancing the reliability of our findings.
(10) Data extraction and synthesizing: Through systematic data extraction, we obtained relevant information from the selected publications, synthesizing the findings to identify key insights. This rigorous process facilitated the
identification and summarization of critical information.
(11) Knowledge base: The final set of selected highly relevant and highquality publications, along with their characteristics, formed a comprehensive
knowledge base. Additionally, the extracted data provided a mapping that
connected specific findings to their respective sources. This knowledge base
is a valuable resource for future research, offering a consolidated summary of
essential findings and enabling further analysis.
(12) Snowballing process: By reviewing the references of selected publications, we identified additional relevant papers that may have been initially
overlooked. This snowballing process ensured our review’s comprehensiveness
and enriched our findings.
By meticulously following this systematic review protocol, we adhered to
rigorous and scientific standards in collecting and analyzing the relevant literature on user intent modeling approaches. This approach ensured the validity
and reliability of our study, allowing us to address the research questions
identified in our study effectively.

3.1 Review protocol
This section explains how we followed the review protocol presented in Figure 1
to conduct our SLR.

3.1.1 Paper collection
During the automatic search phase of our systematic literature review, we
implemented a robust search strategy to retrieve pertinent and high-quality
publications from scientific search engines. To formulate our search query,
we extracted keywords from an initial set of publications obtained through
the manual search process. These keywords were identified based on the frequent terms used by researchers in highly relevant and high-quality papers.
We further refined the keyword selection using a topic modeling tool, Sketch
Engine [63], which helped identify additional relevant terms. In total, we identified 314 highly relevant and high-quality publications during the initial part
of this phase of the SLR.
The search query was carefully constructed to target publications that
specifically addressed user intent modeling in the context of search engines
and recommender systems. It aimed to cover various topics such as intent

Understanding User Intent Modeling for CRS: An SLR

9

detection, intent prediction, interactive intent modeling, conversational search,
intent classification, and user behavior modeling. The query was formulated
using logical operators ”AND” and ”OR” to combine the selected keywords.
The search query in this SLR is as follows.
(”user intent” OR ”user intent modeling” OR ”topic model” OR ”user intent
detection” OR ”user intent prediction” OR ”interactive intent modeling” OR
”conversational search” OR ”intent classification” OR ”intent mining” OR ”conversational recommender system” OR ”user response prediction” OR ”user behavior
modeling” OR ”interactive user intent” OR ”intent detection” OR ”concept discovery”) AND (”search engine” OR ”recommender system”)

The search query was employed during the automatic search phase, and
the resulting publications (a total of 3,828 out of 13,168 results considered in
the pool of publications) underwent a rigorous screening process based on our
predefined inclusion/exclusion criteria. This ensured that only relevant and
high-quality publications were included in our data extraction and analysis.
The effectiveness of the search query was assessed by comparing the search
results with those obtained from the manual search to ensure consistency and
comprehensiveness. The search query used in our study was derived from previous research and validated to retrieve publications relevant to user intent
modeling in search engines and recommender systems.

3.1.2 Inclusion/exclusion criteria
Inclusion/exclusion criteria are essential guidelines used to determine the relevance and eligibility of studies for inclusion in a systematic literature review or
meta-analysis. These criteria are crucial in ensuring that the selected studies
are high quality and directly address the research question under investigation. Inclusion criteria specify the characteristics or attributes a study must
possess to be considered for inclusion in the review.
We employed rigorous inclusion and exclusion criteria during this study
phase to filter out irrelevant and low-quality publications. Our criteria encompassed several factors, including the quality of the publication venue, the
publication year, the number of citations, and the relevancy of the publication to our research topic. These criteria were carefully defined and
consistently applied to ensure that only high-quality and relevant publications were included in our review. By adhering to these criteria, we evaluated
publications that provided valuable insights and contributed significantly to
our research topic. After applying our predefined inclusion/exclusion criteria,
we identified and selected 1,067 publications out of the initial pool of 3,828
publications.

3.1.3 Quality assessment
During the SLR, we comprehensively assessed the quality of the selected
publications after applying the inclusion/exclusion criteria. Several factors
were taken into consideration to evaluate the quality and suitability of the
publications for our research:

10

Understanding User Intent Modeling for CRS: An SLR

Research Method: We evaluated whether the chosen research method was
appropriate for addressing the research question. The clarity and transparency
of the research methodology were also assessed.
Research Type: We considered whether the publication presented original
research, a review article, a case study, or a meta-analysis. The relevance and
scope of the research in the field of machine learning were also taken into
account.
Data Collection Method: We evaluated the appropriateness of the data collection method in relation to the research question. The adequacy and clarity
of the reported data collection process were also assessed.
Evaluation Method: We assessed whether the chosen evaluation method was
suitable for addressing the research question. The transparency and statistical
significance of the reported results were considered.
Problem Statement: We evaluated whether the publication identified the
research problem and provided sufficient background information. The clarity
and definition of the research question were also taken into account.
Research Questions: We assessed the relevance, clarity, and definition of the
research questions in relation to the research problem.
Research Challenges: We considered whether the publication identified and
acknowledged the challenges and limitations associated with the research.
Statement of Findings: We evaluated whether the publication reported the
research results and whether the findings were relevant to the research problem
and questions.
Real-World Use Cases: We assessed whether the publication provided realworld use cases or applications for the proposed method or model.
Based on the aforementioned factors’ assessment, a team of five researchers
involved in the SLR evaluated the publications’ quality. Each researcher independently assessed the publications based on the established criteria. In cases
where there were discrepancies or differences in evaluating a publication’s quality, the researchers engaged in discussions to reach a consensus and ensure a
consistent assessment.
Through this collaborative evaluation process, a final selection of 791 publications was made from the initial pool of 1,067 publications. These selected
publications demonstrated high quality and relevance to our research question,
meeting the predefined inclusion/exclusion criteria. The consensus reached by
the research team ensured a rigorous and reliable selection of publications for
further analysis and data extraction in the SLR.

3.1.4 Data extraction and synthesizing
During the data extraction and synthesis phase of the SLR, our primary objective was to address the identified research questions and gain insights into the
foundational models commonly employed by researchers in their intent modeling approaches. We aimed to understand the features of these models, the
associated quality attributes, and the evaluation measures utilized by research

Understanding User Intent Modeling for CRS: An SLR

11

modelers to assess their approaches. Furthermore, we explored the potential combinations of models that researchers incorporated into their research
papers.
We extracted relevant data from the papers included in our review to
achieve these objectives. In our perspective, evaluation measures encompassed
a range of measurements and key performance indicators (KPIs) used to
evaluate the performance of the models. Quality attributes represent the characteristics of models that are not easily quantifiable and are typically assigned
values using Likert scales or similar approaches. For example, authors may
assess the performance of a model as high or low compared to other models. On the other hand, features encompassed any characteristics of models
that authors highlighted to demonstrate specific functionalities. These features
played a role in the selection of models by research modelers. Examples of
features include ranking and prediction capabilities.
In this context, ”models” refer to mathematical, algorithmic models or
processes that can be applied in various domains. For instance, Support Vector
Machines (SVM) [28, 29] and Bayesian Personalized Ranking (BPR) [64, 65]
are examples of models commonly utilized in intent modeling.
By extracting and analyzing this data, we aimed to comprehensively understand the existing literature, including popular open-access datasets used for
training and evaluating the models. This knowledge empowered us to contribute insights and recommendations to the academic community, supporting
them in selecting appropriate models and approaches for their intent modeling
research endeavors.

3.2 Search process
In this study, we followed the review protocol presented in this section (see
Figure 1) to gather relevant studies. The search process involved an automated
search phase, which utilized renowned digital libraries such as ACM DL, IEEE
Xplore, ScienceDirect, and Springer. However, Google Scholar was excluded
from the automated search due to its tendency to generate numerous irrelevant
studies. Furthermore, Google Scholar significantly overlaps the other digital
libraries considered in this SLR. Table 1 provides a comprehensive overview
of the sequential phases of the search process, outlining the number of studies
encompassed within each stage.
Table 1 provides insights into the search process conducted in four phases:
Phase 1, Phase 2, Phase 3, and Phase 4.
Phase 1 (Pool of Publications): We initially performed a manual search,
resulting in 314 relevant publications from Google Scholar. Additionally, automated searches from ACM DL, IEEE Xplore, ScienceDirect, and Springer
contributed to the pool of publications with 586, 82, 921, and 1896 relevant
papers, respectively.
Phase 2 (Publication pruning process): In this phase, the inclusion/exclusion criteria were applied to the collected publications, ensuring the selection

12

Understanding User Intent Modeling for CRS: An SLR

Table 1 presents an overview of the systematic search process employed to identify
relevant publications on user intent modeling. The search process involved both
manual and automatic searches, incorporating specific inclusion/exclusion criteria
to ensure the retrieval of high-quality results. The search query used in the
automatic search was carefully designed to retrieve relevant publications from
scientific search engines, while the manual search involved screening articles from
selected venues. The final set of articles obtained from both searches was then
subjected to comprehensive analysis and synthesis to provide valuable insights into
the current state of research on user intent modeling.
Google Scholar
ACM DL
IEEE Xplore
ScienceDirect
Springer
Snowballing

#hits
3,940
2,152
89
1,528
5,459
N/A
13,168

Phase 1
314
586
82
921
1,896
29
3,828

Phase 2
96
311
9
246
379
26
1,067

Phase 3
96
311
9
246
379
26
1,067

Phase 4
68
243
7
190
263
20
791

of high-quality and relevant studies. The numbers were reduced to 96 in ACM
DL, 9 in IEEE Xplore, 246 in ScienceDirect, and 379 in Springer.
Phase 3 (Quality assessment process): Quality assessment was conducted
for the publications based on several criteria, resulting in a final selection of
1067 studies from all sources.
Phase 4 (Data extraction and synthesizing + Snowballing process):
During this phase, data extraction and synthesis were performed to gain
insights into foundational intent modeling models, quality attributes, evaluation measures, and potential combinations of models used by researchers.
Additionally, snowballing, involving reviewing references of selected publications, led to an additional 20 relevant papers. By carefully applying the
review protocol and snowballing, we retrieved 791 high-quality studies for our
comprehensive analysis and synthesis in this systematic literature review.

4 Findings and Analysis
In this section, we present the SLR results and provide an overview of the
collected data, which were analyzed to address the research questions identified
in our study.

4.1 Models
The SLR conducted in our study has revealed a diverse array of models employed in user intent modeling. These models encompass a range of
approaches, each characterized by unique characteristics and methodologies.
For a comprehensive understanding of these models, including their definitions
and descriptions, please refer to the appendix (Appendix A).
We have examined their underlying principles and methodologies to categorize these models effectively. The appendix (Appendix B) provides detailed
definitions and explanations of the identified categories, offering comprehensive
insights into each category and its specific characteristics.

Understanding User Intent Modeling for CRS: An SLR

13

Among the identified categories, prominent ones include Classification [13,
66] and Clustering [67, 68] models, Convolutional Neural Network (CNN)[10,
13], Deep Belief Networks (DBN)[29, 69], and Graph Neural Networks
(GNN) [70, 71], among others. These categories encompass a broad range of
modeling techniques applied in user intent modeling research. However, it is
important to note that these categories represent only a subset of the diverse
range of models identified in our SLR.

Supervised Learning
Unsupervised Learning
Collaborative Filtering
Statistical Method
Classification
Probabilistic
Regression
Recurrent Neural Networks
Deep Belief Networks
Clustering
Optimization

x x x

x x x
x x x
x x x
x x

Vector Space Model
Graph Neural Networks
Self-Supervised Learning Model
Measurement model
Semi-Supervised Learning
Convolutional Neural Network
Reinforcement Learning
6 5 4

x
x x
x

x x

x

x x
x x

x

RankNet

PCA (Principal Component Analysis)

MLE (Maximum Likelihood Estimation)

RGM (Random Group Model)

HMM (Hidden Markov Model)

PageRank

CTR (Collaborative Topic Regression)

SGD (Stochastic Gradient Descent)

MLP (Multi-Layer Perceptron)

DNN (Deep Neural Network)

BM25 (Best Match 25)

Singular Value Decomposition (SVD)

KL (Kullback–Leibler Divergence)

LSA (Latent Semantic Analysis)

Rocchio

DeepCoNN (Deep Cooperative Neural Networks)

NCF (Neural Collaborative Filtering)

Cosine similarity

Self-attention

SDAE (Stacked Denoising Autoencoder)

LSI (Latent Semantic Indexing)

CDL (Collaborative Deep Learning)

SVD++ (Singular Value Decomposition Plus Plus)

BiLSTM (Bidirectional Long Short-Term Memory)

BPR (Bayesian Personalized Ranking)

PMI (Pointwise Mutual Information)

Gibbs sampling

SVM (Support Vector Machines)

Skip-gram

Word2vec

k-means (k-means clustering)

EM (Expectation-Maximization)

BERT (Bidirectional Encoder Representations from Transformers)

LR (Logistic Regression)

Markov Chain

CRF (Conditional Random Fields)

MF (Matrix factorization)

CF (Collaborative Filtering)

Random Forest

ALS (Alternating Least Squares)

RBM (Restricted Boltzmann Machines)

SVR (Support Vector Regression)

NER (Named Entity Recognition)

GBDT (Gradient Boosting Decision Trees)

x x x

RW (Random Walk)

LambdaMART

FM (Factorization Machine)

NMF (Non-negative Matrix Factorization)

KNN (K-Nearest Neighbors Algorithm)

x x
x x
x x

PMF (Probabilistic Matrix Factorization)

Naive Bayes

PLSA (Probabilistic Latent Semantic Analysis)

LSTM (Long Short-Term Memory)

LDA (Latent Dirichlet allocation)

VSM (Vector Space Model)

15
15
x 15
x x
x x
x
x x
x
x
x
x
13
x x
x x
x x
x
x
x
x
13
x
x x
x x
x x x
x
x
10
x
x
x x x
x
x
10
x
x
x x
x x
9
x
x
x x
x
x x
x
8
x
x
x
x
6
x
x
x
x
4
x
x
x
3
x
x
2
x x
2
x
x
2
x
x
2
x
1
x
1
3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 1 1 1 1 1 1 1 1 1 1 1 1 1 1
x

x

TF-IDF (Term Frequency-Inverse Document Frequency)

MMR (Maximal Marginal Relevance)

GRU (Gated Recurrent Units)

GRU4Rec (Gated Recurrent Unit for Recommender Systems)

Table 2 shows the mapping of 59 models to their respective categories in user intent
modeling. The table showcases the models that appear in at least six publications.
However, for access to the complete list of models, please refer to the supplementary
materials available on Mendeley Data [72].

x x
x x x

x

x x

x

x x
x x
x

x

x

x

x

x

x

Table 2 presents an overview of the 59 most frequently mentioned models in the SLR on user intent modeling. The table showcases the models
appearing in at least six publications (columns) and their corresponding 18
categories (rows). Each model in user intent modeling can often be categorized
into multiple categories, highlighting their versatility and diverse functionalities. For example, GRU4Rec, a widely recognized model in the field (cited
in 10 publications included in our review), exhibits characteristics that align
with various categories. GRU4Rec falls under Supervised Learning, as it uses
labeled examples during training to predict user intent. Additionally, it incorporates Collaborative Filtering techniques by analyzing user behavior and
preferences to generate personalized recommendations, associating it with the
Collaborative Filtering category [73]. Moreover, GRU4Rec can be classified as
a Classification model as it categorizes input data into specific classes or categories to predict user intent [74]. It also demonstrates traits of Regression
models by estimating and predicting user preferences or ratings based on the
available data. Considering its reliance on recurrent connections, GRU4Rec can
be associated with the Recurrent Neural Networks (RNN) category, enabling

14

Understanding User Intent Modeling for CRS: An SLR

it to process sequential data and capture temporal dependencies [75]. Lastly,
GRU4Rec’s ability to cluster similar users or items based on their behavior
and preferences places it within the Clustering category. This clustering capability provides valuable insights and recommendations to users based on their
respective clusters.

4.2 Features
Our study conducted a comprehensive investigation of the features supported
by models in user intent modeling, emphasizing their significance in the field.
We identified a total of 74 distinct features that were consistently mentioned
in at least six publications1 , highlighting their relevance and impact in intent
modeling research. For a comprehensive understanding of these features, please
consult Appendix C, where detailed definitions and explanations are provided.
To effectively organize and comprehend these features, we categorized them
into 20 categories based on their context, domain, and applications. Machine
learning models possess the versatility to support a wide range of features, each
tailored to specific use cases and applications. Some common features include
historical data [76–78], enabling models to learn from past experiences and predict future outcomes. Algorithm-agnostic models [79–81] provide the flexibility
to select the most suitable algorithm for a particular task. Model-based [82–
84] features leverage statistical methods [85, 86] and semantic analysis [87, 88]
to offer predictions based on specific models.
Table 3 illustrates the mapping of features to models in user intent modeling, highlighting the frequency of explicit mentions in relevant publications.
Each cell represents the number of publications that specifically refer to the
corresponding feature in relation to the associated models. Authors of these
papers have emphasized their feature requirements as a pivotal factor in selecting particular models. The color-coded cells indicate the range of publication
counts, ranging from low to high, reflecting the level of support for each feature by the models. It is noteworthy that gray cells indicate the absence of
evidence supporting the feature’s compatibility with a specific model, based
on the comprehensive review of 791 papers conducted in this study. For example, among the analyzed publications, we identified 29 instances where LDA
(Latent Dirichlet Allocation) was mentioned as being applicable in patternbased approaches within the context of rule-based methods [89, 90]. This
implies that researchers and authors found LDA to be relevant and applicable in scenarios where patterns are analyzed, and rules are used to extract
meaningful information or make decisions.
This mapping process involves determining which models are most suitable
for addressing specific features in a given problem. It necessitates a comprehensive analysis of the problem’s characteristics and an understanding of the
capabilities, strengths, and weaknesses of the available models. For instance,
1
For access to the complete list of features, please refer to the supplementary materials available
on Mendeley Data [72].

Understanding User Intent Modeling for CRS: An SLR

15

Recommendation
Techniques

Feature Analysis
and Selection
Data
Preprocessing and
Model
Optimization
Learning Methods

Image Processing

Model Training

Clustering
Techniques
System Design

Analysis
Techniques

Feedback And
Relevance

Flexible Data
Processing

GBDT

NCF

CDL

GRU4Rec

LambdaMART

MMR

MLE

RW

DeepCoNN

PageRank

NER

Self-attention

SVR

SDAE

RBM

ALS

Random Forest

PCA

RankNet

Cosine similarity

RGM

Rocchio

Popularity

FM

Gibbs sampling

GRU

SGD

VSM

MLP

LSA

NMF

Skip-gram

Word2vec

DNN

PMF

Naive Bayes

k-means

KL

EM

KNN

LR

PLSA

Markov Chain

BM25

SVD

BERT

MF

CTR

CF

LSTM

LDA

SVD++

Content-Based
Personalization

Interaction-Based
Personalization

BiLSTM

Temporal
Personalization

LSI

User-Based
Personalization

HMM

Text Analytics

CRF

Predictive
Modeling
Generative
Modeling

Pattern-Based 29 9 0 0 0 0 15 14 0 0 0 0 0 0 0 6 0 0 0 3 0 3 3 1 0 0 0 0 0 0
Template-Based 0 0 0 0 0 0 0 0 0 0 0 0 0 0 9 0 0 0 0 0 0 0 0 0 0 0 0 0 5 0
Structure-Based 0 0 0 0 0 0 0 0 0 0 0 0 0 12 4 0 0 0 0 0 0 4 0 3 0 0 0 0 0 0
Constraint-Based 0 0 0 0 0 0 0 8 0 0 0 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Rule-Based Tagging 0 0 0 0 0 12 0 0 5 0 0 0 0 0 0 0 0 0 0 0 3 4 0 0 0 0 0 0 0 0
Query-Based 48 34 0 0 10 0 0 15 0 21 0 0 0 0 8 8 8 7 2 0 7 9 6 8 4 4 0 0 0 0
Query Refinement 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0
Query Scoping 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Query Suggestions 0 0 0 0 0 6 0 0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 2 0 0
Query Segmentation 0 0 13 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0
Prediction 0 0 86 99 55 50 49 31 0 23 0 0 0 28 0 17 16 23 21 17 20 0 11 13 15 18 17 17 14 13
Ratings Prediction 0 0 34 38 22 0 26 0 12 0 0 0 0 0 7 0 8 0 9 5 0 0 0 0 0 0 7 0 2 3
Prediction Uncertainty 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 2 0 0 0 0 0 2 0 1 0 0 0 0 0 0
Generative Model 0 0 0 0 0 0 12 0 0 0 7 19 0 0 0 13 0 0 0 5 0 8 7 5 0 0 0 0 0 0
Graph Generation 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0
Topic Modeling 179 0 0 0 0 0 17 0 0 0 18 30 18 12 0 0 12 0 0 8 0 10 12 16 14 6 0 0 4 0
Text Similarity 31 24 0 0 0 0 0 0 0 4 7 0 2 0 0 0 0 0 0 3 0 0 6 0 1 0 0 0 1 0
Word Cluster 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 9 0 0 0 0 0 0 0 0 0
Semantic Analysis 47 0 22 0 0 0 0 0 6 0 4 12 6 5 0 4 7 10 0 4 0 4 6 3 2 4 0 0 1 0
Term Weighting 0 76 0 0 0 0 0 0 0 16 0 0 0 0 0 0 0 0 0 0 0 0 8 0 0 0 0 0 0 0
Opinion Mining 14 10 17 0 0 5 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 2 0 0 0 0 0 0 0 0
Activity-Based Recommendations 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Session-Based Recommendations 3 0 2 3 5 4 5 2 5 0 1 1 3 0 1 0 1 0 1 2 2 0 0 0 0 2 5 3 6 1
Behavior-Based Recommendations 0 0 0 0 0 0 0 0 0 0 0 0 0 0 15 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0
Time-Aware Recommendations 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0
Time-Based Recommendations 0 0 0 0 0 17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0
Historical Data-Driven Recommendations 0 0 39 46 27 0 21 15 0 0 0 0 0 13 0 8 12 10 9 0 0 7 0 6 0 9 0 9 5 0
Content-Based Recommendations 113 75 63 0 0 26 0 0 17 17 19 16 18 18 19 11 0 17 13 8 0 10 0 10 0 0 0 10 0 5
Context-Aware Recommendations 64 0 0 0 0 0 0 19 0 0 0 0 0 0 13 0 0 0 8 8 2 0 4 0 4 0 0 7 6 0
Geographic Support Recommendations 0 0 0 0 0 0 0 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0
Click-Through Recommendations 0 0 0 0 0 0 0 0 0 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0
Search Trail-Based Recommendations 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Recommendations Using User Feedback 0 0 0 17 0 0 23 0 0 0 3 5 0 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
User Interaction (Interactivity) 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 10 0 8 0 0 0 0 0 0
Item Recommendation 43 0 0 46 27 23 22 0 0 0 7 8 0 0 4 5 0 0 13 0 0 5 0 0 0 0 9 0 0 0
Hybrid Recommendation 54 31 0 0 0 0 11 0 0 0 6 0 0 0 0 6 0 0 5 0 0 3 0 4 0 0 6 0 0 0
Multi-Criteria Ratings 0 0 0 16 6 8 5 0 0 0 7 3 0 0 0 0 0 0 0 3 0 2 0 1 0 0 0 0 0 0
Ranking 0 107 95 94 48 47 50 0 30 33 0 27 30 28 0 16 17 0 0 15 0 17 0 16 15 0 0 13 0 0
Graph Ranking 0 0 0 19 8 0 19 12 0 0 0 0 0 0 0 0 0 0 0 7 0 0 0 0 0 0 0 0 0 0
Dimensionality Reduction 0 0 0 0 3 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Feature Selection 5 4 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Sampling-Based 0 0 0 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0
Filtering 91 63 40 74 0 0 26 22 0 0 18 14 12 9 15 14 6 8 0 14 0 6 0 8 0 0 0 7 0 0
Smoothing 0 0 0 0 0 0 10 0 0 9 0 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0 0 0 0 0
Pruning 0 0 0 4 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0
Representation Learning 0 0 39 33 20 23 33 15 19 0 6 11 8 17 0 0 10 6 9 10 6 9 4 3 4 0 0 5 7 4
Memory-Based Approaches 0 0 18 21 13 18 7 0 0 0 0 0 2 0 4 0 2 0 6 7 0 0 0 0 0 0 0 0 0 0
Contextual Graph 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Image-Based 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 2 0 0
Image Similarity 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Image Recognition 2 0 2 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Trained-Based 0 0 37 35 28 0 21 0 0 15 0 0 0 14 0 10 13 3 7 6 11 9 4 4 6 7 0 0 6 0
Pre-Trained Model 0 0 0 0 3 0 4 3 15 2 3 1 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 0
Transformer-Based 0 0 0 0 0 0 0 0 21 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Network Architecture 0 0 0 0 0 21 0 0 17 0 0 0 6 0 0 0 5 0 0 8 0 8 0 0 0 6 0 0 5 0
Parameter Estimation 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Multi-Task Learning 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Hierarchical Clustering 0 0 0 0 0 0 0 0 0 0 0 0 3 0 6 0 8 0 0 0 0 0 0 0 0 0 0 0 0 0
Density-Based 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Tree Based 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
End-To-End Approach 0 0 0 4 5 12 6 0 6 0 0 0 0 3 0 0 2 0 0 4 0 0 0 0 0 4 0 0 2 0
Randomization 0 0 0 21 0 0 0 0 0 0 0 0 0 15 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 2
Anomaly Detection 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Co-Occurrence Analysis 67 0 0 17 0 0 12 0 0 0 6 13 9 12 0 0 11 0 0 0 9 3 0 5 0 0 0 3 0 0
Neighborhood-Based 0 0 0 0 0 0 0 0 0 0 0 0 0 0 8 0 0 0 7 0 0 0 0 1 0 0 0 0 0 0
Attentive 0 0 0 0 10 15 8 0 11 0 0 1 0 2 0 0 0 0 0 6 0 0 0 0 3 0 0 0 6 0
Positive Relevance Feedback 0 0 0 2 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Frequency-Based 0 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 0 0 0 0 0 0
Tag Relevance 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Algorithm Flexibility (Algorithm-Agnostic) 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 1 0 0 0 0 0 0 0
Language Diversity (Multilingual) 18 19 0 0 0 0 0 0 8 0 0 0 2 2 0 1 0 2 0 2 0 0 0 3 0 3 0 0 4 1
Data Dimensionality (Multidimensional) 0 0 26 0 12 10 0 0 0 0 0 13 6 0 0 0 8 0 6 4 0 0 5 4 4 4 0 0 2 0
Data Modality (Multimodal) 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Entity Variability (Multi-Type Entities) 0 0 0 0 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

BPR

Query Processing

Features

PMI

Rule-Based
Approaches

SVM

Categories

TF-IDF

Table 3 illustrates a mapping of features to models in user intent modeling. The table
presents the comprehensive mapping of 74 distinct features to the corresponding models,
grouped into 20 categories. For detailed definitions and explanations of the features, please
refer to Appendix C.

0

0

2

0

0

4

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

90

0

0

0

0

0 10

0

0

0

0

0

0

0

5

0

0

0

0

0

0

7

0

0

0

0

0

0

0

0

36

0

0

0

0

7

0

0

0

0

0

0

0

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

24

0

0

0

4

0

0

0

0

0

0

2

0

6

0

0

0

0

0

0

2

0

0

0

0

0

0

1

0

0

214

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

2

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

13

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

16

0

0 10

0

0

0

0

0 10

0 10

0

0

9

0

0

0

0

0

8

0

0

7

7

0

0

0

0

5

719

5

0

0

0

0

4

0

4

3

3

0

0

0

0

0

0

0

0

0

1

1

3

0

0

0

0

0

0

0

197

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

3

0

0

0

5

0

0

7

0

0

0

2

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

370

1

0

1

0

0

0

5

0

0

0

0

2

0

0

4

0

0

0

1

0

0

0

0

0

0

1

1

0

1

96

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

3

12

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

1

0

0

2

0

1

0

0

4

0

2

158

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

100

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

53

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

3

0

4

0

1

0

0

0

0

2

0

4

1

0

1

0

2

0

0

2

0

1

1

1

0

0

0

0

0

1

79

0

0

0

0

0

6

0

0

0

0

0

0

0

5

0

0

0

0

0

0

4

0

0

0

0

0

0

0

0

40

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

1

0

0

1

0

0

0

0

0

5

0

0

3

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

2

0

0

0

0

0

0

0

0

0

0

24

0

0

7

0

0

0

0

0

0

0

5

0

0

4

0

0

0

0

0

2

0

0

0

0

0

0

0

0

0

254

7

8

4

0

0

0

7

0

0

0

2

0

6

0

6

5

0

4

0

0

6

0

0

2

0

0

5

0

0

547

5

0

5

0

0

5

0

0

0

0

0

0

0

0

3

0

0

4

0

2

3

0

0

0

0

0

0

0

0

162

0

0

0

0

0

0

0

0

0

0

2

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

10

0

0

0

0

0

0

0

0

0

0

0

6

0

0

2

0

0

0

0

2

0

0

0

0

0

0

0

0

0

24

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

18

0 10

0

0

0

0

0

6

7

5

8

0

0

0

1

6

0

0

0

0

3

3

0

0

0

0

0

3

0

264

0

141

33
15

3

7
76

4
59

1

4

0

0

2

0

1

0

4

0

0

0

0

0

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

2

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

53

0

11 11 11 12

0

0

0 10

0

8

9

0

0

8

0

8

0

0

0

0

0

0

7

0

6

6

0

0

805

0

0

0

0

0

0

0

4

0

1

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

71

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

12

0

0

2

0

0

4

0

0 10

0

4

0

0

0

6

0

0

4

0

0

7

3

0

4

4

0

5

0

0

500

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

2

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

8

4

0

2

0

9

4

0

4

4

4

0

4

4

0

2

0

0

3

6

0

1

4

0

0

0

0

0

0

0

356

0

0

0

0

0

0

0

7

0

3

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

109

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

6

0

0

4

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

0

4

1

0

3

2

0

0

0

1

2

256

0

0

0

0

0

1

0

0

0

4

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

39

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

21

0

0

0

0

0

2

0

0

3

0

3

0

0

0

1

3

1

0

3

0

0

2

0

0

0

2

0

0

0

96

0

1

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

18

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

3

0

0

0

0

9

0

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

13

0

0

0

0

0

1

0

0

2

0

0

0

0

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

0

54

0

0

0

0

9

4

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

3

0

59

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

2

8

0

0

0

0

0

0

0

0

0

2

0

2

0

3

0

0

0

0

0

0

0

0

2

0

0

2

1

0

187

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

2

0

0

18

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

7

0

0

0

0

0

0

0

0

0

0

69

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

6

4

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

24

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

5

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

2

0

0

0

0

0

0

0

0

0

0

0

67

0

0

0

0

0

0

0

2

0

0

2

0

0

0

0

0

0

0

0

0

1

0

0

1

0

0

0

0

0

110

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

1

0

0

0

0

0

0

0

0

1

0

0

0

0

0

3

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

0

9

808 468 537 601 309 299 403 156 178 153 114 182 125 206 122 128 152 86 116 161 70 139 82 127 74 67 44 78 90 29 34 35 55 22 48 54 19 28 54 25 54 27 19 26 39 16 10 20 25 27 41 19 11 28

4

9 26 10 14

4
11

29

4
1

2

2

in the domain of image classification, deep learning models such as Convolutional Neural Networks (CNNs) and Recurrent Neural Networks (RNNs) have
proven to be effective in handling features related to image recognition and processing. Conversely, for time series forecasting problems, models like ARIMA,
LSTM, or GRU may be more suitable choices.

4.3 Model combinations
Following the completion of the data extraction and synthesis phase of the
SLR, a total of 59 models were identified, each mentioned in at least six publications. It became evident that some of these models were integrated to address
the considerations of research modelers, including feature requirements, quality
attributes, and evaluation measures (see Figure 3). The selected publications

16

Understanding User Intent Modeling for CRS: An SLR

proposed viable combinations of models based on the authors’ research and
assessed the outcomes resulting from these combinations.
LDA
LDA 205 TF-IDF
TF-IDF 57 122 SVM
SVM 35 20 109 CF
CF 37 25 5 107 MF
MF 18 9 4 32 59 LSTM
LSTM 10 9 7 7 8 56 CTR
CTR 9 4 5 11 2 1 54 Markov Chain
Markov Chain 13 6 8 2 4 4 0 39 BERT
BERT 3 7 3 3 1 8 3 0 38 BM25
BM25 7 11 8 2 0 2 3 3 4 34 SVD
SVD 19 14 4 13 12 2 1 2 2 2 33 PLSA
PLSA 23 8 6 7 1 0 2 2 0 1 3 32 KL
KL 8 5 8 3 4 0 2 2 1 0 0 0 32 LR
LR 8 3 14 1 1 3 3 1 1 1 1 0 0 29 KNN
KNN 11 8 14 4 3 1 0 4 1 0 2 4 1 3 29 EM
EM 8 5 4 5 2 1 1 7 1 2 2 5 0 1 1 24 k-means
k-means 7 5 2 2 1 0 2 0 2 2 3 1 0 0 1 2 23 Naive Bayes
Naive Bayes 8 4 17 3 0 1 0 0 0 0 1 0 1 5 3 0 0 23 PMF
PMF 14 5 0 13 10 3 7 2 2 0 4 1 3 0 1 2 0 0 22 DNN
DNN 5 4 2 7 3 8 5 1 2 1 2 0 0 2 0 0 0 0 3 20 Word2vec
Word2vec 6 7 0 2 2 5 0 0 4 1 3 0 0 0 0 0 0 0 0 1 20 Skip-gram
Skip-gram 7 4 3 2 1 2 0 0 2 2 3 1 1 0 0 0 2 0 0 0 4 19 LSA
LSA 11 9 4 1 0 1 0 0 0 1 6 8 1 0 3 1 1 0 0 0 0 2 18 VSM
VSM 8 14 3 4 0 0 1 2 0 2 2 3 1 0 0 0 2 0 0 0 2 0 2 18 NMF
NMF 12 8 1 8 6 3 0 2 0 1 6 0 1 2 1 1 1 0 6 1 1 0 0 1 18 MLP
MLP 5 4 1 4 5 6 2 0 3 0 2 0 0 0 0 0 0 0 3 1 0 0 0 0 3 18 FM
FM 5 3 2 6 6 6 2 2 2 0 4 0 0 1 0 0 0 0 2 3 2 0 0 0 2 3 18 SGD
SGD 3 3 2 4 9 4 1 2 0 0 4 0 0 2 3 0 1 0 1 2 0 0 0 0 2 3 3 17 GRU
GRU 2 3 1 1 2 7 1 1 6 1 1 0 0 0 0 1 0 0 2 2 1 0 0 0 1 3 3 2 17 Gibbs sampling
Gibbs sampling 12 2 3 1 1 1 0 1 1 0 0 2 2 1 0 0 1 0 1 0 1 1 1 1 1 0 0 0 0 16 PMI
PMI 5 2 3 2 1 0 1 2 0 3 1 1 1 0 0 0 1 0 0 0 2 2 0 0 1 0 0 0 0 0 14 BPR
BPR 2 1 0 2 4 1 2 2 1 0 2 1 0 0 3 1 1 0 2 0 0 0 1 0 0 0 0 3 2 0 0 14 HMM
HMM 3 1 3 0 1 2 0 4 0 1 0 1 0 0 1 1 2 0 1 0 0 1 0 0 0 0 1 1 0 0 0 2 13 BiLSTM
BiLSTM 3 2 3 1 0 8 1 1 5 1 2 1 0 1 1 1 0 0 0 3 2 1 0 0 0 0 2 1 4 0 1 0 0 13 GBDT
GBDT 0 0 3 0 0 1 1 1 0 2 0 0 1 1 0 0 0 2 0 1 0 0 0 0 0 1 0 0 0 0 2 0 0 0 12 CRF
CRF 4 1 6 0 0 1 1 3 0 1 0 1 0 0 1 2 1 0 0 0 0 0 0 0 0 1 0 0 0 1 1 0 2 0 0 12 LSI
LSI 10 6 4 0 0 0 0 1 0 1 6 2 0 0 0 0 1 1 0 0 0 1 3 1 0 0 0 0 0 0 0 0 0 0 0 0 11 SVD++
SVD++ 4 2 1 7 6 5 0 0 0 1 7 0 0 2 0 1 0 0 3 3 0 0 0 0 5 2 2 2 1 0 0 0 0 0 0 0 0 11 NCF
NCF 4 3 0 4 4 4 0 2 0 0 2 1 0 0 1 0 0 0 2 2 0 0 0 0 1 4 1 2 3 0 0 1 1 1 0 0 0 2 11 CDL
CDL 7 3 0 8 3 3 4 0 0 0 2 0 0 0 0 0 0 0 6 2 0 0 0 0 3 3 2 1 1 0 0 0 0 0 0 0 0 3 2 10 GRU4Rec
GRU4Rec 2 0 0 0 2 1 1 3 0 0 0 0 0 0 1 0 0 0 1 2 0 0 0 0 0 0 1 2 1 0 0 2 1 1 0 0 0 0 2 0 10 LambdaMART
LambdaMART 1 0 1 1 0 0 1 0 1 0 0 0 1 1 0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 9 MMR
MMR 0 1 2 0 0 1 1 1 1 1 0 0 1 0 1 2 0 0 0 0 1 0 0 0 0 0 0 0 1 0 0 1 0 1 1 0 0 0 0 0 0 0 9 MLE
MLE 2 0 3 0 0 0 1 0 0 0 0 1 1 0 1 1 0 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 1 0 0 1 0 9 RW
RW 4 2 2 1 1 0 1 2 1 1 0 0 0 1 1 1 0 1 1 1 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 9 DeepCoNN
DeepCoNN 6 3 0 5 4 5 1 1 1 0 2 0 1 0 0 0 0 0 6 2 0 0 0 0 5 5 4 2 3 0 0 0 0 1 0 0 0 3 2 5 1 0 0 0 0 9 PageRank
PageRank 2 2 2 0 0 0 0 1 0 0 0 0 4 0 1 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0 8 NER
NER 2 0 2 0 0 1 0 0 0 1 0 1 0 0 1 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 8 Self-attention
Self-attention 1 0 0 1 2 1 1 1 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 8 SVR
SVR 3 2 4 2 1 1 0 0 1 0 1 0 1 1 2 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 8 SDAE
SDAE 4 2 0 5 3 2 1 0 0 0 1 0 0 0 0 0 0 0 2 1 0 0 0 0 1 1 0 2 1 0 0 0 0 0 0 0 0 1 2 4 0 0 0 0 0 2 0 0 0 0 7 RBM
RBM 3 2 1 3 3 1 1 0 0 0 2 0 0 0 0 1 1 0 3 1 0 0 0 0 2 2 3 3 1 0 0 0 0 0 0 0 0 1 1 3 0 0 0 0 0 3 0 0 0 0 2 7 ALS
ALS 1 0 1 4 4 0 0 0 0 0 2 0 0 1 0 0 0 0 1 0 0 0 0 0 1 0 2 2 0 0 0 1 0 0 0 0 0 1 0 0 1 0 0 0 0 0 0 0 0 0 0 1 7 Random Forest
Random Forest 0 1 4 0 0 1 0 0 0 0 0 0 0 2 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7 PCA
PCA 3 0 2 1 0 0 0 1 1 0 2 2 1 1 0 1 2 0 0 0 0 1 3 2 0 0 0 1 0 1 0 0 0 0 0 0 2 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 7 RankNet
RankNet 0 0 2 0 0 0 0 0 2 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 6 Cosine similarity
Cosine similarity 2 3 0 2 1 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6 RGM
RGM 2 0 2 1 0 1 0 2 1 1 0 1 0 0 0 2 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 1 0 6 Rocchio
Rocchio 0 1 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6
451 249 182 198 124 109 55 62 49 34 81 38 24 28 28 21 20

7

47 29 16 11 11

5

28 29 24 26 20

2

5

7

5

5

2

3

2

12 10 12

4

3

0

0

2

5

0

0

0

0

2

1

0

0

0

1

0

0

Fig. 2 shows a matrix representation of model combinations in user intent modeling
research. The matrix illustrates the combinations of 59 selected models, where each cell
indicates the number of publications discussing the corresponding model combination. The
diagonal cells represent the number of publications discussing each model individually. Green
cells indicate a higher research volume, while yellow and red cells indicate lower volumes.
Gray cells represent areas where no evidence was found for valid combinations. The last
row of the matrix represents the frequency of publications in which the models on the
diagonal cells were considered in combination with others. For instance, we identified 451
publications that mentioned LDA as one of their design decisions in combination with other
models. The combination matrix provides insights into the frequency and popularity of
model combinations, aiding researchers in identifying existing combinations and areas for
further investigation.

To thoroughly examine the various model combinations, a matrix resembling a symmetric adjacency matrix was constructed, treating the models as
nodes and the combinations as edges in a graph representation. The upper or
lower triangular matrix was utilized to depict unique combinations. Figure 2
visually presents this combination matrix, encompassing the 59 selected models. The diagonal cells of the matrix indicate the number of publications
discussing each model independently. For instance, our analysis identified 205
papers concerning LDA [30, 31] and 122 papers focusing on TF-IDF [91, 92].

Understanding User Intent Modeling for CRS: An SLR

17

Within the matrix, the cells represent the number of papers discussing
the combinations of the corresponding columns and rows. For example, there
were 57 papers discussing the combination of LDA and TF-IDF [93], while 35
papers delved into the combination of SVM and LDA [94].
The color coding in the matrix indicates the number of research articles associated with each combination. Green cells signify a higher volume of
research conducted in the literature, while yellow and red cells denote lower
volumes. Additionally, gray cells indicate areas without evidence regarding
valid combinations based on the authors’ perspectives. However, it is crucial
to note that these gray cells represent potential areas warranting further investigation, offering researchers opportunities to explore the feasibility of such
combinations.
Overall, the combination matrix serves as an extensive overview of the
model combinations in user intent modeling research, shedding light on the
frequency of their occurrence in the literature. It can be considered a valuable resource for researchers and practitioners seeking to identify existing
combinations and areas requiring further exploration.

4.4 Model trends
In recent studies, machine learning models have witnessed significant advancements across various fields, leading to notable trends in their development and
application. However, it is worth noting that our study goes beyond recent
years. By using the term ”models,” we refer to a wide range of models that
research modelers can employ in user intent modeling.

GRU4Rec

MMR

MLE

RW

DeepCoNN

PageRank

NER

Self-attention

SVR

SDAE

RBM

ALS

Random Forest

PCA

RankNet

Cosine similarity

RGM

Rocchio

7

6

6

6

6

CF

LSTM

MF

LDA

SVM

TF-IDF

NCF

7

SVD++

7

CDL

7

LSI

7

CRF

8

GBDT

8

BiLSTM

8

HMM

8

BPR

9

2
3
3
2
3
4
1
1
1
0
0
0
0
0
0
0
0
0
0
0
0
0

PMI

9

6
2
2
3
3
1
2
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0

Gibbs sampling

9

3
0
1
3
5
2
3
1
1
0
2
0
1
0
0
0
0
0
0
0
0
0

GRU

9

2
0
1
1
0
2
4
2
2
2
1
2
1
1
1
0
0
0
0
0
0
1

SGD

9

0
1
2
0
3
1
1
4
1
0
0
4
0
0
3
2
0
0
0
1
0
0

FM

205 122 109 107 59 56 54 39 38 34 33 32 32 29 29 24 23 23 22 20 20 19 18 18 18 18 18 17 17 16 14 14 13 13 12 12 11 11 11 10 10

0
2
0
1
2
2
2
1
2
0
2
2
3
1
2
2
0
0
0
0
0
0

MLP

0
1
1
0
0
1
1
0
0
1
0
0
0
1
0
0
0
0
0
0
0
0

1
4
1
1
4
2
1
1
3
3
1
1
3
1
0
2
0
0
0
0
0
0

NMF

0
1
0
1
0
0
0
0
0
0
1
1
1
0
1
0
0
0
0
0
0
0

1
2
3
3
3
1
0
0
1
0
3
1
8
1
1
1
0
0
0
0
0
0

Skip-gram

0
1
1
0
0
2
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0

0
2
0
1
3
1
2
1
7
5
2
1
3
3
0
0
1
0
0
0
0
0

VSM

0
2
0
1
0
0
0
0
0
0
1
0
0
0
0
0
0
2
0
0
0
0

0
2
0
1
2
1
4
4
2
2
4
0
3
3
2
2
0
0
0
0
0
0

LSA

1
0
0
0
1
1
0
0
2
0
0
0
1
0
1
0
0
0
0
0
0
0

1
4
1
7
4
1
2
3
1
2
2
1
1
0
2
0
0
1
0
0
0
0

DNN

0
0
2
3
0
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0

9 0
12 2
7 2
9 3
1 1
0 1
0 1
0 5
0 1
0 1
0 3
0 2
0 3
0 2
0 5
0 1
0 0
0 0
0 1
0 0
0 0
0 0

Word2vec

0
0
0
4
1
1
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

1
4
0
5
2
5
1
0
2
1
2
2
4
2
6
0
0
2
0
0
0
0

Naive Bayes

0
0
1
1
1
1
1
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0

k-means

0
0
3
0
0
1
2
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0

2023 5 3 2 10 2 4 2
2022 9 9 5 6 5 7 5
2021 17 11 8 7 4 8 2
2020 21 15 8 14 11 11 7
2019 25 12 9 14 16 17 2
2018 22 14 10 9 5 6 3
2017 16 9 5 13 7 2 5
2016 20 11 7 9 2 1 5
2015 11 8 7 6 3 0 3
2014 9 3 3 5 4 0 2
2013 19 11 5 5 0 0 3
2012 8 4 8 3 0 0 6
2011 9 4 10 2 0 0 2
2010 5 3 8 1 0 0 1
2009 3 2 9 2 0 0 4
2008 3 3 2 1 0 0 2
2007 0 0 0 0 0 0 0
2006 2 0 3 0 0 0 0
2005 1 0 0 0 0 0 0
2004 0 0 0 0 0 0 0
2003 0 0 0 0 0 0 0
2002 0 0 0 0 0 0 0

PMF

0
0
1
1
2
1
0
0
0
1
0
1
1
0
0
0
0
0
0
0
0
0

EM

0
0
3
2
2
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

KNN

0
0
1
1
0
1
0
0
1
0
0
2
0
1
1
0
0
0
0
0
0
0

LR

0
0
0
0
0
0
1
0
1
0
2
1
0
1
0
1
0
1
0
0
0
0

KL

2
1
1
1
3
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

PLSA

1
0
2
1
1
0
0
0
0
0
1
1
1
0
0
1
0
0
0
0
0
0

SVD

1
1
0
0
0
0
0
1
2
0
1
0
0
0
2
1
0
0
0
0
0
0

BM25

0
1
0
0
0
1
2
0
1
0
1
0
2
0
1
0
0
0
0
0
0
0

BERT

0
1
0
1
0
1
0
2
1
0
1
1
1
0
0
0
0
0
0
0
0
0

Markov Chain

3
2
3
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

CTR

LambdaMART

Table 4 illustrates the trend of models mentioned in user intent modeling research over
publication years, highlighting the popularity and emergence of various models.

0
3
0
3
3
3
1
4
0
0
0
2
0
0
0
0
0
0
0
0
0
0

0
1
0
2
2
2
1
2
0
0
2
2
2
1
1
0
0
0
0
0
0
0

0
1
3
1
0
2
0
3
3
0
1
0
2
0
1
1
0
0
0
0
0
0

0
3
2
3
5
1
0
0
0
1
2
0
0
0
0
1
0
0
0
0
0
0

3
3
4
1
5
0
0
1
0
0
1
0
0
0
0
0
0
0
0
0
0
0

3
4
2
4
2
2
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

1
1
2
2
4
2
1
1
1
1
1
0
0
0
0
0
0
0
0
0
0
0

5
4
2
3
1
0
0
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0

1
0
1
0
1
0
2
2
2
1
4
1
0
1
0
0
0
0
0
0
0
0

0
0
1
1
1
0
2
1
0
1
1
3
1
1
1
0
0
0
0
0
0
0

0
2
1
3
0
3
2
1
0
1
0
0
1
0
0
0
0
0
0
0
0
0

0
0
0
2
0
5
0
0
1
2
0
3
0
0
0
0
0
0
0
0
0
0

3
3
2
0
3
1
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

0
0
1
0
1
1
0
1
0
0
2
1
2
1
2
0
0
0
0
0
0
0

1
0
0
1
2
0
1
0
0
1
0
3
1
2
0
0
0
0
0
0
0
0

0
0
1
0
0
2
1
2
0
0
1
1
0
0
1
1
0
1
0
0
0
0

0
1
1
2
3
1
1
0
0
1
1
0
0
0
0
0
0
0
0
0
0
0

2
3
3
0
2
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

1
0
1
0
4
2
1
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0

18

Understanding User Intent Modeling for CRS: An SLR

To gain insights into the usage patterns of these models, we organized the
59 selected models (mentioned in at least six publications2 ) based on the publication years of the studies that referenced them. The span of these publications
ranges from 2002 to 2023. Table 4 provides an overview of these trends.
Among the selected models, LDA, TF-IDF, SVM, CF, and MF emerged as
the top five most frequently mentioned models, appearing in over 500 papers.
It is important to note that while some recently gained substantial attention,
such as BERT [34], CF [95], LSTM [96, 97], DNN [98], and GRU [99, 100], our
study encompasses models from various time periods.
These trends shed light on the popularity and usage patterns of different models in user intent modeling. By identifying frequently mentioned
models and observing shifts in their prevalence over time, researchers and
practitioners can stay informed about the evolving landscape of user intent
modeling and make informed decisions when selecting models for their specific
applications [55, 101].

4.5 Quality models and evaluation measures
In AI-based projects, high-quality models and comprehensive evaluation measures are crucial. Quality attributes refer to a set of metrics that assess
the performance of a model [50, 102], while evaluation measures quantitatively gauge the quality of model outputs [55]. These attributes and
measures play a critical role in ensuring the generation of accurate and reliable
results [50, 103, 104].
Table 5 shows an overview of quality models and evaluation measures used in machine
learning, including performance metrics such as accuracy, precision, recall, F1 score, and
AUC-ROC, as well as other evaluation techniques such as cross-validation, holdout
validation, and confusion matrices.
#F Quality attributes

#F Quality attributes

#F Quality attributes

#F Evaluation measures

675 Performance
363 Efficiency
Effectiveness

89 Validity

21 Classification
19 Accuracy
Clarification

233 Precision

252 Diversity

48 Resource Utilization
43 Flexibility

18 Classification
15 Performance
Query Accuracy

150 F1-Score

206 Usefulness
203 Stability

42 Computational Cost

14 Appropriateness

158 Scalability

42 Interpretability

10 Comparability

120 Normalized Discounted Cumulative Gain
81 (NDCG)
Mean Average Precision (MAP)

139 Recommendation
128 Performance
Satisfaction

41 Retrieval Performance

10 Retrieval Accuracy

76 Mean Reciprocal Rank (MRR)

40 Convergence

9

Readability

54 Area Under the ROC Curve (AUC)

125 Coverage

8

Persuasiveness

27 Mean Absolute Error (MAE)

122 Robustness

40 Recommendation
35 Effectiveness
Transparency

8

Scrutability

24 Hit Rate (HR)

114 Resource Efficiency

31 Informativeness

6

Unexpectedness

22 Discounted Cumulative Gain (DCG)

111 Simplicity

24 Recommendation Efficiency

6

Memory Efficiency

19 Root Mean Squared Error (RMSE)

99 Reliability

22 Predictability

72 Novelty

200 Recall
120 Accuracy

9

Normalized Mutual Information (NMI)

While accuracy is a commonly employed evaluation measure, it may
not adequately represent the model’s performance, especially in imbalanced
classes. Alternative measures such as precision [105, 106], recall [107, 108],
and F1-score [109, 110] are used to evaluate model performance, particularly
when dealing with imbalanced data. Additionally, evaluation measures like the
area under the curve (AUC)[111, 112] and receiver operating characteristic
2
For access to the complete list of model, please refer to the supplementary materials available
on Mendeley Data[72].

Understanding User Intent Modeling for CRS: An SLR

19

(ROC)[10, 113] curve are frequently used to assess binary classifiers. These
measures provide insights into the model’s ability to differentiate between positive and negative instances, particularly when the costs associated with false
positives and false negatives differ.
For ranking problems, evaluation measures such as mean average precision
(MAP)[114, 115] and normalized discounted cumulative gain (NDCG)[116,
117] are commonly employed. These measures evaluate the quality of the
ranked lists generated by the model and estimate its effectiveness in predicting
relevant instances.
When evaluating regression models, measures such as root mean squared
error (RMSE)[118, 119] and mean absolute error (MAE)[95, 120] are used to
quantify the discrepancy between predicted values and actual values of the
target variable.
The selection of appropriate evaluation measures is crucial to ensure the
accuracy and reliability of machine learning models. The suitable measure(s)
choice depends on the specific problem domain, data type, and project objectives. These factors are pivotal in selecting the most appropriate quality
attributes and evaluation measures. Table 5 presents the quality attributes
and evaluation measures identified in at least six publications3 . Performance,
Effectiveness, Diversity, Usefulness, and Stability are among the top five quality attributes. Precision, Recall, F1-Score, Accuracy, and NDCG are among
the top five evaluation measures identified in the SLR. For detailed explanations of the identified quality attributes and evaluation measures, please refer
to Appendix D.

4.6 Datasets
Datasets are fundamental to machine learning and data science research, as
they provide the raw material for training and testing models and enable the
development of solutions to complex problems. They come in various forms
and sizes, ranging from small, well-curated collections to large, messy datasets
with millions of records. The quality of datasets is crucial [103], as high-quality
data ensures the accuracy and reliability of models, while poor-quality data
can introduce biases and inaccuracies. Data quality encompasses completeness, accuracy, consistency, and relevance, and ensuring data quality involves
cleaning, normalization, transformation, and validation.
The size and complexity of datasets pose challenges in terms of storage,
processing, and analysis. Big datasets require specialized tools and infrastructure to handle the volume and velocity of data. On the other hand, complex
datasets, such as graphs, images, and text, may require specialized techniques
and models for extracting meaningful information and patterns.
Furthermore, the availability of datasets is a vital consideration in advancing machine learning research and applications. Open datasets that are freely
3
For access to the complete list of quality attributes and evaluation measures, please refer to
the supplementary materials available on Mendeley Data[72].

TREC
MovieLens
Yelp
AOL

twitter
Last.FM
Yahoo webscope

Netflix
Google
TripAdvisor

Wikipedia
CiteULike
ODP

ReDial
Qulac
Snippets

Sina Weibo
DBLP
DBpedia

Foursquare
HetRec
MSN

Stack Overflow
Epinions
Gowalla

public
Criteo
Toys

TG-ReDial
SemEval
Taobao

MIMIC
BibSonomy
Ciao

Book-Crossing
industrial
digg

Ohsumed
youtube
Bing

Douban Movie
NTCIR
TMALL

IMDB
Delicious
NLU

ATIS
Amazon 5-core
Movies

Etsy
SRR
OpenDialKG

MMD
QuAC
DuRecDial

CRM
Meituan
MyPersonality

WordNet
AMiner
LibraryThing

NIPS Dataset
Douban
ACM Digital Library

CLINC
Amazon Book
Diginetica

yoochoose
Flixster
e-commerce

MOOC
ACL
AP

product
PascalVOC07
QALD

8tracks
DrugBank
20newsgroup

1
3
2
0
0
1
0
0
0
1
0
0
0
0
0
0
0
0
0
1
0
0
0
0
1
0
0
0
2
1
1
1
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
20

5
6 10
5
1
2
3
2
0
1
1
0
0
0
6
2
1
0
2
1
1
1
1
1
1
1
1
1
2
2
0
1
1
0
0
0
1
0
0
0
0
1
0
1
0
1
0
0
0
0
0
1
1
1
1
0
0
1
0
0
0
1
0
0
0
1
1
1
2
0
0
0
0
0
0
0
0
0
0
0
77

2
8
1
2
2
3
4
0
1
1
1
0
1
0
1
2
1
0
1
1
2
1
0
0
0
0
0
1
0
0
0
0
1
0
0
2
0
0
1
0
0
0
0
0
1
0
0
0
1
0
0
0
1
1
0
0
1
1
0
0
0
0
0
0
0
1
1
0
0
0
0
0
1
0
0
0
0
0
0
0
49

4
5
5
4
3
0
2
0
1
0
1
0
1
1
0
2
1
0
0
0
2
1
0
1
1
2
0
0
0
0
2
0
0
0
0
0
1
0
0
0
0
0
0
0
1
0
0
0
1
2
2
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
1
0
1
0
0
0
0
0
0
0
0
0
0
49

2
6 10
8
2
1
3
0
2
1
2
0
2
1
0
0
1
2
1
1
0
1
0
2
0
0
3
0
1
0
0
2
0
1
1
1
1
1
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
1
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
1
0
0
1
1
1
0
0
66

1
2
3
2
0
3
0
0
1
0
0
1
0
0
0
0
0
1
1
0
0
0
0
0
0
1
0
0
1
0
1
0
0
0
0
0
0
0
0
0
0
1
1
1
0
0
2
2
0
0
0
0
0
0
0
0
0
0
2
0
1
0
0
0
0
0
0
0
0
0
2
2
0
0
0
0
0
1
0
0
33

1
7
4
2
0
3
1
0
2
0
1
1
0
0
0
0
1
0
0
1
0
0
0
0
2
0
0
0
0
0
0
0
0
0
1
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
1
0
0
1
0
0
0
0
1
0
0
0
0
0
0
0
0
0
1
33

2
2
1
1
2
2
3
1
1
0
0
0
2
0
0
0
0
0
0
0
0
1
1
0
0
0
0
2
0
0
0
0
0
0
0
0
0
1
0
2
1
0
1
0
0
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
28

2
1
0
0
3
3
1
1
0
0
0
1
1
0
0
0
0
2
1
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
1
0
21

0
2
0
0
2
0
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
1
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
13

7
1
1
0
0
0
0
0
1
1
0
1
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
18

3
1
3
0
3
1
0
5
1
1
1
0
0
0
0
0
0
0
0
1
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
23

5
1
2
0
1
3
0
1
1
1
0
1
0
2
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
21

4
1
0
0
0
1
0
0
0
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
0
0
0
10

3
0
2
0
2
0
0
2
0
1
0
2
0
3
0
0
0
0
0
1
0
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
2
0
0
0
0
0
22

3
1
1
0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
6

2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
2

1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1

0
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1

48 46 46 26 22 22 19 12 12
8
8
8
7
7
7
6
6
6
6
6
6
5
5
5
5
5
4
4
4
4
4
4
3
3
3
3
3
3
3
3
3
3
3
3
3
3
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2
2

https://www.kaggle.com/general/65624

https://www.kaggle.com/datasets/andrewmvd/trip-advisor-hotel-reviews

https://www.kaggle.com/c/wikichallenge/data

https://www.kaggle.com/datasets/minnieliang/rec-system

https://www.kaggle.com/joniarroba/noshowappointments

https://paperswithcode.com/dataset/redial

https://paperswithcode.com/dataset/qulac

https://www.kaggle.com/datasets/simiotic/github-code-snippets

https://paperswithcode.com/dataset/weibo

https://hpi.de/naumann/projects/repeatability/datasets/dblp-dataset.html

http://wikidata.dbpedia.org/develop/datasets

https://sites.google.com/site/yangdingqi/home/foursquare-dataset

https://grouplens.org/datasets/hetrec-2011/

https://learn.microsoft.com/en-us/azure/open-datasets/dataset-microsoft-news?tabs=azureml-opendatasets

https://www.kaggle.com/competitions/foursquare-location-matching

https://alchemy.cs.washington.edu/data/epinions/

https://www.kaggle.com/datasets/sashababybird/gowalla

https://towardsai.net/p/machine-learning/best-datasets-for-machine-learning-and-data-science-d80e9f030279

https://ailab.criteo.com/download-criteo-1tb-click-logs-dataset/

https://www.kaggle.com/datasets/carlolepelaars/toy-dataset

https://paperswithcode.com/dataset/tg-redial

https://www.kaggle.com/datasets/azzouza2018/semevaldatadets

https://www.kaggle.com/datasets/pavansanagapati/ad-displayclick-data-on-taobaocom

https://github.com/microsoft/MIMICS

https://www.kde.cs.uni-kassel.de/wp-content/uploads/bibsonomy/

https://www.kaggle.com/datasets/aravindaraman/ciao-data

http://www2.informatik.uni-freiburg.de/~cziegler/BX/

https://www.v7labs.com/blog/best-free-datasets-for-machine-learning

http://datasets.syr.edu/datasets/Digg.html

https://www.kaggle.com/datasets/weipengfei/ohr8r52

https://www.kaggle.com/datasets/datasnaek/youtube-new

https://www.cdata.com/drivers/bingsearch/sync/

https://www.kaggle.com/datasets/utmhikari/doubanmovieshortcomments
https://ntcir.datasearch.jp/

https://github.com/CCIIPLab/GCE-GNN/issues/3

https://github.com/tilde-nlp/NLU-datasets

https://github.com/howl-anderson/ATIS_dataset/blob/master/README.en-US.md
http://jmcauley.ucsd.edu/data/amazon

https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
https://www.kaggle.com/datasets/sepidafs/etsy-shops
https://catalog.data.gov/dataset/srr-hood-canal

https://github.com/facebookresearch/opendialkg
https://paperswithcode.com/dataset/mmd
http://quac.ai

https://paperswithcode.com/dataset/durecdial
https://www.kaggle.com/nihandincer/customer-relationship-management-crm
https://www.kaggle.com/c/meituan-dianping

https://www.kaggle.com/code/testaccount93/mypersonality/data
https://wordnet.princeton.edu/
https://www.aminer.cn/aminer_data

https://www.librarything.com/services/
https://www.kaggle.com/datasets/benhamner/nips-papers
https://www.kaggle.com/datasets/fengzhujoey/douban-datasetratingreviewside-information

https://www.kaggle.com/datasets/thedevastator/academic-publications-metrics-from-acm-ieee-and
https://www.kaggle.com/competitions/mayo-clinic-strip-ai/data
https://www.kaggle.com/datasets/shrutimehta/amazon-book-reviews-webscraped

https://darel13712.github.io/rs_datasets/Datasets/diginetica/
https://www.yoochoose.com/
http://datasets.syr.edu/datasets/Flixster.html

https://www.kaggle.com/datasets/mervemenekse/ecommerce-dataset
https://www.kaggle.com/datasets/samyakjhaveri/mooc-final
https://paperswithcode.com/dataset/acl-arc-1
https://www.kaggle.com/c/products-10k
https://paperswithcode.com/sota/zero-shot-object-detection-on-pascal-voc-07

http://qald.sebastianwalter.org
https://breached.vc/Thread-8tracks-Database-Leaked-Download
https://go.drugbank.com/

https://www.kaggle.com/datasets/crawford/20-newsgroups

accessible and well-documented foster collaboration and innovation, while proprietary datasets may restrict access and impede progress [13, 101, 121]. Data
sharing and ethical considerations in data use are increasingly recognized,
leading to efforts to promote open access and responsible data practices.
In this study, we identified 80 datasets that researchers have utilized in
the context of intent modeling approaches, and these datasets were mentioned
in at least two publications4 . Table 6 provides an overview of these datasets
and their frequency of usage from 2005 to 2023. Notably, TREC, MovieLens,
Amazon, Yelp, and AOL emerged as the top five datasets commonly used in
evaluating intent modeling approaches for recommender systems [10, 122, 123]
and search engines [6, 124, 125]. These datasets have been utilized in over 200
publications, highlighting their significance and wide adoption in the field.
Amazon

URL
1

https://trec.nist.gov/data.html

2023
2022
2021
2020
2019
2018
2017
2016
2015
2014
2013
2012
2011
2010
2009
2008
2007
2006
2005

https://paperswithcode.com/dataset/ap

https://paperswithcode.com/dataset/delicious

https://www.kaggle.com/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews

https://www.kaggle.com/datasets/shivamb/netflix-shows

https://webscope.sandbox.yahoo.com/

https://www.kaggle.com/datasets/ravichaubey1506/lastfm

https://github.com/shaypal5/awesome-twitter-data

https://www.kaggle.com/datasets/dineshydv/aol-user-session-collection-500k

https://www.yelp.com/dataset

http://jmcauley.ucsd.edu/data/amazon

https://grouplens.org/datasets/movielens/

20
Understanding User Intent Modeling for CRS: An SLR

Table 6 shows datasets commonly used for user intent modeling approaches. The table
includes the names of the datasets and their corresponding URLs.

5 Decision making process

This section describes how researchers make decisions when selecting intent
modeling approaches. It illustrates a systematic approach to choosing intent
modeling methods based on academic literature.

5.1 Decision meta-model

Research modelers face the challenge of selecting the most suitable combination of models to develop an intent modeling approach for a conversational
recommender system. In this section, we present a meta-model for the decisionmaking process in the context of intent modeling. The adoption of this
meta-model is based on the principles outlined in the ISO/IEC/IEEE standard
42010 [126], which provides a framework for conceptual modeling of Architecture Description. This process requires a systematic approach to ensure that
the chosen models effectively capture and understand users’ intentions. Let’s
consider a scenario where research modelers encounter this challenge and go
through the decision-making process:

4
For access to the complete list of datasets, please refer to the supplementary materials available
on Mendeley Data[72].

Understanding User Intent Modeling for CRS: An SLR

21

Goal and Concerns: The research modelers aim to build an intent modeling
approach for a conversational recommender system. Their goal is to accurately
determine the underlying purposes or goals behind users’ requests, enabling
personalized and precise responses. The modelers have concerns regarding
quality attributes and functional requirements, and they aim to achieve an
acceptable level of quality based on their evaluation measures.
Identification of Models and Features: To address this problem, the
modelers consider various models that can capture users’ intentions in the
conversational context. They identify essential features, such as user intent
prediction or context analysis based on their concerns. They explore the
available models and techniques, such as Supervised Learning, Unsupervised
Learning, Recurrent Neural Networks, Deep Belief Networks, Clustering, and
Self-Supervised Learning Models. The modelers also consider the recent trends
in employing models for intent modeling.
Evaluation of Models: The modelers review the descriptions and capabilities
of several models that align with capturing users’ intentions in conversational
interactions. They analyze each model’s strengths, limitations, and applicability to the intent modeling problem. They consider factors such as the models’
ability to handle natural language input, understand context, and predict user
intents accurately. This evaluation allows them to shortlist a set of candidate models that have the potential to address the intent modeling challenge
effectively.
In-depth Analysis: The research modelers conduct a more detailed analysis
of the shortlisted models. They examine the associated techniques for each
model to ensure their suitability in the conversational recommender system.
They assess factors such as training data requirements, model complexity,
interpretability, and scalability. Additionally, they explore the possibility of
combining models to identify compatible combinations or evaluate the existing
literature on such combinations. If necessary, further study may be conducted
to assess the feasibility of model combinations. This step helps them identify
the optimal combination of models that best capture users’ intentions in the
conversational setting and address their concerns.

5.2 A decision model for intent modeling selection
Decision theories have wide-ranging applications in various fields, including
e-learning [127] and software production [128–130]. In the literature, decisionmaking is commonly defined as a process involving problem identification, data
collection, defining alternatives, and selecting feasible solutions with ranked
preferences [131–136]. However, decision-makers approach decision problems
differently, as they have their own priorities, tacit knowledge, and decisionmaking policies [137]. These differences in judgment necessitate addressing
them in decision models, which is a primary focus in the field of multiplecriteria decision-making (MCDM).

22

Understanding User Intent Modeling for CRS: An SLR
features

has

modeling rationale

modeler

1..*
has
combination

0..*

1..*
1..*

model

expresses

raises

1..*

0..*

1..*
1..*

0..*

applied model

pertains to
0..*

0..*

1..*

1..*

concern
1..*
0..*

0..*

0..*

affects

1..*

0..*

0..*

model selection

depends upon

applies

1..*
contains

1..*

affects

design decision

intent modeling
approach

has

justifies
considers

1..*
1..*

1..*

1..*

trend

0..*
affects

quality attribute

impacts on
1..*

1..*

1..*

evaluation
measure

1..*

feature
requirement

meets

Fig. 3 illustrates the decision-making process researchers employ in selecting intent modeling approaches within the academic literature.

MCDM problems involve evaluating a set of alternatives and considering
decision criteria [59]. The challenge lies in selecting the most suitable alternatives based on decision-makers’ preferences and requirements [138]. It is
important to note that MCDM problems do not have a single optimal solution,
and decision-makers’ preferences play a vital role in differentiating between
solutions [138]. In this study, we approach the problem of model selection
as an MCDM problem within the context of intent modeling approaches for
conversational recommender systems.
Let M odels = m1 , m2 , . . . , m∥M odels∥ be a set of models found in the literature (decision space), such as LDA, SVM, and BERT. Let F eatures =
f1 , f2 , . . . , f∥F eatures∥ be a set of features associated with the models, such
as ranking, prediction, and recommendation. Each model m ∈ M odels supports a subset of the set F eatures and satisfies a set of evaluation measures
(M easures = e1 , e2 , . . . , e∥M easures∥ ) and quality attributes (Qualities =
q1 , q2 , . . . , q∥Qualities∥ ). The objective is to identify the most suitable models,
or a combination of models, represented by the set Solutions ⊂ M odels, that
address the concerns of researchers denoted as Concerns, where Concerns ⊆
{F eatures ∪ M easures ∪ Qualities}. Accordingly, research modelers can
adopt a systematic strategy to select combinations of models by employing an MCDM approach. This approach involves taking M odels and their
associated F eatures as input and applying a weighting method to prioritize
the F eatures based on the preferences of decision-makers. Subsequently, the
defined Concerns are considered, and an aggregation method is utilized to
rank the M odels and propose fitting Solutions. Consequently, the MCDM
approach can be formally expressed as follows:
M CDM : M odels × F eatures × Concerns → Solutions

Understanding User Intent Modeling for CRS: An SLR

23

The decision model developed for intent modeling, using MCDM theory
and depicted in Figure 3, is a valuable tool for researchers working on conversational recommender systems. This approach helps researchers explore options
systematically, consider important factors for conversational interactions, and
choose the best combination of models to create an effective intent modeling
approach. The decision model suggests five steps for selecting a combination
of models for conversational recommender systems:
(1) Models: In this phase, researchers should gain insights into best practices
and well-known models employed by other researchers in designing conversational recommender systems. Appendix A can be used to understand the
definitions of models, while Appendix B can help in becoming familiar with
the categories used to classify these models. Table 2 illustrates the categorization of models in this study, and Table 4 presents the trends observed
among research modelers in utilizing models to build their conversational
recommender systems.
(2) Feature Requirements Elicitation: In this step, researchers need to
fully understand the core aspects of the intent modeling problem they are
studying. They should carefully analyze their specific scenario to identify the
key characteristics required in the models they are seeking, which may involve
using a combination of models. For instance, researchers might consider prediction, ranking, and recommendation as essential feature requirements for their
conversational recommender systems. Researchers can refer to Appendix C to
gain a better understanding of feature definitions and model characteristics,
which will help them select the most suitable features for their intent modeling
project.
(3) Finding Feasible Solutions: In this step, researchers should identify
models that can feasibly fulfill all of their feature requirements. Table 3 can
be used to determine which models support specific features. For example, the
table shows that 99 publications explicitly mentioned Collaborative Filtering
(CF) as a suitable model for applications requiring predictions, and 94 publications indicated CF’s applicability for ranking. Moreover, 46 studies employed
CF for item recommendation. Based on these findings, if a conversational
recommender system requires these three feature requirements, CF could be
selected as one of the potential solutions. If the number of feature requirements
increases, the selection problem can be converted into a set covering problem
[139] to identify the smallest sub-collection of models that collectively satisfy
all feature requirements.
(4) Selecting Feasible Combinations: In this phase, researchers need to
assess whether the identified models can be integrated or combined. Figure 2
provides information on the feasibility of combining models based on the
reviewed articles in this study. If the table does not indicate a potential combination, it does not necessarily imply that the combination is impossible.
It simply means no evidence supports its feasibility, and researchers should
investigate the combination independently.

24

Understanding User Intent Modeling for CRS: An SLR

(5) Performance Analysis: After identifying a set of feasible combinations, researchers should address their remaining concerns regarding quality
attributes and evaluation measures. Table 5 and Appendix D can be used to
understand the typical concerns other researchers in the field employ. Additionally, Table 6 provides insights into frequently used datasets across domains
and applications. Researchers can then utilize off-the-shelf models from various libraries, such as TensorFlow and scikit-learn, to build their own solutions
(pipelines). These solutions can be evaluated using desired datasets to assess
whether they meet all the specified concerns. This phase of the decision model
differs from the previous four phases, as it requires significant ad-hoc efforts
in developing, training, and evaluating the models.
By employing this decision-making process, research modelers can develop
an intent modeling approach that accurately captures and understands users’
intentions in the conversational recommender system. This enables personalized and precise responses, enhancing the overall user experience and
satisfaction.

6 Evaluation of Findings: Case Studies
In this section, we present an evaluation of the proposed decision model (refer
to Section 5) through two scientific case studies conducted by eight researchers
from the University of California San Diego in the United States and the University of Klagenfurt in Austria. The primary objective of the case studies
was to understand the applicability of the decision model to the participants’
projects and gain insights into their decision-making processes. The participants emphasized their specific feature requirements throughout the case
studies, which we diligently documented in Table 3. Drawing from this information, we identified feasible models based on the comprehensive data presented
in Table 2 and Table 3. We further explored the viable combinations of these
models, as outlined in Figure 2. To assess the attention and recognition received
by the selected models in the academic literature, we conducted a thorough
analysis, referring to Table 4. This analysis provided valuable insights into the
popularity and relevance of the models over time among researchers. Finally,
the prominent and trending feasible combinations were shared with the case
study participants. Figure 3 offers an overview of the typical decision-making
process employed by researchers when selecting intent modeling models.
In Table 7, we have provided a comprehensive overview of the case studies
conducted in this research. The table includes details about the specific contexts of each case study, the feature requirements identified by the case study
participants, the design decisions (model selection) made by the researchers
based on those requirements, and the outcomes of our decision model for each
case study. Subsequent sections of this paper provide an in-depth exploration
of the case studies, covering the addressed concerns, the outcomes obtained
through utilizing the decision model, and the implications derived from our
rigorous analysis.

Understanding User Intent Modeling for CRS: An SLR

25

Table 7 provides an overview of the feature requirements considered by the case study
participants[140, 141] during their decision-making process for developing their
conversational recommender systems. The selected feature requirements were instrumental
in guiding the participants’ model selection. We employed the decision model based on the
defined feature requirements to identify feasible combinations of models. The results of the
decision model are also presented in this table, showcasing how it aligns with the
participants’ choices, validating the effectiveness of the decision-making process for
developing innovative and effective conversational recommender systems.
Cae Study 1
Domain Conversational recommender systems
Approach CRB-CRS

ASLI

Dataset Movielens, ReDial

Etsy, Alibaba

Year 2022

2020

Research institute University of California San Diego
Country Austria

A*

Venue Information Systems
Design decisions by case study participants TF-IDF, BERT

GRU, LDA
6

✓

Prediction
Semantic Analysis

✓

Term Weighting

✓
✓

Historical Data-Driven Recommendations
✓

✓

Click-Through Recommendations

✓

Item Recommendation
Ranking

✓

Transformer-Based

✓

✓
✓

Network Architecture
Attentive

8
✓

Pattern-Based

End-To-End Approach

WWW
self-attention

Decision model results TF-IDF, BERT

Content-Based Recommendations

University of Klagenfurt
US

CORE ranking A*

#Feature requirements

Cae Study 2
Recommender system

✓
✓

6.1 Case Study Method
Case study research is an empirical research method [60] that investigates a
phenomenon within a particular context in the domain of interest [62]. Case
studies can be employed to describe, explain, and evaluate a hypothesis. They
involve collecting data regarding a specific phenomenon and applying a tool to
evaluate its efficiency and effectiveness, often through interviews. In our study,
we followed the guidelines outlined by Yin [46] to conduct and plan the case
studies.
Objective: The main aim of this research was to conduct case studies to
evaluate the effectiveness of the decision model and its applicability in the
academic setting for supporting research modelers in selecting appropriate
models for their intent modeling approaches.
The cases: We conducted two case studies within the academic domain to
assess the practicality and usefulness of the proposed decision model. The case
studies aimed to evaluate the decision model’s effectiveness in assisting research
modelers and researchers in selecting models for their intent modeling tasks.
Methods: For the case studies, we engaged with research modelers and
researchers actively involved in intent modeling approaches. We collected data

26

Understanding User Intent Modeling for CRS: An SLR

through expert interviews and discussions to gain a comprehensive understanding of their specific requirements, preferences, and challenges when
selecting models. The case study participants provided valuable insights into
the decision-making process and offered feedback on the suitability of the
decision model for their intent modeling needs.
Selection strategy: In line with our research objective, we employed a multiple case study approach [46] to capture a diverse range of perspectives and
scenarios within the academic domain. This selection strategy aimed to ensure
the credibility and reliability of our findings. We deliberately selected two
publications from highly regarded communities with an A* CORE rank. We
verified the expertise of the authors, who actively engage in selecting and implementing intent modeling models. Their knowledge and experience allowed us
to consider various factors in different application contexts, including quality
attributes, evaluation measures, and feature requirements.
By conducting these case studies, our research aimed to validate the practicality of the decision model and demonstrate its value in supporting research
modelers and researchers in their intent modeling endeavors. The insights
gained from the case studies provided valuable feedback for refining the decision model and contributed to advancing the intent modeling field within the
academic community.

6.2 Case Study 1:
The first case study presented in our paper revolves around a research project
conducted at the University of Klagenfurt in Austria. The study focused on
investigating a retrieval-based approach for conversational recommender systems (CRS) [140]. The primary objective of the researchers was to assess the
effectiveness of this approach as an alternative or complement to language generation methods in CRS. They conducted user studies and carefully analyzed
the results to understand the potential benefits of retrieval-based approaches
in enhancing user intent modeling for conversational recommender systems.
Throughout the project, the case study participants made two important
design decisions (models), TF-IDF and BERT, to develop the CRS. They
evaluated their approach using Movielens and ReDial datasets to measure its
performance.
By applying the decision model presented in our paper (in Section 5.2),
the case study participants identified six essential features that were crucial in guiding their decision-making process for selecting the most suitable
models and datasets. These features provided valuable insights into designing and implementing an effective retrieval-based approach for conversational
recommender systems, contributing to improving user intent modeling in this
context.

Understanding User Intent Modeling for CRS: An SLR

27

6.2.1 Feature requirements:
In this section, we outline the feature requirements that the case study participants considered during their decision-making process for the research project.
Each feature requirement was carefully chosen based on its relevance and
potential to enhance the retrieval-based approach for CRS. Below are the
feature requirements and their rationale for selection:
Semantic Analysis: The case study participants recognized the importance
of analyzing the meaning and context of words and phrases in natural language data. Semantic analysis helps the model understand user intents more
accurately, leading to more relevant and contextually appropriate recommendations.
Term Weighting: Assigning numerical weights to terms or words in a document or dataset helps the machine learning model comprehend the significance
of different terms in the data. The participants adopted term weighting to
improve the model’s ability to identify relevant features and make better
recommendations.
Content-Based Recommendations: This feature involves utilizing item
characteristics or features to recommend similar items to users. The participants valued this approach, allowing the system to tailor recommendations
based on users’ past interactions and preferences.
Ranking: The case study participants sought a model capable of ranking items
or entities based on their relevance to specific queries or users. By incorporating
ranking, the system ensures that the most relevant recommendations appear
at the top, enhancing user satisfaction.
Transformer-Based: Transformer-based models, such as neural networks,
excel at learning contextual relationships in sequential data like natural language. The participants chose this approach to effectively leverage the model’s
ability to understand and process conversational context.
End-To-End Approach: The case study participants preferred an end-toend modeling strategy, where a single model directly learns complex tasks from
raw data inputs to desired outputs. By avoiding intermediate stages and handcrafted features, the participants aimed to simplify the model and improve its
performance in CRS tasks.

6.2.2 Results and analysis:
During the expert interview session with the case study participants, we systematically followed the decision model presented in Section 5.2 to identify
appropriate combinations of models that align with the defined feature requirements for their conversational recommender systems. In the initial steps (Steps
1 and 2), we collaboratively established the essential feature requirements for
their CRS, carefully considering the critical aspects that would enhance their
system’s performance. Subsequently, we referred to Table 3 (Steps 3 and 4) to
evaluate which models could fulfill these specific feature requirements.

28

Understanding User Intent Modeling for CRS: An SLR

Upon analyzing the table, both the case study participants and we discovered that BERT offered support for Semantic Analysis, Content-Based Recommendations, Ranking, Transformer-Based, and End-To-End Approaches.
Additionally, TF-IDF was found to be supportive of Term Weighting, ContentBased Recommendations, and Ranking. This insightful information made us
realize that combining these two models would adequately address all six feature requirements for their CRS. Consequently, the case study participants
confirmed that combining BERT and TF-IDF would be a suitable choice to
fulfill their CRS needs. This combination was validated as a compatible and
valid option, consistent with the guidance provided by the decision model.
The data presented in Table 4 further reinforces the popularity and
relevance of BERT and TF-IDF as widely used models for conversational recommender systems. The case study participants were well-aware of these trends
and acknowledged that their model choices aligned with prevailing practices.
This alignment provides additional validation to their model selections, demonstrating their dedication to adopting the latest technologies in their research
project to create an effective CRS.
Furthermore, Table 6 provided valuable insights into the popularity and significance of various datasets, including Movielens and ReDial. These datasets
have been cited and utilized in over 50 publications, underscoring their recognition within the research community. The case study participants acknowledged
the widespread use of these datasets by other researchers, reflecting an interesting trend in dataset selection. This awareness further highlights their
commitment to utilizing well-established and reputable datasets in their
research, contributing to the credibility and reliability of their study findings.

6.3 Case Study 2:
The second case study presented in our paper focuses on a research project
conducted at the University of California San Diego in the United States [141].
The study introduces the Attentive Sequential model of Latent Intent (ASLI)
to enhance recommender systems by capturing users’ hidden intents from their
interactions.
Understanding user intent is essential for delivering relevant recommendations in conventional recommender systems. However, user intents are often
latent, meaning they are not directly observable from their interactions. ASLI
addresses this challenge by uncovering and leveraging these latent user intents.
Using a self-attention layer, the researchers (case study participants)
designed a model that initially learns item similarities based on users’ interaction histories. They incorporated a Temporal Convolutional Network (TCN)
layer to derive latent representations of user intent from their actions within
specific categories. ASLI employs an attentive model guided by the latent
intent representation to predict the next item for users. This enables ASLI
to capture the dynamic behavior and preferences of users, resulting in stateof-the-art performance on two major e-commerce datasets from Etsy and
Alibaba.

Understanding User Intent Modeling for CRS: An SLR

29

By utilizing the decision model presented in our paper (in Section 5.2),
the case study participants identified eight essential features crucial in guiding their decision-making process for selecting the most suitable models and
datasets.

6.3.1 Feature requirements:
In this section, we present the feature requirements that were crucial considerations for the case study participants during their decision-making process
for the research project. The following are the feature requirements and the
reasons behind their selection:
Pattern-Based: In the case study, the researchers aimed to improve conversational recommender systems by capturing users’ hidden intents from their
interactions. By identifying user interactions and behavior patterns, the ASLI
model can make informed guesses about users’ intents and preferences, leading
to more accurate and relevant recommendations.
Prediction: The ASLI model predicts the next item for users based on their
latent intents derived from their historical interactions within specific categories. The model can deliver personalized and effective recommendations by
predicting users’ preferences and future actions.
Historical Data-Driven Recommendations: The researchers used previously collected data from users’ interactions to train the ASLI model. By
analyzing historical data, the model can identify patterns, relationships, and
trends in users’ behaviors, which inform its predictions and recommendations
for future interactions.
Click-Through Recommendations: In the case study, the ASLI model
considers users’ clicks on items to understand their preferences and improve
the relevance and ranking of future recommendations. The model can adapt
and refine its recommendations by utilizing click-through data to meet users’
needs better.
Item Recommendation: The ASLI model suggests items to users based on
their previous interactions, enabling it to offer personalized recommendations
tailored to individual users’ preferences and behaviors.
Transformer-Based: ASLI is a neural network model based on the Transformer architecture. Transformers are well-suited for learning context and
meaning from sequential data, making them suitable for capturing the dynamic
behavior and preferences of users in conversational recommender systems.
Network Architecture: The ASLI model’s network architecture is crucial in
guiding information flow through the model’s layers. By designing an effective
network architecture, the researchers ensure that the model can capture and
leverage users’ latent intents to make accurate recommendations.
Attentive: ASLI utilizes attention mechanisms to focus on the most relevant
parts of users’ interactions and behaviors. The model can better understand
users’ intents and preferences by paying attention to critical information,
leading to more attentive and accurate recommendations.

30

Understanding User Intent Modeling for CRS: An SLR

6.3.2 Results and analysis:
During the expert interview session with the case study participants, we used
the decision model (outlined in Section 5.2) to identify suitable combinations
of models that align with the defined feature requirements for their conversational recommender systems. In Steps 1 and 2, we collaboratively established
the essential feature requirements for the ASLI, carefully considering critical
aspects to enhance system performance. Then, in Steps 3 and 4, we referred to
Table 3 to evaluate models that could fulfill these specific feature requirements.
According to the table,both the case study participants and ourselves
found that the GRU model supports Prediction, Historical Data-Driven Recommendations, Click-Through Recommendations, Network Architecture, and
Attentive features. Additionally, the LDA model supports Pattern-Based and
Item Recommendation features. We also discovered that BERT is the only
model in our list supporting Transformer-Based features, and the case study
participants agreed with this combination, considering these models as the
baseline of their approach. However, after performance analysis, they found
that GRU’s performance was unsatisfactory in their setting. Consequently,
they chose to develop their own model from scratch, modifying the selfattentive model. It’s worth noting that the Self-attentive model only supports
Network Architecture and Attentive features, making it a suitable baseline in
combination with other models for their solutions. The case study participants
mentioned considering LDA and BERT as potential models for their upcoming research project due to their similar requirements, although they were not
previously aware of this combination. As per Step 5 of the decision model,
researchers should address any remaining concerns about quality attributes
and evaluation measures after identifying feasible combinations. Thus, the
decision model provided valid models in this case study, but in real-world
scenarios, model combinations may be modified based on other researchers’
concerns, such as quality attributes and evaluation measures.
The case study participants emphasized the value of the data presented
in Table 4 and their intention to incorporate it into their future design decisions. Understanding trends in model usage is crucial to identify models that
may perform well in conversational recommender systems, taking into account
similar concerns and requirements from other researchers.
Furthermore, Table 6 indicates that Etsy and Alibaba datasets are not
widely known in the context of user intent modeling, although the case study
participants clarified that these datasets are well-known in e-commerce services, aligning with their project’s specific domain of focus. Nonetheless, they
expressed their intention to utilize the data presented in this table to explore
potential datasets for evaluating their approach and comparing their work
against other approaches in the literature.

Understanding User Intent Modeling for CRS: An SLR

31

7 Discussion
7.1 SLR outcomes
In our comprehensive review of 791 publications, only 68 of them (8.59%)
explicitly mentioned sharing their code repositories, such as GitHub. This finding highlights that a significant number of researchers do not openly share
their code, which can create challenges in replicating experiments and hinder
the progress of scientific research. Openly providing access to code is essential to promote transparency and ensure reproducibility in machine learning
research [142].
Throughout the systematic literature review, we collected 600 models, out
of which 352 were singletons, representing 58.66% of the total models. This
observation indicates that many researchers develop and use unique models
tailored to their research questions. However, relying heavily on singletons
can restrict the generalizability of research outcomes and impede meaningful comparisons between different approaches. Encouraging the adoption of
common models or establishing standards for model evaluation could significantly enhance the reproducibility and comparability of machine learning
research [143].
In some instances, the methodology for combining models was not clearly
described in the publications. This lack of transparency challenges understanding the underlying techniques used and evaluating their effectiveness. Explicitly
providing descriptions of model combination techniques and the reasons behind
their selection is crucial to increase transparency and facilitate the replication
and extension of research findings [144].
Our analysis revealed a substantial number of variations in the collected models, including BERT4Rec [145], SBERT [146], BERT-NeuQS [147],
BioBERT [148], ELBERT [149], and RoBERTa [150], among others. These
variations are derived from BERT [151], a well-known language model, and
we found 35 publications related to this model based on Figure 2. Researchers
often leverage diverse model variations to address different research questions
and tasks. However, the extensive use of multiple variations can make comparisons with other models complex and hinder the replication of experiments.
Developing standardized categories and taxonomies for model variations would
be beneficial to address this challenge. Such categorization would greatly assist
researchers in understanding the differences and similarities between models,
thereby promoting the sharing and reuse of models across various research
domains. This standardized approach can enhance collaboration and facilitate
advancements in machine learning research [152].
Figure 2 displays that LDA is the most prevalent model in the context of
user intent modeling approaches (as indicated in Table 4). It is important to
recognize that LDA and other traditional models have significantly influenced
the field and inspired the development of newer models like BERT [151]. These
traditional models have served as foundational building blocks, offering initial
insights into various NLP tasks. While traditional models like LDA [153] have

32

Understanding User Intent Modeling for CRS: An SLR

been widely used and contributed to understanding natural language, their
adoption may have gradually decreased over time for several reasons. One
crucial factor is the advent of more sophisticated and advanced models like
BERT. BERT’s bidirectional contextual embeddings and transformer architecture have shown exceptional performance on various NLP tasks, setting new
benchmarks and gaining substantial attention in the research community [154].
Moreover, larger datasets and advancements in computational resources have
facilitated the training and fine-tuning of complex models like BERT, making them more practical and feasible for real-world applications. Additionally,
the interpretability and ease of use of traditional models like LDA have been
balanced by the increased complexity and opaqueness of modern models like
BERT. This trade-off between interpretability and performance has influenced
researchers and practitioners in selecting the most suitable models for their
specific tasks. Furthermore, the diversity of downstream NLP applications has
also influenced the preference for modern models [155]. While traditional models may perform well in specific tasks, BERT’s ability to generalize and excel
across a wide range of NLP benchmarks has made it a popular choice for
various applications.
Regarding dataset usage, we observed that only 394 out of 791 publications (49.81%) opted to utilize public and open-access datasets. This finding
implies that more than half of the publications relied on proprietary datasets
that were specifically generated for individual cases, rendering them inaccessible for reuse by other researchers. Our investigation further revealed the
existence of 253 public open-access datasets that authors employed to evaluate and train their approaches. However, it is worth noting that 173 of these
datasets (68.37%) were mentioned in only one publication and were not subsequently reused by other researchers in the domain of user intent modeling.
This observation highlights a potential deficiency in dataset-sharing and reuse
practices within this research area, which could have significant consequences
for the advancement and credibility of scientific endeavors in the field.
The limited availability of previous datasets presents researchers with
challenges in reproducing and validating reported results, as access to such
datasets is often restricted. Consequently, the ability to objectively compare
and benchmark different models becomes hampered, impeding the identification of state-of-the-art techniques and areas for improvement [156]. Moreover,
the absence of diverse and openly accessible datasets may result in biased
model development and evaluation, limiting the generalizability of models to
real-world scenarios and diverse user populations [157]. The consequences of
this issue extend further, as the duplication of effort in collecting and preparing new datasets consumes valuable resources and consequently decelerates
research progress. To mitigate these challenges, fostering a culture of openness
and collaboration within the research community is essential.

Understanding User Intent Modeling for CRS: An SLR

33

7.2 Case Study Participants
The case study participants showed a careful and thorough approach to
decision-making by conducting extensive research and literature reviews.
This method allowed them to carefully select models for their research
project carefully, showcasing the effectiveness of the decision model in helping
researchers make well-informed and compatible model choices for developing
conversational recommender systems.
Both case study participants emphasized the value of using the decision
model and the knowledge gained during this study. They expressed their intention to use this information to make informed decisions when selecting the
appropriate combinations of models for user intent modeling approaches.
Furthermore, the case study participants recognized that the decision
model serves as a valuable tool for generating an initial list of models to
develop their approaches. However, they acknowledged that Step 5 of the decision model highlights the importance of further analysis, such as performance
testing, to identify the right combinations of models that work well for specific use cases. This recognition underscores the need for practical testing and
validation to ensure the chosen model combinations are effective and suitable
for their particular research goals.
The use of well-known datasets, such as Movielens and ReDial in the first
case study, and Etsy and Alibaba datasets in the second case study, underlines
the researchers’ commitment to using credible data sources for evaluation.
The decision model allowed researchers to consider dataset popularity and
relevance, enhancing the credibility and reliability of their study findings.
The decision model provided valuable insights into the trends in model
usage, as presented in Table 4. Both case study participants expressed interest
in incorporating these trends into their future research decisions, ensuring they
stay up-to-date with the latest advancements in intent modeling approaches.
Throughout the case studies, the discussion highlighted the dynamic nature
of the decision-making process. While the decision model offered feasible model
combinations based on feature requirements, the final choices were influenced
by additional factors such as model performance, quality attributes, and evaluation measures. This adaptability showcased the decision model’s flexibility
in accommodating researchers’ unique priorities and preferences.
Both case studies effectively demonstrated that the decision model offers
a systematic approach to model selection and helps researchers explore various options and combinations of models. This exploratory nature allowed
researchers to consider novel solutions and build upon existing models, creating
innovative intent modeling approaches.
The success of the decision model in assisting researchers in their model
selection process holds promising implications for the broader academic community. By providing a structured and comprehensive methodology, the
decision model can streamline the development of conversational recommender
systems with accurate intent modeling capabilities, ultimately enhancing user
experience and satisfaction.

34

Understanding User Intent Modeling for CRS: An SLR

7.3 Threat to Validity
Validity evaluation is paramount in empirical studies, encompassing systematic
literature reviews (SLRs) and case study research [158]. This paper’s validity
assessment covers various dimensions, including Construct Validity, Internal
Validity, External Validity, and Conclusion Validity. Although other types of
validity, such as Theoretical Validity and Interpretive Validity, are relevant to
intent modeling, they are not explicitly addressed in this context due to their
relatively limited exploration.
Construct Validity pertains to the accuracy of operational measures or
tests used to investigate concepts. In this research, we developed a metamodel (refer to Figure 3) based on the ISO/IEC/IEEE standard 42010 [126]
to represent the decision-making process in intent modeling for conversational
recommender systems. We formulated comprehensive research questions by
utilizing the meta-model’s essential elements, ensuring an exhaustive coverage
of pertinent publications on intent modeling approaches.
Internal Validity concerns verifying cause-effect relationships within the
study’s scope and ensures the study’s robustness. We employed a rigorous
quasi-gold standard (QGS) [159] to minimize selection bias in paper inclusion. Combining manual and automated search strategies, the QGS provided
an accurate evaluation of sensitivity and precision. Our search spanned four
major online digital libraries, widely regarded to encompass a substantial portion of high-quality publications relevant to intent modeling for conversational
recommender systems. Additionally, we used snowballing to complement our
search and mitigate the risk of missing essential publications. The review process involved a team of researchers, including three principal investigators and
five research assistants. Furthermore, the findings were validated by real-world
researchers in intent modeling to ensure their practicality and effectiveness.
External Validity pertains to the generalizability of research findings to
real-world applications. This study considered publications discussing intent
modeling approaches across multiple years. Although some exclusions and inaccessibility of studies may impact the generalizability of SLR and case study
results, the proportion of inaccessible studies (less than 2%) is not expected
to affect the overall findings significantly. The knowledge extracted from this
research can be applied to support the development of new theories and
methods for future intent modeling challenges, benefiting both academia and
practitioners in this field.
Conclusion Validity ensures that the study’s methods, including data collection and analysis, can be replicated to yield consistent results. We extracted
knowledge from selected publications, encompassing various aspects such as
Models, Datasets, Evaluation Metrics, Quality Attributes, Combinations, and
Trends in intent modeling approaches. The accuracy of the extracted knowledge was safeguarded through a well-defined protocol governing the knowledge
extraction strategy and format. The authors proposed and reviewed the review
protocol, establishing a clear and consistent approach to knowledge extraction. A data extraction form was employed to ensure uniform extraction of

Understanding User Intent Modeling for CRS: An SLR

35

relevant knowledge, and the acquired knowledge was validated against the
research questions. All authors independently determined quality assessment
criteria, and crosschecking was conducted among reviewers, with at least three
researchers independently extracting data, thus enhancing the reliability of the
results.

8 Related work
This section contextualizes our study within the broader landscape of systematic literature reviews (SLRs) focused on intent modeling approaches.
Table 8 situates our study within the existing body of literature on user intent modeling,
as identified through our SLR.
Ref.
Our Study
[102]
[24]
[103]
[160]
[55]
[161]
[162]
[104]
[163]
[164]
[51]
[73]
[4]
[165]
[50]
[166]
[57]

Year
2023
2020
2021
2022
2022
2022
2023
2023
2012
2022
2010
2015
2021
2019
2013
2019
2014
2020

Type
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Aca
Gry
Gry
Aca
Gry

RM
SLR/CS
SLR
SLR
SLR
Survey
Survey
Survey
Survey
Survey
Survey
Survey
Survey
Review
Survey
Survey
Review
Review
Review

#Pub
791
58
83
29
N/A
88
116
21
N/A
N/A
N/A
N/A
N/A
N/A
N/A
N/A
15
N/A

DM
Yes
No
No
No
No
No
No
No
Yes
No
No
No
No
No
No
No
No
No

Tr.
Yes
No
No
No
No
Yes
No
No
Yes
No
No
Yes
No
Yes
No
No
No
No

DS
Yes
No
No
Yes
Yes
Yes
No
No
No
No
No
No
Yes
No
No
Yes
Yes
Yes

Cat
Yes
Yes
Yes
Yes
No
No
No
No
No
Yes
No
No
No
Yes
No
Yes
Yes
Yes

MC
Yes
No
No
No
No
No
No
No
No
No
No
No
No
No
No
Yes
No
Yes

F
Yes
No
No
No
No
No
No
No
No
No
No
No
No
No
No
No
No
No

#QA
38
7
8
7
8
5
6
4
8
2
5
7
3
6
6
4
5
3

#F
74
4
4
6
12
8
7
7
7
7
4
8
5
8
7
11
4
8

#E
13
8
5
7
14
9
5
9
5
3
10
10
10
6
7
6
2
1

#M
59
6
9
14
15
18
11
11
11
8
8
19
14
15
13
12
3
15

#CQA
38
6
6
4
5
4
6
4
8
2
3
5
2
6
5
4
5
2

#CF
74
3
5
3
9
7
7
4
7
7
4
5
3
7
5
11
4
5

#CE
13
5
3
5
10
5
2
9
5
1
4
9
7
3
5
3
1
1

#CM
59
2
2
7
7
5
8
5
11
4
4
9
8
8
10
9
2
8

Cov. (%)
100
64.00
61.54
55.88
63.27
52.50
79.31
70.97
100
70.00
55.56
63.64
62.50
68.57
75.76
81.82
85.71
59.26

Table 8 provides a comprehensive overview of our study’s position within
the existing body of literature on user intent modeling, identified through
our systematic literature review. Our review encompassed a substantial number of publications, totaling 791, making our investigation one of the most
extensive in this domain. The table comprises various columns, each serving
distinct purposes. Through the SLR process, we curated both academic literature (Aca) and gray literature (Gry) reviews that contributed to a well-rounded
understanding of user intent modeling.
Academic literature reviews (Aca) were prevalent among the selected studies, accounting for over 80 percent of the reviewed literature. This choice aligns
with our approach, which primarily focuses on academic sources. The research
methods (RM) employed in the selected studies include SLR, Case Study (CS),
Survey (Surv.), and Review (Rev.). Notably, none of the reviewed SLRs utilized
case studies (CS) to evaluate their findings; instead, they solely reported on the
outcomes of the SLR process. In contrast, our study took a more comprehensive approach by incorporating case studies within the research methods (RM),
enabling a holistic perspective on decision-making in user intent modeling.
In comparison to the reviewed SLRs, our study stands out for its emphasis on decision-making processes and decision models (DM). While only one
paper [104] among the reviewed SLRs reported on this aspect, our study introduced a decision model based on the evidence extracted from the literature.
This decision model serves as a valuable tool for research modelers, guiding

36

Understanding User Intent Modeling for CRS: An SLR

informed decisions and identifying suitable individual models or combinations
that address specific concerns.
Regarding observed trends (Tr.) within the models, four studies [4, 51,
55, 104] (23.52%) reported on this aspect. Additionally, seven studies [50, 55,
57, 73, 103, 160, 166] (41.17%) provided valuable insights into open-access
datasets (DS) suitable for training or evaluating the models, serving as valuable
resources for the research community.
Furthermore, our study categorized (Cat) the models, in line with eight
other SLRs [4, 24, 50, 57, 102, 103, 163, 166] (47.05%) in the field. However, we
noted that only two publications [50, 57] (11.76%) reported on combinations
of models (MC), making it challenging to ascertain which models are feasible
to combine effectively.
The table underscores the rigorous analysis conducted, encompassing a significant number of models (#M), evaluation measures (#E), quality attributes
(#QA), and features (#F), compared to other studies. Moreover, we identified
common concepts among our results and the selected publications, presented in
the last four columns, #CQA, #CF, #CE, and #CM, along with the percentage of coverage (Cov.). Additionally, the last five columns of the table indicate
that our study covers almost 70 percent of the models, quality attributes, evaluation measures, and features reported in other SLRs, showcasing the relevance
of our research to the broader literature on user intent modeling.
To maintain conciseness, we have focused on concepts mentioned in more
than five publications in our report. For a comprehensive understanding and
access to the complete set of data and references, we encourage readers to
explore our repository on Mendeley Data [72]. Furthermore, our study’s inclusion of both academic literature and gray literature reviews contributes to a
comprehensive understanding of user intent modeling, incorporating insights
from diverse sources.
The combination of SLR and case study methods offers a robust research
design, allowing us to explore existing literature while also delving deeper
into specific real-world scenarios. By examining decision-making processes and
introducing a decision model, our study addresses a crucial aspect often overlooked in the reviewed SLRs, providing valuable guidance to researchers and
practitioners. Moreover, our analysis reveals emerging trends within the models
and the availability of open-access datasets, enhancing the visibility of valuable resources for the research community. Categorizing the models facilitates
a structured taxonomy, aiding researchers in navigating the diverse landscape
of user intent modeling approaches. While only a limited number of publications explored combinations of models, our study highlights this as a potential
avenue for further investigation. By shedding light on the relationships between
models, our findings can inform the development of more robust and effective
ensemble approaches. The extensive coverage of models, evaluation measures,
quality attributes, and features in our analysis offers a comprehensive view
of user intent modeling, providing valuable insights for researchers seeking to
refine their models and evaluation strategies.

Understanding User Intent Modeling for CRS: An SLR

37

9 Conclusion and future work
In this paper, we have undertaken a comprehensive investigation of the
decision-making process involved in intent modeling for conversational recommender systems. Our main objective was to address the challenge faced by
research modelers in selecting the most effective combination of models for
developing intent modeling approaches.
To ensure the credibility and reliability of our findings, we conducted a
systematic literature review and carried out two academic case studies, meticulously examining various dimensions of validity, including Construct Validity,
Internal Validity, External Validity, and Conclusion Validity.
Drawing inspiration from the ISO/IEC/IEEE standard 42010 [126], we
devised a meta-model as the foundational framework for representing the
decision-making process in intent modeling. By formulating comprehensive
research questions, we ensured the inclusion of relevant studies and achieved
an exhaustive coverage of pertinent publications.
Our study offers a holistic understanding of user intent modeling within the
context of conversational recommender systems. The SLR analyzed over 13,000
papers from the last decade, identifying 59 distinct models and 74 commonly
used features. These analyses provide valuable insights into the design and
implementation of user intent modeling approaches, contributing significantly
to the advancement of the field.
Building on the findings from the SLR, we proposed a decision model to
guide researchers and practitioners in selecting the most suitable models for
developing conversational recommender systems. The decision model takes into
account essential factors such as model characteristics, evaluation measures,
and dataset requirements, facilitating informed decision-making and enhancing
the development of more effective and efficient intent modeling approaches.
We demonstrated the practical applicability of the decision model through
two case studies, showcasing its usefulness in real-world scenarios. The decision
model aids researchers in identifying initial model sets and considering essential
quality attributes and functional requirements, streamlining the process and
enhancing its reliability.
The significance of contributions in User Intent Modeling cannot be overstated in the current landscape of scientific research. Whether actively engaged
in advancing the fundamentals or exploring its applications within their respective domains, scientists are undeniably conscious of this field. Amidst this
crucial juncture, our study holds paramount importance as it contributes to the
consolidation of the field’s foundations. We envision our research to become an
integral component of essential literature for newcomers, fostering the promotion of this vital field and streamlining researchers’ efforts in selecting suitable
models and techniques. By solidifying the understanding and relevance of User
Intent Modeling, we aim to facilitate future advancements and innovation in
this area of study.
To ensure the longevity and up-to-dateness of the knowledge base constructed from our SLR, we are enthusiastic about taking the necessary steps

38

Understanding User Intent Modeling for CRS: An SLR

to maintain its relevance and value for future researchers embarking on similar
projects. We plan to establish a collaborative platform or repository, inviting
researchers to contribute their latest findings and studies pertaining to the
addressed research challenges. By fostering a community-driven approach, we
aim to create an engaging environment that encourages regular and meaningful contributions. To streamline the process, we intend to develop user-friendly
interfaces and implement effective content moderation to ensure the knowledge
base’s scientific integrity.
Moreover, we are excited to explore implementing an automated data
crawling mechanism, periodically and systematically searching reputable literature sources and academic databases. This technology will enable seamless
integration of the latest research into the knowledge base. Additionally, we are
committed to maintaining a meticulous record of changes and updates to the
knowledge base, including precise timestamps and new information sources.
This transparent documentation will empower future researchers to follow the
knowledge base’s evolution and confidently leverage it for their specific research
needs.
By embracing these proactive measures, we envision establishing a continuously updated and robust knowledge base that serves as a valuable resource for
researchers in the dynamic domain of user intent modeling and recommender
systems.

Acknowledgement
We extend our sincere gratitude to the domain experts who actively participated in and contributed to this research project. Their valuable insights and
expertise have significantly enriched the quality of this study. We would like
to express our appreciation to Sjaak Brinkkemper, Fabiano Dalpiaz, Gerard
Wagenaar, Fernando Castor de Lima Filho, and Sergio Espana Cubillo for
their invaluable feedback, which has helped us in presenting the results of this
study more effectively.
We are also deeply thankful to all the participants of the case studies for
their cooperation and willingness to share their valuable publications, which
served as essential resources in evaluating and validating the proposed decision model. Their contributions have been pivotal in ensuring the practical
applicability and effectiveness of the decision model in real-world scenarios.
Finally, we extend our appreciation to the journal editors and reviewers
for their meticulous review of this manuscript and their constructive feedback.
Their efforts have played a crucial role in enhancing the quality and clarity of this research, making it a more valuable contribution to the scientific
community.

Understanding User Intent Modeling for CRS: An SLR

39

References
[1] Carmel, D., Chang, Y., Deng, H., Nie, J.-Y.: Future directions of
query understanding. Query Understanding for Search Engines, 205–224
(2020)
[2] Khilji, A.F.U.R., Sinha, U., Singh, P., Ali, A., Dadure, P., Manna,
R., Pakray, P.: Multimodal recipe recommendation system using deep
learning and rule-based approach. SN Computer Science 4(4), 421
(2023)
[3] Ge, S., Dou, Z., Jiang, Z., Nie, J.-Y., Wen, J.-R.: Personalizing search
results using hierarchical rnn with query-aware attention. In: Proceedings of the 27th ACM International Conference on Information and
Knowledge Management, pp. 347–356 (2018)
[4] Zhang, S., Yao, L., Sun, A., Tay, Y.: Deep learning based recommender system: A survey and new perspectives. ACM computing surveys
(CSUR) 52(1), 1–38 (2019)
[5] Oulasvirta, A., Blom, J.: Motivations in personalisation behaviour.
Interacting with computers 20(1), 1–16 (2008)
[6] Konishi, T., Ohwa, T., Fujita, S., Ikeda, K., Hayashi, K.: Extracting
search query patterns via the pairwise coupled topic model. In: Proceedings of the Ninth ACM International Conference on Web Search and
Data Mining, pp. 655–664 (2016)
[7] Bendersky, M., Wang, X., Metzler, D., Najork, M.: Learning from user
interactions in personal search via attribute parameterization. In: Proceedings of the Tenth ACM International Conference on Web Search and
Data Mining, pp. 791–799 (2017)
[8] Cao, Y., Li, S., Liu, Y., Yan, Z., Dai, Y., Yu, P.S., Sun, L.: A comprehensive survey of ai-generated content (aigc): A history of generative ai
from gan to chatgpt. arXiv preprint arXiv:2303.04226 (2023)
[9] Tanjim, M.M., Su, C., Benjamin, E., Hu, D., Hong, L., McAuley, J.:
Attentive sequential models of latent intent for next item recommendation. In: Proceedings of The Web Conference 2020, pp. 2528–2534
(2020)
[10] Wang, J., Ding, K., Hong, L., Liu, H., Caverlee, J.: Next-item recommendation with sequential hypergraphs. In: Proceedings of the 43rd
International ACM SIGIR Conference on Research and Development in
Information Retrieval, pp. 1101–1110 (2020)

40

Understanding User Intent Modeling for CRS: An SLR

[11] Guo, L., Hua, L., Jia, R., Fang, F., Zhao, B., Cui, B.: Edgedipn: a unified
deep intent prediction network deployed at the edge. Proceedings of the
VLDB Endowment 14(3), 320–328 (2020)
[12] Paul, H., Nikolaev, A.: Fake review detection on online e-commerce
platforms: a systematic literature review. Data Mining and Knowledge
Discovery 35(5), 1830–1881 (2021)
[13] Zhang, C., Fan, W., Du, N., Yu, P.S.: Mining user intentions from medical queries: A neural network based heterogeneous jointly modeling
approach. In: Proceedings of the 25th International Conference on World
Wide Web, pp. 1373–1384 (2016)
[14] Wang, Y., Wang, S., Li, Y., Dou, D.: Recognizing medical search query
intent by few-shot learning. In: Proceedings of the 45th International
ACM SIGIR Conference on Research and Development in Information
Retrieval, pp. 502–512 (2022)
[15] Liu, Z., Chen, H., Sun, F., Xie, X., Gao, J., Ding, B., Shen, Y.: Intent
preference decoupling for user representation on online recommender system. In: Proceedings of the Twenty-Ninth International Conference on
International Joint Conferences on Artificial Intelligence, pp. 2575–2582
(2021)
[16] Bhaskaran, S., Santhi, B.: An efficient personalized trust based hybrid
recommendation (tbhr) strategy for e-learning system in cloud computing. Cluster Computing 22, 1137–1149 (2019)
[17] Ding, X., Liu, T., Duan, J., Nie, J.-Y.: Mining user consumption
intention from social media using domain adaptive convolutional neural network. In: Proceedings of the AAAI Conference on Artificial
Intelligence, vol. 29 (2015)
[18] Wang, W., Hosseini, S., Awadallah, A.H., Bennett, P.N., Quirk, C.:
Context-aware intent identification in email conversations. In: Proceedings of the 42nd International ACM SIGIR Conference on Research and
Development in Information Retrieval, pp. 585–594 (2019)
[19] Penha, G., Hauff, C.: What does bert know about books, movies and
music? probing bert for conversational recommendation. In: Proceedings
of the 14th ACM Conference on Recommender Systems, pp. 388–397
(2020)
[20] Hashemi, S.H., Williams, K., El Kholy, A., Zitouni, I., Crook, P.A.:
Measuring user satisfaction on smart speaker intelligent assistants using
intent sensitive query embeddings. In: Proceedings of the 27th ACM
International Conference on Information and Knowledge Management,

Understanding User Intent Modeling for CRS: An SLR

41

pp. 1183–1192 (2018)
[21] Gharibshah, Z., Zhu, X., Hainline, A., Conway, M.: Deep learning for
user interest and response prediction in online display advertising. Data
Science and Engineering 5(1), 12–26 (2020)
[22] Bilenko, M., Richardson, M.: Predictive client-side profiles for personalized advertising. In: Proceedings of the 17th ACM SIGKDD
International Conference on Knowledge Discovery and Data Mining, pp.
413–421 (2011)
[23] Yamamoto, T., Sakai, T., Iwata, M., Yu, C., Wen, J.-R., Tanaka, K.:
The wisdom of advertisers: mining subgoals via query clustering. In:
Proceedings of the 21st ACM International Conference on Information
and Knowledge Management, pp. 505–514 (2012)
[24] Rapp, A., Curti, L., Boldi, A.: The human side of human-chatbot
interaction: A systematic literature review of ten years of research on
text-based chatbots. International Journal of Human-Computer Studies
151, 102630 (2021)
[25] Villegas, N.M., Sánchez, C., Dı́az-Cely, J., Tamura, G.: Characterizing context-aware recommender systems: A systematic literature review.
Knowledge-Based Systems 140, 173–200 (2018)
[26] Auch, M., Weber, M., Mandl, P., Wolff, C.: Similarity-based analyses on
software applications: A systematic literature review. Journal of Systems
and Software 168, 110669 (2020)
[27] Obidallah, W.J., Raahemi, B., Ruhi, U.: Clustering and association rules
for web service discovery and recommendation: a systematic literature
review. SN Computer Science 1, 1–33 (2020)
[28] Xia, C., Zhang, C., Yan, X., Chang, Y., Yu, P.S.: Zero-shot user intent
detection via capsule neural networks. arXiv preprint arXiv:1809.00385
(2018)
[29] Hu, Z., Zhang, Z., Yang, H., Chen, Q., Zuo, D.: A deep learning approach
for predicting the quality of online health expert question-answering
services. Journal of biomedical informatics 71, 241–253 (2017)
[30] Chen, L., Wang, Y., Yu, Q., Zheng, Z., Wu, J.: Wt-lda: user tagging augmented lda for web service clustering. In: Service-Oriented Computing:
11th International Conference, ICSOC 2013, Berlin, Germany, December
2-5, 2013, Proceedings 11, pp. 162–176 (2013). Springer
[31] Weismayer, C., Pezenka, I.: Identifying emerging research fields: a

42

Understanding User Intent Modeling for CRS: An SLR
longitudinal latent semantic keyword analysis. Scientometrics 113(3),
1757–1785 (2017)

[32] Hu, Y., Da, Q., Zeng, A., Yu, Y., Xu, Y.: Reinforcement learning to rank
in e-commerce search engine: Formalization, analysis, and application.
In: Proceedings of the 24th ACM SIGKDD International Conference on
Knowledge Discovery & Data Mining. KDD ’18, pp. 368–377. Association
for Computing Machinery, New York, NY, USA (2018). https://doi.org/
10.1145/3219819.3219846. https://doi.org/10.1145/3219819.3219846
[33] Gu, Y., Zhao, B., Hardtke, D., Sun, Y.: Learning global term weights
for content-based recommender systems. In: Proceedings of the 25th
International Conference on World Wide Web. WWW ’16, pp. 391–
400. International World Wide Web Conferences Steering Committee,
Republic and Canton of Geneva, CHE (2016). https://doi.org/10.1145/
2872427.2883069. https://doi.org/10.1145/2872427.2883069
[34] Yao, S., Tan, J., Chen, X., Zhang, J., Zeng, X., Yang, K.: Reprbert:
Distilling bert to an efficient representation-based relevance model for
e-commerce. In: Proceedings of the 28th ACM SIGKDD Conference on
Knowledge Discovery and Data Mining, pp. 4363–4371 (2022)
[35] Da’u, A., Salim, N.: Sentiment-aware deep recommender system with
neural attention networks. IEEE Access 7, 45472–45484 (2019). https:
//doi.org/10.1109/ACCESS.2019.2907729
[36] Ye, Q., Wang, F., Li, B.: Starrysky: A practical system to track millions
of high-precision query intents. In: Proceedings of the 25th International
Conference Companion on World Wide Web. WWW ’16 Companion,
pp. 961–966. International World Wide Web Conferences Steering Committee, Republic and Canton of Geneva, CHE (2016). https://doi.org/
10.1145/2872518.2890588. https://doi.org/10.1145/2872518.2890588
[37] Xu, H., Ding, W., Shen, W., Wang, J., Yang, Z.: Deep convolutional
recurrent model for region recommendation with spatial and temporal contexts. Ad Hoc Networks 129, 102545 (2022). https://doi.org/10.
1016/j.adhoc.2021.102545
[38] Qu, Y., Cai, H., Ren, K., Zhang, W., Yu, Y., Wen, Y., Wang, J.: Productbased neural networks for user response prediction. In: 2016 IEEE
16th International Conference on Data Mining (ICDM), pp. 1149–1154
(2016). https://doi.org/10.1109/ICDM.2016.0151
[39] Ricci, F., Rokach, L., Shapira, B.: Recommender systems: introduction
and challenges. Recommender systems handbook, 1–34 (2015)

Understanding User Intent Modeling for CRS: An SLR

43

[40] Portugal, I., Alencar, P., Cowan, D.: The use of machine learning algorithms in recommender systems: A systematic review. Expert Systems
with Applications 97, 205–227 (2018)
[41] Allamanis, M., Barr, E.T., Devanbu, P., Sutton, C.: A survey of machine
learning for big code and naturalness. ACM Computing Surveys (CSUR)
51(4), 1–37 (2018)
[42] Hill, C., Bellamy, R., Erickson, T., Burnett, M.: Trials and tribulations
of developers of intelligent systems: A field study. In: 2016 IEEE Symposium on Visual Languages and Human-Centric Computing (VL/HCC),
pp. 162–170 (2016). IEEE
[43] Kitchenham, B., Brereton, O.P., Budgen, D., Turner, M., Bailey, J.,
Linkman, S.: Systematic literature reviews in software engineering–a systematic literature review. Information and software technology 51(1),
7–15 (2009)
[44] Xiao, Y., Watson, M.: Guidance on conducting a systematic literature
review. Journal of planning education and research 39(1), 93–112 (2019)
[45] Okoli, C., Schabram, K.: A guide to conducting a systematic literature
review of information systems research (2015)
[46] Yin, R.K.: Case Study Research: Design and Methods vol. 5. sage, ???
(2009)
[47] Ye, Q., Wang, F., Li, B.: Starrysky: A practical system to track millions
of high-precision query intents. In: Proceedings of the 25th International
Conference Companion on World Wide Web, pp. 961–966 (2016)
[48] Wang, X., Huang, T., Wang, D., Yuan, Y., Liu, Z., He, X., Chua, T.-S.:
Learning intents behind interactions with knowledge graph for recommendation. In: Proceedings of the Web Conference 2021, pp. 878–887
(2021)
[49] Nguyen, H., Santos Jr, E., Zhao Jr, Q., Wang Jr, H.: Capturing user
intent for information retrieval. In: Proceedings of the Human Factors
and Ergonomics Society Annual Meeting, vol. 48, pp. 371–375 (2004).
SAGE Publications Sage CA: Los Angeles, CA
[50] Hernández-Rubio, M., Cantador, I., Bellogı́n, A.: A comparative analysis
of recommender systems based on item aspect opinions extracted from
user reviews. User Modeling and User-Adapted Interaction 29(2), 381–
441 (2019)
[51] Chen, L., Chen, G., Wang, F.: Recommender systems based on user

44

Understanding User Intent Modeling for CRS: An SLR
reviews: the state of the art. User Modeling and User-Adapted Interaction 25, 99–154 (2015)

[52] Jordan, M.I., Mitchell, T.M.: Machine learning: Trends, perspectives,
and prospects. Science 349(6245), 255–260 (2015)
[53] Telikani, A., Tahmassebi, A., Banzhaf, W., Gandomi, A.H.: Evolutionary
machine learning: A survey. ACM Computing Surveys (CSUR) 54(8),
1–35 (2021)
[54] Singh, A., Thakur, N., Sharma, A.: A review of supervised machine learning algorithms. In: 2016 3rd International Conference on Computing for
Sustainable Global Development (INDIACom), pp. 1310–1315 (2016).
Ieee
[55] Zaib, M., Zhang, W.E., Sheng, Q.Z., Mahmood, A., Zhang, Y.: Conversational question answering: A survey. Knowledge and Information
Systems 64(12), 3151–3195 (2022)
[56] von Rueden, L., Mayer, S., Sifa, R., Bauckhage, C., Garcke, J.: Combining machine learning and simulation to a hybrid modelling approach:
Current and future directions. In: Advances in Intelligent Data Analysis XVIII: 18th International Symposium on Intelligent Data Analysis,
IDA 2020, Konstanz, Germany, April 27–29, 2020, Proceedings 18, pp.
548–560 (2020). Springer
[57] Yuan, S., Zhang, Y., Tang, J., Hall, W., Cabotà, J.B.: Expert finding in
community question answering: a review. Artificial Intelligence Review
53, 843–874 (2020)
[58] Farshidi, S., Jansen, S., van der Werf, J.M.: Capturing software architecture knowledge for pattern-driven design. Journal of Systems and
Software 169, 110714 (2020)
[59] Farshidi, S.: Multi-criteria decision-making in software production. PhD
thesis, Utrecht University (2020)
[60] Jansen, S.: Applied multi-case research in a mixed-method research
project: Customer configuration updating improvement. In: Information Systems Research Methods, Epistemology, and Applications, pp.
120–139. IGI Global, ??? (2009)
[61] Johnson, R.B., Onwuegbuzie, A.J.: Mixed methods research: A research
paradigm whose time has come. Educational researcher 33(7), 14–26
(2004)
[62] Yin, R.K.: Case Study Research and Applications: Design and Methods.

Understanding User Intent Modeling for CRS: An SLR

45

Sage publications, ??? (2017)
[63] Kilgarriff, A., Baisa, V., Bušta, J., Jakubı́ček, M., Kovář, V., Michelfeit,
J., Rychlỳ, P., Suchomel, V.: The sketch engine: ten years on. Lexicography 1(1), 7–36 (2014)
[64] Ni, J., Huang, Z., Cheng, J., Gao, S.: An effective recommendation model
based on deep representation learning. Information Sciences 542, 324–
342 (2021)
[65] Wang, W., Yin, H., Huang, Z., Wang, Q., Du, X., Nguyen, Q.V.H.:
Streaming ranking based recommender systems. In: The 41st International ACM SIGIR Conference on Research & Development in
Information Retrieval, pp. 525–534 (2018)
[66] Qu, C., Yang, L., Croft, W.B., Zhang, Y., Trippas, J.R., Qiu, M.: User
intent prediction in information-seeking conversations. In: Proceedings
of the 2019 Conference on Human Information Interaction and Retrieval,
pp. 25–33 (2019)
[67] Zhang, H., Xu, H., Lin, T.-E., Lyu, R.: Discovering new intents with deep
aligned clustering. In: Proceedings of the AAAI Conference on Artificial
Intelligence, vol. 35, pp. 14365–14373 (2021)
[68] Agarwal, N., Sikka, G., Awasthi, L.K.: Evaluation of web service clustering using dirichlet multinomial mixture model based approach for dimensionality reduction in service representation. Information Processing &
Management 57(4), 102238 (2020)
[69] Zhang, Y., Yin, H., Huang, Z., Du, X., Yang, G., Lian, D.: Discrete
deep learning for fast content-aware recommendation. In: Proceedings of
the Eleventh ACM International Conference on Web Search and Data
Mining, pp. 717–726 (2018)
[70] Yu, B., Zhang, R., Chen, W., Fang, J.: Graph neural network based
model for multi-behavior session-based recommendation. GeoInformatica 26(2), 429–447 (2022)
[71] Lin, H., Liu, G., Li, F., Zuo, Y.: Where to go? predicting next location
in iot environment. Frontiers of Computer Science 15, 1–13 (2021)
[72] Farshidi, S., Rezaee, K.: Understanding User Intent: A Systematic Literature Review of Modeling Techniques. Mendeley Data (2023). http:
//dx.doi.org/10.17632/nw79y7mcvd.1
[73] Latifi, S., Mauro, N., Jannach, D.: Session-aware recommendation: A

46

Understanding User Intent Modeling for CRS: An SLR
surprising quest for the state-of-the-art. Information Sciences 573, 291–
315 (2021)

[74] Park, C., Kim, D., Yang, M.-C., Lee, J.-T., Yu, H.: Click-aware purchase prediction with push at the top. Information Sciences 521, 350–364
(2020)
[75] Ludewig, M., Jannach, D.: Evaluation of session-based recommendation
algorithms. User Modeling and User-Adapted Interaction 28, 331–390
(2018)
[76] Zhou, K., Zhao, W.X., Wang, H., Wang, S., Zhang, F., Wang, Z., Wen,
J.-R.: Leveraging historical interaction data for improving conversational
recommender system. In: Proceedings of the 29th ACM International
Conference on Information & Knowledge Management, pp. 2349–2352
(2020)
[77] White, R.W., Chu, W., Hassan, A., He, X., Song, Y., Wang, H.: Enhancing personalized search by mining and modeling task behavior. In:
Proceedings of the 22nd International Conference on World Wide Web,
pp. 1411–1420 (2013)
[78] Zou, J., Kanoulas, E., Ren, P., Ren, Z., Sun, A., Long, C.: Improving
conversational recommender systems via transformer-based sequential
modelling. In: Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval, pp.
2319–2324 (2022)
[79] Zhou, X., Qin, D., Chen, L., Zhang, Y.: Real-time context-aware social
media recommendation. The VLDB Journal 28, 197–219 (2019)
[80] Musto, C., Narducci, F., Lops, P., de Gemmis, M., Semeraro, G.: Linked
open data-based explanations for transparent recommender systems.
International Journal of Human-Computer Studies 121, 93–107 (2019)
[81] Mandayam Comar, P., Sengamedu, S.H.: Intent based relevance estimation from click logs. In: Proceedings of the 2017 ACM on Conference on
Information and Knowledge Management, pp. 59–66 (2017)
[82] Ding, H., Liu, Q., Hu, G.: Tdtmf: A recommendation model based on
user temporal interest drift and latent review topic evolution with regularization factor. Information Processing & Management 59(5), 103037
(2022)
[83] Pradhan, T., Kumar, P., Pal, S.: Claver: An integrated framework of
convolutional layer, bidirectional lstm with attention mechanism based
scholarly venue recommendation. Information Sciences 559, 212–235

Understanding User Intent Modeling for CRS: An SLR

47

(2021)
[84] Yu, S., Liu, J., Yang, Z., Chen, Z., Jiang, H., Tolba, A., Xia, F.: Pave:
Personalized academic venue recommendation exploiting co-publication
networks. Journal of Network and Computer Applications 104, 38–47
(2018)
[85] Schlaefer, N., Chu-Carroll, J., Nyberg, E., Fan, J., Zadrozny, W.,
Ferrucci, D.: Statistical source expansion for question answering. In: Proceedings of the 20th ACM International Conference on Information and
Knowledge Management, pp. 345–354 (2011)
[86] Kim, D., Park, C., Oh, J., Yu, H.: Deep hybrid recommender systems via
exploiting document context and statistics of items. Information Sciences
417, 72–87 (2017)
[87] Zhang, H., Zhong, G.: Improving short text classification by learning vector representations of both words and hidden topics. Knowledge-Based
Systems 102, 76–86 (2016)
[88] Xu, Z., Chen, L., Chen, G.: Topic based context-aware travel recommendation method exploiting geotagged photos. Neurocomputing 155,
99–107 (2015)
[89] Tang, J., Yao, L., Zhang, D., Zhang, J.: A combination approach to web
user profiling. ACM Transactions on Knowledge Discovery from Data
(TKDD) 5(1), 1–44 (2010)
[90] Li, L., Deng, H., Dong, A., Chang, Y., Zha, H.: Identifying and labeling
search tasks via query-based hawkes processes. In: Proceedings of the
20th ACM SIGKDD International Conference on Knowledge Discovery
and Data Mining, pp. 731–740 (2014)
[91] Binkley, D., Lawrie, D., Morrell, C.: The need for software specific natural language techniques. Empirical Software Engineering 23, 2398–2425
(2018)
[92] Izadi, M., Akbari, K., Heydarnoori, A.: Predicting the objective and
priority of issue reports in software repositories. Empirical Software
Engineering 27(2), 50 (2022)
[93] Venkateswara Rao, P., Kumar, A.S.: The societal communication of the
q&a community on topic modeling. The Journal of Supercomputing
78(1), 1117–1143 (2022)
[94] Yu, J., Zhu, T.: Combining long-term and short-term user interest for
personalized hashtag recommendation. Frontiers of Computer Science 9,

48

Understanding User Intent Modeling for CRS: An SLR
608–622 (2015)

[95] Yadav, N., Pal, S., Singh, A.K., Singh, K.: Clus-dr: Cluster-based pretrained model for diverse recommendation generation. Journal of King
Saud University-Computer and Information Sciences 34(8), 6385–6399
(2022)
[96] Xu, H., Ding, W., Shen, W., Wang, J., Yang, Z.: Deep convolutional
recurrent model for region recommendation with spatial and temporal
contexts. Ad Hoc Networks 129, 102545 (2022)
[97] Gozuacik, N., Sakar, C.O., Ozcan, S.: Technological forecasting based on
estimation of word embedding matrix using lstm networks. Technological
Forecasting and Social Change 191, 122520 (2023)
[98] Yengikand, A.K., Meghdadi, M., Ahmadian, S.: Dhsirs: a novel deep
hybrid side information-based recommender system. Multimedia Tools
and Applications, 1–27 (2023)
[99] Chen, T., Wong, R.C.-W.: Handling information loss of graph neural
networks for session-based recommendation. In: Proceedings of the 26th
ACM SIGKDD International Conference on Knowledge Discovery &
Data Mining, pp. 1172–1180 (2020)
[100] Elfaik, H., et al.: Leveraging feature-level fusion representations and
attentional bidirectional rnn-cnn deep models for arabic affect analysis
on twitter. Journal of King Saud University-Computer and Information
Sciences 35(1), 462–482 (2023)
[101] Ittoo, A., van den Bosch, A., et al.: Text analytics in industry: Challenges, desiderata and trends. Computers in Industry 78, 96–107 (2016)
[102] de Barcelos Silva, A., Gomes, M.M., da Costa, C.A., da Rosa Righi, R.,
Barbosa, J.L.V., Pessin, G., De Doncker, G., Federizzi, G.: Intelligent
personal assistants: A systematic literature review. Expert Systems with
Applications 147, 113193 (2020)
[103] Pan, R., Bagherzadeh, M., Ghaleb, T.A., Briand, L.: Test case selection
and prioritization using machine learning: a systematic literature review.
Empirical Software Engineering 27(2), 29 (2022)
[104] Pu, P., Chen, L., Hu, R.: Evaluating recommender systems from the
user’s perspective: survey of the state of the art. User Modeling and
User-Adapted Interaction 22(4), 317–355 (2012)
[105] Salle, A., Malmasi, S., Rokhlenko, O., Agichtein, E.: Cosearcher: studying the effectiveness of conversational search refinement and clarification

Understanding User Intent Modeling for CRS: An SLR

49

through user simulation. Information Retrieval Journal 25(2), 209–238
(2022)
[106] Baykan, E., Henzinger, M., Marian, L., Weber, I.: A comprehensive
study of features and algorithms for url-based topic classification. ACM
Transactions on the Web (TWEB) 5(3), 1–29 (2011)
[107] Wang, X., Li, Q., Yu, D., Cui, P., Wang, Z., Xu, G.: Causal disentanglement for semantics-aware intent learning in recommendation. IEEE
Transactions on Knowledge and Data Engineering (2022)
[108] Phan, X.-H., Nguyen, C.-T., Le, D.-T., Nguyen, L.-M., Horiguchi, S.,
Ha, Q.-T.: A hidden topic-based framework toward building applications
with short web documents. IEEE Transactions on Knowledge and Data
Engineering 23(7), 961–976 (2010)
[109] Yu, Z., Lian, J., Mahmoody, A., Liu, G., Xie, X.: Adaptive user modeling
with long and short-term preferences for personalized recommendation.
In: IJCAI, pp. 4213–4219 (2019)
[110] Ashkan, A., Clarke, C.L., Agichtein, E., Guo, Q.: Classifying and characterizing query intent. In: Advances in Information Retrieval: 31th
European Conference on IR Research, ECIR 2009, Toulouse, France,
April 6-9, 2009. Proceedings 31, pp. 578–586 (2009). Springer
[111] Xu, P., Sugano, Y., Bulling, A.: Spatio-temporal modeling and prediction
of visual attention in graphical user interfaces. In: Proceedings of the
2016 CHI Conference on Human Factors in Computing Systems, pp.
3299–3310 (2016)
[112] Liu, P., Liao, D., Wang, J., Wu, Y., Li, G., Xia, S.-T., Xu, J.: Multitask ranking with user behaviors for text-video search. In: Companion
Proceedings of the Web Conference 2022, pp. 126–130 (2022)
[113] Wu, L., Quan, C., Li, C., Wang, Q., Zheng, B., Luo, X.: A contextaware user-item representation learning for item recommendation. ACM
Transactions on Information Systems (TOIS) 37(2), 1–29 (2019)
[114] Mao, M., Lu, J., Han, J., Zhang, G.: Multiobjective e-commerce recommendations based on hypergraph ranking. Information Sciences 471,
269–287 (2019)
[115] Ni, X., Lu, Y., Quan, X., Wenyin, L., Hua, B.: User interest modeling and
its application for question recommendation in user-interactive question
answering systems. Information Processing & Management 48(2), 218–
233 (2012)

50

Understanding User Intent Modeling for CRS: An SLR

[116] Liu, P., Zhang, L., Gulla, J.A.: Dynamic attention-based explainable
recommendation with textual and visual fusion. Information Processing
& Management 57(6), 102099 (2020)
[117] Kaptein, R., Kamps, J.: Exploiting the category structure of wikipedia
for entity ranking. Artificial Intelligence 194, 111–129 (2013)
[118] Cai, Y., Lau, R.Y., Liao, S.S., Li, C., Leung, H.-F., Ma, L.C.: Object
typicality for effective web of things recommendations. Decision support
systems 63, 52–63 (2014)
[119] Colace, F., De Santo, M., Greco, L., Moscato, V., Picariello, A.: A collaborative user-centered framework for recommending items in online
social networks. Computers in Human Behavior 51, 694–704 (2015)
[120] Yao, Y., Zhao, W.X., Wang, Y., Tong, H., Xu, F., Lu, J.: Version-aware
rating prediction for mobile app recommendation. ACM Transactions on
Information Systems (TOIS) 35(4), 1–33 (2017)
[121] Teevan, J., Dumais, S.T., Liebling, D.J.: To personalize or not to personalize: modeling queries with variation in user intent. In: Proceedings
of the 31st Annual International ACM SIGIR Conference on Research
and Development in Information Retrieval, pp. 163–170 (2008)
[122] Wang, H.-C., Jhou, H.-T., Tsai, Y.-S.: Adapting topic map and social
influence to the personalized hybrid recommender system. Information
Sciences 575, 762–778 (2021)
[123] Papadimitriou, A., Symeonidis, P., Manolopoulos, Y.: A generalized taxonomy of explanations styles for traditional and social recommender
systems. Data Mining and Knowledge Discovery 24, 555–583 (2012)
[124] Fan, L., Li, Q., Liu, B., Wu, X.-M., Zhang, X., Lv, F., Lin, G., Li, S., Jin,
T., Yang, K.: Modeling user behavior with graph convolution for personalized product search. In: Proceedings of the ACM Web Conference
2022, pp. 203–212 (2022)
[125] Liu, J., Dou, Z., Zhu, Q., Wen, J.-R.: A category-aware multi-interest
model for personalized product search. In: Proceedings of the ACM Web
Conference 2022, pp. 360–368 (2022)
[126] ISO: Iec/ieee systems and software engineering: Architecture description.
ISO/IEC/IEEE 42010: 2011 (E)(Revision of ISO/IEC 42010: 2007 and
IEEE Std 1471-2000) (2011)
[127] Garg, R., Kumar, R., Garg, S.: Madm-based parametric selection and
ranking of e-learning websites using fuzzy copras. IEEE Transactions on

Understanding User Intent Modeling for CRS: An SLR

51

Education 62(1), 11–18 (2018)
[128] Xu, L., Brinkkemper, S.: Concepts of product software. European
Journal of Information Systems 16(5), 531–541 (2007)
[129] Fitzgerald, B., Stol, K.-J.: Continuous software engineering and beyond:
trends and challenges. In: Proceedings of the 1st International Workshop
on Rapid Continuous Software Engineering, pp. 1–9 (2014)
[130] Rus, I., Halling, M., Biffl, S.: Supporting decision-making in software
engineering with process simulation and empirical studies. International
Journal of Software Engineering and Knowledge Engineering 13(05),
531–545 (2003)
[131] Fitzgerald, D.R., Mohammed, S., Kremer, G.O.: Differences in the way
we decide: The effect of decision style diversity on process conflict
in design teams. Personality and Individual Differences 104, 339–344
(2017)
[132] Kaufmann, L., Kreft, S., Ehrgott, M., Reimann, F.: Rationality in
supplier selection decisions: The effect of the buyer’s national task environment. Journal of Purchasing and Supply Management 18(2), 76–91
(2012)
[133] Garg, R.: Mcdm-based parametric selection of cloud deployment models
for an academic organization. IEEE Transactions on Cloud Computing
(2020)
[134] Garg, R., Sharma, R., Sharma, K.: Mcdm based evaluation and ranking
of commercial off-the-shelf using fuzzy based matrix method. Decision
Science Letters 6(2), 117–136 (2017)
[135] Sandhya, Garg, R., Kumar, R.: Computational madm evaluation and
ranking of cloud service providers using distance-based approach. International Journal of Information and Decision Sciences 10(3), 222–234
(2018)
[136] Garg, R.: Parametric selection of software reliability growth models
using multi-criteria decision-making approach. International Journal of
Reliability and Safety 13(4), 291–309 (2019)
[137] Doumpos, M., Grigoroudis, E.: Multicriteria decision aid and artificial
intelligence. Whiley (UK) (2013)
[138] Majumder, M.: Multi criteria decision making. In: Impact of Urbanization on Water Shortage in Face of Climatic Aberrations, pp. 35–47.
Springer, ??? (2015)

52

Understanding User Intent Modeling for CRS: An SLR

[139] Caprara, A., Toth, P., Fischetti, M.: Algorithms for the set covering
problem. Annals of Operations Research 98(1-4), 353–371 (2000)
[140] Manzoor, A., Jannach, D.: Towards retrieval-based conversational recommendation. Information Systems 109, 102083 (2022). https://doi.
org/10.1016/j.is.2022.102083
[141] Tanjim, M.M., Su, C., Benjamin, E., Hu, D., Hong, L., McAuley,
J.: Attentive sequential models of latent intent for next item
recommendation. In: Proceedings of The Web Conference 2020.
WWW ’20, pp. 2528–2534. Association for Computing Machinery,
New York, NY, USA (2020). https://doi.org/10.1145/3366423.3380002.
https://doi.org/10.1145/3366423.3380002
[142] Haefliger, S., Von Krogh, G., Spaeth, S.: Code reuse in open source
software. Management science 54(1), 180–193 (2008)
[143] Amershi, S., Begel, A., Bird, C., DeLine, R., Gall, H., Kamar, E.,
Nagappan, N., Nushi, B., Zimmermann, T.: Software engineering for
machine learning: A case study. In: 2019 IEEE/ACM 41st International
Conference on Software Engineering: Software Engineering in Practice
(ICSE-SEIP), pp. 291–300 (2019). IEEE
[144] Kuwajima, H., Yasuoka, H., Nakae, T.: Engineering problems in machine
learning systems. Machine Learning 109(5), 1103–1126 (2020)
[145] Chen, Y., Liu, Z., Li, J., McAuley, J., Xiong, C.: Intent contrastive learning for sequential recommendation. In: Proceedings of the ACM Web
Conference 2022, pp. 2172–2182 (2022)
[146] Garcia, K., Berton, L.: Topic detection and sentiment analysis in twitter content related to covid-19 from brazil and the usa. Applied soft
computing 101, 107057 (2021)
[147] Hashemi, H., Zamani, H., Croft, W.B.: Guided transformer: Leveraging
multiple external sources for representation learning in conversational
search. In: Proceedings of the 43rd International Acm Sigir Conference
on Research and Development in Information Retrieval, pp. 1131–1140
(2020)
[148] Carvallo, A., Parra, D., Lobel, H., Soto, A.: Automatic document screening of medical literature using word and text embeddings in an active
learning setting. Scientometrics 125, 3047–3084 (2020)
[149] Gao, C., Lam, W.: Search clarification selection via query-intentclarification graph attention. In: European Conference on Information
Retrieval, pp. 230–243 (2022). Springer

Understanding User Intent Modeling for CRS: An SLR

53

[150] Wu, Z., Liang, J., Zhang, Z., Lei, J.: Exploration of text matching methods in chinese disease q&a systems: A method using ensemble based on
bert and boosted tree models. Journal of biomedical informatics 115,
103683 (2021)
[151] Devlin, J., Chang, M.-W., Lee, K., Toutanova, K.: Bert: Pre-training
of deep bidirectional transformers for language understanding. arXiv
preprint arXiv:1810.04805 (2018)
[152] Sarker, I.H.: Machine learning: Algorithms, real-world applications and
research directions. SN computer science 2(3), 160 (2021)
[153] Blei, D.M., Ng, A.Y., Jordan, M.I.: Latent dirichlet allocation. Journal
of machine Learning research 3(Jan), 993–1022 (2003)
[154] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M.,
Zhou, Y., Li, W., Liu, P.J.: Exploring the limits of transfer learning
with a unified text-to-text transformer. The Journal of Machine Learning
Research 21(1), 5485–5551 (2020)
[155] Ribeiro, M.T., Singh, S., Guestrin, C.: ” why should i trust you?”
explaining the predictions of any classifier. In: Proceedings of the 22nd
ACM SIGKDD International Conference on Knowledge Discovery and
Data Mining, pp. 1135–1144 (2016)
[156] Pujol, D., McKenna, R., Kuppam, S., Hay, M., Machanavajjhala, A.,
Miklau, G.: Fair decision making using privacy-protected data. In:
Proceedings of the 2020 Conference on Fairness, Accountability, and
Transparency, pp. 189–199 (2020)
[157] Bagdasaryan, E., Poursaeed, O., Shmatikov, V.: Differential privacy has
disparate impact on model accuracy. Advances in neural information
processing systems 32 (2019)
[158] Zhou, X., Jin, Y., Zhang, H., Li, S., Huang, X.: A map of threats to
validity of systematic literature reviews in software engineering. In: 2016
23rd Asia-Pacific Software Engineering Conference (APSEC), pp. 153–
160 (2016). IEEE
[159] Zhang, H., Babar, M.A., Tell, P.: Identifying relevant studies in software engineering. Information and Software Technology 53(6), 625–637
(2011)
[160] Keyvan, K., Huang, J.X.: How to approach ambiguous queries in conversational search: A survey of techniques, approaches, tools, and challenges.
ACM Computing Surveys 55(6), 1–40 (2022)

54

Understanding User Intent Modeling for CRS: An SLR

[161] Iovine, A., Narducci, F., Musto, C., de Gemmis, M., Semeraro, G.: Virtual customer assistants in finance: From state of the art and practices
to design guidelines. Computer Science Review 47, 100534 (2023)
[162] Saka, A.B., Oyedele, L.O., Akanbi, L.A., Ganiyu, S.A., Chan, D.W.,
Bello, S.A.: Conversational artificial intelligence in the aec industry:
A review of present status, challenges and opportunities. Advanced
Engineering Informatics 55, 101869 (2023)
[163] Liu, T., Wu, Q., Chang, L., Gu, T.: A review of deep learning-based
recommender system in e-learning environments. Artificial Intelligence
Review 55(8), 5953–5980 (2022)
[164] Tamine-Lechani, L., Boughanem, M., Daoud, M.: Evaluation of contextual information retrieval effectiveness: overview of issues and research.
Knowledge and Information Systems 24, 1–34 (2010)
[165] Jiang, D., Pei, J., Li, H.: Mining search and browse logs for web search:
A survey. ACM Transactions on Intelligent Systems and Technology
(TIST) 4(4), 1–37 (2013)
[166] Jindal, V., Bawa, S., Batra, S.: A review of ranking approaches for
semantic search on web. Information Processing & Management 50(2),
416–425 (2014)

Understanding User Intent Modeling for CRS: An SLR

55

A Models
Table 9 Model definitions
Name

Definition

ALS (Alternating Least Squares) a type of matrix factorization algorithm that alternates between solving for user and item factors to minimize the squared error between observed and predicted ratings.
BERT (Bidirectional Encoder Representations from Transformers) a deep learning model used for natural language processing tasks, such as text classification and question answering
BiLSTM (Bidirectional Long Short-Term Memory) a type of recurrent neural network used for modeling sequential data, where information flows in both forward and backward directions.
BM25 (Best Match 25) a ranking function used in information retrieval to rank documents based on their relevance to a query
BPR (Bayesian Personalized Ranking) a ranking algorithm used in recommender systems that is based on bayesian inference and models the preferences of individual users.
CDL (Collaborative Deep Learning) a technique that combines deep learning models with collaborative filtering algorithms for recommendation systems.
CF (Collaborative Filtering) a technique used in recommender systems to make predictions by leveraging the similarity between users or items
Cosine similarity a measure of similarity between two vectors that calculates the cosine of the angle between them.
CRF (Conditional Random Fields) a probabilistic model used for structured prediction tasks, such as named entity recognition and part-of-speech tagging.
CTR (Collaborative Topic Regression) a probabilistic model that combines topic modeling and collaborative filtering
DeepCoNN (Deep Cooperative Neural Networks) a type of neural network architecture that jointly learns the user and item embeddings to model user behavior for personalized recommendations.
DNN (Deep Neural Network) a type of artificial neural network with multiple hidden layers, used for learning representations of complex data such as images, audio, and natural language.
EM (Expectation-Maximization) an iterative algorithm used to find maximum likelihood or maximum a posteriori estimates of parameters in statistical models
FM (Factorization Machine) a type of machine learning model used for predicting interactions between pairs of variables, often used in recommendation systems.
GBDT (Gradient Boosting Decision Trees) a machine learning algorithm that combines multiple decision trees in an ensemble, used for supervised learning tasks such as classification and regression.
Gibbs sampling a technique used for generating samples from complex probability distributions, often used in bayesian inference.
GRU (Gated Recurrent Units) a type of recurrent neural network used for modeling sequential data, particularly for applications such as natural language processing and speech recognition.
GRU4Rec (Gated Recurrent Unit for Recommender Systems) a type of neural network architecture that uses gated recurrent units to model user behavior for personalized recommendations.
HMM (Hidden Markov Model) a probabilistic model used to model sequential data, where the underlying states of the system are hidden but can be inferred from observed outputs.
k-means (k-means clustering) an unsupervised machine learning algorithm used to group similar data points into k clusters
KL (Kullback–Leibler Divergence) a measure of how different two probability distributions are from each other
KNN (K-Nearest Neighbors Algorithm) a supervised machine learning algorithm used for classification and regression by finding the k closest data points to the new data point and making predictions based on their labels
LambdaMART a ranking algorithm used in information retrieval, based on a gradient boosting framework that combines multiple decision trees.
LDA (Latent Dirichlet allocation) a generative statistical model used for topic modeling
LR (Logistic Regression) a supervised machine learning algorithm used for binary classification
LSA (Latent Semantic Analysis) a technique used to uncover the underlying topics in a corpus by decomposing a term-document matrix using singular value decomposition
LSI (Latent Semantic Indexing) a technique used for dimensionality reduction in text data, based on matrix factorization methods such as svd.
LSTM (Long Short-Term Memory) a type of recurrent neural network that can handle long-term dependencies in sequence data
Markov Chain a mathematical model used to describe a sequence of events where the probability of each event depends only on the state attained in the previous event
MF (Matrix factorization) a technique used in recommender systems to decompose a user-item matrix into two lower-rank matrices, which can then be used to make recommendations
MLE (Maximum Likelihood Estimation) a statistical method that estimates the parameters of a probability distribution by maximizing the likelihood of the observed data.
MLP (Multi-Layer Perceptron) a type of neural network consisting of multiple layers of perceptrons, used for supervised learning tasks such as classification and regression.
MMR (Maximal Marginal Relevance) a ranking algorithm used in information retrieval, that maximizes the relevance of a set of documents while minimizing redundancy.
Naive Bayes a probabilistic algorithm used for classification based on bayes' theorem and the assumption of independence between features
NCF (Neural Collaborative Filtering) a type of collaborative filtering algorithm that uses neural networks to learn the user and item representations to predict the user-item interaction.
NER (Named Entity Recognition) a task in natural language processing that involves identifying and classifying named entities in text, such as people, organizations, and locations.
NMF (Non-negative Matrix Factorization) a matrix factorization technique used for dimensionality reduction and feature extraction
PageRank a ranking algorithm used in web search engines, that assigns scores to web pages based on the structure of the web graph.
PCA (Principal Component Analysis) a dimensionality reduction technique that finds the principal components of a dataset by decomposing the covariance matrix of the data.
PLSA (Probabilistic Latent Semantic Analysis) a statistical technique used to uncover the latent topics within a set of documents
PMF (Probabilistic Matrix Factorization) a probabilistic model used in recommender systems to learn low-dimensional representations of users and items
PMI (Pointwise Mutual Information) a measure of the association between two terms in a corpus, often used in natural language processing tasks such as text classification and information retrieval.
Random Forest a type of ensemble learning method that combines multiple decision trees to make predictions.
RankNet a type of neural network architecture that learns to rank items by minimizing the pairwise ranking loss between items.
RBM (Restricted Boltzmann Machines) a type of unsupervised learning algorithm that models probability distributions over inputs by minimizing the free energy of the system.
RGM (Random Group Model) a type of matrix factorization algorithm that models the interactions between users and items using random group effects.
Rocchio a type of content-based filtering algorithm that calculates the similarity between a target item and user's previously rated items using a vector space model and updates the user's profile based on the similarity scores.
RW (Random Walk) a graph traversal algorithm used in network analysis and ranking algorithms such as pagerank.
SDAE (Stacked Denoising Autoencoder) a type of autoencoder neural network that learns to remove noise from input data by encoding and decoding it through multiple hidden layers.
Self-attention (Intra Attention) a mechanism used in neural networks, particularly in natural language processing tasks, that allows the model to selectively focus on different parts of the input sequence.
SGD (Stochastic Gradient Descent) a popular optimization algorithm used for training machine learning models, particularly neural networks.
Singular Value Decomposition (SVD) a technique used for matrix factorization and dimensionality reduction. SVD can be used for tasks such as collaborative filtering, where it helps identify latent features or factors in a dataset.
Skip-gram a variant of word2vec that focuses on predicting the context words given a target word
SVD++ (Singular Value Decomposition Plus Plus) an extension of svd used in collaborative filtering algorithms for recommendation systems, that incorporates user-item interactions and user/item biases.
SVM (Support Vector Machines) a supervised machine learning algorithm that classifies data by finding the best hyperplane to separate two classes
SVR (Support Vector Regression) a type of regression algorithm that uses support vector machines to minimize the margin error between predicted and actual values.
TF-IDF (Term Frequency-Inverse Document Frequency) a numerical statistic that reflects how important a word is in a document or corpus
VSM (Vector Space Model) a mathematical model used in information retrieval to represent documents as vectors in a high-dimensional space
Word2vec a deep learning model used to learn word embeddings that capture the meaning of words based on their context in a corpus

B Categories
Table 10 Categories
Name

Definition
Classification

classification is a supervised machine learning technique that involves predicting a categorical target variable based on input features. the algorithm learns from labeled examples during training and creates a model that
can classify new, unseen data.

Clustering clustering is a machine learning technique that groups similar objects together into clusters based on their similarities and differences, without the need for predefined labels or output.
Collaborative Filtering collaborative filtering is a technique used in recommender systems that predicts the preferences and interests of a user by analyzing the behavior and choices of a large number of similar users.
Convolutional Neural Network (CNN)
Deep Belief Networks (DBN)
Graph Neural Networks (GNN)
Measurement model

a convolutional neural network (cnn) is a type of deep neural network that is widely used for image and video recognition tasks. it uses a series of convolutional layers to automatically learn and extract features from input
data, followed by fully connected layers for classification or regression. cnns are trained using backpropagation to minimize the error between predicted and actual output.
deep belief networks (dbn) are deep learning neural networks that consist of multiple layers of hidden units and are trained in an unsupervised manner using a generative model. they have been used for tasks involving
complex, hierarchical data structures such as speech recognition, image recognition, and natural language processing.
graph neural networks (gnns) are deep learning models designed to operate on data with a graph structure, which iteratively pass information between connected nodes in a graph to learn representations that can be used
for various tasks on the graph.
a measurement model is a statistical model used to assess the relationship between observed variables and underlying constructs or latent variables, often used in fields such as psychology, sociology, and marketing
research to quantify the relationship between observable data and the underlying constructs they represent.

Optimization

optimization models are mathematical or computational models that are used to find the best solution to a problem while taking into account constraints and objectives. they involve identifying the optimal value of one or
more variables within a given set of constraints.

Probabilistic

a probabilistic model is a mathematical framework for representing uncertainty and quantifying the probability of different outcomes or events based on available information and assumptions about the underlying
mechanisms.

Recurrent Neural Networks (RNN)

recurrent neural networks (rnns) are a type of artificial neural network designed to process sequential data by maintaining an internal state or "memory" of previous inputs, enabling the network to make predictions about
future inputs. rnns have variants such as lstm, gru, and bi-rnns, and are used in applications such as language translation, speech recognition, and image captioning.

Reinforcement Learning (RL)

reinforcement learning is a type of machine learning where an agent learns to make decisions by interacting with an environment and receiving feedback in the form of rewards or penalties, with the goal of maximizing the
total reward over time.

Self-Supervised Learning Model self-supervised learning is a type of machine learning in which a model learns to represent data by predicting certain attributes or properties of the data without explicit supervision, using unlabeled data.
Semi-Supervised Learning

semi-supervised learning is a type of machine learning that uses both labeled and unlabeled data to train algorithms for making predictions or classifications. it is useful when labeled data is limited or costly to obtain, and
is commonly used in applications such as speech recognition, image classification, and natural language processing.

Statistical Method statistical methods are a set of tools, techniques, and procedures used to collect, analyze, interpret, and present data to make conclusions or inferences about a population or sample.
Supervised Learning supervised learning is a machine learning technique in which an algorithm learns to predict output values based on input data and their corresponding labeled examples.
Unsupervised Learning unsupervised learning is a type of machine learning where the algorithm learns patterns and relationships in unlabeled data without specific guidance or supervision.
Vector space model a vector space model is a mathematical model used to represent text documents as vectors of numerical values, where each dimension corresponds to a particular term or word in the document collection.

56

Understanding User Intent Modeling for CRS: An SLR

C Features
Table 11 Features
Name

Definition

Activity-Based Recommendations

refers to the features that capture the activities or behavior patterns of users. for example, in recommender systems, activity-based features may include the number of times a user has viewed, rated, purchased, or liked a particular item or
category. these features can provide valuable insights into user preferences and can be used to make personalized recommendations.

Algorithm Flexibility (Algorithm-Agnostic) refers to the ability of a model or system to work with different types of algorithms or methods without being specific to any one of them.
Anomaly Detection anomaly detection is examining specific data points and detecting rare occurrences that seem suspicious because they're different from the established pattern of behaviors.
Attentive refers to the ability of the model to focus on certain parts of the input that are most relevant for the task at hand. this is typically achieved through mechanisms such as attention networks or attention heads in neural networks.
Behavior-Based Recommendations refers to the approach of capturing user behavior and patterns in order to make predictions or recommendations.
Click-Through Recommendations refers to the process of using user clicks on search results to improve the relevance and ranking of search results for future queries.
Co-Occurrence Analysis refers to the identification and analysis of the frequency of occurrence of two or more items or concepts together in a given context.
Constraint-Based refers to incorporating domain-specific constraints into the learning algorithm to improve its performance.
Content-Based Recommendations refers to a type of recommendation system that uses the characteristics or features of an item to recommend similar items to users.
Context-Aware Recommendations takes into account the context or environment in which a particular task is performed, to improve the accuracy of the model's predictions or recommendations.
Contextual Graph it is a directed acyclic graph with one input and one output that provides a uniform r.epresentation of elements of reasoning and of contexts in problem solving.
Data Dimensionality (Multidimensional) refers to the ability of the algorithm to handle data with multiple input features or dimensions.
Data Modality (Multimodal)

refers to a type of data that includes multiple types of information or input modalities. this means that the data being used for the model contains features that come from different sources such as text, audio, images, video, or other types of sensory
data. multimodal machine learning models are designed to handle and learn from this diverse set of features, and to combine them in a meaningful way to achieve better performance than models that use only a single modality of data.

Density-Based refers to machine learning techniques that identify dense regions of data points in a dataset, which are then used to cluster similar data points together.
Dimensionality Reduction dimensionality reduction, or dimension reduction, is the transformation of data from a high-dimensional space into a low-dimensional space so that the low-dimensional representation retains some meaningful properties of the original data, ideally
close
to its intrinsic
dimension.
in
machine
learning, the
end-to-end approach refers to a modeling strategy that involves training a single model to perform a complex task directly from raw data inputs to desired outputs, without relying on intermediate stages or hand-crafted
End-To-End Approach
features. this approach is in contrast to the traditional pipeline approach, where different modules or stages are designed and trained independently to perform specific sub-tasks and then combined to form the final system.
Entity Variability (Multi-Type Entities)
Feature Selection

refer to situations where there are multiple types of entities in the dataset, such as people, organizations, and locations. this feature is relevant for tasks such as named entity recognition and entity disambiguation, where the model must identify and
differentiate between various types of entities.
feature selection refers to the process of selecting a subset of relevant features (or variables) from a larger set of features in a dataset to use as input for a machine learning model. the goal of feature selection is to improve model performance,
reduce computational complexity, and increase interpretability by eliminating irrelevant, redundant, or noisy features

Filtering refers to the process of selecting or excluding certain data points based on a set of criteria or conditions.
Frequency-Based refers to a type of approach in machine learning where the frequency of occurrence of certain items or events is used to derive patterns, associations, or predictions.
Generative Model "generative models" are a type of machine learning model that can be used to generate new data that is similar to the data it was trained on.
Geographic Support Recommendations

refers to the use of geographic or location information as a feature in the model. this information can be used to improve the accuracy of the model in predicting outcomes or providing recommendations based on the user's location or the location of
relevant data.

Graph Generation graph generation, whose purpose is to generate new graphs from a distribution similar to the observed graphs
Graph Ranking "graph ranking" is a feature in machine learning models that involves ranking or scoring nodes in a graph based on their importance or relevance.
Hierarchical Clustering

involves grouping data points into nested clusters based on their similarity to one another. it involves a series of iterative steps that build a hierarchy of clusters, where smaller clusters are combined into larger ones until all of the data points are in a
single cluster.

Historical Data-Driven Recommendations refers to the use of previously collected data to train machine learning models. this data is typically used to identify patterns, relationships, and trends that can inform future predictions or decisions.
Hybrid Recommendation refers to a feature that combines different recommendation approaches, such as content-based and collaborative filtering, to generate personalized recommendations for users.
Image Recognition the process of identifying an object or a feature in an image or video.
Image Similarity

"image similarity" is a feature used in machine learning models that involves comparing two or more images to determine how similar they are. this is typically done by computing a distance metric between the images based on their pixel values or
features extracted from the images.

Image-Based refers to the use of visual content, such as images or videos, as a basis for machine learning models.
Item Recommendation refers to the ability of a model to suggest items to a user based on their previous interactions with a system or similar users' behaviors.
Language Diversity (Multilingual) refers to the ability of the algorithm to work with and understand multiple languages.
Memory-Based Approaches

memory-based approaches in machine learning refer to algorithms that store and retrieve training data directly, without explicit model training. these methods often involve computing similarities between new input data and the stored training data
to make predictions or classifications.

Multi-Criteria Ratings refers to the ability of a model to consider multiple criteria or factors when assigning a rating or score to an item or entity.
Multi-Task Learning refers to a single shared machine learning model that can perform multiple different (albeit related) tasks.
Neighborhood-Based

refers to the use of information about the items or users in the local neighborhood of a given item or user to make recommendations. it is based on the idea that users with similar preferences tend to rate items in a similar way, and items that are
rated similarly tend to have similar properties.

Network Architecture refers to the structure of a neural network. it is made up of layers of artificial neurons, and each layer is connected to the layers above and below it.
Opinion Mining involves analyzing and categorizing people's opinions, sentiments, emotions, and attitudes expressed in text data such as reviews, social media posts, and online forums.
Parameter Estimation parameter estimation is the process of computing a model's parameter values from measured data.
Pattern-Based involves identifying patterns in the data that can be used to make predictions or classifications.
Positive Relevance Feedback
Pre-Trained Model

"positive relevance feedback" is a feature of some information retrieval systems. the idea behind relevance feedback is to take the results that are initially returned from a given query, to gather user feedback, and to use information about whether
or not those results are relevant to perform a new query. the system takes user feedbacks into account in order to refine and improve future search results.
pre-trained models are machine learning models that were trained on a large dataset of data, and can be used as a starting point for training a new model on a different dataset. they can save a lot of time and effort, and can be very effective.
however, they may not be as accurate as models that are trained from scratch on a specific dataset,

Prediction refers to the ability of a machine learning model to make informed guesses or forecasts about future outcomes based on patterns and trends it has learned from past data.
Prediction Uncertainty refers to the ability of a model to estimate the uncertainty associated with its predictions.
Pruning

in machine learning, pruning is a technique used to reduce the size of a decision tree by removing sections of the tree that provide little power to classify instances. pruning reduces the complexity of the final classifier and hence improves predictive
accuracy by the reduction of overfitting.

Query Refinement refers to the process of improving a search query by modifying, expanding, or narrowing its terms or parameters to retrieve more relevant results.
Query Scoping involves identifying and segmenting user queries into specific categories or topics.
Query Segmentation involves breaking down a user's query or input into smaller, more manageable parts in order to extract relevant information and provide more accurate results or recommendations.
Query Suggestions involves generating and presenting a list of recommended queries to a user based on their initial search query or input.
Query-Based

refers to models that can be used to respond to user queries, such as in search engines or question-answering systems. these systems use machine learning models to interpret the user's query and retrieve relevant information from a large
database or corpus.

Randomization in machine learning, randomization refers to the process of introducing randomness into the learning algorithm to improve its performance. randomness is often used to break any patterns in the data that might cause the model to overfit or underfit.
Ranking refers to the ability of a model to rank items or entities based on their relevance to a specific query or user.
Ratings Prediction

"ratings prediction" is a feature in machine learning models that involves predicting the rating or preference of a user for a particular item or product. this is a common application in recommender systems, where the goal is to predict the rating that a
user would give to a particular item based on their past behavior or preferences. this feature can be implemented using various approaches, such as collaborative filtering, matrix factorization, or content-based filtering.

Recommendations Using User Feedback involves incorporating user feedback into the recommendation process to improve the relevance and personalization of the recommendations provided.
Representation Learning refers to the process of automatically learning a representation or a set of features that capture the underlying patterns and structure in user intent data.
Rule-Based Tagging involves the use of predefined rules to automatically assign tags or labels to input data.
Sampling-Based

sampling-based is a feature in machine learning models that involves randomly selecting a subset of data from the entire dataset. this is done to make computations and analysis more efficient and faster, especially when dealing with a large
dataset.

Search Trail-Based Recommendations refers to the ability of a model to analyze a user's search history or search behavior to provide more personalized and relevant search results.
Semantic Analysis refers to the process of analyzing the meaning and context of words and phrases in natural language data.
Session-Based Recommendations refers to the use of a user's current session behavior, such as their current search queries and clicks, to generate personalized recommendations.
Smoothing

refers to a technique used to handle unknown or rare events in probabilistic models. it involves adjusting the probability estimates of events based on their frequency of occurrence in the training data. the basic idea is to redistribute probability mass
from more frequent events to less frequent events. this helps prevent overfitting and improves the accuracy of the model's predictions.

Structure-Based refers to the use of structural information or prior knowledge about a problem domain to guide the learning process.
Tag Relevance refers to the use of tags or keywords that are deemed relevant to a particular item or content.
Template-Based refers to the use of pre-defined templates or rules to generate responses in natural language processing (nlp) tasks such as chatbots or virtual assistants.
Term Weighting
Text Similarity

term weighting is a feature in machine learning models that involves assigning a numerical weight to each term or word in a document or dataset. the purpose of term weighting is to help the machine learning model better understand the
importance of different terms or words in the data.
measures how similar two pieces of text are to each other. it involves analyzing the text to extract its key features and comparing those features between the two pieces of text to determine their degree of similarity. this feature is often used in tasks
such as document classification, clustering, and information retrieval.

Time-Aware Recommendations refers to the consideration of the temporal dimension of data when building the model. this means that the model takes into account the sequence in which events occur over time and can make predictions based on this information.
Time-Based Recommendations refers to the inclusion of time or temporal information in the data used for a machine learning task, in order to model time-dependent patterns or to make predictions based on changes over time.
Topic Modeling

refers to the ability of the algorithm to automatically identify topics or themes in a collection of text documents. this feature is particularly useful in natural language processing applications, where the goal is to extract insights or understand the
content of large text datasets.

Trained-Based

refers to an approach in which a mathematical model is used to learn from training data and make predictions or decisions based on new data. this approach involves selecting a model that is appropriate for the specific task at hand, training it on
the available data, and then using it to make predictions on new, unseen data.

Transformer-Based
Tree Based

a neural network that learns context and thus meaning by tracking relationships in sequential data like the words in this sentence.
"tree-based" feature in machine learning refers to algorithms that use decision trees to make predictions. decision trees are tree-like structures where each node represents a feature or attribute, and each branch represents a possible value for that
feature.

User Interaction (Interactivity) refers to the ability of a model to interact with a user or other systems in real-time.
Word Cluster

"word cluster" is a feature used in natural language processing and machine learning models that groups similar words into clusters based on their semantic meaning. this feature is used to represent the meaning of a word in a more abstract and
generalized way, which can improve the performance of machine learning models that deal with natural language data.

Understanding User Intent Modeling for CRS: An SLR

57

D Quality attributes and evaluation measures
Table 12 Quality attributes and evaluation measures
Name

Definition
Accuracy it measures the proportion of correctly classified instances in a binary classification problem.

Area Under the ROC Curve (AUC) it stands for area under the roc curve and is used to evaluate the performance of a binary classification model. it measures the ability of the model to distinguish between positive and negative instances.
Discounted Cumulative Gain (DCG) it stands for discounted cumulative gain and is used to evaluate the quality of a ranking of items. it measures the usefulness of each item in the ranking, taking into account its position in the list.
F1-Score it is the harmonic mean of precision and recall, and is used as a single metric to evaluate the performance of a recommendation system.
Mean Absolute Error (MAE) it stands for mean absolute error and is used to evaluate the performance of a regression model. it measures the average difference between the predicted and actual values.
Mean Average Precision (MAP) it stands for mean average precision and is used to evaluate the quality of a ranking of items. it measures the average precision across all relevant items.
Mean Reciprocal Rank (MRR) it stands for mean reciprocal rank and is used to evaluate the quality of a ranking of items. it measures the average of the reciprocal rank of the first relevant item.
Normalized Discounted Cumulative Gain (NDCG) it is an evaluation metric commonly used in information retrieval and recommendation systems to assess the quality and ranking of the recommended items or search results.
Normalized Mutual Information (NMI) it stands for normalized mutual information and is used to evaluate the similarity between two clusterings of data.
Precision it measures the accuracy of the positive predictions made by the model, indicating how well it identifies true positive instances.
Recall it quantifies the proportion of actual positive instances that are correctly classified as positive by the model.
Root Mean Squared Error (RMSE) it stands for root mean squared error and is used to evaluate the performance of a regression model. it measures the square root of the average of the squared differences between the predicted and actual values.
Quality Attribiutes
Computational Cost it measures the amount of computational resources, such as processing time or energy consumption, required by a software system to perform a particular operation or function, which can impact its performance, scalability, and cost-effectiveness
Convergence it is a quality measure that evaluates how quickly an algorithm is able to find a solution or reach an optimal state.
Coverage is a quality measurethat evaluates the extent to which an algorithm or system can offer comprehensive and diverse information about a specific topic or data set, by assessing the amount of captured and included information in the results or output.
Diversity it decreases the redundancy in the training data, the learned model as well as the inference and provide more information for machine learning process.
Effectiveness it measures the degree to which a system meets its functional requirements and achieves its intended goals.
Flexibility it refers to the ability of a software system to be easily modified or adapted to changing requirements or environments, which can reduce costs and risks associated with major software rewrites or redesigns.
Informativeness it is a quality attribute that refers to the degree to which a software system provides useful and relevant information to its users, which can aid in understanding and using the system effectively.
Interpretability it refers to the ability of a software system, particularly in the field of machine learning and artificial intelligence, to explain its decisions and actions in a clear and understandable manner, to both technical and non-technical users.
Novelty it is a quality attribute in recommendation systems that measures the system's ability to suggest new and diverse content to users.
Performance Efficiency it is a software quality attribute that measures the ability of a system to use computing resources effectively to meet performance requirements.
Predictability it is the ability of a system or software to produce expected and consistent results given specific conditions or inputs.
Recommendation Effectiveness it measures how well a software system can provide accurate and useful recommendations to users, which is important for increasing user engagement and satisfaction.
Recommendation Efficiency it refers to the ability of a recommendation system to efficiently generate relevant and accurate recommendations for a user.
Recommendation Performance it measures how well a recommendation system suggests relevant items to users.
Reliability it measures the ability of a system to perform its intended functions in a consistent and predictable manner, without unexpected or erroneous behavior.
Resource Efficiency it measures the ability of a system to use computing resources, such as memory, processing power, and storage, in an efficient and effective manner.
Resource Utilization it is a software quality attribute that measures the efficient and effective use of computing resources, such as memory, processing power, and storage, by a software system, which can impact its performance, scalability, and cost-effectiveness.
Retrieval Performance it measures how effectively and efficiently a software system can retrieve relevant information from a large collection of data.
Robustness it measures the ability of a system to remain stable and reliable under various abnormal or unexpected conditions, such as invalid inputs, system failures, or attacks from malicious users.
Satisfaction it measures the extent to which a system meets or exceeds the expectations and needs of its users, resulting in a positive user experience.
Scalability it measures the ability of a system to handle increasing amounts of work or users without experiencing a degradation in performance.
Simplicity it refers to the quality or state of being simple, straightforward, or easy to understand. In various domains and contexts, simplicity is often valued as it promotes clarity, efficiency, and usability.
Stability it measures the ability of a system to maintain its performance and reliability over time, even under changing conditions or in the face of failures or errors.
Transparency it refers to the ability of a software system to provide clear and understandable information to users, which can increase their trust and satisfaction in using the system.
Usefulness it measures the extent to which a system is capable of satisfying user needs and delivering value to its intended users.
Validity it refers to the accuracy and correctness of the data and information processed by a system, including recommendation systems.
