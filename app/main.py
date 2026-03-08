from fastapi import FastAPI
from app.data_loader import load_financial_data
from app.anomaly_detector import detect_amount_anomalies

app = FastAPI(title="AI Financial Agent")


@app.get("/")
def root():
    return {"message": "AI Financial Agent is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/invoices")
def get_invoices():
    df = load_financial_data()
    return df.to_dict(orient="records")


@app.get("/anomalies")
def get_anomalies():
    df = load_financial_data()
    anomalies = detect_amount_anomalies(df)
    return {"anomalies": anomalies}