# 🛡️ UPI Fraud Detector

A comprehensive Machine Learning pipeline designed to detect fraudulent UPI (Unified Payments Interface) transactions in real-time. This project features an **XGBoost** classification model, a **FastAPI** backend, and an interactive **Streamlit** dashboard.

---

## 🚀 Key Features
* **XGBoost Classifier:** High-performance gradient boosting model for detecting anomalous transactions.
* **Synthetic Data Generation:** Uses `Faker` to simulate realistic UPI transaction logs (Amount, Timestamp, Location, Device ID).
* **FastAPI Backend:** A production-grade REST API to serve real-time fraud predictions.
* **Interactive Dashboard:** Built with `Streamlit` and `Plotly` to visualize transaction trends and model performance.
* **Containerized:** Fully Dockerized for easy deployment.

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **ML Frameworks:** XGBoost, Scikit-Learn, PyTorch
* **Data Handling:** Pandas, NumPy
* **APIs & Web:** FastAPI, Uvicorn, Streamlit
* **Visuals:** Plotly, Matplotlib
* **DevOps:** Docker

---

## 📁 Project Structure
```bash
├── api/             # FastAPI implementation for model serving
├── dashboard/       # Streamlit frontend for data visualization
├── data/            # Raw and processed datasets (generated via Faker)
├── evaluate/        # Scripts for model metrics and performance analysis
├── features/        # Feature engineering and preprocessing logic
├── models/          # Saved model weights (.pkl or .pt files)
├── Dockerfile       # Containerization instructions
└── requirements.txt # Project dependencies
