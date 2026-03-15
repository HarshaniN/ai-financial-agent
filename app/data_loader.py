import pandas as pd
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "financial_data.csv"
CURRENT_DATA_PATH_FILE = Path(__file__).resolve().parent.parent / "data" / "current_dataset.txt"


def get_active_data_path() -> Path:
    if CURRENT_DATA_PATH_FILE.exists():
        saved_path = CURRENT_DATA_PATH_FILE.read_text().strip()
        if saved_path:
            candidate = Path(saved_path)
            if candidate.exists():
                return candidate
    return DEFAULT_DATA_PATH


def set_active_data_path(path: str) -> None:
    CURRENT_DATA_PATH_FILE.write_text(path)


def reset_active_data_path() -> None:
    if CURRENT_DATA_PATH_FILE.exists():
        CURRENT_DATA_PATH_FILE.unlink()


def load_financial_data() -> pd.DataFrame:
    data_path = get_active_data_path()
    df = pd.read_csv(data_path)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    return df