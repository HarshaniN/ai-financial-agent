from fastapi import FastAPI
from app.data_loader import load_financial_data, set_active_data_path
from app.anomaly_detector import detect_amount_anomalies
from app.schemas import QueryRequest, DatasetPathRequest
from app.agent import run_financial_agent

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


@app.post("/query")
def query_financial_data(request: QueryRequest):
    return run_financial_agent(request.question)


@app.post("/set-dataset")
def set_dataset(request: DatasetPathRequest):
    set_active_data_path(request.file_path)
    return {"message": "Dataset updated successfully", "file_path": request.file_path}


@app.post("/reset-dataset")
def reset_dataset():
    from app.data_loader import reset_active_data_path
    reset_active_data_path()
    return {"message": "Dataset reset to default sample file"}

@app.get("/active-dataset")
def active_dataset():
    from app.data_loader import get_active_data_path
    path = get_active_data_path()
    return {
        "file_name": path.name,
        "file_path": str(path.resolve())
    }