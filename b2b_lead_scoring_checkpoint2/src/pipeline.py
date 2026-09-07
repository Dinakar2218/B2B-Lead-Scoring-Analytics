"""Validate, clean and aggregate B2B lead data."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "leads.csv"
OUT = ROOT / "data" / "processed"
DB = ROOT / "data" / "lead_scoring.db"
REQUIRED = ["lead_id","created_date","industry","company_size","enquiry_type","response_time_hours","number_of_rfqs","converted"]

def load_and_validate(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = sorted(set(REQUIRED)-set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df["lead_id"].duplicated().any():
        raise ValueError("Duplicate lead_id values found")
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    numeric = ["response_time_hours","number_of_rfqs","converted"]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=REQUIRED).copy()
    if (df[["response_time_hours","number_of_rfqs"]] < 0).any().any():
        raise ValueError("Negative response time or RFQ values found")
    if not df["converted"].isin([0,1]).all():
        raise ValueError("converted must contain only 0 or 1")
    df["created_month"] = df["created_date"].dt.to_period("M").astype(str)
    df["fast_response"] = (df["response_time_hours"] <= 6).astype(int)
    return df

def build_metrics(df: pd.DataFrame) -> pd.DataFrame:
    items = {
        "total_leads": len(df), "converted_leads": int(df.converted.sum()),
        "conversion_rate_pct": round(df.converted.mean()*100,2),
        "median_response_hours": round(df.response_time_hours.median(),2),
        "average_response_hours": round(df.response_time_hours.mean(),2),
        "average_rfqs": round(df.number_of_rfqs.mean(),2),
        "fast_response_rate_pct": round(df.fast_response.mean()*100,2),
        "duplicate_lead_ids": int(df.lead_id.duplicated().sum()),
        "missing_values_after_cleaning": int(df[REQUIRED].isna().sum().sum())
    }
    return pd.DataFrame(items.items(), columns=["metric","value"])

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_and_validate(INPUT)
    metrics = build_metrics(df)
    df.to_csv(OUT / "leads_clean.csv", index=False)
    metrics.to_csv(OUT / "baseline_metrics.csv", index=False)
    with sqlite3.connect(DB) as conn:
        df.to_sql("leads_clean", conn, if_exists="replace", index=False)
    print(metrics.to_string(index=False))

if __name__ == "__main__":
    main()

