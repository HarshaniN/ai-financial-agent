import json
import ollama


def classify_financial_query(question: str) -> dict:
    prompt = f"""
Classify this financial analysis request.

Possible intents:
- detect_anomalies
- list_invoices
- health_check
- unknown

Return valid JSON only in this format:
{{"intent": "detect_anomalies"}}

User question: {question}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
    )

    text = response["message"]["content"].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"intent": "unknown"}


def explain_anomaly(anomaly: dict) -> str:
    prompt = f"""
You are a financial analyst assistant.

Given this invoice anomaly, write a short professional explanation in 1 to 2 sentences.

Invoice anomaly:
{json.dumps(anomaly, default=str)}

Focus on why it may be unusual based on amount, vendor pattern, and business risk.
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"].strip()