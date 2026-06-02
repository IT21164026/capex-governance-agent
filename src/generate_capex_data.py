from pathlib import Path
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
np.random.seed(11)

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

today = pd.Timestamp.today().normalize()

projects = []

for i in range(1, 251):
    budget = float(np.random.randint(5000, 500000))
    actual = budget * np.random.uniform(0.2, 1.45)

    approved = np.random.choice([0, 1], p=[0.12, 0.88])

    cap_rule = np.random.choice(
        ["Capitalize", "Expense", "Review Required"],
        p=[0.65, 0.20, 0.15]
    )

    start = today - pd.Timedelta(days=int(np.random.randint(10, 400)))
    planned_end = start + pd.Timedelta(days=int(np.random.randint(30, 250)))
    actual_end = planned_end + pd.Timedelta(days=int(np.random.randint(-20, 120)))

    roi = np.random.uniform(-0.10, 0.35)

    projects.append([
        f"CAPEX-{1000 + i}",
        fake.bs().title(),
        np.random.choice(["Plant A", "Plant B", "Plant C", "HQ"]),
        budget,
        round(actual, 2),
        approved,
        cap_rule,
        start.date(),
        planned_end.date(),
        actual_end.date(),
        round(roi, 3),
        np.random.choice([0, 1], p=[0.20, 0.80])
    ])

capex = pd.DataFrame(
    projects,
    columns=[
        "project_id",
        "project_name",
        "location",
        "approved_budget",
        "actual_spend",
        "approval_flag",
        "capitalization_rule",
        "start_date",
        "planned_end_date",
        "actual_end_date",
        "expected_roi",
        "supporting_docs_flag"
    ]
)

capex.to_csv(RAW / "capex_projects.csv", index=False)

print("Capex sample data created successfully.")
print(f"File saved to: {RAW / 'capex_projects.csv'}")
print(f"Total records created: {len(capex)}")