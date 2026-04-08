import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

# Add this import at the top of train.py
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from features.engineer import engineer_features

os.makedirs('models/saved', exist_ok=True)

def train_all_models():
    print("Loading data...")
    df = pd.read_csv('data/raw_transactions.csv')
    df, feature_cols = engineer_features(df)
    df = df.dropna(subset=feature_cols)
    
    X = df[feature_cols].values
    y = df['is_fraud'].values
    
    # ── SCALE FEATURES ──────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, 'models/saved/scaler.pkl')
    joblib.dump(feature_cols, 'models/saved/feature_cols.pkl')
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # ── MODEL 1: ISOLATION FOREST (unsupervised) ─────────────────
    print("\nTraining Isolation Forest...")
    iso = IsolationForest(
        n_estimators=200,
        contamination=0.06,   # ~6% fraud rate
        max_features=0.8,
        random_state=42,
        n_jobs=-1
    )
    iso.fit(X_train)
    joblib.dump(iso, 'models/saved/isolation_forest.pkl')
    
    # Isolation Forest score: -1=anomaly, 1=normal → convert to probability
    iso_scores = -iso.score_samples(X_test)  # higher = more anomalous
    iso_pred = (iso_scores > np.percentile(iso_scores, 94)).astype(int)
    
    from sklearn.metrics import classification_report
    print("Isolation Forest:")
    print(classification_report(y_test, iso_pred))
    
    # ── MODEL 2: XGBOOST (supervised) ───────────────────────────
    print("\nTraining XGBoost...")
    scale_pos_weight = (y == 0).sum() / (y == 1).sum()  # handle imbalance
    
    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric='logloss',
        random_state=42,
        n_jobs=-1
    )
    xgb.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=50
    )
    joblib.dump(xgb, 'models/saved/xgboost.pkl')
    
    xgb_prob = xgb.predict_proba(X_test)[:,1]
    xgb_pred = (xgb_prob > 0.4).astype(int)  # lower threshold = higher recall
    
    print("\nXGBoost:")
    print(classification_report(y_test, xgb_pred))
    
    # ── ENSEMBLE SCORE ──────────────────────────────────────────
    # Combine both models: weighted average
    iso_prob_test = (-iso.score_samples(X_test) - (-iso.score_samples(X_test)).min())
    iso_prob_test = iso_prob_test / iso_prob_test.max()
    
    ensemble = 0.4 * iso_prob_test + 0.6 * xgb_prob
    ensemble_pred = (ensemble > 0.45).astype(int)
    
    print("\nEnsemble (ISO + XGB):")
    print(classification_report(y_test, ensemble_pred))
    
    # Save test results for dashboard
    results = pd.DataFrame({
        'y_true': y_test,
        'xgb_prob': xgb_prob,
        'iso_score': iso_prob_test,
        'ensemble_score': ensemble,
        'predicted_fraud': ensemble_pred
    })
    results.to_csv('data/test_results.csv', index=False)
    
    print("\n✅ All models saved to models/saved/")
    return xgb, iso, scaler, feature_cols

if __name__ == "__main__":
    train_all_models()