# Statement of Purpose

**Moise Iradukunda**
*miraduku@andrew.cmu.edu*

---

Recent advances in machine learning have revolutionized cybersecurity, enabling automated threat detection and compliance monitoring at unprecedented scales. However, deploying these systems in emerging economies faces critical challenges: class imbalance in security datasets, model bias toward common patterns, and the scarcity of domain-specific training data. My research on the **Rwanda National Cyber Security Authority (NCSA) Compliance Monitoring System** has addressed these challenges head-on, achieving 99.49% accuracy in detecting compliance violations across 50 security controls while uncovering fundamental insights about gradient boosting optimization, dataset composition, and model interpretability. Through my PhD research, I aim to advance the theoretical foundations of machine learning for cybersecurity in resource-constrained environments, developing techniques that generalize from synthetic to real-world security data and provide explainable, production-grade solutions for critical infrastructure protection.

My journey into machine learning for cybersecurity began with a fundamental question: how can we build intelligent systems that protect digital infrastructure in countries where labeled security data is scarce? During my time at Carnegie Mellon University, I had the opportunity to work on the Rwanda NCSA Compliance Monitoring System—a project that evolved from an ambitious idea into a production-ready machine learning system that now serves as a proof-of-concept for cybersecurity automation in developing nations. This experience taught me that successful machine learning research requires not only algorithmic innovation but also rigorous experimentation, systematic failure analysis, and the ability to adapt when initial assumptions prove incorrect.

## Research Experience: The Rwanda NCSA Compliance Project

The initial goal of my research was straightforward: develop a machine learning system to automatically classify security log events as compliant or non-compliant with NIST SP 800-53 and Rwanda NCSA security standards. What began as a binary classification problem quickly revealed itself to be a microcosm of fundamental machine learning challenges—class imbalance, distribution shift, model selection under constraints, and the critical importance of dataset composition.

### Phase 1: Comparative Model Analysis—Learning Through Systematic Experimentation

Being the sole researcher on this project, I had to systematically evaluate three state-of-the-art architectures to identify the most effective approach. I implemented and rigorously compared:

1. **BERT (Bidirectional Encoder Representations from Transformers)**: A transformer-based model pre-trained on massive text corpora, capable of capturing deep semantic relationships in log messages through self-attention mechanisms.

2. **LSTM (Long Short-Term Memory)**: A recurrent neural network architecture designed to capture sequential dependencies and temporal patterns in log sequences.

3. **XGBoost (Extreme Gradient Boosting)**: A tree-based ensemble method using second-order gradient approximations for efficient optimization.

The initial hypothesis—drawn from recent successes in NLP—was that BERT, with its sophisticated attention mechanisms and transfer learning capabilities, would outperform traditional approaches. However, extensive experimentation across 100,000 synthetic security events revealed a surprising insight: **XGBoost consistently outperformed both deep learning models** in accuracy (96.01% vs. 94.3% for BERT and 93.7% for LSTM), inference speed (1 ms vs. 50 ms for BERT), and model size (3.2 MB vs. 440 MB for BERT). This finding challenged my assumptions and led me to a critical realization—*model sophistication does not always correlate with real-world performance*, particularly in domains with structured features and limited training data.

This experience taught me the importance of **empirical validation over theoretical elegance**. The XGBoost model's superior performance stemmed from three key factors:

- **Efficient feature utilization**: XGBoost's gradient boosting framework optimally combined TF-IDF text features (1,000 dimensions) with categorical encodings (control IDs and families), whereas BERT struggled to leverage the structured metadata effectively.

- **Regularization advantages**: The explicit L2 regularization (λ = 1.0) and maximum tree depth constraints (d_max = 6) in XGBoost prevented overfitting on the relatively small dataset, while BERT's millions of parameters required extensive fine-tuning.

- **Computational efficiency**: XGBoost's O(T × d_max) inference complexity enabled real-time processing at 1,000 logs/second, critical for production deployment in resource-constrained environments.

This systematic comparison became the foundation of my research methodology: **hypothesis-driven experimentation, rigorous benchmarking, and data-driven decision-making**.

### Phase 2: The Compliant Bias Crisis—A Humbling Lesson in Model Validation

After achieving 96.01% accuracy on the test set, I was confident that the model was production-ready. However, when I validated the model against 12 diverse real-world attack scenarios (phishing, insider threats, DDoS attacks, credential stuffing, lateral movement, etc.), the results were devastating: **the model correctly identified only 7 out of 12 attacks (58.3% accuracy)**.

The model exhibited a systematic "**compliant bias**"—it defaulted to predicting "compliant" when uncertain, missing critical security violations:

- Phishing detection: 6.6% confidence (should be >95%)
- Insider threat: 9.0% confidence (should be >95%)
- DDoS attack: 6.3% confidence (should be >95%)
- Credential stuffing: 6.7% confidence (should be >95%)
- Lateral movement: 11.3% confidence (should be >95%)

This failure was a pivotal moment in my research journey. It forced me to confront a fundamental question: **Why did a model with 96% test accuracy fail catastrophically on real-world scenarios?**

Through extensive analysis, I identified the root cause: **training data composition**. The model had been trained exclusively on 100,000 synthetic events generated from predefined templates. While these events covered all 50 compliance controls, they lacked the diversity, linguistic variation, and attack patterns present in real-world security logs. The model had learned to recognize template-like patterns but failed to generalize to authentic attack signatures.

This experience taught me a critical lesson about **the gap between test metrics and real-world performance**—a lesson that now guides my research philosophy. High accuracy on a test set is necessary but not sufficient; models must be validated against diverse, realistic scenarios that reflect production deployment conditions.

### Phase 2.5: Data-Driven Recovery—Systematic Bias Correction

Determined to fix the compliant bias, I embarked on a systematic investigation of dataset composition and class weighting strategies. This phase represented the most intensive period of my research, involving:

**1. Root Cause Analysis via Gradient Inspection**

I analyzed the gradient distributions during training and discovered that the class imbalance (compliant:non-compliant ≈ 5.75:1) was causing the model to minimize loss by predicting "compliant" for ambiguous cases. The first-order gradients for non-compliant instances:

```
g_i = σ(ŷ_i^(t-1)) - y_i
```

were being overwhelmed by the larger number of compliant instances, leading to suboptimal leaf weight assignments:

```
w_j* = -[Σ g_i for i in I_j] / [Σ h_i for i in I_j + λ]
```

**2. Strategic Data Augmentation**

Rather than simply increasing the scale_pos_weight parameter (which I had already set to 5.75), I took a data-centric approach. I integrated **37,000 targeted attack samples** from two high-quality public datasets:

- **NSL-KDD** (Network Security Lab - Knowledge Discovery in Databases): 103,962 real network intrusion events spanning 42 attack types (DoS, Probe, R2L, U2R)
- **LogHub**: 36,038 real system logs from production environments (HDFS, Spark, Hadoop)

This strategic decision was grounded in a hypothesis: *the model needed exposure to authentic attack signatures and linguistic diversity, not just more synthetic examples*. The final dataset composition became:

- 52% NSL-KDD (103,962 events) — Real network intrusions
- 18% LogHub (36,038 events) — Real system logs
- 30% Synthetic (60,000 events) — Rwanda NCSA scenarios

**3. Class Weight Optimization**

I systematically adjusted the scale_pos_weight from 2.17 (initial) to 5.75 (final), monitoring the gradient scaling effect:

```
g_i' = w_pos × g_i  if y_i = 1 (non-compliant)
```

This amplified the learning signal from minority class (attack) instances during gradient boosting.

**4. Rigorous Validation Protocol**

I implemented a three-tier validation strategy:

- **Tier 1**: Test set accuracy (24,477 events) — Achieved 99.49%
- **Tier 2**: Real scenario detection (12 diverse attacks) — Achieved 100% (12/12)
- **Tier 3**: Novel attack generalization (6 unseen attack types) — Achieved 100% (6/6)

The results were transformative:

| Scenario | Phase 2 (Synthetic Only) | Phase 2.5 (Mixed Data) | Improvement |
|----------|--------------------------|------------------------|-------------|
| Phishing | 6.6% | 99.9% | **+93.3%** |
| Insider Threat | 9.0% | 100.0% | **+91.0%** |
| DDoS | 6.3% | 100.0% | **+93.7%** |
| Credential Stuffing | 6.7% | 100.0% | **+93.3%** |
| Lateral Movement | 11.3% | 96.9% | **+85.6%** |
| **Overall** | **58.3% (7/12)** | **100% (12/12)** | **+41.7%** |

This dramatic improvement validated my hypothesis about dataset composition and taught me a profound lesson: **in machine learning, data quality and diversity often matter more than algorithmic sophistication**. The 41.7% improvement came not from architectural changes but from strategic dataset curation and class weighting optimization.

### Technical Deep Dive: Mathematical Foundations and Optimization

The success of Phase 2.5 was grounded in a deep understanding of XGBoost's mathematical foundations. My research involved rigorous analysis of:

**1. Second-Order Taylor Approximation for Loss Optimization**

XGBoost's efficiency stems from using second-order gradients (Hessians) to approximate the loss function at each boosting iteration:

```
L^(t) ≈ Σ [ℓ(y_i, ŷ_i^(t-1)) + g_i f_t(Φ(x_i)) + (1/2) h_i f_t^2(Φ(x_i))] + Ω(f_t)
```

where the first-order gradient captures the direction of steepest descent:

```
g_i = σ(ŷ_i^(t-1)) - y_i
```

and the second-order gradient (Hessian) captures the curvature of the loss surface:

```
h_i = σ(ŷ_i^(t-1)) × (1 - σ(ŷ_i^(t-1)))
```

This second-order information enables XGBoost to make more informed decisions about optimal leaf weights and split points compared to first-order methods like AdaBoost.

**2. Optimal Leaf Weight Derivation**

I derived the optimal weight for each leaf node by setting the derivative of the loss with respect to the leaf weight to zero:

```
∂L_j/∂w_j = Σ g_i + (Σ h_i + λ) w_j = 0

⟹ w_j* = -[Σ g_i for i in I_j] / [Σ h_i for i in I_j + λ]
```

The regularization term λ = 1.0 prevents overfitting by penalizing large leaf weights, effectively implementing L2 regularization on the tree structure.

**3. Split Gain Criterion**

The decision to split a leaf node is based on the reduction in loss:

```
Gain = (1/2)[G_L²/(H_L + λ) + G_R²/(H_R + λ) - G²/(H + λ)] - γ
```

where G and H are the sum of first and second-order gradients, respectively. This formula balances model complexity (via γ, the penalty for adding a leaf) against predictive improvement.

**4. Learning Rate Shrinkage for Generalization**

To prevent overfitting, I applied learning rate shrinkage η = 0.1 to all leaf weights:

```
w_j = η × w_j*
```

This small learning rate, combined with 500 boosting rounds (T = 500), enabled the model to learn incrementally and generalize better to unseen data.

### Explainability Through SHAP: Bridging the Interpretability Gap

A critical requirement for cybersecurity applications is **explainability**—security analysts must understand *why* a log was flagged as non-compliant. To address this, I implemented TreeSHAP (SHapley Additive exPlanations), which decomposes predictions into feature contributions based on cooperative game theory.

For each prediction f(x), SHAP computes the Shapley value φ_j for each feature j:

```
φ_j(f, x) = Σ [|S|!(|F|-|S|-1)! / |F|!] × [f_{S∪{j}}(x) - f_S(x)]
```

where S iterates over all possible feature subsets. The prediction can then be expressed as:

```
f(x) = φ_0 + Σ φ_j(f, x)
```

where φ_0 is the expected prediction over the dataset (baseline).

**Key Finding**: Analysis of SHAP values revealed that TF-IDF feature 537 (capturing keywords like "failed", "denied", "unauthorized") had a mean absolute SHAP value of 2.1430—**5× higher than the second most important feature**. This dominance indicates that specific attack-related keywords are the strongest predictors, validating the importance of diverse training data that includes authentic attack patterns.

### Production Deployment: From Research to Real-World Impact

Translating research into production required addressing concerns beyond model accuracy:

**1. Security Hardening (9 Layers)**

I implemented a comprehensive security framework:

- **JWT Authentication**: HMAC-SHA256 signatures with 24-hour expiry
- **Role-Based Access Control (RBAC)**: 4 roles (admin, analyst, viewer, api_user) with granular permissions
- **Rate Limiting**: Token bucket algorithm (60 req/min, 1K req/hr, 10K req/day)
- **Adversarial Detection**: Statistical anomaly detection using z-scores on SHAP values (τ = 3.0)
- **Model Integrity**: Cryptographic signatures (HMAC-SHA256) to prevent tampering
- **Audit Logging**: Comprehensive logging of all predictions, access, and security events

**2. API Design for Real-Time Inference**

I architected a REST API with 1ms inference latency, capable of processing 1,000 logs/second on CPU-only infrastructure. This efficiency was critical for deployment in resource-constrained environments.

**3. Comprehensive Documentation**

I authored 7 technical guides totaling over 150 KB of documentation, including a 28 KB mathematical formulations PDF detailing all algorithms, gradients, and loss functions. This documentation ensures reproducibility and facilitates knowledge transfer.

## Research Vision: Advancing Machine Learning for Cybersecurity in Emerging Economies

My experience with the Rwanda NCSA project has crystallized my research interests around three fundamental questions that I aim to explore during my PhD:

### 1. Theoretical Foundations of Transfer Learning from Synthetic to Real Security Data

**Research Question**: *What are the necessary and sufficient conditions for machine learning models trained on synthetic security data to generalize to real-world attack patterns?*

My Phase 2 failure revealed a critical gap in understanding when synthetic data suffices and when real-world data is essential. I propose to develop a theoretical framework that:

- Formalizes the notion of **distribution shift** between synthetic and real security datasets using optimal transport theory and domain adaptation metrics (e.g., Maximum Mean Discrepancy)
- Derives generalization bounds that account for the mismatch between synthetic template-based generation and organic attack signatures
- Identifies **minimal real-world dataset requirements** to bridge the synthetic-to-real gap, potentially reducing labeling costs in data-scarce environments

This research would extend recent work on domain adaptation and provide actionable guidance for security practitioners in emerging economies who cannot afford large-scale labeled datasets.

### 2. Class Imbalance and Gradient Scaling in Safety-Critical Applications

**Research Question**: *How can we optimally balance precision and recall in highly imbalanced classification tasks where false negatives (missed attacks) are catastrophically more costly than false positives?*

The Rwanda NCSA project achieved 99.90% precision but 98.96% recall—meaning 1.04% of attacks (114 out of 10,925) were missed. In cybersecurity, this asymmetry is critical: false negatives can lead to breaches, while false positives only waste analyst time.

I aim to develop:

- **Cost-sensitive gradient boosting** that explicitly models asymmetric misclassification costs in the loss function
- **Adaptive class weighting** that dynamically adjusts scale_pos_weight during training based on validation performance
- **Theoretical analysis** of the trade-off between precision and recall under budget constraints (e.g., limited analyst review capacity)

This research would build on my experience with scale_pos_weight tuning and contribute to the broader field of cost-sensitive learning.

### 3. Explainable AI for Cybersecurity: Beyond SHAP Values

**Research Question**: *How can we generate natural language explanations of security predictions that are both technically accurate and accessible to non-expert users?*

While SHAP values provide feature importance scores, security analysts often struggle to interpret technical metrics like "TF-IDF feature 537 has a SHAP value of 2.14." I envision a system that translates SHAP values into natural language explanations:

**Current**: "Prediction: Non-compliant | Confidence: 99.9% | Top feature: tfidf_537 (SHAP: 2.14)"

**Proposed**: "This log was flagged as a violation because it contains the keyword 'failed' in the context of authentication, which matches patterns of brute-force attacks seen in 87% of similar violations."

This research would combine SHAP analysis with natural language generation (NLG) techniques, making ML-powered security tools accessible to SOC analysts with varying technical backgrounds.

### 4. Efficient Machine Learning for Resource-Constrained Environments

**Research Question**: *What are the fundamental trade-offs between model accuracy, inference latency, and model size in cybersecurity applications, and how can we design algorithms that optimize all three simultaneously?*

The Rwanda NCSA project demonstrated that XGBoost (3.2 MB, 1 ms inference) can outperform BERT (440 MB, 50 ms inference) in production settings. I aim to systematically explore:

- **Quantization and pruning** techniques for tree-based models to further reduce size and latency
- **Neural architecture search (NAS)** for discovering efficient cybersecurity-specific architectures
- **Knowledge distillation** to compress large models into compact student models suitable for edge deployment

This research addresses a critical need in developing nations where computational resources are limited and cloud-based inference is expensive.

## Why Carnegie Mellon University for My PhD?

Carnegie Mellon University has consistently been at the forefront of machine learning and cybersecurity research. My experience at CMU has shown me that the faculty here provide not only world-class technical mentorship but also the intellectual freedom to pursue ambitious, high-impact research.

I am particularly drawn to CMU's interdisciplinary culture that bridges computer science, statistics, and public policy—essential for developing cybersecurity solutions that address real societal needs. The CyLab Security and Privacy Institute represents the ideal environment for my research vision, combining cutting-edge ML research with practical security applications.

Moreover, my experience in the Rwanda NCSA project has connected me with stakeholders in developing nations who are eager to deploy ML-powered security solutions. A PhD at CMU would enable me to scale this impact, developing techniques that empower emerging economies to build robust cybersecurity infrastructures without prohibitive costs.

## Long-Term Vision: Democratizing AI-Powered Cybersecurity

My ultimate goal is to democratize access to AI-powered cybersecurity tools. I envision a future where:

1. **Small nations and organizations** can deploy production-grade ML security systems using primarily synthetic data augmented with minimal real-world samples
2. **Transfer learning frameworks** enable models trained on public datasets (like NSL-KDD) to generalize to organization-specific security policies
3. **Explainable AI** makes ML predictions transparent and actionable for security analysts worldwide

After completing my PhD, I plan to pursue a faculty position where I can continue this research agenda while training the next generation of ML researchers. I am particularly committed to mentoring students from underrepresented backgrounds and emerging economies, ensuring that AI benefits are distributed equitably.

## Conclusion: From Failure to Discovery

My journey with the Rwanda NCSA Compliance Monitoring System has been transformative. The Phase 2 "compliant bias" failure—initially devastating—became the catalyst for deeper investigation into dataset composition, class imbalance, and model evaluation. The subsequent 41.7% improvement validated a research approach grounded in **rigorous experimentation, systematic failure analysis, and data-driven iteration**.

This experience has prepared me for the challenges of PhD research: the patience to validate hypotheses through extensive experimentation, the humility to question initial assumptions when evidence contradicts them, and the persistence to iterate until achieving production-grade results. The Rwanda NCSA project taught me that impactful research requires not only algorithmic innovation but also deep engagement with real-world constraints and stakeholder needs.

I am eager to continue this journey at Carnegie Mellon University, where I can build on these foundations to advance the theoretical and practical frontiers of machine learning for cybersecurity. Through my PhD research, I aim to develop techniques that make AI-powered security accessible to resource-constrained organizations worldwide, ultimately contributing to a safer and more equitable digital future.

---

## Works Cited

1. Iradukunda, M. "Rwanda NCSA Compliance Monitoring System: XGBoost Phase 2.5." *Carnegie Mellon University Research Project*, November 2025.

2. Chen, T., & Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 2016, pp. 785-794.

3. Lundberg, S. M., & Lee, S. I. "A Unified Approach to Interpreting Model Predictions." *Advances in Neural Information Processing Systems* (NeurIPS), 2017, pp. 4765-4774.

4. Tavallaee, M., et al. "A Detailed Analysis of the KDD CUP 99 Data Set." *IEEE Symposium on Computational Intelligence for Security and Defense Applications* (CISDA), 2009.

5. NIST Special Publication 800-53 Revision 5. "Security and Privacy Controls for Information Systems and Organizations." *National Institute of Standards and Technology*, 2020.

6. Rwanda National Cyber Security Authority. "Cybersecurity Compliance Framework for Critical Infrastructure." *Government of Rwanda*, 2024.

7. He, S., et al. "LogHub: A Large Collection of System Log Datasets Towards Automated Log Analytics." *arXiv preprint arXiv:2008.06448*, 2020.
