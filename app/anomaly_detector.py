from typing import List, Dict
import pandas as pd
from app.llm_service import explain_anomaly


def detect_amount_anomalies(df: pd.DataFrame) -> List[Dict]:
    mean_amount = df["amount"].mean()
    std_amount = df["amount"].std()

    threshold = mean_amount + (2 * std_amount)

    anomalies = df[df["amount"] > threshold].copy()
    anomalies["anomaly_reason"] = (
        "Invoice amount is significantly higher than historical average"
    )

    results = anomalies.to_dict(orient="records")

    for anomaly in results:
        anomaly["llm_explanation"] = explain_anomaly(anomaly)

    return results