import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.queryguard.evaluators.quality_eval import run_quality_checks
from src.queryguard.agents.sql_agent import load_data_to_sqlite, ask
from src.queryguard.agents.explain_agent import explain_issues
from src.queryguard.scoring.aggregate import calculate_score

st.set_page_config(page_title="QueryGuard", page_icon="🛡️", layout="wide")
st.title("🛡️ QueryGuard")
st.markdown("**AI-Powered Data Quality Validator & SQL Chat Agent**")
st.divider()

with st.sidebar:
    st.header("⚙️ Settings")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    rules_file = st.selectbox("Select Rules", ["scenarios/sales_rules.yaml"])
    st.divider()
    st.markdown("**Built by:** Sadvilas Buddiga")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.to_csv("examples/uploaded_data.csv", index=False)
    csv_path = "examples/uploaded_data.csv"
else:
    csv_path = "examples/sales_data.csv"
    df = pd.read_csv(csv_path)

conn, df = load_data_to_sqlite(csv_path)

tab1, tab2, tab3 = st.tabs(["📊 Data Quality", "💬 Chat With Data", "📋 Raw Data"])

with tab1:
    st.subheader("Data Quality Report")
    if st.button("🔍 Run Quality Checks", type="primary"):
        with st.spinner("Running checks..."):
            try:
                results = run_quality_checks(df, rules_file)
                score_data = calculate_score(results)
                explanation = explain_issues(results)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Quality Score", f"{score_data['score']}/100")
                col2.metric("Grade", score_data["grade"])
                col3.metric("Checks Passed", f"{score_data['passed']}/{score_data['total_checks']}")
                col4.metric("Failed", score_data["failed"])
                st.divider()
                st.subheader("🤖 AI Explanation")
                st.info(explanation)
                st.divider()
                st.subheader("📋 Check Results")
                results_df = pd.DataFrame(results)
                results_df["status"] = results_df["passed"].apply(lambda x: "✅ PASS" if x else "❌ FAIL")
                st.dataframe(results_df[["rule", "column", "status", "severity", "detail"]], use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("👆 Click Run Quality Checks to validate your data")

with tab2:
    st.subheader("💬 Ask Questions About Your Data")
    examples = ["What is the total revenue by store?", "Show me the top products by quantity sold", "What is the revenue by region?", "Show average price by product"]
    cols = st.columns(len(examples))
    question = ""
    for i, ex in enumerate(examples):
        if cols[i].button(ex, key=f"ex_{i}"):
            question = ex
    user_question = st.text_input("Or type your own question:", value=question, placeholder="e.g. What is the total revenue by store?")
    if user_question:
        with st.spinner("Thinking..."):
            result = ask(user_question, conn)
        if result["error"]:
            st.error(f"Error: {result['error']}")
        else:
            st.success(f"Mode: {result['mode'].upper()}")
            st.code(result["sql"], language="sql")
            st.dataframe(result["result"], use_container_width=True)

with tab3:
    st.subheader("📋 Raw Data Preview")
    st.caption(f"{len(df)} rows · {len(df.columns)} columns")
    st.dataframe(df, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", len(df))
    col2.metric("Total Columns", len(df.columns))
    col3.metric("Null Values", int(df.isnull().sum().sum()))
