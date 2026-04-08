import os, joblib, json, numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# 1. Create Folder
os.makedirs('models/saved', exist_ok=True)

# 2. Create minimal dummy data to build a valid scaler/model
X = np.random.rand(10, 17) # 17 features
y = [0, 1, 0, 0, 1, 0, 0, 0, 1, 0]

scaler = StandardScaler().fit(X)
xgb_m = xgb.XGBClassifier().fit(X, y)
iso_m = IsolationForest().fit(X)
features = ['hour', 'day_of_week', 'is_weekend', 'is_late_night', 'is_business_hours', 'log_amount', 'is_round_amount', 'amount_zscore', 'txn_count_1h', 'txn_sum_1h', 'txn_count_24h', 'receiver_familiarity', 'is_new_receiver', 'amount_vs_user_avg', 'txn_type_enc', 'bank_enc', 'suspicious_device']

# 3. Save everything exactly where the API expects it
joblib.dump(xgb_m, 'models/saved/xgboost.pkl')
joblib.dump(iso_m, 'models/saved/isolation_forest.pkl')
joblib.dump(scaler, 'models/saved/scaler.pkl')
joblib.dump(features, 'models/saved/feature_cols.pkl')
with open('models/saved/threshold.json', 'w') as f:
    json.dump({"threshold": 0.5}, f)

print("SUCCESS: 5 model files created in models/saved/")