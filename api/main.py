from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
import joblib
import json
import sqlite3
import os
import time
from datetime import datetime
from contextlib import asynccontextmanager

# --- GLOBAL MODEL VARIABLES ---
xgb_model = None
iso_model = None
scaler = None
feature_cols = []
threshold = 0.5

# ── LIFESPAN (Handles Startup and Shutdown) ────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global xgb_model, iso_model, scaler, feature_cols, threshold
    
    # Ensure directories exist
    os.makedirs('models/saved', exist_ok=True)
    os.makedirs('data', exist_ok=True)

    # Attempt to load models
    try:
        xgb_model    = joblib.load('models/saved/xgboost.pkl')
        iso_model    = joblib.load('models/saved/isolation_forest.pkl')
        scaler       = joblib.load('models/saved/scaler.pkl')
        feature_cols = joblib.load('models/saved/feature_cols.pkl')
        
        with open('models/saved/threshold.json') as f:
            threshold = json.load(f).get('threshold', 0.5)
        print(f"✅ Models loaded. Threshold: {threshold}")
    except Exception as e:
        print(f"⚠️  Warning: Models not loaded. Please run training script. Error: {e}")

    # Init SQLite
    conn = sqlite3.connect('data/transactions.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS scored_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT, timestamp TEXT, sender_upi TEXT, 
        receiver_upi TEXT, amount REAL, fraud_score REAL, 
        is_flagged INTEGER, scored_at TEXT
    )''')
    conn.commit()
    conn.close()

    yield # API starts here

# ── APP INIT ──────────────────────────────────────────────────
app = FastAPI(title="UPI Fraud Detector API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SCHEMAS ───────────────────────────────────────────────────
class Transaction(BaseModel):
    transaction_id: str
    sender_upi: str
    receiver_upi: str
    amount: float
    transaction_type: str = "P2P"
    bank: str = "SBI"
    device_id: str = "dev_1234"
    location_pin: str = "560001"
    timestamp: Optional[str] = None

class FraudResult(BaseModel):
    transaction_id: str
    fraud_score: float
    is_fraud: bool
    risk_level: str
    reasons: List[str]
    processing_ms: float

# ── LOGIC ─────────────────────────────────────────────────────
def extract_features_single(txn: Transaction) -> np.ndarray:
    ts = datetime.fromisoformat(txn.timestamp) if txn.timestamp else datetime.now()
    features = {
        'hour': ts.hour,
        'day_of_week': ts.weekday(),
        'is_weekend': int(ts.weekday() in [5, 6]),
        'is_late_night': int(0 <= ts.hour <= 5),
        'is_business_hours': int(9 <= ts.hour <= 18),
        'log_amount': np.log1p(txn.amount),
        'is_round_amount': int(txn.amount % 1000 == 0),
        'amount_zscore': (txn.amount - 5000) / 8000,
        'txn_count_1h': 1, 'txn_sum_1h': txn.amount, 'txn_count_24h': 1,
        'receiver_familiarity': 0, 'is_new_receiver': 1,
        'amount_vs_user_avg': txn.amount / 5000,
        'txn_type_enc': 0 if txn.transaction_type == 'P2P' else 1,
        'bank_enc': 0, # Defaulting to 0 for stability
        'suspicious_device': int(txn.device_id.split('_')[-1].isdigit() and int(txn.device_id.split('_')[-1]) >= 9000)
    }
    return np.array([[features.get(c, 0) for c in feature_cols]])

@app.post("/score", response_model=FraudResult)
def score_transaction(txn: Transaction):
    start = time.time()
    if xgb_model is None:
        raise HTTPException(status_code=503, detail="Models not found in models/saved/")
    
    try:
        X = extract_features_single(txn)
        X_scaled = scaler.transform(X)
        xgb_prob = float(xgb_model.predict_proba(X_scaled)[0, 1])
        iso_raw = float(-iso_model.score_samples(X_scaled)[0])
        iso_prob = min(max((iso_raw + 0.5) / 1.5, 0), 1)
        
        fraud_score = round(0.4 * iso_prob + 0.6 * xgb_prob, 4)
        is_fraud = bool(fraud_score >= threshold)
        
        # Simple logging to DB
        conn = sqlite3.connect('data/transactions.db')
        conn.execute("INSERT INTO scored_transactions (transaction_id, timestamp, sender_upi, receiver_upi, amount, fraud_score, is_flagged, scored_at) VALUES (?,?,?,?,?,?,?,?)",
                     (txn.transaction_id, txn.timestamp, txn.sender_upi, txn.receiver_upi, txn.amount, fraud_score, int(is_fraud), datetime.now().isoformat()))
        conn.commit()
        conn.close()

        return FraudResult(
            transaction_id=txn.transaction_id,
            fraud_score=fraud_score,
            is_fraud=is_fraud,
            risk_level="HIGH" if fraud_score > 0.6 else "LOW",
            reasons=["High score"] if is_fraud else ["Normal"],
            processing_ms=round((time.time() - start) * 1000, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "models_ready": xgb_model is not None}