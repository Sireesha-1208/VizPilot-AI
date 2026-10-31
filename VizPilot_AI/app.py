
import streamlit as st
import pandas as pd
import plotly.express as px
from src.agent import VisualizationAgent

st.set_page_config(
    page_title="VizPilot AI",
    page_icon="✦",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7ff, #eef0ff);
}
.block-container {
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(120deg, #111827, #312e81, #4f46e5);
    padding: 40px;
    border-radius: 20px;
    color: white;
}
.hero h1 {
    font-size: 44px;
    color: white;
}
.hero p {
    color: #dbeafe;
    font-size: 17px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>✦ VizPilot AI</h1>
    <p>Natural Language to Data Visualization Agent with Self-Correction</p>
    <p>Ask questions. Generate SQL. Discover insights through interactive charts.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("✦ VizPilot AI")
st.sidebar.caption("Intelligent Data Analytics")

uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV dataset",
    type=["csv"]
)

if st.sidebar.button("Load Sample Dataset"):
    st.session_state.df = pd.read_csv("data/sample_sales.csv")

if uploaded_file:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"Unable to read CSV: {e}")

st.title("Your Data Analytics Workspace")

if "df" not in st.session_state:
    st.info("Upload a CSV file or click Load Sample Dataset in the sidebar.")
    st.stop()

df = st.session_state.df

a, b, c = st.columns(3)
a.metric("Total Records", len(df))
b.metric("Total Columns", len(df.columns))
c.metric("Missing Values", int(df.isna().sum().sum()))

with st.expander("View Dataset"):
    st.dataframe(df.head(20), use_container_width=True)

st.subheader("Ask Your Data")

question = st.text_input(
    "Enter your question",
    placeholder="Example: Show total sales by region"
)

st.caption(
    "Try: Which category has the highest sales? "
    "Show total profit by region. Count records by category."
)

if st.button("Generate Visualization", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing your question..."):
            agent = VisualizationAgent()
            result = agent.run(question, df)

        if result["status"] == "success":
            st.success("Visualization generated successfully!")

            st.write("###", result["title"])
            st.write(result["explanation"])

            output = result["data"]
            chart = result["chart_type"]
            x = result.get("x")
            y = result.get("y")

            if chart == "line" and x and y:
                fig = px.line(output, x=x, y=y, markers=True)
            elif chart == "pie" and x and y:
                fig = px.pie(output, names=x, values=y)
            elif chart == "scatter" and x and y:
                fig = px.scatter(output, x=x, y=y)
            elif chart == "histogram" and x:
                fig = px.histogram(output, x=x)
            elif chart == "box" and x and y:
                fig = px.box(output, x=x, y=y)
            elif x and y:
                fig = px.bar(output, x=x, y=y)
            else:
                fig = None

            if fig is not None:
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Query Result")
            st.dataframe(output, use_container_width=True)

            with st.expander("Generated SQL"):
                st.code(result["sql"], language="sql")

            with st.expander("Agent Execution Trace"):
                for step in result["trace"]:
                    st.write("•", step)

            st.download_button(
                "Download Results",
                output.to_csv(index=False),
                "vizpilot_results.csv",
                "text/csv"
            )

        else:
            st.error(result["error"])
            st.write(result["trace"])

st.divider()
st.markdown(
    "<center>VizPilot AI | Intelligent Data Visualization</center>",
    unsafe_allow_html=True
)
