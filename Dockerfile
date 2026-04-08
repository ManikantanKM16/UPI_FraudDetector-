FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-generate data and train models
RUN python data/generate_data.py && \
    python features/engineer.py && \
    python models/train.py && \
    python evaluate/tune_threshold.py

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]