from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]

RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)


def get_risk_level(score):
    if score >= 80:
        return "Critical"
    elif score >= 60:
        return "High"
    elif score >= 35:
        return "Medium"
    else:
        return "Low"


def build_capex_exceptions():
    input_file = RAW / "capex_projects.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            "capex_projects.csv not found. Please run generate_capex_data.py first."
        )

    df = pd.read_csv(
        input_file,
        parse_dates=["start_date", "planned_end_date", "actual_end_date"]
    )

    # Calculate finance governance metrics
    df["budget_variance"] = df["actual_spend"] - df["approved_budget"]
    df["budget_variance_pct"] = (
        df["budget_variance"] / df["approved_budget"]
    ).round(3)

    df["delay_days"] = (
        df["actual_end_date"] - df["planned_end_date"]
    ).dt.days

    exceptions = []

    for _, row in df.iterrows():
        score = 0
        reasons = []
        actions = []

        # Rule 1: Missing approval
        if row["approval_flag"] == 0:
            score += 35
            reasons.append("Missing approval")
            actions.append("Hold further spend until approval is obtained")

        # Rule 2: Budget overrun above 10%
        if row["budget_variance_pct"] > 0.10:
            overrun_score = min(int(row["budget_variance_pct"] * 100), 35)
            score += overrun_score
            reasons.append(f"Budget overrun {row['budget_variance_pct']:.1%}")
            actions.append("Request variance explanation and approval")

        # Rule 3: Project delay above 30 days
        if row["delay_days"] > 30:
            score += 15
            reasons.append(f"Project delayed by {int(row['delay_days'])} days")
            actions.append("Review delivery plan and capitalization timing")

        # Rule 4: Low expected ROI
        if row["expected_roi"] < 0.05:
            score += 15
            reasons.append(f"Low ROI {row['expected_roi']:.1%}")
            actions.append("Revalidate the business case")

        # Rule 5: Missing supporting documents
        if row["supporting_docs_flag"] == 0:
            score += 20
            reasons.append("Missing supporting documents")
            actions.append(
                "Attach quotation, approval memo, invoice, and completion certificate"
            )

        # Rule 6: Capitalization review required
        if row["capitalization_rule"] == "Review Required":
            score += 15
            reasons.append("Capitalization rule requires review")
            actions.append("Finance review required for capitalization vs expense treatment")

        final_score = min(score, 100)

        if final_score > 0:
            exceptions.append({
                "exception_id": f"EX-{row['project_id']}",
                "project_id": row["project_id"],
                "project_name": row["project_name"],
                "location": row["location"],
                "risk_score": final_score,
                "risk_level": get_risk_level(final_score),
                "exception_summary": "; ".join(reasons),
                "recommended_action": "; ".join(actions),
                "financial_exposure": round(max(row["budget_variance"], 0), 2),
                "status": "Open"
            })

    exception_df = pd.DataFrame(exceptions)

    if not exception_df.empty:
        exception_df = exception_df.sort_values(
            by="risk_score",
            ascending=False
        )

    enriched_output = PROCESSED / "capex_enriched.csv"
    exceptions_output = PROCESSED / "capex_exceptions.csv"

    df.to_csv(enriched_output, index=False)
    exception_df.to_csv(exceptions_output, index=False)

    print("Capex governance exception engine completed successfully.")
    print(f"Enriched data saved to: {enriched_output}")
    print(f"Exceptions saved to: {exceptions_output}")
    print(f"Total capex projects reviewed: {len(df)}")
    print(f"Total exceptions created: {len(exception_df)}")


if __name__ == "__main__":
    build_capex_exceptions()