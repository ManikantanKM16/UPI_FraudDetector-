import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)

def generate_upi_transactions(n_legit=47000, n_fraud=3000):
    """Generate realistic UPI transaction data with fraud patterns."""
    
    users = [f"user{i}@okaxis" for i in range(1, 2001)]
    merchants = [f"merchant{i}@paytm" for i in range(1, 501)]
    records = []

    # ---- THE FIX: FREQUENCY POOL ----
    # We create a list of 1000 hours. If an hour has 4% weight, 
    # we put it in the list 40 times. No decimals = No errors.
    hour_pool = []
    weights = [0.005]*6 + [0.04]*4 + [0.07]*8 + [0.06]*4 + [0.02]*2
    for hr, w in enumerate(weights):
        # Multiply weight by 1000 to get an integer count
        count = int(w * 1000)
        hour_pool.extend([hr] * count)
    # ---------------------------------

    print(f"Generating {n_legit} legitimate transactions...")
    for _ in range(n_legit):
        sender = random.choice(users)
        receiver = random.choice(merchants + users)
        
        # Pull directly from the pool - no probabilities needed!
        hour = random.choice(hour_pool)
        
        ts = datetime.now() - timedelta(
            days=random.randint(0, 365),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        ts = ts.replace(hour=hour)
        
        amount = round(np.random.lognormal(mean=6.5, sigma=1.2), 2)
        amount = max(1.0, min(amount, 100000))
        
        records.append({
            'transaction_id': fake.uuid4(),
            'timestamp': ts,
            'sender_upi': sender,
            'receiver_upi': receiver,
            'amount': amount,
            'transaction_type': random.choice(['P2P','P2M','P2M','P2M']),
            'bank': random.choice(['SBI','HDFC','ICICI','Axis','Kotak']),
            'device_id': f"dev_{random.randint(1000,9999)}",
            'location_pin': str(random.randint(100000, 999999)),
            'is_fraud': 0
        })

    print(f"Generating {n_fraud} fraud transactions...")
    fraud_patterns = ['late_night_large', 'rapid_succession', 'new_receiver_large', 'round_amount', 'account_takeover']
    
    for i in range(n_fraud):
        pattern = random.choice(fraud_patterns)
        sender = random.choice(users)
        
        if pattern == 'late_night_large':
            hour = random.randint(1, 4)
            amount = round(random.uniform(15000, 100000), 2)
        elif pattern == 'rapid_succession':
            hour = random.randint(0, 23)
            amount = round(random.uniform(500, 5000), 2)
        elif pattern == 'new_receiver_large':
            hour = random.randint(10, 22)
            amount = round(random.uniform(20000, 99000), 2)
        elif pattern == 'round_amount':
            hour = random.randint(2, 5)
            amount = float(random.choice([10000, 25000, 50000, 75000, 100000]))
        else:  # account_takeover
            hour = random.randint(0, 6)
            amount = round(random.uniform(10000, 80000), 2)
        
        ts = datetime.now() - timedelta(days=random.randint(0, 365))
        ts = ts.replace(hour=hour, minute=random.randint(0,59))
        
        records.append({
            'transaction_id': fake.uuid4(),
            'timestamp': ts,
            'sender_upi': sender,
            'receiver_upi': f"suspicious{random.randint(1,200)}@ybl",
            'amount': amount,
            'transaction_type': random.choice(['P2P','P2P','P2M']),
            'bank': random.choice(['SBI','HDFC','ICICI','Axis','Kotak']),
            'device_id': f"dev_{random.randint(9000,9999)}", 
            'location_pin': str(random.randint(100000, 999999)),
            'is_fraud': 1
        })
    
    df = pd.DataFrame(records)
    df = df.sample(frac=1).reset_index(drop=True)
    
    os.makedirs('data', exist_ok=True)
    output_path = 'data/raw_transactions.csv'
    
    try:
        df.to_csv(output_path, index=False)
        print(f"\n--- SUCCESS! ---")
        print(f"File created at: {output_path}")
        print(f"Total rows: {len(df)}")
    except PermissionError:
        print(f"\n⚠️ PermissionError! The file {output_path} might be open in another program.")
        fallback_path = 'data/raw_transactions_fallback.csv'
        df.to_csv(fallback_path, index=False)
        print(f"Saved to fallback file: {fallback_path}")
        
    return df

if __name__ == "__main__":
    generate_upi_transactions()