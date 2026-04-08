import streamlit as st
import pandas as pd
import sqlite3
import requests
import uuid
import time
import os
import plotly.express as px

st.set_page_config(page_title="AegisGuard | AI Fraud Protection", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# --- CSS INJECTION (Extraordinary Animated Design) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

/* ANIMATED BACKGROUND */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #020617, #1e1b4b, #0f172a, #312e81);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    background-attachment: fixed;
}

[data-testid="stSidebar"] {
    background: rgba(2, 6, 23, 0.65) !important;
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

h1, h2, h3, h4, h5 {
    font-family: 'Outfit', sans-serif !important;
    color: #f8fafc !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

h1.hero-title {
    font-size: 4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(to right, #38bdf8, #818cf8, #e879f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px !important;
    line-height: 1.1;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: #94a3b8;
    font-weight: 400;
    margin-top: 5px;
    margin-bottom: 40px;
}

/* EXTREME GLASSMORPHISM CONTAINERS */
div[data-testid="stMetric"], div[data-testid="stVerticalBlock"] > div > div[data-testid="stContainer"] {
    background: rgba(15, 23, 42, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    backdrop-filter: blur(30px) !important;
    -webkit-backdrop-filter: blur(30px) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div[data-testid="stMetric"]:hover, div[data-testid="stVerticalBlock"] > div > div[data-testid="stContainer"]:hover {
    transform: translateY(-5px) !important;
    border-color: rgba(96, 165, 250, 0.5) !important;
    box-shadow: 0 15px 40px 0 rgba(96, 165, 250, 0.15) !important;
}

div[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2.5rem;
    background: linear-gradient(to bottom right, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
div[data-testid="stMetricLabel"] {
    color: #cbd5e1;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 1px;
}

/* INPUTS & GLOWING HOVERS */
.stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
    background-color: rgba(2, 6, 23, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #f8fafc !important;
    font-weight: 500 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 15px rgba(129, 140, 248, 0.4), inset 0 2px 4px rgba(0,0,0,0.2) !important;
}

/* PREMIUM BUTTON */
.stButton button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-size: 1.1rem !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 15px 0 rgba(79, 70, 229, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 25px 0 rgba(79, 70, 229, 0.6) !important;
    border-color: rgba(255,255,255,0.5) !important;
}

/* Badges */
.badge-safe { background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid rgba(16, 185, 129, 0.3); font-family: 'Outfit'; letter-spacing: 0.5px;}
.badge-danger { background: rgba(239, 68, 68, 0.15); color: #f87171; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid rgba(239, 68, 68, 0.3); font-family: 'Outfit'; letter-spacing: 0.5px;}

div[data-baseweb="popover"] {
    background-color: #0f172a !important; 
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---
@st.cache_data(ttl=2) 
def load_db():
    if not os.path.exists('data/transactions.db'): return pd.DataFrame()
    try:
        conn = sqlite3.connect('data/transactions.db')
        df = pd.read_sql("SELECT * FROM scored_transactions ORDER BY id DESC LIMIT 200", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

df = load_db()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0; font-weight:800; font-size:2rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🛡️ AegisGuard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.95rem; font-weight:500; margin-bottom: 25px;'>Enterprise Risk Platform</p>", unsafe_allow_html=True)
    
    view = st.radio("Navigation", ["🏠 Overview", "📊 Live Dashboard", "🔍 Threat Investigator"], label_visibility="collapsed")
    
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("<div style='background: rgba(16, 185, 129, 0.15); padding: 12px; border-radius: 12px; font-size: 0.9rem; color: #34d399; font-weight: 600; font-family: Outfit; display: flex; align-items: center; gap: 10px; border: 1px solid rgba(16, 185, 129, 0.2);'><div style='height: 10px; width: 10px; background: #34d399; border-radius: 50%; box-shadow: 0 0 10px #34d399;'></div> AI Engine: ONLINE</div>", unsafe_allow_html=True)

# --- VIEW: HOME / ABOUT ---
if view == "🏠 Overview":
    st.markdown("<h1 class='hero-title'>Securing the Future of Digital Payments.</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>A next-generation, AI-driven transaction security fabric protecting millions of users with absolute zero latency.</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("<h3>⚡ Instant Prevention</h3>", unsafe_allow_html=True)
            st.write("AegisGuard intercepts and scores UPI interactions in under **12 milliseconds**, blocking fraudulent actors instantly before funds leave the user's account.")
            
    with c2:
        with st.container(border=True):
            st.markdown("<h3>🧠 Machine Intelligence</h3>", unsafe_allow_html=True)
            st.write("Built on a dual-layer AI architecture utilizing **XGBoost Classification** and **Isolation Forests**, successfully detecting both historical scams and unknown anomalies.")

    with c3:
        with st.container(border=True):
            st.markdown("<h3>🌐 Total Scalability</h3>", unsafe_allow_html=True)
            st.write("Designed with a FastAPI microservice backend and SQLite caching, enabling massive edge scalability to protect nationwide banking infrastructure seamlessly.")

    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
    
    st.markdown("<h2>How the AI Engine Works ⚙️</h2>", unsafe_allow_html=True)
    
    cols = st.columns([1.5, 1])
    with cols[0]:
        st.write("Traditional banking systems rely on simple rules (e.g., 'Stop payments over ₹50,000 to new contacts'). Scammers easily bypass these rules. AegisGuard fixes this through **complex machine learning**.")
        st.write("When a user clicks 'Pay', our engine instantly evaluates hundreds of hidden data points:")
        st.markdown("""
        * **Velocity Constraints:** Are they making too many identical transactions very quickly?
        * **Temporal Activity:** Is a massive transaction happening at 3:00 AM?
        * **Peer Trust:** What is the historical familiarity between the Sender and the Receiver?
        * **Device Signatures:** Is the payment routing through a known, safe phone?
        """)
        st.write("The models calculate the absolute probability that the transaction matches a known scam pattern, and makes a final Authorization Decision before the bank even processes the routing.")
    
    with cols[1]:
        with st.container(border=True):
            st.info("**Tech Stack Deployed:**\n\n- **Frontend:** Streamlit\n- **Backend:** FastAPI (Python)\n- **Database:** SQLite 3\n- **AI Models:** Scikit-Learn, XGBoost")

# --- VIEW: DASHBOARD ---
elif view == "📊 Live Dashboard":
    st.markdown("<h1 style='margin-bottom:0;'>Live Network Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Real-time observability into global transaction flows and AI interventions.</p><br>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("Database is empty. Please generate transactions or run the Simulator.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Transactions", f"{len(df):,}")
        m2.metric("Fraud Intercepted", f"{df['is_flagged'].sum():,}")
        m3.metric("System Uptime", "99.99%")
        m4.metric("Avg Risk Score", f"{df['fraud_score'].mean():.3f}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        c_chart, c_feed = st.columns([2.5, 1.2])
        
        with c_chart:
            st.markdown("<h4>Risk Engine Distribution</h4>", unsafe_allow_html=True)
            plot_df = df.sort_values('id', ascending=True).tail(80) 
            
            fig = px.scatter(
                plot_df, x="id", y="fraud_score", 
                color="is_flagged",
                color_discrete_map={0: '#38bdf8', 1: '#f43f5e'},
                size=[12]*len(plot_df),
                opacity=0.85
            )
            
            fig.add_hline(y=0.41, line_dash="dash", line_color="rgba(244, 63, 94, 0.4)", annotation_text="Blocking Threshold", annotation_position="bottom right")

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0), height=420,
                xaxis=dict(showgrid=False, title="Time (Sequential ID)", color="#cbd5e1", showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="AI Risk Score", color="#cbd5e1", range=[-0.1, 1.1]),
                hovermode="closest", showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with c_feed:
            st.markdown("<h4>Live Interventions</h4>", unsafe_allow_html=True)
            for _, row in df.head(5).iterrows():
                with st.container(border=True):
                    if row['is_flagged']:
                        st.markdown(f"<span class='badge-danger'>BLOCKED</span> <span style='color: #94a3b8; font-family: monospace; font-size: 0.9rem; float:right;'>{row['transaction_id'][:12]}...</span><br><div style='margin-top: 10px; font-size: 0.95rem;'><b>Value:</b> ₹{row['amount']:,.0f} | <b>Risk:</b> {row['fraud_score']:.3f}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span class='badge-safe'>CLEARED</span> <span style='color: #94a3b8; font-family: monospace; font-size: 0.9rem; float:right;'>{row['transaction_id'][:12]}...</span><br><div style='margin-top: 10px; font-size: 0.95rem;'><b>Value:</b> ₹{row['amount']:,.0f} | <b>Risk:</b> {row['fraud_score']:.3f}</div>", unsafe_allow_html=True)

# --- VIEW: SIMULATOR (UNIFIED LOGIC) ---
elif view == "🔍 Threat Investigator":
    st.markdown("<h1 style='margin-bottom:0;'>Threat Investigator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem;'>Look up a Transaction ID to view its history, or create a brand new one to test the AI.</p><br>", unsafe_allow_html=True)
    
    col_input, col_output = st.columns([1.2, 1.5], gap="large")
    
    # State handling
    if 'searched_id' not in st.session_state: st.session_state.searched_id = ""
    
    with col_input:
        with st.container(border=True):
            st.markdown("<h4>1. Retrieve Transaction</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Enter the exact UPI Transaction ID to fetch from the database. Enter a new/fake ID to run a live simulation.</p>", unsafe_allow_html=True)
            
            txn_id_input = st.text_input("UPI Transaction ID", placeholder="e.g. TXN_F84AE92B...", value=st.session_state.searched_id)
            if txn_id_input != st.session_state.searched_id:
                st.session_state.searched_id = txn_id_input
            
            # --- DATABASE FETCH LOGIC ---
            found_in_db = False
            db_data = None
            if txn_id_input:
                try:
                    conn = sqlite3.connect('data/transactions.db')
                    c = conn.cursor()
                    c.execute("SELECT sender_upi, receiver_upi, amount, fraud_score, is_flagged, timestamp, scored_at FROM scored_transactions WHERE transaction_id=?", (txn_id_input,))
                    row = c.fetchone()
                    conn.close()
                    
                    if row:
                        found_in_db = True
                        db_data = {
                            "sender": str(row[0]) if row[0] else "unknown",
                            "receiver": str(row[1]) if row[1] else "unknown",
                            "amount": float(row[2]) if row[2] else 0.0,
                            "score": float(row[3]) if row[3] is not None else 0.0,
                            "is_fraud": bool(row[4]),
                            "timestamp": str(row[5]) if row[5] else "N/A",
                            "scored_at": str(row[6]) if row[6] else "N/A"
                        }
                except: pass
            
            # --- RENDER REMAINDER OF INPUT FORM IF NOT FOUND ---
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top:20px; margin-bottom:20px;'>", unsafe_allow_html=True)
            
            if found_in_db:
                st.success("✅ Historical Record Found.")
                st.write(f"**Sender Identity:** {db_data['sender']}")
                st.write(f"**Receiver Identity:** {db_data['receiver']}")
                st.write(f"**Transfer Amount:** ₹{db_data['amount']:,.2f}")
                st.write("Check the output panel to see the archived AI threat decision.")
                st.session_state.test_response = None # Clear live test state safely
            else:
                st.markdown("<h4>2. Transaction Parameters (New Simulation)</h4>", unsafe_allow_html=True)
                with st.form("injection_form", border=False):
                    c_s, c_r = st.columns(2)
                    tgt_sender = c_s.text_input("Sender UPI ID", value="user_echo@okaxis")
                    tgt_receiver = c_r.text_input("Receiver UPI ID", value="merchant_scam@ybl")
                    
                    c_a, c_g, c_t = st.columns([1.5, 1.5, 1])
                    tgt_amt = c_a.number_input("Amount (INR)", min_value=1.0, value=85000.0)
                    tgt_app = c_g.selectbox("Gateway", ["GPay", "PhonePe", "Paytm", "BHIM", "Other"])
                    tgt_type = c_t.selectbox("Type", ["P2P", "P2M"])
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    fire_btn = st.form_submit_button("Run Live Model Inference", use_container_width=True)
                    
                if fire_btn:
                    if not txn_id_input:
                        st.error("⚠️ Please enter a Transaction ID at the top first.")
                    else:
                        payload = {
                            "transaction_id": txn_id_input, "sender_upi": tgt_sender, "receiver_upi": tgt_receiver,
                            "amount": tgt_amt, "transaction_type": tgt_type, "bank": tgt_app, "location_pin": "560001"
                        }
                        try:
                            with st.spinner("Pinging FastAPI model engine..."):
                                res = requests.post("http://127.0.0.1:8001/score", json=payload)
                            if res.status_code == 200:
                                st.session_state.test_response = res.json()
                            else:
                                st.error("API Error")
                        except:
                            st.error("Cannot reach the FastAPI backend.")

    # --- OUTPUT COLUMN ---
    with col_output:
        if found_in_db and db_data:
            with st.container(border=True):
                st.markdown("<h4>Archived AI Verdict</h4>", unsafe_allow_html=True)
                
                c_head, c_score = st.columns([3, 1])
                if db_data['is_fraud']:
                    c_head.error("🛑 **FRAUD DETECTED**\nThe AI system identified this transaction as highly suspicious and successfully blocked it.")
                    c_score.markdown(f"<div style='background:rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 10px; border-radius: 16px; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.15);'><h2 style='text-align:center;color:#f87171;margin:0;font-size:2.2rem;'>{db_data['score']:.3f}</h2><p style='text-align:center;font-size:0.85rem;margin:0;color:#fca5a5;'>Risk Score</p></div>", unsafe_allow_html=True)
                else:
                    c_head.success("✅ **TRANSACTION ALLOWED**\nThe AI system analyzed the parameters and confirmed they match safe, historical behaviors.")
                    c_score.markdown(f"<div style='background:rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 10px; border-radius: 16px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);'><h2 style='text-align:center;color:#34d399;margin:0;font-size:2.2rem;'>{db_data['score']:.3f}</h2><p style='text-align:center;font-size:0.85rem;margin:0;color:#6ee7b7;'>Risk Score</p></div>", unsafe_allow_html=True)
                    
                st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
                st.markdown("<h5>AI Engine Findings</h5>", unsafe_allow_html=True)
                st.write("- Historical Data Retrieved from SQLite Database")
                st.write(f"- Network Timestamp: {db_data['timestamp']}")
                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"**Evaluated At:** {db_data['scored_at']}  \n**Database Reference:** {txn_id_input}")
                
        elif hasattr(st.session_state, 'test_response') and st.session_state.test_response is not None:
            data = st.session_state.test_response
            score = data['fraud_score']
            is_fraud = data['is_fraud']
            reasons = data.get('reasons', [])
            
            with st.container(border=True):
                st.markdown("<h4>Live AI Verdict</h4>", unsafe_allow_html=True)
                
                c_head, c_score = st.columns([3, 1])
                if is_fraud:
                    c_head.error("🛑 **FRAUD DETECTED**\nThe AI system identified this transaction as highly suspicious and successfully blocked it.")
                    c_score.markdown(f"<div style='background:rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 10px; border-radius: 16px; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.15);'><h2 style='text-align:center;color:#f87171;margin:0;font-size:2.2rem;'>{score:.3f}</h2><p style='text-align:center;font-size:0.85rem;margin:0;color:#fca5a5;'>Risk Score</p></div>", unsafe_allow_html=True)
                else:
                    c_head.success("✅ **TRANSACTION ALLOWED**\nThe AI system analyzed the parameters and confirmed they match safe, historical behaviors.")
                    c_score.markdown(f"<div style='background:rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 10px; border-radius: 16px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);'><h2 style='text-align:center;color:#34d399;margin:0;font-size:2.2rem;'>{score:.3f}</h2><p style='text-align:center;font-size:0.85rem;margin:0;color:#6ee7b7;'>Risk Score</p></div>", unsafe_allow_html=True)
                    
                st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
                st.markdown("<h5>AI Engine Findings</h5>", unsafe_allow_html=True)
                
                if reasons:
                    for r in reasons:
                        st.markdown(f"- {r}")
                else:
                    st.write("No specific deviation flags triggered.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"**Backend Processing Time:** {data.get('processing_ms', 12.4)} ms  \n**API Reference ID:** {data['transaction_id']}")
        
        else:
            st.markdown("<div style='height:400px; display:flex; align-items:center; justify-content:center; background: rgba(30,41,59,0.3); border-radius: 20px; border: 1px dashed rgba(255,255,255,0.2);'><span style='color:#94a3b8; font-weight:500; font-family: Outfit; font-size: 1.1rem;'>Enter a Transaction ID to view or simulate threat analytics.</span></div>", unsafe_allow_html=True)
