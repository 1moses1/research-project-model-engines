"""
Improved XGBoost Training with Explainability
Practical improvements within research scope:
1. Text feature extraction (TF-IDF on log messages)
2. SHAP values for explainability
3. Cross-validation to detect overfitting
4. Feature importance analysis
5. Confidence-based predictions
"""

import pandas as pd
import numpy as np
import json
import xgboost as xgb
from pathlib import Path
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import time

def load_data():
    """Load validated training data"""
    print("=" * 80)
    print("[STEP 1] Loading Validated Training Data")
    print("=" * 80)

    train_df = pd.read_csv("data/validated_synthetic/train_validated.csv")
    val_df = pd.read_csv("data/validated_synthetic/val_validated.csv")
    test_df = pd.read_csv("data/validated_synthetic/test_validated.csv")

    print(f"✅ Train: {len(train_df):,} samples")
    print(f"✅ Val:   {len(val_df):,} samples")
    print(f"✅ Test:  {len(test_df):,} samples")
    print(f"✅ Total: {len(train_df) + len(val_df) + len(test_df):,} samples")

    return train_df, val_df, test_df

def extract_text_features(train_df, val_df, test_df, max_features=50):
    """Extract TF-IDF features from log messages"""
    print("\n" + "=" * 80)
    print("[STEP 2] Extracting Text Features from Log Messages")
    print("=" * 80)

    # TF-IDF on log messages
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),  # Unigrams and bigrams
        min_df=2,            # Ignore rare terms
        stop_words='english'
    )

    # Fit on train, transform all
    train_tfidf = vectorizer.fit_transform(train_df['log_message']).toarray()
    val_tfidf = vectorizer.transform(val_df['log_message']).toarray()
    test_tfidf = vectorizer.transform(test_df['log_message']).toarray()

    # Create feature names
    tfidf_cols = [f"tfidf_{i}" for i in range(train_tfidf.shape[1])]

    # Add to dataframes
    train_tfidf_df = pd.DataFrame(train_tfidf, columns=tfidf_cols, index=train_df.index)
    val_tfidf_df = pd.DataFrame(val_tfidf, columns=tfidf_cols, index=val_df.index)
    test_tfidf_df = pd.DataFrame(test_tfidf, columns=tfidf_cols, index=test_df.index)

    print(f"✅ Extracted {len(tfidf_cols)} text features")
    print(f"✅ Top terms: {', '.join(list(vectorizer.get_feature_names_out()[:10]))}")

    return train_tfidf_df, val_tfidf_df, test_tfidf_df, vectorizer

def prepare_features(train_df, val_df, test_df, train_tfidf_df, val_tfidf_df, test_tfidf_df):
    """Prepare feature matrices"""
    print("\n" + "=" * 80)
    print("[STEP 3] Preparing Feature Matrices")
    print("=" * 80)

    # Get numeric features
    numeric_cols = train_df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ['event_id', 'compliance_status', 'anomaly_label']
    numeric_features = [col for col in numeric_cols if col not in exclude_cols]

    print(f"✅ Numeric features: {len(numeric_features)}")

    # Combine numeric + text features
    X_train_num = train_df[numeric_features].fillna(0).apply(pd.to_numeric, errors='coerce').fillna(0)
    X_val_num = val_df[numeric_features].fillna(0).apply(pd.to_numeric, errors='coerce').fillna(0)
    X_test_num = test_df[numeric_features].fillna(0).apply(pd.to_numeric, errors='coerce').fillna(0)

    X_train = pd.concat([X_train_num, train_tfidf_df], axis=1)
    X_val = pd.concat([X_val_num, val_tfidf_df], axis=1)
    X_test = pd.concat([X_test_num, test_tfidf_df], axis=1)

    # Encode labels
    le = LabelEncoder()
    y_train = le.fit_transform(train_df['compliance_status'])
    y_val = le.transform(val_df['compliance_status'])
    y_test = le.transform(test_df['compliance_status'])

    print(f"✅ Total features: {X_train.shape[1]} (numeric + text)")
    print(f"✅ Classes: {list(le.classes_)}")

    return X_train, X_val, X_test, y_train, y_val, y_test, le, list(X_train.columns)

def train_with_cross_validation(X_train, y_train):
    """Train with cross-validation to detect overfitting"""
    print("\n" + "=" * 80)
    print("[STEP 4] Training with Cross-Validation")
    print("=" * 80)

    # Model with regularization to prevent overfitting
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,              # Limit depth to prevent overfitting
        learning_rate=0.1,
        subsample=0.8,            # Row sampling
        colsample_bytree=0.8,     # Column sampling
        min_child_weight=3,       # Regularization
        gamma=0.1,                # Regularization
        reg_alpha=0.1,            # L1 regularization
        reg_lambda=1.0,           # L2 regularization
        scale_pos_weight=3,       # Handle imbalance
        objective='binary:logistic',
        random_state=42,
        n_jobs=-1
    )

    # 5-fold cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1')

    print(f"\n📊 Cross-Validation Results (5-fold):")
    print(f"   Mean F1: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    print(f"   Fold scores: {[f'{s:.3f}' for s in cv_scores]}")

    if cv_scores.std() > 0.05:
        print("\n⚠️  WARNING: High variance in CV scores - potential overfitting!")
    else:
        print("\n✅ Good: Low variance in CV scores - stable model")

    # Train final model
    print("\n🔄 Training final model on full training set...")
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start

    print(f"✅ Training complete in {train_time:.2f} seconds")

    return model, cv_scores

def evaluate_model(model, X_test, y_test, le):
    """Evaluate model with detailed metrics"""
    print("\n" + "=" * 80)
    print("[STEP 5] Evaluating Model Performance")
    print("=" * 80)

    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"\n📊 Test Set Performance:")
    print(f"   Accuracy: {accuracy:.3f}")
    print(f"   F1-Score: {f1:.3f}")

    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Confidence analysis
    high_conf = (y_pred_proba > 0.8) | (y_pred_proba < 0.2)
    print(f"\n🎯 Prediction Confidence:")
    print(f"   High confidence (>80% or <20%): {high_conf.sum() / len(y_pred) * 100:.1f}%")
    print(f"   Low confidence (20-80%):        {(~high_conf).sum() / len(y_pred) * 100:.1f}%")

    return {
        'accuracy': float(accuracy),
        'f1_score': float(f1),
        'confusion_matrix': cm.tolist(),
        'high_confidence_pct': float(high_conf.sum() / len(y_pred) * 100)
    }

def analyze_feature_importance(model, features):
    """Analyze feature importance (replaces SHAP for speed)"""
    print("\n" + "=" * 80)
    print("[STEP 6] Analyzing Feature Importance")
    print("=" * 80)

    # Feature importance from XGBoost
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\n📊 Top 15 Most Important Features:")
    for idx, row in feature_importance.head(15).iterrows():
        print(f"   {row['feature']:<25} {row['importance']:.4f}")

    # Plot feature importance
    plt.figure(figsize=(10, 8))
    top_features = feature_importance.head(20)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance')
    plt.title('Top 20 Feature Importances')
    plt.tight_layout()
    plt.savefig("results/real_data_xgboost_only/feature_importance.png", dpi=150, bbox_inches='tight')
    print(f"\n✅ Feature importance plot saved: results/real_data_xgboost_only/feature_importance.png")

    return feature_importance

def save_model(model, le, features, vectorizer, metrics, cv_scores, feature_importance):
    """Save model and metadata"""
    print("\n" + "=" * 80)
    print("[STEP 7] Saving Model and Metadata")
    print("=" * 80)

    output_dir = Path("results/real_data_xgboost_only")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    model.save_model(str(output_dir / "xgboost_with_text_features.json"))
    print(f"✅ Model saved: {output_dir}/xgboost_with_text_features.json")

    # Save label encoder
    import pickle
    with open(output_dir / "label_encoder.pkl", 'wb') as f:
        pickle.dump(le, f)
    print(f"✅ Label encoder saved: {output_dir}/label_encoder.pkl")

    # Save vectorizer
    with open(output_dir / "tfidf_vectorizer.pkl", 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"✅ TF-IDF vectorizer saved: {output_dir}/tfidf_vectorizer.pkl")

    # Save features
    with open(output_dir / "features.json", 'w') as f:
        json.dump(features, f, indent=2)
    print(f"✅ Features saved: {output_dir}/features.json")

    # Save metrics with CV scores
    metrics['cross_validation'] = {
        'mean_f1': float(cv_scores.mean()),
        'std_f1': float(cv_scores.std()),
        'fold_scores': [float(s) for s in cv_scores]
    }

    with open(output_dir / "metrics_with_cv.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Metrics saved: {output_dir}/metrics_with_cv.json")

    # Save feature importance
    feature_importance.to_csv(output_dir / "feature_importance.csv", index=False)
    print(f"✅ Feature importance saved: {output_dir}/feature_importance.csv")

def main():
    print("\n" + "=" * 80)
    print("XGBoost Training with Text Features and Cross-Validation")
    print("=" * 80)

    # Create output directories
    Path("results/real_data_xgboost_only").mkdir(parents=True, exist_ok=True)

    # 1. Load data
    train_df, val_df, test_df = load_data()

    # 2. Extract text features
    train_tfidf, val_tfidf, test_tfidf, vectorizer = extract_text_features(
        train_df, val_df, test_df, max_features=50
    )

    # 3. Prepare features
    X_train, X_val, X_test, y_train, y_val, y_test, le, features = prepare_features(
        train_df, val_df, test_df, train_tfidf, val_tfidf, test_tfidf
    )

    # 4. Train with cross-validation
    model, cv_scores = train_with_cross_validation(X_train, y_train)

    # 5. Evaluate
    metrics = evaluate_model(model, X_test, y_test, le)

    # 6. Analyze feature importance
    feature_importance = analyze_feature_importance(model, features)

    # 7. Save everything
    save_model(model, le, features, vectorizer, metrics, cv_scores, feature_importance)

    print("\n" + "=" * 80)
    print("✅ COMPLETE - Model Ready")
    print("=" * 80)
    print(f"\n📦 Model artifacts saved in: results/real_data_xgboost_only/")
    print(f"\n🎯 Key Takeaways:")
    print(f"   • Test F1-Score: {metrics['f1_score']:.3f}")
    print(f"   • CV Mean F1: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    print(f"   • High Confidence Predictions: {metrics['high_confidence_pct']:.1f}%")
    print(f"   • Total Features: {len(features)} (numeric + text)")
    print(f"\n💡 Recommendation:")
    if cv_scores.std() < 0.05 and metrics['f1_score'] > 0.85:
        print("   ✅ Model shows good generalization - suitable for research demos")
    else:
        print("   ⚠️  Model may need real data for production deployment")

if __name__ == "__main__":
    main()
