
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Customer Analytics", page_icon="👥", layout="wide")

st.title("👥 Customer Analytics Dashboard")
st.caption("Customer data exploration and analysis")

uploaded_file = st.file_uploader("Upload your customer CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.astype(str).str.strip()

    st.sidebar.header("Filters")
    search = st.sidebar.text_input("Search all columns")
    filtered = df.copy()

    text_cols = filtered.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if text_cols:
        col = st.sidebar.selectbox("Filter category", ["All"] + text_cols)
        if col != "All":
            options = sorted(filtered[col].dropna().astype(str).unique().tolist())
            selected = st.sidebar.multiselect("Select values", options, default=options)
            filtered = filtered[filtered[col].fillna("").astype(str).isin(selected)]

    if search:
        mask = filtered.astype(str).apply(
            lambda c: c.str.contains(search, case=False, na=False, regex=False)
        ).any(axis=1)
        filtered = filtered[mask]

    a, b, c, d = st.columns(4)
    a.metric("Customers / Records", f"{len(filtered):,}")
    b.metric("Columns", len(filtered.columns))
    c.metric("Missing Values", f"{filtered.isna().sum().sum():,}")
    d.metric("Duplicate Rows", f"{filtered.duplicated().sum():,}")

    if not filtered.empty:
        tab1, tab2, tab3 = st.tabs(["Overview", "Analysis", "Data"])

        with tab1:
            st.subheader("Dataset Preview")
            st.dataframe(filtered.head(10), use_container_width=True, hide_index=True)

        with tab2:
            cats = filtered.select_dtypes(include=["object", "category", "string"]).columns.tolist()
            nums = filtered.select_dtypes(include="number").columns.tolist()

            if cats:
                cat = st.selectbox("Choose customer category", cats)
                counts = filtered[cat].fillna("Missing").astype(str).value_counts().head(15)
                chart = counts.rename_axis(cat).reset_index(name="Count")
                fig = px.bar(chart, x=cat, y="Count", title=f"Records by {cat}")
                st.plotly_chart(fig, use_container_width=True)

            if nums:
                num = st.selectbox("Choose numeric measure", nums)
                fig = px.histogram(filtered, x=num, title=f"Distribution of {num}")
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.dataframe(filtered, use_container_width=True, hide_index=True)
            st.download_button(
                "Download filtered CSV",
                filtered.to_csv(index=False).encode("utf-8"),
                "customer_filtered.csv",
                "text/csv"
            )
else:
    st.info("Upload your customer CSV file to explore the dashboard.")
