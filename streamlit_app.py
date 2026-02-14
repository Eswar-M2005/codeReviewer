import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import tempfile
import os

from modules.module1 import read_python_file, detect_issues_ast
from modules.module2_ollama import build_results_with_ai, build_results
from modules.module3 import aggregate_module3_results


# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Powered Python Code Reviewer")
st.markdown("Professional code quality analysis & AI feedback")

# -----------------------------------
# FILE UPLOAD
# -----------------------------------

uploaded_file = st.file_uploader("Upload Python File", type=["py"])

if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    code = read_python_file(tmp_path)
    issues = detect_issues_ast(code)

    results_offline = build_results(issues)

    # Tabs Layout
    tab1, tab2, tab3, tab4 = st.tabs([
        " Scan",
        " AI Review",
        " Dashboard",
        " Report"
    ])

    # =====================================
    # TAB 1 — SCAN
    # =====================================
    with tab1:
        st.subheader("Code Structure Metrics")

        tree = ast.parse(code)

        num_functions = sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree))
        num_classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
        num_loops = sum(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree))
        num_conditionals = sum(isinstance(n, ast.If) for n in ast.walk(tree))

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Functions", num_functions)
        col2.metric("Classes", num_classes)
        col3.metric("Loops", num_loops)
        col4.metric("Conditionals", num_conditionals)
        col5.metric("Total Issues", len(results_offline))

    # =====================================
    # TAB 2 — AI REVIEW
    # =====================================
    with tab2:
        st.subheader("AI Code Review")

        if not issues:
            st.success("No issues detected 🎉")
        else:
            with st.spinner("Generating AI feedback via Ollama..."):
                results_ai = build_results_with_ai(issues, code)

            df = pd.DataFrame(results_ai)
            st.dataframe(df, use_container_width=True)

    # =====================================
    # TAB 3 — DASHBOARD (Charts)
    # =====================================
    with tab3:
        st.subheader("Issue Analytics Dashboard")

        if not results_offline:
            st.info("No issues detected.")
        else:
            df = pd.DataFrame(results_offline)

            # Severity Distribution
            severity_counts = df["severity"].value_counts().reset_index()
            severity_counts.columns = ["Severity", "Count"]

            col1, col2 = st.columns(2)

            with col1:
                fig_bar = px.bar(
                    severity_counts,
                    x="Severity",
                    y="Count",
                    title="Issues by Severity",
                    color="Severity"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                fig_pie = px.pie(
                    severity_counts,
                    names="Severity",
                    values="Count",
                    title="Severity Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # Issue Types
            issue_counts = df["issue"].value_counts().reset_index()
            issue_counts.columns = ["Issue", "Count"]

            fig_issue = px.bar(
                issue_counts,
                x="Issue",
                y="Count",
                title="Issue Type Distribution",
                color="Issue"
            )

            st.plotly_chart(fig_issue, use_container_width=True)

    # =====================================
    # TAB 4 — REPORT
    # =====================================
    with tab4:
        st.subheader("Export Report")

        if results_offline:

            summary = aggregate_module3_results(results_offline, tmp_path)
            st.json(summary)

            df = pd.DataFrame(results_offline)

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download CSV Report",
                data=csv,
                file_name="code_review_report.csv",
                mime="text/csv"
            )

        else:
            st.info("No issues to export.")

    os.unlink(tmp_path)

else:
    st.info("Upload a Python file to begin analysis.")
