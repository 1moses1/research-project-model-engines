"""
Explainability CLI for XGBoost Compliance Model
Explains WHY an event was flagged as non-compliant
"""

import pandas as pd
import numpy as np
import json
import pickle
import xgboost as xgb
from pathlib import Path
import argparse

def load_model():
    """Load trained model and artifacts"""
    model_path = "results/real_data_xgboost_only/xgboost_with_text_features.json"
    le_path = "results/real_data_xgboost_only/label_encoder.pkl"
    vec_path = "results/real_data_xgboost_only/tfidf_vectorizer.pkl"
    features_path = "results/real_data_xgboost_only/features.json"

    model = xgb.XGBClassifier()
    model.load_model(model_path)

    with open(le_path, 'rb') as f:
        le = pickle.load(f)

    with open(vec_path, 'rb') as f:
        vectorizer = pickle.load(f)

    with open(features_path, 'r') as f:
        features = json.load(f)

    return model, le, vectorizer, features

def prepare_event(event, vectorizer, features):
    """Prepare single event for prediction"""
    # Extract text features
    log_message = event.get('log_message', '')
    tfidf = vectorizer.transform([log_message]).toarray()[0]

    # Combine with numeric features
    feature_values = []
    tfidf_idx = 0

    for feat in features:
        if feat.startswith('tfidf_'):
            feature_values.append(tfidf[tfidf_idx])
            tfidf_idx += 1
        else:
            feature_values.append(event.get(feat, 0))

    return np.array([feature_values])

def explain_prediction(model, X, features, event):
    """Explain why prediction was made"""
    # Get prediction
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    # Get feature contributions (approximate with feature_importances * values)
    contributions = model.feature_importances_ * X[0]

    # Get top contributing features
    contrib_df = pd.DataFrame({
        'feature': features,
        'value': X[0],
        'importance': model.feature_importances_,
        'contribution': contributions
    }).sort_values('contribution', ascending=False)

    return pred, proba, contrib_df

def main():
    parser = argparse.ArgumentParser(description='Explain compliance predictions')
    parser.add_argument('--event-file', type=str, help='JSON file with event data')
    parser.add_argument('--log-message', type=str, help='Log message to analyze')
    parser.add_argument('--status-code', type=int, default=200, help='HTTP status code')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    print("=" * 80)
    print("XGBoost Compliance Explainability CLI")
    print("=" * 80)

    # Load model
    print("\n🔄 Loading model...")
    model, le, vectorizer, features = load_model()
    print("✅ Model loaded")

    # Get event data
    if args.event_file:
        with open(args.event_file, 'r') as f:
            event = json.load(f)
    elif args.interactive:
        print("\n📝 Enter event details:")
        event = {
            'log_message': input("Log message: "),
            'status_code': int(input("Status code (default 200): ") or 200),
            'hour_of_day': int(input("Hour of day (0-23): ") or 12),
            'port': int(input("Port (default 443): ") or 443)
        }
    else:
        # Use command line args
        event = {
            'log_message': args.log_message or "User login successful",
            'status_code': args.status_code,
            'hour_of_day': 12,
            'port': 443
        }

    print("\n📋 Event:")
    print(json.dumps(event, indent=2))

    # Prepare and predict
    X = prepare_event(event, vectorizer, features)
    pred, proba, contrib_df = explain_prediction(model, X, features, event)

    # Display results
    print("\n" + "=" * 80)
    print("PREDICTION RESULT")
    print("=" * 80)

    prediction = le.classes_[pred]
    confidence = proba[pred] * 100

    print(f"\n🎯 Prediction: {prediction.upper()}")
    print(f"📊 Confidence: {confidence:.1f}%")
    print(f"   Compliant:     {proba[0]*100:.1f}%")
    print(f"   Non-compliant: {proba[1]*100:.1f}%")

    # Show top contributing features
    print("\n" + "=" * 80)
    print("TOP CONTRIBUTING FEATURES")
    print("=" * 80)

    print("\nTop 10 features that influenced this prediction:\n")
    for idx, row in contrib_df.head(10).iterrows():
        # Decode feature name
        feat_name = row['feature']
        if feat_name.startswith('tfidf_'):
            feat_idx = int(feat_name.split('_')[1])
            vocab = vectorizer.get_feature_names_out()
            if feat_idx < len(vocab):
                feat_name = f"Text: '{vocab[feat_idx]}'"

        print(f"{idx+1}. {feat_name:<30} (contribution: {row['contribution']:.4f})")
        print(f"   Value: {row['value']:.4f} | Importance: {row['importance']:.4f}")
        print()

    # Recommendation
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    if prediction == 'non_compliant':
        print("\n⚠️  This event was flagged as NON-COMPLIANT")
        print("\nPossible reasons:")
        top_feat = contrib_df.iloc[0]['feature']
        if 'status_code' in top_feat:
            print("• HTTP status code indicates an error or unauthorized access")
        print("• Review the event context and verify if this is a legitimate violation")
        print("• Check associated control requirements in Rwanda NCSA framework")
    else:
        print("\n✅ This event appears COMPLIANT")
        print("\nNo immediate action required, but consider:")
        print("• Periodic review of compliant events for anomalies")
        print("• Ensure proper logging is maintained per Rwanda NCSA requirements")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
