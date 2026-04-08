import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw UPI data into ML-ready features."""
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # ── TIME FEATURES ──────────────────────────────────────────
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_late_night'] = df['hour'].between(0, 5).astype(int)
    df['is_business_hours'] = df['hour'].between(9, 18).astype(int)
    
    # ── AMOUNT FEATURES ────────────────────────────────────────
    df['log_amount'] = np.log1p(df['amount'])
    df['is_round_amount'] = (df['amount'] % 1000 == 0).astype(int)
    df['amount_zscore'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
    
    # ── VELOCITY FEATURES (key fraud signal) ───────────────────
    # How many transactions has this sender made in last 1 hour?
    df = df.sort_values(['sender_upi', 'timestamp'])
    
    def rolling_count(group):
        group = group.set_index('timestamp')
        group['txn_count_1h'] = group['amount'].rolling('1H').count()
        group['txn_sum_1h'] = group['amount'].rolling('1H').sum()
        group['txn_count_24h'] = group['amount'].rolling('24H').count()
        return group.reset_index()
    
    df = df.groupby('sender_upi', group_keys=False).apply(rolling_count)
    
    # ── RECEIVER FAMILIARITY ────────────────────────────────────
    # How many times has this sender paid this receiver before?
    pair_counts = df.groupby(['sender_upi', 'receiver_upi']).cumcount()
    df['receiver_familiarity'] = pair_counts
    df['is_new_receiver'] = (df['receiver_familiarity'] == 0).astype(int)
    
    # ── SENDER BEHAVIOR BASELINE ────────────────────────────────
    sender_stats = df.groupby('sender_upi')['amount'].agg(['mean','std']).reset_index()
    sender_stats.columns = ['sender_upi','sender_avg_amt','sender_std_amt']
    df = df.merge(sender_stats, on='sender_upi', how='left')
    df['amount_vs_user_avg'] = df['amount'] / (df['sender_avg_amt'] + 1)
    
    # ── ENCODE CATEGORICALS ─────────────────────────────────────
    df['txn_type_enc'] = df['transaction_type'].map({'P2P': 0, 'P2M': 1}).fillna(0)
    bank_map = {b: i for i, b in enumerate(df['bank'].unique())}
    df['bank_enc'] = df['bank'].map(bank_map).fillna(0)
    
    # ── SUSPICIOUS DEVICE PATTERN ───────────────────────────────
    # Device IDs 9000-9999 were our fraud pattern
    extracted_digits = df['device_id'].str.extract(r'(\d+)')[0]
    df['device_num'] = pd.to_numeric(extracted_digits, errors='coerce').fillna(0)
    df['suspicious_device'] = (df['device_num'] >= 9000).astype(int)
    
    # Drop columns not used in model
    feature_cols = [
        'hour', 'day_of_week', 'is_weekend', 'is_late_night', 'is_business_hours',
        'log_amount', 'is_round_amount', 'amount_zscore',
        'txn_count_1h', 'txn_sum_1h', 'txn_count_24h',
        'receiver_familiarity', 'is_new_receiver',
        'amount_vs_user_avg', 'txn_type_enc', 'bank_enc',
        'suspicious_device'
    ]
    
    return df, feature_cols

if __name__ == "__main__":
    df = pd.read_csv('data/raw_transactions.csv')
    df_feat, cols = engineer_features(df)
    df_feat.to_csv('data/features.csv', index=False)
    print("Features created:", cols)
    print(df_feat[cols].describe())