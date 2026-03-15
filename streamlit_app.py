import streamlit as st
import requests
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AI Financial Agent", layout="wide")

st.title("AI Financial Agent")
st.caption("LLM-powered financial analysis and anomaly detection dashboard")

API_BASE_URL = "http://127.0.0.1:8001"
API_URL = f"{API_BASE_URL}/query"
INVOICES_URL = f"{API_BASE_URL}/invoices"
ANOMALIES_URL = f"{API_BASE_URL}/anomalies"
SET_DATASET_URL = f"{API_BASE_URL}/set-dataset"
RESET_DATASET_URL = f"{API_BASE_URL}/reset-dataset"
ACTIVE_DATASET_URL = f"{API_BASE_URL}/active-dataset"

try:
    active_response = requests.get(ACTIVE_DATASET_URL, timeout=30)
    active_response.raise_for_status()
    active_data = active_response.json()
    st.info(f"Active dataset: {active_data['file_name']}")
except requests.exceptions.RequestException:
    st.warning("Could not determine active dataset.")

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.sidebar.header("Quick Questions")
quick_question = st.sidebar.selectbox(
    "Choose an example",
    [
        "",
        "show suspicious invoices",
        "list all invoices",
        "is the system healthy?",
    ],
)

st.sidebar.subheader("Upload a CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    save_path = UPLOAD_DIR / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        response = requests.post(
            SET_DATASET_URL,
            json={"file_path": str(save_path.resolve())},
            timeout=30,
        )
        response.raise_for_status()
        st.sidebar.success(f"Using uploaded dataset: {uploaded_file.name}")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Could not set uploaded dataset: {e}")

question = st.text_input(
    "Enter your financial question:",
    value=quick_question,
    placeholder="Example: show suspicious invoices",
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    run_clicked = st.button("Run Analysis", use_container_width=True)

with col2:
    show_all_clicked = st.button("Show Invoice Summary", use_container_width=True)

with col3:
    show_anomalies_clicked = st.button("Show Anomalies", use_container_width=True)

with col4:
    reset_dataset_clicked = st.button("Reset Dataset", use_container_width=True)

if reset_dataset_clicked:
    try:
        response = requests.post(RESET_DATASET_URL, timeout=30)
        response.raise_for_status()
        result = response.json()
        st.success(result.get("message", "Dataset reset successfully."))
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reset dataset: {e}")

if run_clicked:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            response = requests.post(API_URL, json={"question": question}, timeout=120)
            response.raise_for_status()
            result = response.json()

            st.subheader("AI Response")
            st.write(result.get("answer", "No answer returned."))

            st.subheader("Detected Intent")
            st.code(result.get("intent", "unknown"))

            results = result.get("results", [])

            if results:
                df = pd.DataFrame(results)

                st.subheader("Results Table")
                st.dataframe(df, use_container_width=True)

                if "amount" in df.columns:
                    st.subheader("Amount Distribution")
                    chart_df = df[["invoice_id", "amount"]].copy() if "invoice_id" in df.columns else df[["amount"]].copy()
                    if "invoice_id" in chart_df.columns:
                        st.bar_chart(chart_df.set_index("invoice_id"))
                    else:
                        st.bar_chart(chart_df)

                if "llm_explanation" in df.columns:
                    st.subheader("AI Explanations")
                    for _, row in df.iterrows():
                        invoice_id = row.get("invoice_id", "Unknown Invoice")
                        explanation = row.get("llm_explanation", "")
                        st.markdown(f"**{invoice_id}**")
                        st.info(explanation)
            else:
                st.info("No results returned.")

        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the API: {e}")

if show_all_clicked:
    try:
        response = requests.get(INVOICES_URL, timeout=120)
        response.raise_for_status()
        invoices = response.json()

        df = pd.DataFrame(invoices)

        st.subheader("All Invoices")
        st.dataframe(df, use_container_width=True)

        if "vendor_name" in df.columns and "amount" in df.columns:
            vendor_totals = (
                df.groupby("vendor_name", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            st.subheader("Total Spend by Vendor")
            st.bar_chart(vendor_totals.set_index("vendor_name"))

    except requests.exceptions.RequestException as e:
        st.error(f"Could not load invoice summary: {e}")

if show_anomalies_clicked:
    try:
        response = requests.get(ANOMALIES_URL, timeout=120)
        response.raise_for_status()
        result = response.json()
        anomalies = result.get("anomalies", [])

        st.subheader("Detected Anomalies")

        if anomalies:
            df = pd.DataFrame(anomalies)
            st.dataframe(df, use_container_width=True)

            if "llm_explanation" in df.columns:
                st.subheader("AI Explanations")
                for _, row in df.iterrows():
                    invoice_id = row.get("invoice_id", "Unknown Invoice")
                    explanation = row.get("llm_explanation", "")
                    st.markdown(f"**{invoice_id}**")
                    st.info(explanation)
        else:
            st.info("No anomalies found in the active dataset.")

    except requests.exceptions.RequestException as e:
        st.error(f"Could not load anomalies: {e}")