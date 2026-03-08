import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/financial_data.csv")

def load_financial_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    return df