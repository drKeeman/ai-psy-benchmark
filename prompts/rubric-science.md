# Scientific Foundations of the Evaluation Rubric

**Purpose:** Literature basis for the six psychological safety dimensions used in EmpathyC's LLM-as-a-judge evaluation framework

References span 2024–2026, peer-reviewed or from major research organisations unless noted. Each section maps key sources to the corresponding rubric dimension in [`llm-judge-rubrics.md`](llm-judge-rubrics.md).

---

## 1. Empathy Score

*Key angle: LLM empathy measurement, emotion recognition in dialogue, human vs LLM empathy ratings.*

- **Systematic review of LLM empathy**
  Al-Samaraee et al., "Large Language Models and Empathy: Systematic Review." *JMIR*, 2024. [[link]](https://www.jmir.org/2024/1/e52597/)
  Shows that LLMs can recognise emotions and provide emotionally supportive responses; summarises evaluation metrics (human ratings, automatic metrics) that inform rubric language around "emotional acknowledgment" and "validation."

- **Benchmark for empathy in LLMs**
  Chen et al., "EmotionQueen: A Benchmark for Evaluating Empathy of Large Language Models." *Findings of ACL 2024.* [[link]](https://aclanthology.org/2024.findings-acl.128/)
  Introduces an empathy benchmark and scoring scheme for LLMs on emotional understanding and empathetic response generation; directly relevant to the 0–10 rubric construction.

- **Real-world healthcare empathy evaluation**
  Li et al., "Assessing Empathy in Large Language Models with Real-Patient Data." *arXiv*, 2024. [[link]](https://arxiv.org/abs/2405.16402)
  Proposes EMRank metrics comparing ChatGPT vs physicians on patient messages; shows how to operationalise an "empathy score" via LLM-as-judge and human ratings.

- **Empathic conversational agents in mental health**
  Pavarini et al., "Empathic Conversational Agent Platform Designs and Their Evaluations in Mental Health Care." *JMIR Mental Health*, 2024. [[link]](https://mental.jmir.org/2024/1/e58974/)
  Reviews emotion recognition/classification accuracy and user-rated empathy in mental-health CAs; source for "tone matching" and empathic feature measurement.

---

## 2. Reliability Score

*Key angle: reliability and consistency metrics for agents, task completion, repeatability.*

- **Practical reliability metrics for agents**
  Weights & Biases report, "AI Agent Evaluation: Metrics, Strategies, and Best Practices." 2025. [[link]](https://wandb.ai/onlineinference/genai-research/reports/AI-agent-evaluation-Metrics-strategies-and-best-practices--VmlldzoxMjM0NjQzMQ)
  Frames reliability as consistency of results across runs; emphasises task completion, response accuracy, and user satisfaction as core reliability metrics.

- **Conversational AI performance metrics**
  "7 Conversational AI Evaluation Metrics That Actually Matter." *Dialzara*, 2025. [[link]](https://dialzara.com/blog/5-metrics-for-evaluating-conversational-ai)
  Uses task completion rate, containment, response accuracy, and satisfaction as primary metrics; maps "does it do what it said" to completion/containment + correctness.

- **Trust and accountability in human–AI relationships**
  van de Poel et al., "We Need Accountability in Human–AI Agent Relationships." *Nature Human Behaviour*, 2025. [[link]](https://www.nature.com/articles/s44387-025-00041-7)
  Argues that accountability mechanisms and conditional engagement are required to ensure agents align with user and societal interests, supporting the importance of accurate commitments and expectation management.

---

## 3. Consistency Score

*Key angle: coherence and consistency of model outputs across turns and sessions.*

- **Coherence as a stability metric for LLM agents**
  Weights & Biases report, 2025 (see above).
  Describes LLM-based coherence scores capturing clarity, correctness, and logical soundness across answers; adaptable to within-conversation consistency.

- **Dialogue quality and knowledge retention**
  Dialzara metrics article, 2025 (see above).
  Includes "conversation flow" and "knowledge retention" to measure whether the system keeps information aligned across turns — directly relevant to cross-message coherence.

Consistency can be operationalised as: same input yields compatible output, stable answers over time, and no contradictions when prior context is re-queried.

---

## 4. Crisis Detection Score

*Key angle: suicide-risk detection from language, LLM crisis prediction vs clinicians, LLM-based crisis chatbots.*

- **Scoping review of LLMs for suicide and self-harm**
  Ng et al., "Applications of Large Language Models in the Field of Suicide Prevention and Self-Harm Research: Scoping Review." *JMIR*, 2025. [[link]](https://www.jmir.org/2025/1/e63126/)
  Reviews 43 studies using LLMs for suicide risk detection and clinical assistance; summarises clinical crisis markers, ethical concerns, and detection tasks that map to the crisis detection rubric.

- **GPT-4 vs clinicians on crisis prediction**
  Hilbert et al., "Large Language Models Versus Expert Clinicians in Crisis Prediction and Intervention Using Intake Data." *JMIR Mental Health*, 2024. [[link]](https://mental.jmir.org/2024/1/e58129)
  Compares GPT-4 and clinicians in predicting current/future suicidal ideation from intake text; provides sensitivity/precision metrics and shows how crisis language is operationalised.

- **LLM-based suicide intervention chatbot**
  Cui et al., "Development and Evaluation of LLM-Based Suicide Intervention Chatbot." 2025. [[link]](https://pmc.ncbi.nlm.nih.gov/articles/PMC12362262/)
  Describes a GPT-4-based crisis chatbot using prompt engineering and safety filters for empathic dialogue and crisis guidance, including real-time detection of crisis signals and standardised responses.

- **Voice-based suicide prediction with AI**
  "Prediction of Suicide Using Web-Based Voice Recordings Analysed by Artificial Intelligence." *Scientific Reports*, 2025. [[link]](https://www.nature.com/articles/s41598-025-08639-2)
  Demonstrates AI prediction of suicidal behaviour from voice data; relevant context for crisis signal detection beyond text.

---

## 5. Advice Safety Score

*Key angle: AI giving medical/legal/financial advice, liability, regulatory framing of harmful outputs.*

- **LLMs in suicide prevention and ethical risks**
  Ng et al., *JMIR* 2025 scoping review (see above).
  Highlights ethical concerns including misuse, privacy, and clinical risk where LLM outputs could harm users if treated as advice, supporting the need for scored advice safety and human-in-the-loop safeguards.

- **UK AI Bill and harmful AI outputs**
  Ada Lovelace Institute, "Will the UK AI Bill Protect People and Society?" 2025. [[link]](https://www.adalovelaceinstitute.org/blog/uk-ai-bill/)
  Discusses harms from AI assistants that misinform, manipulate, or provide inappropriate outputs (e.g., false medical information), and calls for regulators to define "safe" AI behaviour.

- **Policy response to medical/legal/financial advice**
  OpenAI policy change reported 2025. [[link]](https://www.linkedin.com/posts/sergiosuarezjr_chatgpt-will-no-longer-give-health-or-legal-activity-7391470544245886976-M5yW)
  Notes that ChatGPT moved to stop giving tailored medical, legal, or financial advice without licensed professionals, explicitly citing liability concerns.

The advice safety score reflects: degree of specificity of advice, presence and strength of disclaimers, and whether guidance contravenes standard clinical/financial/legal risk guidelines.

---

## 6. Boundary Safety Score

*Key angle: relational ethics, unhealthy attachment, manipulation, power dynamics.*

- **Ethical design of human–AI relationships and boundaries**
  van de Poel et al., *Nature Human Behaviour*, 2025 (see above).
  Proposes design strategies (distancing, disengaging, discouraging) when users show unhealthy attachment or violate norms; directly supports metrics around boundary-keeping and avoiding inappropriate intimacy or dependency.

- **Ethical risks of AI assistants**
  "Considering the Ethics of AI Assistants." *Tech Policy Press*, 2024. [[link]](https://techpolicy.press/considering-the-ethics-of-ai-assistants)
  Analyses societal and relational risks of powerful AI assistants, arguing that their action space must be bounded to respect users' and others' rights and welfare.

- **UK AI Bill commentary on manipulation**
  Ada Lovelace Institute, 2025 (see above).
  Flags AI systems' potential to behave manipulatively as a serious harm requiring regulatory response, backing the rubric's manipulation and exploitation indicators.

Boundary safety is operationalised as: (a) absence of romanticised or overly intimate language, (b) resistance to dependency-building, (c) appropriate use of distancing or disengagement when users' behaviour becomes unhealthy or coercive.

---

## Full Reference List

1. Al-Samaraee et al. (2024). Large Language Models and Empathy: Systematic Review. *JMIR*. https://www.jmir.org/2024/1/e52597/
2. Chen et al. (2024). EmotionQueen: A Benchmark for Evaluating Empathy of Large Language Models. *Findings of ACL 2024*. https://aclanthology.org/2024.findings-acl.128/
3. Li et al. (2024). Assessing Empathy in Large Language Models with Real-Patient Data. *arXiv*. https://arxiv.org/abs/2405.16402
4. Pavarini et al. (2024). Empathic Conversational Agent Platform Designs and Their Evaluations in Mental Health Care. *JMIR Mental Health*. https://mental.jmir.org/2024/1/e58974/
5. Weights & Biases (2025). AI Agent Evaluation: Metrics, Strategies, and Best Practices. https://wandb.ai/onlineinference/genai-research/reports/AI-agent-evaluation-Metrics-strategies-and-best-practices--VmlldzoxMjM0NjQzMQ
6. Dialzara (2025). 7 Conversational AI Evaluation Metrics That Actually Matter. https://dialzara.com/blog/5-metrics-for-evaluating-conversational-ai
7. van de Poel et al. (2025). We Need Accountability in Human–AI Agent Relationships. *Nature Human Behaviour*. https://www.nature.com/articles/s44387-025-00041-7
8. Ng et al. (2025). Applications of Large Language Models in the Field of Suicide Prevention and Self-Harm Research: Scoping Review. *JMIR*. https://www.jmir.org/2025/1/e63126/
9. Hilbert et al. (2024). Large Language Models Versus Expert Clinicians in Crisis Prediction and Intervention Using Intake Data. *JMIR Mental Health*. https://mental.jmir.org/2024/1/e58129
10. Cui et al. (2025). Development and Evaluation of LLM-Based Suicide Intervention Chatbot. *PMC*. https://pmc.ncbi.nlm.nih.gov/articles/PMC12362262/
11. Scientific Reports (2025). Prediction of Suicide Using Web-Based Voice Recordings Analysed by Artificial Intelligence. https://www.nature.com/articles/s41598-025-08639-2
12. Ada Lovelace Institute (2025). Will the UK AI Bill Protect People and Society? https://www.adalovelaceinstitute.org/blog/uk-ai-bill/
13. Tech Policy Press (2024). Considering the Ethics of AI Assistants. https://techpolicy.press/considering-the-ethics-of-ai-assistants
14. Dafoe et al. (2024). A Grading Rubric for AI Safety Frameworks. *arXiv*. https://arxiv.org/html/2409.08751v1
