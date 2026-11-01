
import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path
from src.agent import VisualizationAgent


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="VizPilot AI",
    page_icon="✦",
    layout="wide"
)


# --------------------------------
# CUSTOM CSS
# --------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7ff, #eef0ff);
}

.block-container {
    padding-top: 2rem;
}

.hero {
    background: linear-gradient(
        120deg, #111827, #312e81, #4f46e5
    );
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


# --------------------------------
# HEADER
# --------------------------------

st.markdown("""
<div class="hero">
    <h1>✦ VizPilot AI</h1>
    <p>Natural Language to Data Visualization Agent with Self-Correction</p>
    <p>Ask questions. Generate SQL. Discover insights through interactive charts.</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------
# SIDEBAR
# --------------------------------

st.sidebar.title("✦ VizPilot AI")
st.sidebar.caption("Intelligent Data Analytics")

uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV dataset",
    type=["csv"]
)


# --------------------------------
# DATASET LOADING
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "data" / "sample_sales.csv"

if "df" not in st.session_state:
    st.session_state.df = None

# Load sample dataset if available
if st.session_state.df is None and CSV_PATH.exists():
    try:
        st.session_state.df = pd.read_csv(CSV_PATH)
    except Exception as e:
        st.error(f"Unable to load sample dataset: {e}")

# Load uploaded dataset
if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.sidebar.success("Dataset uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Unable to read CSV: {e}")


# --------------------------------
# MAIN WORKSPACE
# --------------------------------

st.title("Your Data Analytics Workspace")

if (
    st.session_state.df is None
    or st.session_state.df.empty
):
    st.info(
        "Please upload a CSV dataset using the sidebar "
        "or add data/sample_sales.csv to your project."
    )
    st.stop()

df = st.session_state.df


# --------------------------------
# DATASET METRICS
# --------------------------------

a, b, c = st.columns(3)

a.metric("Total Records", len(df))
b.metric("Total Columns", len(df.columns))
c.metric(
    "Missing Values",
    int(df.isna().sum().sum())
)


# --------------------------------
# VIEW DATASET
# --------------------------------

with st.expander("View Dataset"):
    st.dataframe(
        df.head(20),
        use_container_width=True
    )

with st.expander("Dataset Information"):
    st.write("Column Names:")
    st.write(list(df.columns))

    st.write("Data Types:")
    st.write(df.dtypes.astype(str))


# --------------------------------
# ASK YOUR DATA
# --------------------------------

st.subheader("Ask Your Data")

question = st.text_input(
    "Enter your question",
    placeholder="Example: Show total sales by region"
)

st.caption(
    "Try: Which category has the highest sales? "
    "Show total profit by region. "
    "Count records by category."
)


# --------------------------------
# GENERATE VISUALIZATION
# --------------------------------

if st.button(
    "Generate Visualization",
    type="primary"
):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            with st.spinner(
                "Analyzing your question..."
            ):

                agent = VisualizationAgent()

                result = agent.run(question, df)

            if result.get("status") == "success":

                st.success(
                    "Visualization generated successfully!"
                )

                # Chart title
                st.subheader(
                    result.get("title", "Generated Visualization")
                )

                # Explanation
                st.write(
                    result.get(
                        "explanation",
                        "Analysis completed successfully."
                    )
                )

                # Result data
                output = result["data"]

                chart = result.get("chart_type")

                x = result.get("x")
                y = result.get("y")

                # --------------------------------
                # CHART GENERATION
                # --------------------------------

                if chart == "line" and x and y:

                    fig = px.line(
                        output,
                        x=x,
                        y=y,
                        markers=True
                    )

                elif chart == "pie" and x and y:

                    fig = px.pie(
                        output,
                        names=x,
                        values=y
                    )

                elif chart == "scatter" and x and y:

                    fig = px.scatter(
                        output,
                        x=x,
                        y=y
                    )

                elif chart == "histogram" and x:

                    fig = px.histogram(
                        output,
                        x=x
                    )

                elif chart == "box" and x and y:

                    fig = px.box(
                        output,
                        x=x,
                        y=y
                    )

                elif x and y:

                    fig = px.bar(
                        output,
                        x=x,
                        y=y
                    )

                else:

                    fig = None

                if fig is not None:

                    fig.update_layout(
                        template="plotly_white",
                        title=result.get("title", "")
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                # --------------------------------
                # QUERY RESULT
                # --------------------------------

                st.subheader("Query Result")

                st.dataframe(
                    output,
                    use_container_width=True
                )

                # --------------------------------
                # GENERATED SQL
                # --------------------------------

                with st.expander("Generated SQL"):

                    st.code(
                        result.get("sql", "SQL unavailable"),
                        language="sql"
                    )

                # --------------------------------
                # EXECUTION TRACE
                # --------------------------------

                with st.expander("Agent Execution Trace"):

                    for step in result.get("trace", []):
                        st.write("•", step)

                # --------------------------------
                # DOWNLOAD RESULTS
                # --------------------------------

                st.download_button(
                    label="Download Results",
                    data=output.to_csv(index=False),
                    file_name="vizpilot_results.csv",
                    mime="text/csv"
                )

            else:

                st.error(
                    result.get(
                        "error",
                        "Unable to generate visualization."
                    )
                )

                st.write(
                    result.get("trace", [])
                )

        except Exception as e:

            st.error(
                "An error occurred while processing your question."
            )

            st.exception(e)


# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.markdown(
    """
    <center>
        VizPilot AI | Intelligent Data Visualization
    </center>
    """,
    unsafe_allow_html=True
)
