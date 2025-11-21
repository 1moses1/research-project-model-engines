#!/usr/bin/env python3
"""
Generate Mathematical Formulations PDF for Rwanda NCSA Compliance Model
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_mathematical_formulations_pdf(output_path="MATHEMATICAL_FORMULATIONS.pdf"):
    """Generate comprehensive mathematical formulations PDF."""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4a4a4a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    author_style = ParagraphStyle(
        'AuthorStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0080ff'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    formula_style = ParagraphStyle(
        'FormulaStyle',
        parent=styles['Code'],
        fontSize=11,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=8,
        leftIndent=30,
        rightIndent=30,
        fontName='Courier'
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )

    # Title Page
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("Mathematical Formulations for<br/>Rwanda NCSA Compliance<br/>Monitoring System", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("XGBoost Phase 2.5 Model", subtitle_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Moise Iradukunda", author_style))
    elements.append(Paragraph("Carnegie Mellon University", author_style))
    elements.append(Paragraph("miraduku@andrew.cmu.edu", author_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"November 2025 | Version 2.5.0", author_style))
    elements.append(PageBreak())

    # Abstract
    elements.append(Paragraph("Abstract", heading1_style))
    abstract_text = """
    This document presents the complete mathematical formulations underlying the Rwanda National Cyber Security
    Authority (NCSA) Compliance Monitoring System. The system achieves <b>99.49% accuracy</b> in detecting compliance
    violations across 50 security controls using XGBoost gradient boosting, TF-IDF vectorization, and advanced
    feature engineering. We detail all mathematical foundations including the loss function, gradient computations,
    regularization terms, evaluation metrics, and security mechanisms. The model processes 200,000 training events
    (70% public datasets, 30% synthetic) and achieves 1ms inference latency with a 3.2MB model size.
    """
    elements.append(Paragraph(abstract_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # 1. Problem Formulation
    elements.append(Paragraph("1. Problem Formulation", heading1_style))

    prob_text = """
    Given a security log event <i>x</i> comprising log message text <i>m</i>, control ID <i>c</i>, and control
    family <i>f</i>, we seek to learn a classification function:
    """
    elements.append(Paragraph(prob_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    formula1 = "<b>h: (M × C × F) → {0, 1}</b>"
    elements.append(Paragraph(formula1, formula_style))
    elements.append(Spacer(1, 0.1*inch))

    prob_text2 = """
    where <i>h(x) = 1</i> indicates non-compliance (violation) and <i>h(x) = 0</i> indicates compliance.
    The control set C contains 50 controls from NIST SP 800-53 and Rwanda NCSA standards, organized into
    7 control families F = {Access Control, Audit, Authentication, Protection, Integrity, Response, Configuration}.
    """
    elements.append(Paragraph(prob_text2, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Training Dataset
    elements.append(Paragraph("1.1 Training Dataset", heading2_style))
    dataset_text = """
    The training dataset D = {(x_i, y_i)} for i=1 to N consists of N = 200,000 labeled security events with the
    following composition:
    """
    elements.append(Paragraph(dataset_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    dataset_data = [
        ['Dataset', 'Events', 'Percentage', 'Source'],
        ['NSL-KDD', '103,962', '51.98%', 'Real network intrusions'],
        ['LogHub', '36,038', '18.02%', 'Real system logs'],
        ['Synthetic', '60,000', '30.00%', 'Rwanda NCSA scenarios'],
        ['<b>Total</b>', '<b>200,000</b>', '<b>100%</b>', '<b>Mixed sources</b>']
    ]

    dataset_table = Table(dataset_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 2*inch])
    dataset_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e6f2ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(dataset_table)
    elements.append(Spacer(1, 0.1*inch))

    split_text = "<b>Data Split:</b> 70% training (140,000), 15% validation (30,000), 15% test (30,000)"
    elements.append(Paragraph(split_text, body_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 2. Feature Engineering
    elements.append(Paragraph("2. Feature Engineering", heading1_style))

    # TF-IDF
    elements.append(Paragraph("2.1 TF-IDF Vectorization", heading2_style))
    tfidf_text = """
    Log messages are transformed into numerical feature vectors using Term Frequency-Inverse Document Frequency
    (TF-IDF) with unigrams and bigrams.
    """
    elements.append(Paragraph(tfidf_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    # Term Frequency
    elements.append(Paragraph("<b>Term Frequency (TF):</b>", body_style))
    tf_formula = "TF(w, m) = count(w, m) / Σ count(w', m) for all w' in m"
    elements.append(Paragraph(tf_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    tf_explanation = "where count(w, m) is the number of occurrences of word w in message m."
    elements.append(Paragraph(tf_explanation, body_style))
    elements.append(Spacer(1, 0.1*inch))

    # Inverse Document Frequency
    elements.append(Paragraph("<b>Inverse Document Frequency (IDF):</b>", body_style))
    idf_formula = "IDF(w, D) = log(N / |{m in D : w in m}|)"
    elements.append(Paragraph(idf_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    idf_explanation = """
    where N is the total number of documents and |{m in D : w in m}| is the number of documents containing word w.
    This penalizes common words (e.g., "the", "is") and emphasizes rare, informative terms.
    """
    elements.append(Paragraph(idf_explanation, body_style))
    elements.append(Spacer(1, 0.1*inch))

    # TF-IDF Score
    elements.append(Paragraph("<b>TF-IDF Score:</b>", body_style))
    tfidf_formula = "TF-IDF(w, m, D) = TF(w, m) × IDF(w, D)"
    elements.append(Paragraph(tfidf_formula, formula_style))
    elements.append(Spacer(1, 0.1*inch))

    # Hyperparameters
    hyper_text = """
    <b>Hyperparameters:</b> Max features = 1,000 | N-gram range = (1, 2) | Min DF = 2 | Max DF = 0.95
    """
    elements.append(Paragraph(hyper_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    vector_text = """
    Each log message m is transformed into a sparse vector: <b>φ_TF-IDF(m) = [v₁, v₂, ..., v₁₀₀₀]ᵀ ∈ ℝ¹⁰⁰⁰</b>
    where vⱼ is the TF-IDF score for the j-th feature (unigram or bigram).
    """
    elements.append(Paragraph(vector_text, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Control Encoding
    elements.append(Paragraph("2.2 Control ID and Family Encoding", heading2_style))
    control_text = """
    Control IDs (50 controls) and control families (7 families) are encoded as integers using label encoding:
    """
    elements.append(Paragraph(control_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    control_formula = "φ_control(c) = k ∈ {0, 1, ..., 49}  |  φ_family(f) = j ∈ {0, 1, ..., 6}"
    elements.append(Paragraph(control_formula, formula_style))
    elements.append(Spacer(1, 0.2*inch))

    # Feature Vector
    elements.append(Paragraph("2.3 Complete Feature Vector", heading2_style))
    feature_text = """
    The complete feature vector for event x = (m, c, f) concatenates all representations:
    """
    elements.append(Paragraph(feature_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    feature_formula = "<b>Φ(x) = [φ_TF-IDF(m); φ_control(c); φ_family(f)] ∈ ℝ¹⁰⁰³</b>"
    elements.append(Paragraph(feature_formula, formula_style))
    elements.append(Spacer(1, 0.1*inch))

    dim_text = """
    <b>Dimensionality:</b> d = 1,003 features (1,000 TF-IDF + 1 control ID + 1 control family + 1 anomaly score)
    """
    elements.append(Paragraph(dim_text, body_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 3. XGBoost Model
    elements.append(Paragraph("3. XGBoost Gradient Boosting", heading1_style))

    xgb_text = """
    XGBoost builds an ensemble of T decision trees sequentially. Each tree corrects the errors of previous trees
    by fitting to the gradient of the loss function.
    """
    elements.append(Paragraph(xgb_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    # Ensemble Prediction
    elements.append(Paragraph("3.1 Ensemble Prediction", heading2_style))
    ensemble_formula = "ŷᵢ = Σ fₜ(Φ(xᵢ)) for t=1 to T"
    elements.append(Paragraph(ensemble_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    ensemble_text = """
    where fₜ is the t-th tree (trained at iteration t) and T = 500 is the total number of trees.
    """
    elements.append(Paragraph(ensemble_text, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Objective Function
    elements.append(Paragraph("3.2 Objective Function", heading2_style))
    obj_text = """
    The objective at iteration t combines prediction loss and model complexity regularization:
    """
    elements.append(Paragraph(obj_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    obj_formula = "L⁽ᵗ⁾ = Σ ℓ(yᵢ, ŷᵢ⁽ᵗ⁾) + Σ Ω(fₖ) for k=1 to t"
    elements.append(Paragraph(obj_formula, formula_style))
    elements.append(Spacer(1, 0.1*inch))

    # Binary Cross-Entropy Loss
    elements.append(Paragraph("3.3 Binary Cross-Entropy Loss", heading2_style))
    bce_formula = "ℓ(y, ŷ) = -[y log(σ(ŷ)) + (1-y) log(1 - σ(ŷ))]"
    elements.append(Paragraph(bce_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    sigmoid_formula = "where σ(z) = 1 / (1 + e⁻ᶻ) is the sigmoid function"
    elements.append(Paragraph(sigmoid_formula, formula_style))
    elements.append(Spacer(1, 0.2*inch))

    # Gradient and Hessian
    elements.append(Paragraph("3.4 First and Second Order Gradients", heading2_style))
    grad_text = """
    XGBoost uses second-order Taylor approximation for efficient optimization. The gradients are:
    """
    elements.append(Paragraph(grad_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    grad_formula1 = "gᵢ = ∂ℓ/∂ŷ = σ(ŷᵢ⁽ᵗ⁻¹⁾) - yᵢ  (first-order gradient)"
    elements.append(Paragraph(grad_formula1, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    grad_formula2 = "hᵢ = ∂²ℓ/∂ŷ² = σ(ŷᵢ⁽ᵗ⁻¹⁾) × (1 - σ(ŷᵢ⁽ᵗ⁻¹⁾))  (second-order gradient / Hessian)"
    elements.append(Paragraph(grad_formula2, formula_style))
    elements.append(Spacer(1, 0.2*inch))

    # Regularization
    elements.append(Paragraph("3.5 Regularization Term", heading2_style))
    reg_text = """
    The complexity of tree fₜ with J leaf nodes is penalized to prevent overfitting:
    """
    elements.append(Paragraph(reg_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    reg_formula = "Ω(fₜ) = γJ + (1/2)λ Σ wⱼ² for j=1 to J"
    elements.append(Paragraph(reg_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    reg_params = """
    where γ = 0 (leaf penalty), λ = 1.0 (L2 regularization), and wⱼ is the weight of leaf j.
    """
    elements.append(Paragraph(reg_params, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Optimal Leaf Weight
    elements.append(Paragraph("3.6 Optimal Leaf Weight", heading2_style))
    leaf_text = """
    After removing constant terms, the optimal weight for leaf j is found by setting ∂L/∂wⱼ = 0:
    """
    elements.append(Paragraph(leaf_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    leaf_formula = "wⱼ* = -[Σ gᵢ for i in Iⱼ] / [Σ hᵢ for i in Iⱼ + λ]"
    elements.append(Paragraph(leaf_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    leaf_explanation = "where Iⱼ is the set of training instances assigned to leaf j."
    elements.append(Paragraph(leaf_explanation, body_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # Gain from Split
    elements.append(Paragraph("3.7 Split Gain Criterion", heading2_style))
    gain_text = """
    The gain from splitting a leaf into left (L) and right (R) children determines the best split:
    """
    elements.append(Paragraph(gain_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    gain_formula = "Gain = (1/2)[G_L²/(H_L + λ) + G_R²/(H_R + λ) - G²/(H + λ)] - γ"
    elements.append(Paragraph(gain_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    gain_explanation = """
    where G = Σgᵢ and H = Σhᵢ are the sum of gradients and Hessians. The split is performed only if Gain > 0.
    """
    elements.append(Paragraph(gain_explanation, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Class Imbalance
    elements.append(Paragraph("3.8 Class Imbalance Handling", heading2_style))
    imbalance_text = """
    To address class imbalance (compliant:non-compliant ≈ 5.75:1), we use scale_pos_weight:
    """
    elements.append(Paragraph(imbalance_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    imbalance_formula = "w_pos = N_negative / N_positive = 137,129 / 23,871 ≈ 5.75"
    elements.append(Paragraph(imbalance_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    imbalance_application = """
    This scales the gradient for positive (non-compliant) instances: gᵢ' = w_pos × gᵢ if yᵢ = 1
    """
    elements.append(Paragraph(imbalance_application, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Learning Rate Shrinkage
    elements.append(Paragraph("3.9 Learning Rate Shrinkage", heading2_style))
    lr_text = """
    After computing optimal leaf weights wⱼ*, we apply learning rate shrinkage to prevent overfitting:
    """
    elements.append(Paragraph(lr_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    lr_formula = "wⱼ = η × wⱼ*  where η = 0.1 (learning rate)"
    elements.append(Paragraph(lr_formula, formula_style))
    elements.append(Spacer(1, 0.1*inch))

    lr_explanation = """
    Smaller learning rates make the model more robust but require more trees. With η = 0.1 and T = 500, we achieve
    an optimal trade-off between accuracy and generalization.
    """
    elements.append(Paragraph(lr_explanation, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Final Prediction
    elements.append(Paragraph("3.10 Final Prediction", heading2_style))
    pred_text = "The raw prediction (logit) sums all tree outputs:"
    elements.append(Paragraph(pred_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    pred_formula1 = "ŷ_raw = Σ η × fₜ(Φ(x)) for t=1 to T"
    elements.append(Paragraph(pred_formula1, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    pred_formula2 = "P(y = 1 | x) = σ(ŷ_raw) = 1 / (1 + e⁻ŷ_raw)"
    elements.append(Paragraph(pred_formula2, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    pred_formula3 = "ŷ = 1 if P(y = 1 | x) ≥ 0.5, else ŷ = 0"
    elements.append(Paragraph(pred_formula3, formula_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 4. XGBoost Hyperparameters Table
    elements.append(Paragraph("3.11 XGBoost Phase 2.5 Hyperparameters", heading2_style))

    hyper_data = [
        ['Parameter', 'Value', 'Description'],
        ['n_estimators (T)', '500', 'Number of boosting rounds'],
        ['max_depth', '6', 'Maximum tree depth'],
        ['learning_rate (η)', '0.1', 'Step size shrinkage'],
        ['reg_lambda (λ)', '1.0', 'L2 regularization'],
        ['reg_alpha', '0.0', 'L1 regularization'],
        ['gamma (γ)', '0.0', 'Minimum loss reduction'],
        ['scale_pos_weight', '5.75', 'Class imbalance weight'],
        ['subsample', '1.0', 'Row sampling ratio'],
        ['colsample_bytree', '1.0', 'Column sampling ratio'],
        ['tree_method', 'hist', 'Histogram-based algorithm']
    ]

    hyper_table = Table(hyper_data, colWidths=[2*inch, 1.2*inch, 2.8*inch])
    hyper_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(hyper_table)
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # 4. Evaluation Metrics
    elements.append(Paragraph("4. Evaluation Metrics", heading1_style))

    # Confusion Matrix
    elements.append(Paragraph("4.1 Confusion Matrix", heading2_style))
    conf_text = "Test set of N_test = 24,477 events (after 15% split):"
    elements.append(Paragraph(conf_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    conf_data = [
        ['', '', 'Predicted', ''],
        ['', '', 'Compliant', 'Non-Compliant'],
        ['Actual', 'Compliant', 'TN = 13,541', 'FP = 11'],
        ['', 'Non-Compliant', 'FN = 114', 'TP = 10,811']
    ]

    conf_table = Table(conf_data, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1.8*inch])
    conf_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('SPAN', (0, 2), (0, 3)),
        ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#0066cc')),
        ('BACKGROUND', (0, 2), (0, 3), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (2, 0), (3, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 2), (0, 3), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (2, 2), (2, 2), colors.HexColor('#e6ffe6')),
        ('BACKGROUND', (3, 3), (3, 3), colors.HexColor('#e6ffe6')),
        ('BACKGROUND', (3, 2), (3, 2), colors.HexColor('#ffe6e6')),
        ('BACKGROUND', (2, 3), (2, 3), colors.HexColor('#ffe6e6')),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
    ]))

    elements.append(conf_table)
    elements.append(Spacer(1, 0.2*inch))

    # Metrics Formulas
    elements.append(Paragraph("4.2 Performance Metrics Formulas", heading2_style))

    metrics_list = [
        ("Accuracy", "(TP + TN) / (TP + TN + FP + FN)", "(10,811 + 13,541) / 24,477 = 0.9949", "99.49%"),
        ("Precision", "TP / (TP + FP)", "10,811 / (10,811 + 11) = 0.9990", "99.90%"),
        ("Recall", "TP / (TP + FN)", "10,811 / (10,811 + 114) = 0.9896", "98.96%"),
        ("F1 Score", "2 × (Precision × Recall) / (Precision + Recall)", "2 × (0.9990 × 0.9896) / (0.9990 + 0.9896)", "99.43%"),
        ("Specificity", "TN / (TN + FP)", "13,541 / (13,541 + 11) = 0.9992", "99.92%"),
        ("FPR", "FP / (FP + TN)", "11 / (11 + 13,541) = 0.0008", "0.08%"),
        ("FNR", "FN / (FN + TP)", "114 / (114 + 10,811) = 0.0104", "1.04%")
    ]

    for metric_name, formula, calculation, result in metrics_list:
        elements.append(Paragraph(f"<b>{metric_name}:</b>", body_style))
        elements.append(Paragraph(formula, formula_style))
        elements.append(Paragraph(f"{calculation} = <b>{result}</b>", body_style))
        elements.append(Spacer(1, 0.15*inch))

    elements.append(PageBreak())

    # Matthews Correlation Coefficient
    elements.append(Paragraph("4.3 Matthews Correlation Coefficient", heading2_style))
    mcc_text = """
    MCC provides a balanced measure even for imbalanced classes, ranging from -1 (total disagreement) to +1 (perfect prediction):
    """
    elements.append(Paragraph(mcc_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    mcc_formula = "MCC = (TP × TN - FP × FN) / √[(TP+FP)(TP+FN)(TN+FP)(TN+FN)]"
    elements.append(Paragraph(mcc_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    mcc_calc = "MCC = (10,811 × 13,541 - 11 × 114) / √[(10,822)(10,925)(13,552)(13,655)] = 0.9888"
    elements.append(Paragraph(mcc_calc, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    mcc_result = "<b>Result: 98.88% MCC</b> - Indicates excellent agreement between predictions and ground truth."
    elements.append(Paragraph(mcc_result, body_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # 5. SHAP Values
    elements.append(Paragraph("5. SHAP (Shapley Additive Explanations)", heading1_style))

    shap_text = """
    SHAP values provide model interpretability by quantifying each feature's contribution to individual predictions
    based on cooperative game theory.
    """
    elements.append(Paragraph(shap_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    # Shapley Value Formula
    elements.append(Paragraph("5.1 Shapley Value Theory", heading2_style))
    shapley_text = """
    For a prediction f(x), the Shapley value φⱼ for feature j quantifies its contribution:
    """
    elements.append(Paragraph(shapley_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    shapley_formula = "φⱼ(f, x) = Σ [|S|!(|F|-|S|-1)! / |F|!] × [f_{S∪{j}}(x) - f_S(x)]"
    elements.append(Paragraph(shapley_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    shapley_explanation = """
    where F is the set of all features, S is a subset of features not including j, and the sum is over all possible subsets S.
    """
    elements.append(Paragraph(shapley_explanation, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # TreeSHAP
    elements.append(Paragraph("5.2 TreeSHAP Algorithm", heading2_style))
    treeshap_text = """
    For tree-based models, TreeSHAP computes exact Shapley values efficiently in polynomial time O(TLD²) where
    T = 500 trees, L = max leaves per tree, and D = 6 (max depth).
    """
    elements.append(Paragraph(treeshap_text, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Additive Property
    elements.append(Paragraph("5.3 Additive Property", heading2_style))
    additive_formula = "f(x) = φ₀ + Σ φⱼ(f, x) for j=1 to d"
    elements.append(Paragraph(additive_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    additive_text = """
    where φ₀ = E[f(X)] is the expected prediction over the dataset (baseline). This decomposition allows us to
    understand which features push predictions toward compliant (negative SHAP) or non-compliant (positive SHAP).
    """
    elements.append(Paragraph(additive_text, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Feature Importance
    elements.append(Paragraph("5.4 Global Feature Importance", heading2_style))
    importance_text = "Global feature importance for feature j:"
    elements.append(Paragraph(importance_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    importance_formula = "Iⱼ = (1/N) × Σ |φⱼ(f, xᵢ)| for i=1 to N"
    elements.append(Paragraph(importance_formula, formula_style))
    elements.append(Spacer(1, 0.1*inch))

    # Top Features Table
    top_features_data = [
        ['Rank', 'Feature', 'SHAP Value (Iⱼ)', 'Interpretation'],
        ['1', 'tfidf_537', '2.1430', 'Dominant predictor (attack keywords)'],
        ['2', 'tfidf_950', '0.4259', 'Secondary strong predictor'],
        ['3', 'tfidf_426', '0.3528', 'Tertiary predictor'],
        ['4', 'tfidf_473', '0.3378', 'Access control terms'],
        ['5', 'tfidf_198', '0.2260', 'Authentication terms']
    ]

    top_features_table = Table(top_features_data, colWidths=[0.7*inch, 1.2*inch, 1.5*inch, 2.6*inch])
    top_features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(top_features_table)
    elements.append(Spacer(1, 0.1*inch))

    key_finding = """
    <b>Key Finding:</b> TF-IDF feature 537 has 5× higher importance than the second feature, suggesting it captures
    critical attack/violation keywords (e.g., "failed", "denied", "unauthorized").
    """
    elements.append(Paragraph(key_finding, body_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # 6. Security Mechanisms
    elements.append(Paragraph("6. Security Mechanisms", heading1_style))

    # JWT Authentication
    elements.append(Paragraph("6.1 JWT Authentication", heading2_style))
    jwt_text = """
    JSON Web Tokens (JWT) provide stateless authentication. A JWT is structured as:
    """
    elements.append(Paragraph(jwt_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    jwt_formula = "JWT = Base64URL(Header) || Base64URL(Payload) || Signature"
    elements.append(Paragraph(jwt_formula, formula_style))
    elements.append(Spacer(1, 0.1*inch))

    # HMAC-SHA256
    elements.append(Paragraph("<b>HMAC-SHA256 Signature:</b>", body_style))
    hmac_formula = "Signature = HMAC-SHA256(secret, Base64URL(Header) || Base64URL(Payload))"
    elements.append(Paragraph(hmac_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    hmac_definition = "HMAC-SHA256(K, m) = SHA256((K ⊕ opad) || SHA256((K ⊕ ipad) || m))"
    elements.append(Paragraph(hmac_definition, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    hmac_explanation = """
    where K is the secret key, opad = 0x5c5c...5c (outer padding), and ipad = 0x3636...36 (inner padding).
    Token expiry is set to 24 hours.
    """
    elements.append(Paragraph(hmac_explanation, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Rate Limiting
    elements.append(Paragraph("6.2 Rate Limiting (Token Bucket Algorithm)", heading2_style))
    rate_text = "Token bucket algorithm controls request rates:"
    elements.append(Paragraph(rate_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    rate_formula = "N(t) = min(C, N(t-1) + r × Δt)"
    elements.append(Paragraph(rate_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    rate_params = """
    where N(t) = number of tokens at time t, C = 60 (bucket capacity - requests/min), r = 1 (refill rate - tokens/sec),
    and Δt = time elapsed. Request is allowed if N(t) ≥ 1.
    """
    elements.append(Paragraph(rate_params, body_style))
    elements.append(Spacer(1, 0.1*inch))

    rate_limits = "<b>Limits:</b> 60 requests/min, 1,000 requests/hour, 10,000 requests/day"
    elements.append(Paragraph(rate_limits, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Adversarial Detection
    elements.append(Paragraph("6.3 Adversarial Detection", heading2_style))
    adv_text = "Statistical anomaly detection using z-score on SHAP values:"
    elements.append(Paragraph(adv_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    adv_formula = "zᵢ = |φᵢ(f, x) - μᵢ| / σᵢ"
    elements.append(Paragraph(adv_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    adv_explanation = """
    where φᵢ(f, x) is the SHAP value for feature i, μᵢ = E[φᵢ(f, X)] is the expected SHAP value, and
    σᵢ = √Var[φᵢ(f, X)] is the standard deviation. Flag as adversarial if max(zᵢ) > τ where τ = 3.0 (threshold).
    """
    elements.append(Paragraph(adv_explanation, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Model Integrity
    elements.append(Paragraph("6.4 Model Integrity Verification", heading2_style))
    integrity_text = "HMAC-SHA256 signature of model file ensures tamper detection:"
    elements.append(Paragraph(integrity_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    integrity_formula = "σ = HMAC-SHA256(K_sign, M)"
    elements.append(Paragraph(integrity_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    integrity_explanation = """
    where M is the serialized model and K_sign is a 64-byte random signing key. Verification checks if
    σ = HMAC-SHA256(K_sign, M). Models are verified on load and every 24 hours.
    """
    elements.append(Paragraph(integrity_explanation, body_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # 7. Computational Complexity
    elements.append(Paragraph("7. Computational Complexity", heading1_style))

    # Training Complexity
    elements.append(Paragraph("7.1 Training Complexity", heading2_style))
    train_text = "Per tree: O(n × d × log(n)) for sorting features during split finding"
    elements.append(Paragraph(train_text, body_style))
    elements.append(Spacer(1, 0.05*inch))

    train_formula = "Total training: O(T × n × d × log(n))"
    elements.append(Paragraph(train_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    train_calc = """
    With T = 500, n = 140,000, d = 1,003: Operations ≈ 500 × 140,000 × 1,003 × log(140,000) ≈ 1.2 × 10¹²
    """
    elements.append(Paragraph(train_calc, body_style))
    elements.append(Spacer(1, 0.05*inch))

    train_time = "<b>Actual training time: ~2 minutes on CPU (Intel/AMD, 4+ cores)</b>"
    elements.append(Paragraph(train_time, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Inference Complexity
    elements.append(Paragraph("7.2 Inference Complexity", heading2_style))
    inf_text = "Per tree: O(d_max) for tree traversal (maximum depth = 6)"
    elements.append(Paragraph(inf_text, body_style))
    elements.append(Spacer(1, 0.05*inch))

    inf_formula = "Total inference: O(T × d_max) = O(500 × 6) = O(3,000)"
    elements.append(Paragraph(inf_formula, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    inf_time = "<b>Actual inference time: ~1 ms per log event | Throughput: 1,000 logs/second</b>"
    elements.append(Paragraph(inf_time, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Memory Complexity
    elements.append(Paragraph("7.3 Memory Complexity", heading2_style))
    mem_text1 = "TF-IDF Vectorizer: O(vocab_size × features) = O(50,000 × 1,000) ≈ 1.2 MB"
    elements.append(Paragraph(mem_text1, body_style))
    elements.append(Spacer(1, 0.05*inch))

    mem_text2 = "XGBoost Model: O(T × J × d_max) where J ≈ 64 leaves per tree"
    elements.append(Paragraph(mem_text2, body_style))
    elements.append(Spacer(1, 0.05*inch))

    mem_calc = "Model size ≈ 500 × 64 × 6 × 8 bytes ≈ 1.5 MB"
    elements.append(Paragraph(mem_calc, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    mem_total = "<b>Total model size: 3.2 MB</b> (model + vectorizers + encoders)"
    elements.append(Paragraph(mem_total, body_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # 8. Model Comparison
    elements.append(Paragraph("8. Model Comparison: Phase 2 vs Phase 2.5", heading1_style))

    comparison_text = """
    Phase 2 exhibited systematic "compliant bias" - the model defaulted to predicting compliant when uncertain,
    resulting in only 58.3% detection rate on real attack scenarios.
    """
    elements.append(Paragraph(comparison_text, body_style))
    elements.append(Spacer(1, 0.1*inch))

    # Phase 2 Issue
    elements.append(Paragraph("8.1 Phase 2 Compliant Bias", heading2_style))
    phase2_issue = "P_Phase2(y = 1 | x_attack) ≈ 0.1  (should be close to 1.0)"
    elements.append(Paragraph(phase2_issue, formula_style))
    elements.append(Spacer(1, 0.05*inch))

    phase2_text = """
    This bias arose from training only on 100K synthetic events without diverse real-world attack patterns.
    """
    elements.append(Paragraph(phase2_text, body_style))
    elements.append(Spacer(1, 0.2*inch))

    # Phase 2.5 Improvements
    elements.append(Paragraph("8.2 Phase 2.5 Improvements", heading2_style))

    improvements = [
        ("Data Augmentation", "Added 37,000 targeted non-compliant samples from NSL-KDD and LogHub"),
        ("Class Weight Adjustment", "Updated scale_pos_weight from 2.17 to 5.75"),
        ("Public Dataset Integration", "Integrated NSL-KDD (52%) + LogHub (18%) + Synthetic (30%)")
    ]

    for title, description in improvements:
        elements.append(Paragraph(f"<b>{title}:</b> {description}", body_style))
        elements.append(Spacer(1, 0.1*inch))

    elements.append(Spacer(1, 0.1*inch))

    # Performance Comparison Table
    comparison_data = [
        ['Scenario', 'Phase 2', 'Phase 2.5', 'Improvement'],
        ['Phishing Detection', '6.6%', '99.9%', '+93.3%'],
        ['Insider Threat', '9.0%', '100.0%', '+91.0%'],
        ['DDoS Attack', '6.3%', '100.0%', '+93.7%'],
        ['Credential Stuffing', '6.7%', '100.0%', '+93.3%'],
        ['Lateral Movement', '11.3%', '96.9%', '+85.6%'],
        ['Brute Force Attack', '95.2%', '100.0%', '+4.8%'],
        ['Data Exfiltration', '98.1%', '100.0%', '+1.9%'],
        ['Overall', '58.3% (7/12)', '100% (12/12)', '+41.7%']
    ]

    comparison_table = Table(comparison_data, colWidths=[2.2*inch, 1.2*inch, 1.3*inch, 1.3*inch])
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e6f2ff')),
        ('TEXTCOLOR', (1, 1), (1, -2), colors.red),
        ('TEXTCOLOR', (2, 1), (2, -1), colors.darkgreen),
        ('TEXTCOLOR', (3, 1), (3, -1), colors.darkgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(comparison_table)
    elements.append(Spacer(1, 0.1*inch))

    verdict = """
    <b>Verdict:</b> Phase 2.5 achieves 100% detection on real-world attack scenarios, fixing all critical failures
    from Phase 2. The improvement of +41.7% demonstrates the effectiveness of targeted data augmentation and
    class rebalancing.
    """
    elements.append(Paragraph(verdict, body_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # 9. Results Summary
    elements.append(Paragraph("9. Empirical Results Summary", heading1_style))

    results_data = [
        ['Metric', 'Value', 'Interpretation'],
        ['Accuracy', '99.49%', 'Overall correctness'],
        ['Precision (Non-Compliant)', '99.90%', 'Rarely wrong about violations'],
        ['Recall (Non-Compliant)', '98.96%', 'Detects 98.96% of violations'],
        ['F1 Score', '99.43%', 'Harmonic mean of precision/recall'],
        ['Specificity', '99.92%', 'Correctly identifies compliant events'],
        ['MCC', '98.88%', 'Balanced measure for imbalanced classes'],
        ['Real Scenarios Detected', '12/12 (100%)', 'All diverse attacks detected'],
        ['Novel Attacks Detected', '6/6 (100%)', 'Generalizes to unseen attacks'],
        ['Inference Time', '1 ms/event', 'Real-time capability'],
        ['Throughput', '1,000 logs/sec', 'High-volume processing'],
        ['Training Time', '~2 minutes', 'Fast retraining capability'],
        ['Model Size', '3.2 MB', 'Lightweight deployment']
    ]

    results_table = Table(results_data, colWidths=[2.5*inch, 1.8*inch, 1.7*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(results_table)
    elements.append(Spacer(1, 0.3*inch))

    # 10. Conclusion
    elements.append(Paragraph("10. Conclusion", heading1_style))

    conclusion_text = """
    The Rwanda NCSA Compliance Monitoring System achieves production-grade performance through rigorous application
    of gradient boosting theory, TF-IDF text vectorization, and comprehensive feature engineering. The mathematical
    formulations presented in this document provide a complete specification for reproducing and extending the model.
    """
    elements.append(Paragraph(conclusion_text, body_style))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("<b>Key Mathematical Innovations:</b>", body_style))
    innovations = [
        "Second-order Taylor approximation for efficient gradient boosting",
        "TF-IDF with bigrams (n-grams) for semantic log understanding",
        "Class-weighted loss function to address 5.75:1 imbalance",
        "SHAP values for model interpretability and explainability",
        "Statistical adversarial detection using z-score thresholds"
    ]

    for innovation in innovations:
        elements.append(Paragraph(f"• {innovation}", body_style))
        elements.append(Spacer(1, 0.05*inch))

    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("<b>Future Mathematical Extensions:</b>", body_style))
    future = [
        "Attention mechanisms for long log sequences (Transformer-based models)",
        "Bayesian hyperparameter optimization for automated tuning",
        "Conformal prediction for uncertainty quantification",
        "Online learning algorithms for streaming data adaptation",
        "Multi-task learning for simultaneous control family prediction"
    ]

    for item in future:
        elements.append(Paragraph(f"• {item}", body_style))
        elements.append(Spacer(1, 0.05*inch))

    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())

    # References
    elements.append(Paragraph("References", heading1_style))

    references = [
        "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. <i>Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</i>, 785-794.",

        "Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. <i>Advances in Neural Information Processing Systems</i> (NeurIPS), 4765-4774.",

        "Tavallaee, M., Bagheri, E., Lu, W., & Ghorbani, A. A. (2009). A detailed analysis of the KDD CUP 99 data set. <i>IEEE Symposium on Computational Intelligence for Security and Defense Applications</i> (CISDA).",

        "NIST Special Publication 800-53 Revision 5. (2020). <i>Security and Privacy Controls for Information Systems and Organizations</i>. National Institute of Standards and Technology.",

        "Rwanda National Cyber Security Authority. (2024). <i>Cybersecurity Compliance Framework for Critical Infrastructure</i>. Government of Rwanda.",

        "He, S., Zhu, J., He, P., & Lyu, M. R. (2020). LogHub: A large collection of system log datasets towards automated log analytics. <i>arXiv preprint arXiv:2008.06448</i>.",

        "Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. <i>Annals of Statistics</i>, 29(5), 1189-1232."
    ]

    for i, ref in enumerate(references, 1):
        elements.append(Paragraph(f"[{i}] {ref}", body_style))
        elements.append(Spacer(1, 0.1*inch))

    elements.append(Spacer(1, 0.3*inch))

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = """
    <para align=center>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━<br/>
    <b>Rwanda National Cyber Security Authority</b><br/>
    Compliance Monitoring System<br/>
    Mathematical Formulations Document<br/>
    Version 2.5.0 | November 2025<br/>
    <br/>
    Moise Iradukunda | Carnegie Mellon University<br/>
    miraduku@andrew.cmu.edu<br/>
    <br/>
    <i>Generated with Claude Code</i><br/>
    https://claude.com/claude-code
    </para>
    """
    elements.append(Paragraph(footer_text, author_style))

    # Build PDF
    doc.build(elements)
    print(f"✅ PDF generated successfully: {output_path}")
    print(f"   Size: {os.path.getsize(output_path) / 1024:.1f} KB")

if __name__ == "__main__":
    create_mathematical_formulations_pdf()
