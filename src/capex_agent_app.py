from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"

ENRICHED_FILE = PROCESSED / "capex_enriched.csv"
EXCEPTIONS_FILE = PROCESSED / "capex_exceptions.csv"

st.set_page_config(
    page_title="Capex Governance Agent",
    layout="wide"
)

st.title("Capex Governance Agent")
st.caption(
    "Finance risk and control analytics assistant for approvals, budget overruns, "
    "capitalization review, ROI, project delays, missing documents, and audit observations."
)

if not ENRICHED_FILE.exists() or not EXCEPTIONS_FILE.exists():
    st.error(
        "Processed files not found. Please run generate_capex_data.py and capex_engine.py first."
    )
    st.stop()

df = pd.read_csv(ENRICHED_FILE)
exceptions = pd.read_csv(EXCEPTIONS_FILE)

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_capex_spend = df["actual_spend"].sum()
total_budget = df["approved_budget"].sum()
total_variance = total_capex_spend - total_budget
total_projects = len(df)
total_exceptions = len(exceptions)
high_risk_count = exceptions["risk_level"].isin(["Critical", "High"]).sum()
financial_exposure = exceptions["financial_exposure"].sum()
missing_approval_count = int((df["approval_flag"] == 0).sum())
missing_docs_count = int((df["supporting_docs_flag"] == 0).sum())

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Control Panel")
st.sidebar.write("Use this dashboard to review capex governance exceptions.")

risk_filter = st.sidebar.multiselect(
    "Risk Level",
    options=sorted(exceptions["risk_level"].unique()),
    default=sorted(exceptions["risk_level"].unique())
)

location_filter = st.sidebar.multiselect(
    "Location",
    options=sorted(exceptions["location"].unique()),
    default=sorted(exceptions["location"].unique())
)

status_filter = st.sidebar.multiselect(
    "Status",
    options=sorted(exceptions["status"].unique()),
    default=sorted(exceptions["status"].unique())
)

filtered_exceptions = exceptions[
    (exceptions["risk_level"].isin(risk_filter)) &
    (exceptions["location"].isin(location_filter)) &
    (exceptions["status"].isin(status_filter))
]

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Total Projects", total_projects)
kpi2.metric("Total Capex Spend", f"{total_capex_spend / 1_000_000:.2f}M")
kpi3.metric("Budget Variance", f"{total_variance / 1_000_000:.2f}M")
kpi4.metric("Total Exceptions", total_exceptions)
kpi5.metric("Critical / High Risk", int(high_risk_count))

kpi6, kpi7, kpi8 = st.columns(3)

kpi6.metric("Financial Exposure", f"{financial_exposure / 1_000_000:.2f}M")
kpi7.metric("Missing Approval Projects", missing_approval_count)
kpi8.metric("Missing Document Projects", missing_docs_count)

st.divider()

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Executive Dashboard",
        "Exception Worklist",
        "Audit Observation",
        "Ask Agent",
        "Data Download"
    ]
)

# --------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# --------------------------------------------------

with tab1:
    st.subheader("Executive Risk Overview")

    col1, col2 = st.columns(2)

    with col1:
        risk_count = exceptions["risk_level"].value_counts().reset_index()
        risk_count.columns = ["risk_level", "count"]

        fig_risk = px.bar(
            risk_count,
            x="risk_level",
            y="count",
            title="Exceptions by Risk Level",
            text="count"
        )

        st.plotly_chart(fig_risk, use_container_width=True)

    with col2:
        location_exposure = exceptions.groupby("location", as_index=False)[
            "financial_exposure"
        ].sum()

        fig_exposure = px.bar(
            location_exposure,
            x="location",
            y="financial_exposure",
            title="Financial Exposure by Location",
            text_auto=".2s"
        )

        st.plotly_chart(fig_exposure, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        top_overruns = df.sort_values(
            "budget_variance_pct",
            ascending=False
        ).head(10)

        fig_overrun = px.bar(
            top_overruns,
            x="project_id",
            y="budget_variance_pct",
            title="Top 10 Budget Overrun Projects",
            text_auto=".1%"
        )

        st.plotly_chart(fig_overrun, use_container_width=True)

    with col4:
        low_roi = df.sort_values("expected_roi").head(10)

        fig_roi = px.bar(
            low_roi,
            x="project_id",
            y="expected_roi",
            title="Lowest ROI Projects",
            text_auto=".1%"
        )

        st.plotly_chart(fig_roi, use_container_width=True)

# --------------------------------------------------
# TAB 2: EXCEPTION WORKLIST
# --------------------------------------------------

with tab2:
    st.subheader("Capex Exception Worklist")

    st.dataframe(
        filtered_exceptions,
        use_container_width=True,
        height=500
    )

    st.info(
        "This worklist helps finance, audit, and management teams prioritize "
        "capex projects requiring governance review."
    )

# --------------------------------------------------
# TAB 3: AUDIT OBSERVATION
# --------------------------------------------------

with tab3:
    st.subheader("Audit Observation Generator")

    if filtered_exceptions.empty:
        st.warning("No exceptions available for the selected filters.")
    else:
        selected_exception = st.selectbox(
            "Select an exception",
            filtered_exceptions["exception_id"].tolist()
        )

        selected_row = filtered_exceptions[
            filtered_exceptions["exception_id"] == selected_exception
        ].iloc[0]

        observation = f"""
Observation:
A capex governance exception was identified for project {selected_row["project_id"]} - {selected_row["project_name"]}, located at {selected_row["location"]}.

Risk Level:
{selected_row["risk_level"]} risk with a risk score of {selected_row["risk_score"]}.

Condition:
{selected_row["exception_summary"]}.

Financial Exposure:
{selected_row["financial_exposure"]:,.2f}.

Recommended Management Action:
{selected_row["recommended_action"]}.

Management Priority:
This exception should be reviewed by Finance, Operations, and the relevant approval owner before further spend or capitalization treatment is finalized.
"""

        st.code(observation, language="text")

# --------------------------------------------------
# TAB 4: ASK AGENT
# --------------------------------------------------

with tab4:
    st.subheader("Ask the Capex Agent")

    st.write(
        "Ask simple review questions. The agent will filter the capex data "
        "and return the relevant governance worklist."
    )

    question = st.text_input(
        "Ask a review question",
        value="Show high risk projects"
    )

    if st.button("Answer"):
        q = question.lower()

        if "high" in q or "critical" in q:
            result = exceptions[
                exceptions["risk_level"].isin(["Critical", "High"])
            ]
            st.success("Showing Critical and High risk capex exceptions.")
            st.dataframe(result, use_container_width=True)

        elif "roi" in q or "low roi" in q:
            result = df.sort_values("expected_roi").head(20)
            st.success("Showing projects with the lowest expected ROI.")
            st.dataframe(result, use_container_width=True)

        elif "document" in q or "supporting" in q:
            result = df[df["supporting_docs_flag"] == 0]
            st.success("Showing projects with missing supporting documents.")
            st.dataframe(result, use_container_width=True)

        elif "approval" in q or "approved" in q:
            result = df[df["approval_flag"] == 0]
            st.success("Showing projects with missing approval.")
            st.dataframe(result, use_container_width=True)

        elif "overrun" in q or "budget" in q or "variance" in q:
            result = df[df["budget_variance_pct"] > 0.10].sort_values(
                "budget_variance_pct",
                ascending=False
            )
            st.success("Showing projects with budget overrun above 10%.")
            st.dataframe(result, use_container_width=True)

        elif "capitalization" in q or "capitalize" in q:
            result = df[df["capitalization_rule"] == "Review Required"]
            st.success("Showing projects requiring capitalization review.")
            st.dataframe(result, use_container_width=True)

        elif "delay" in q or "delayed" in q:
            result = df[df["delay_days"] > 30].sort_values(
                "delay_days",
                ascending=False
            )
            st.success("Showing projects delayed by more than 30 days.")
            st.dataframe(result, use_container_width=True)

        else:
            st.info(
                "Try asking: high risk projects, low ROI, missing documents, "
                "missing approval, budget overrun, capitalization review, or delayed projects."
            )

# --------------------------------------------------
# TAB 5: DATA DOWNLOAD
# --------------------------------------------------

with tab5:
    st.subheader("Download Processed Outputs")

    st.write("Download the generated governance datasets for review or Power BI use.")

    enriched_csv = df.to_csv(index=False).encode("utf-8")
    exceptions_csv = exceptions.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Capex Enriched Data",
        data=enriched_csv,
        file_name="capex_enriched.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download Capex Exceptions Data",
        data=exceptions_csv,
        file_name="capex_exceptions.csv",
        mime="text/csv"
    )

st.divider()

st.caption(
    "Portfolio project using simulated data only. No confidential company data is included."
)