import json
import re
import ollama


def extract_json_object(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"intent": "unknown"}

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return {"intent": "unknown"}


def classify_financial_query(question: str) -> dict:
    prompt = f"""
You are classifying financial analysis requests.

Possible intents:
- detect_anomalies
- list_invoices
- health_check
- unknown

Return ONLY valid JSON.
Do not include explanations.
Do not include markdown.
Use exactly this format:
{{"intent": "detect_anomalies"}}

User question: {question}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
    )

    text = response["message"]["content"].strip()
    parsed = extract_json_object(text)

    intent = parsed.get("intent", "unknown")
    allowed_intents = {"detect_anomalies", "list_invoices", "health_check", "unknown"}

    if intent not in allowed_intents:
        return {"intent": "unknown"}

    return {"intent": intent}


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