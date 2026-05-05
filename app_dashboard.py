import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Retail Payment Retry Analytics",
    page_icon="💳",
    layout="wide"
)


# =========================================================
# PATH CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

GOLD_1_PATH = DATA_DIR / "GOLD_1_STORE_LEVEL_ANALYSIS.csv"
GOLD_2_PATH = DATA_DIR / "GOLD_2_PAYMENT_RECOVERY.csv"
GOLD_3_PATH = DATA_DIR / "GOLD_3_Monthly_Payment_Behavior.csv"
GOLD_4_PATH = DATA_DIR / "GOLD_4_Quarantine_Rows_Analysis.csv"


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def money(value):
    try:
        return f"${value:,.0f}"
    except Exception:
        return "$0"


def percent(value):
    try:
        return f"{value * 100:.2f}%"
    except Exception:
        return "0.00%"


@st.cache_data
def load_data():
    required_files = {
        "Gold 1 Store Revenue Leakage": GOLD_1_PATH,
        "Gold 2 Payment Recovery": GOLD_2_PATH,
        "Gold 3 Monthly Behavior": GOLD_3_PATH,
        "Gold 4 Quarantine Analysis": GOLD_4_PATH,
    }

    missing_files = [name for name, path in required_files.items() if not path.exists()]

    if missing_files:
        st.error("Some required CSV files are missing inside the data/ folder:")
        for file in missing_files:
            st.write(f"- {file}")
        st.stop()

    gold1 = pd.read_csv(GOLD_1_PATH)
    gold2 = pd.read_csv(GOLD_2_PATH)
    gold3 = pd.read_csv(GOLD_3_PATH)
    gold4 = pd.read_csv(GOLD_4_PATH)

    # Normalize column names
    gold1.columns = [c.strip() for c in gold1.columns]
    gold2.columns = [c.strip() for c in gold2.columns]
    gold3.columns = [c.strip() for c in gold3.columns]
    gold4.columns = [c.strip() for c in gold4.columns]

    # Numeric cleanup
    for col in ["lost_revenue", "recovered_revenue", "total_order_value", "leakage_rate"]:
        if col in gold1.columns:
            gold1[col] = pd.to_numeric(gold1[col], errors="coerce").fillna(0)

    for col in ["attempt_number", "orders_reaching_attempt", "orders_success_at_attempt", "recovered_revenue"]:
        if col in gold2.columns:
            gold2[col] = pd.to_numeric(gold2[col], errors="coerce").fillna(0)

    for col in ["attempt_number", "total_attempts", "success_count", "success_rate", "Success_Rate_Change"]:
        if col in gold3.columns:
            gold3[col] = pd.to_numeric(gold3[col], errors="coerce").fillna(0)

    for col in ["error_type_count", "error_percentage"]:
        if col in gold4.columns:
            gold4[col] = pd.to_numeric(gold4[col], errors="coerce").fillna(0)

    if "YEAR_MONTH" in gold3.columns:
        gold3["YEAR_MONTH"] = gold3["YEAR_MONTH"].astype(str)
        gold3 = gold3.sort_values("YEAR_MONTH")

    return gold1, gold2, gold3, gold4


gold1, gold2, gold3, gold4 = load_data()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("💳 Retail Payment Analytics")
st.sidebar.markdown("Revenue leakage, retry recovery, payment behavior, and data quality.")

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Store Revenue Leakage",
        "Retry Recovery",
        "Monthly Payment Behavior",
        "Data Quality Diagnostics",
        "Raw Gold Tables"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Project Layers")
st.sidebar.markdown(
    """
    **Raw → Silver → Gold → Dashboard**

    - Silver: cleaned and validated records  
    - Quarantine: rejected bad records  
    - Gold: business-ready analytics  
    """
)


# =========================================================
# HEADER
# =========================================================

st.title("Retail Payment Retry & Revenue Leakage Analytics")
st.markdown(
    """
    This dashboard analyzes failed payments, retry behavior, payment method switching, 
    recovered revenue, and raw data quality issues in a self-checkout style retail payment system.
    """
)


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================

if page == "Executive Overview":
    total_revenue = gold1["total_order_value"].sum()
    total_lost = gold1["lost_revenue"].sum()
    total_recovered = gold1["recovered_revenue"].sum()
    avg_leakage = total_lost / total_revenue if total_revenue else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Order Value", money(total_revenue))
    col2.metric("Lost Revenue", money(total_lost))
    col3.metric("Recovered Revenue", money(total_recovered))
    col4.metric("Overall Leakage Rate", percent(avg_leakage))

    st.markdown("## Business Story")

    st.info(
        """
        This project is not just showing payment counts. It connects failed payments to actual money loss,
        measures how much revenue retry attempts recover, tracks how customer payment behavior changes over time,
        and validates how much bad data was removed before analysis.
        """
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Revenue Leakage by Store")
        fig = px.bar(
            gold1.sort_values("lost_revenue", ascending=False),
            x="store_location",
            y="lost_revenue",
            hover_data=["total_order_value", "recovered_revenue", "leakage_rate"],
            title="Which store is losing the most revenue?"
        )
        fig.update_layout(xaxis_title="", yaxis_title="Lost Revenue", height=420)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Recovered Revenue by Retry Attempt")
        retry_df = gold2[gold2["attempt_number"] > 1].sort_values("attempt_number")
        fig = px.bar(
            retry_df,
            x="attempt_number",
            y="recovered_revenue",
            text="recovered_revenue",
            title="How much revenue was saved after retries?"
        )
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(xaxis_title="Attempt Number", yaxis_title="Recovered Revenue", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("## Key Takeaways")

    worst_store = gold1.sort_values("leakage_rate", ascending=False).iloc[0]
    best_retry = gold2[gold2["attempt_number"] > 1].sort_values("recovered_revenue", ascending=False).iloc[0]
    worst_error = gold4.sort_values("error_type_count", ascending=False).iloc[0]

    st.success(
        f"""
        - **Highest leakage store:** {worst_store['store_location']} with a leakage rate of **{percent(worst_store['leakage_rate'])}**.
        - **Most valuable retry attempt:** Attempt **{int(best_retry['attempt_number'])}** recovered **{money(best_retry['recovered_revenue'])}**.
        - **Most common data quality issue:** **{worst_error['error_type']}** in **{worst_error['table_name']}**.
        """
    )


# =========================================================
# STORE REVENUE LEAKAGE
# =========================================================

elif page == "Store Revenue Leakage":
    st.header("Gold 1: Store-Level Revenue Leakage")

    st.markdown(
        """
        This table answers: **Which store is losing the most money because payments failed or were cancelled?**
        """
    )

    selected_store = st.multiselect(
        "Filter store location",
        options=gold1["store_location"].unique(),
        default=list(gold1["store_location"].unique())
    )

    filtered = gold1[gold1["store_location"].isin(selected_store)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Filtered Total Revenue", money(filtered["total_order_value"].sum()))
    col2.metric("Filtered Lost Revenue", money(filtered["lost_revenue"].sum()))
    col3.metric("Filtered Recovered Revenue", money(filtered["recovered_revenue"].sum()))

    fig = px.bar(
        filtered.sort_values("lost_revenue", ascending=False),
        x="store_location",
        y=["lost_revenue", "recovered_revenue"],
        barmode="group",
        title="Lost Revenue vs Recovered Revenue by Store",
        hover_data=["total_order_value", "leakage_rate"]
    )
    fig.update_layout(xaxis_title="", yaxis_title="Revenue", height=500)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        filtered,
        x="total_order_value",
        y="lost_revenue",
        size="recovered_revenue",
        color="store_location",
        hover_name="store_location",
        title="Store Risk Map: Order Value vs Lost Revenue"
    )
    fig.update_layout(xaxis_title="Total Order Value", yaxis_title="Lost Revenue", height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Business Interpretation")
    st.write(
        """
        A store with high total revenue is not automatically bad. The important question is whether a large share of that revenue leaks through failed or cancelled payments.
        Stores with both high lost revenue and high leakage rate should be investigated first.
        """
    )

    st.dataframe(filtered, use_container_width=True)


# =========================================================
# RETRY RECOVERY
# =========================================================

elif page == "Retry Recovery":
    st.header("Gold 2: Payment Retry Recovery")

    st.markdown(
        """
        This table answers: **Are 2nd, 3rd, and 4th payment attempts actually useful?**
        """
    )

    gold2_sorted = gold2.sort_values("attempt_number").copy()
    gold2_sorted["success_rate_at_attempt"] = gold2_sorted.apply(
        lambda row: row["orders_success_at_attempt"] / row["orders_reaching_attempt"]
        if row["orders_reaching_attempt"] else 0,
        axis=1
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Attempts Reached", f"{int(gold2_sorted['orders_reaching_attempt'].sum()):,}")
    col2.metric("Total Successful Attempts", f"{int(gold2_sorted['orders_success_at_attempt'].sum()):,}")
    col3.metric("Retry Recovered Revenue", money(gold2_sorted[gold2_sorted["attempt_number"] > 1]["recovered_revenue"].sum()))

    left, right = st.columns(2)

    with left:
        fig = px.line(
            gold2_sorted,
            x="attempt_number",
            y="orders_reaching_attempt",
            markers=True,
            title="Retry Funnel: Orders Reaching Each Attempt"
        )
        fig.update_layout(xaxis_title="Attempt Number", yaxis_title="Orders Reaching Attempt", height=430)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        retry_only = gold2_sorted[gold2_sorted["attempt_number"] > 1]
        fig = px.bar(
            retry_only,
            x="attempt_number",
            y="recovered_revenue",
            text="recovered_revenue",
            title="Recovered Revenue by Retry Attempt"
        )
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(xaxis_title="Attempt Number", yaxis_title="Recovered Revenue", height=430)
        st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        gold2_sorted,
        x="attempt_number",
        y="success_rate_at_attempt",
        text="success_rate_at_attempt",
        title="Success Rate at Each Attempt"
    )
    fig.update_traces(texttemplate="%{text:.2%}", textposition="outside")
    fig.update_layout(xaxis_title="Attempt Number", yaxis_title="Success Rate", height=450)
    st.plotly_chart(fig, use_container_width=True)

    best_retry = gold2_sorted[gold2_sorted["attempt_number"] > 1].sort_values("recovered_revenue", ascending=False).iloc[0]

    st.success(
        f"""
        Attempt **{int(best_retry['attempt_number'])}** recovered the most revenue: **{money(best_retry['recovered_revenue'])}**.
        This means retries are not just technical events — they directly protect revenue.
        """
    )

    st.dataframe(gold2_sorted, use_container_width=True)


# =========================================================
# MONTHLY PAYMENT BEHAVIOR
# =========================================================

elif page == "Monthly Payment Behavior":
    st.header("Gold 3: Monthly Payment Behavior & Method Analysis")

    st.markdown(
        """
        This table answers: **How do customers behave across payment attempts and payment methods over time?**
        """
    )

    months = sorted(gold3["YEAR_MONTH"].unique())
    methods = sorted(gold3["payment_method"].unique())
    attempts = sorted(gold3["attempt_number"].unique())

    selected_months = st.multiselect("Select months", months, default=months)
    selected_methods = st.multiselect("Select payment methods", methods, default=methods)
    selected_attempts = st.multiselect("Select attempt numbers", attempts, default=attempts)

    filtered = gold3[
        (gold3["YEAR_MONTH"].isin(selected_months)) &
        (gold3["payment_method"].isin(selected_methods)) &
        (gold3["attempt_number"].isin(selected_attempts))
    ].copy()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Attempts", f"{int(filtered['total_attempts'].sum()):,}")
    col2.metric("Total Success Count", f"{int(filtered['success_count'].sum()):,}")
    overall_success = filtered["success_count"].sum() / filtered["total_attempts"].sum() if filtered["total_attempts"].sum() else 0
    col3.metric("Overall Success Rate", percent(overall_success))

    st.subheader("Success Rate Trend by Payment Method")

    fig = px.line(
        filtered,
        x="YEAR_MONTH",
        y="success_rate",
        color="payment_method",
        line_dash="attempt_number",
        markers=True,
        title="Monthly Success Rate by Method and Attempt"
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Success Rate", height=520)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Payment Method Usage by Attempt")

    usage = (
        filtered
        .groupby(["attempt_number", "payment_method"], as_index=False)["total_attempts"]
        .sum()
    )

    fig = px.bar(
        usage,
        x="attempt_number",
        y="total_attempts",
        color="payment_method",
        barmode="group",
        title="Which payment methods are used at each attempt?"
    )
    fig.update_layout(xaxis_title="Attempt Number", yaxis_title="Total Attempts", height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Month-over-Month Success Rate Change")

    change_df = filtered.copy()
    fig = px.bar(
        change_df,
        x="YEAR_MONTH",
        y="Success_Rate_Change",
        color="payment_method",
        facet_row="attempt_number",
        title="Success Rate Change from Previous Month"
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Success Rate Change", height=700)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Story From This Table")
    st.info(
        """
        This analysis shows whether customers keep retrying the same method or switch to another method.
        For example, if TAP is dominant in Attempt 1 but INSERT_CARD performs better in Attempt 2 or 3,
        that suggests customers may recover failed tap payments by switching payment method.
        """
    )

    st.dataframe(filtered.sort_values(["YEAR_MONTH", "attempt_number", "payment_method"]), use_container_width=True)


# =========================================================
# DATA QUALITY
# =========================================================

elif page == "Data Quality Diagnostics":
    st.header("Gold 4: Quarantine Rows Analysis")

    st.markdown(
        """
        This table answers: **How much bad data was rejected before building the business metrics?**
        """
    )

    selected_tables = st.multiselect(
        "Select affected table",
        options=sorted(gold4["table_name"].unique()),
        default=sorted(gold4["table_name"].unique())
    )

    filtered = gold4[gold4["table_name"].isin(selected_tables)].copy()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quarantined Rows", f"{int(filtered['error_type_count'].sum()):,}")
    col2.metric("Error Types", f"{filtered['error_type'].nunique():,}")
    col3.metric("Highest Error Rate", percent(filtered["error_percentage"].max()))

    fig = px.bar(
        filtered.sort_values("error_type_count", ascending=False),
        x="error_type",
        y="error_type_count",
        color="table_name",
        title="Quarantined Rows by Error Type",
        text="error_type_count"
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(xaxis_title="Error Type", yaxis_title="Error Count", height=570)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.treemap(
        filtered,
        path=["table_name", "error_type"],
        values="error_type_count",
        title="Data Quality Issue Breakdown"
    )
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Why This Matters")
    st.warning(
        """
        The dashboard does not blindly trust raw data. Invalid records are separated into quarantine,
        counted by issue type, and measured as a percentage of raw data volume.
        This proves the Gold tables are built from validated records.
        """
    )

    st.dataframe(filtered.sort_values("error_type_count", ascending=False), use_container_width=True)


# =========================================================
# RAW GOLD TABLES
# =========================================================

elif page == "Raw Gold Tables":
    st.header("Raw Gold Tables")

    selected_table = st.selectbox(
        "Select Gold Table",
        [
            "Gold 1 - Store Revenue Leakage",
            "Gold 2 - Payment Retry Recovery",
            "Gold 3 - Monthly Payment Behavior",
            "Gold 4 - Quarantine Analysis"
        ]
    )

    if selected_table == "Gold 1 - Store Revenue Leakage":
        st.dataframe(gold1, use_container_width=True)

    elif selected_table == "Gold 2 - Payment Retry Recovery":
        st.dataframe(gold2, use_container_width=True)

    elif selected_table == "Gold 3 - Monthly Payment Behavior":
        st.dataframe(gold3, use_container_width=True)

    else:
        st.dataframe(gold4, use_container_width=True)
