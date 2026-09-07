"""Generate reproducible DEMO data. Do not represent it as client-supplied data."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "leads.csv"
RNG = np.random.default_rng(42)

def main(rows: int = 12000) -> None:
    dates = pd.date_range("2025-09-01", "2026-08-31", freq="D")
    industry = RNG.choice(["Manufacturing", "Retail", "Healthcare", "Technology", "Construction"], rows, p=[.27,.22,.16,.20,.15])
    size = RNG.choice(["1-50", "51-200", "201-1000", "1001+"], rows, p=[.30,.32,.25,.13])
    enquiry = RNG.choice(["Product enquiry", "Bulk order", "Supplier request", "Price quote"], rows, p=[.30,.24,.18,.28])
    response = np.round(np.clip(RNG.gamma(2.2, 5.0, rows), 0.1, 72), 2)
    rfqs = np.clip(RNG.poisson(2.2, rows), 0, 12)
    logit = -2.7 + .55*(size=="201-1000") + 1.0*(size=="1001+") + .9*(enquiry=="Bulk order") + .35*(enquiry=="Price quote") - .055*response + .42*rfqs + .25*(industry=="Manufacturing")
    probability = 1/(1+np.exp(-logit))
    converted = RNG.binomial(1, probability)
    frame = pd.DataFrame({
        "lead_id": [f"L{i:06d}" for i in range(1, rows+1)],
        "created_date": RNG.choice(dates, rows), "industry": industry,
        "company_size": size, "enquiry_type": enquiry,
        "response_time_hours": response, "number_of_rfqs": rfqs,
        "converted": converted, "data_source": "synthetic_demo"
    }).sort_values("created_date")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT, index=False)
    print(f"Created {len(frame):,} demo leads at {OUTPUT}")

if __name__ == "__main__":
    main()

