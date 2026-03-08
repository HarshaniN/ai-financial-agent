from typing import Dict
from app.data_loader import load_financial_data
from app.anomaly_detector import detect_amount_anomalies


def handle_financial_query(question: str) -> Dict:
    question_lower = question.lower().strip()
    df = load_financial_data()

    if "anomal" in question_lower or "suspicious" in question_lower or "unusual" in question_lower:
        anomalies = detect_amount_anomalies(df)
        return {
            "question": question,
            "intent": "detect_anomalies",
            "answer": "Here are the invoices flagged as anomalous based on unusually high amounts.",
            "results": anomalies,
        }

    if "all invoices" in question_lower or "list invoices" in question_lower or "show invoices" in question_lower:
        return {
            "question": question,
            "intent": "list_invoices",
            "answer": "Here are all invoices in the dataset.",
            "results": df.to_dict(orient="records"),
        }

    if "health" in question_lower or "status" in question_lower:
        return {
            "question": question,
            "intent": "health_check",
            "answer": "The AI Financial Agent is running normally.",
            "results": [{"status": "ok"}],
        }

    return {
        "question": question,
        "intent": "unknown",
        "answer": (
            "I could not understand that request yet. "
            "Try asking things like 'show suspicious invoices' or 'list all invoices'."
        ),
        "results": [],
    }