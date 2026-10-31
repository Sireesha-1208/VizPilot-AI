
import os
import re
from pathlib import Path

import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="VizPilot AI",
    page_icon="✨",
    layout="wide"
)

# --------------------------------------------------
# 2. PROJECT PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

SAMPLE_FILE = BASE_DIR / "data" / "sample_sales.csv"

# --------------------------------------------------
# 3. CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.main-title {
    background: linear-gradient(110deg, #172554, #4338ca);
    padding: 35px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}
.main-title h1 {
    color: white;
    font-size: 38px;
}
.main-title p {
    color: #e0e7ff;
    font-size: 17px;
}
.metric-card {
    background-color: #eef2ff;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 4. SESSION STATE
# --------------------------------------------------

if "df" not in st.session_state:
    st.session_state.df = None

if "last_sql" not in st.session_state:
    st.session_state.last_sql = None

# --------------------------------------------------
# 5. HEADER
# --------------------------------------------------

st.markdown("""
<div class="main-title">
    <h1>✨ VizPilot AI</h1>
    <h3>Natural Language to Data Visualization Agent with Self-Correction</h3>
    <p>
        Ask questions. Generate SQL. Discover insights
        through interactive charts.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 6. SIDEBAR - DATASET UPLOAD
# --------------------------------------------------

st.sidebar.title("✨ VizPilot AI")
st.sidebar.caption("Intelligent Data Analytics")

st.sidebar.subheader("Upload your CSV dataset")

uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.last_sql = None
        st.sidebar.success("Dataset uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Unable to read CSV: {e}")

if st.sidebar.button("Load Sample Dataset", use_container_width=True):

    try:
        if not SAMPLE_FILE.is_file():
            raise FileNotFoundError(
                f"Sample dataset not found at: {SAMPLE_FILE}"
            )

        st.session_state.df = pd.read_csv(SAMPLE_FILE)
        st.session_state.last_sql = None
        st.sidebar.success("Sample dataset loaded successfully!")

    except Exception as e:
        st.sidebar.error(str(e))
        st.sidebar.info(
            "Check that data/sample_sales.csv exists inside "
            "the same folder as app.py."
        )

# --------------------------------------------------
# 7. DATA ANALYTICS WORKSPACE
# --------------------------------------------------

st.title("Your Data Analytics Workspace")

if st.session_state.df is None:

    st.info(
        "Upload a CSV file or click Load Sample Dataset "
        "in the sidebar to get started."
    )

else:

    df = st.session_state.df

    st.success("Dataset is ready for analysis!")

    # --------------------------------------------------
    # 8. DATASET OVERVIEW
    # --------------------------------------------------

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rows", f"{df.shape[0]:,}")
    col2.metric("Total Columns", f"{df.shape[1]:,}")
    col3.metric("Missing Values", f"{int(df.isna().sum().sum()):,}")

    # --------------------------------------------------
    # 9. DATA PREVIEW
    # --------------------------------------------------

    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

    # --------------------------------------------------
    # 10. DATASET STRUCTURE
    # --------------------------------------------------

    with st.expander("View Dataset Structure"):

        structure = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isna().sum().values
        })

        st.dataframe(structure, use_container_width=True)

    # --------------------------------------------------
    # 11. STATISTICAL SUMMARY
    # --------------------------------------------------

    with st.expander("View Statistical Summary"):

        st.dataframe(
            df.describe(include="all").transpose(),
            use_container_width=True
        )

    st.divider()

    # --------------------------------------------------
    # 12. NATURAL LANGUAGE QUESTION
    # --------------------------------------------------

    st.subheader("Ask Your Dataset")

    st.write(
        "Ask a question in normal English. "
        "VizPilot AI will generate SQL and analyze your data."
    )

    question = st.text_input(
        "Enter your question",
        placeholder="Example: Show the top five products by sales"
    )

    # --------------------------------------------------
    # 13. GEMINI API KEY
    # --------------------------------------------------

    def get_api_key():

        key = os.environ.get("GEMINI_API_KEY")

        try:
            if not key:
                key = st.secrets.get("GEMINI_API_KEY", None)
        except Exception:
            pass

        return key

    # --------------------------------------------------
    # 14. GENERATE SQL USING GEMINI
    # --------------------------------------------------

    def generate_sql(user_question, columns, previous_sql=None,
                     error_message=None):

        api_key = get_api_key()

        if not api_key:
            raise ValueError(
                "Gemini API key is missing. Add GEMINI_API_KEY "
                "to Streamlit Cloud Secrets."
            )

        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an expert SQL data analyst.

Your task is to convert natural language questions into
DuckDB SQL queries.

Dataset table name: dataset

Available columns:
{columns}

User question:
{user_question}

Rules:
1. Generate valid DuckDB SQL.
2. Use only the table named dataset.
3. Use only the available column names.
4. Return only one SQL query.
5. Generate SELECT queries only.
6. Do not generate INSERT, UPDATE, DELETE, DROP or ALTER.
7. Do not invent column names.
8. Use appropriate aggregation and sorting.
9. If the user asks for top five, use LIMIT 5.
10. Return SQL only, without explanations or Markdown.

"""

        if previous_sql and error_message:
            prompt += f"""

The previous SQL query failed.

Previous SQL:
{previous_sql}

Execution error:
{error_message}

Correct the SQL query using the available columns.
Return only the corrected SQL.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        sql = response.text.strip()

        sql = re.sub(
            r"^```(?:sql)?\s*|\s*```$",
            "",
            sql,
            flags=re.IGNORECASE
        ).strip()

        return sql

    # --------------------------------------------------
    # 15. VALIDATE SQL
    # --------------------------------------------------

    def validate_sql(sql):

        cleaned = sql.strip().rstrip(";").strip()

        if not re.match(r"^(SELECT|WITH)\b", cleaned, re.I):
            raise ValueError("Only SELECT queries are allowed.")

        if ";" in cleaned:
            raise ValueError("Multiple SQL statements are not allowed.")

        forbidden = (
            r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|"
            r"COPY|ATTACH|DETACH|INSTALL|LOAD|EXPORT|IMPORT|"
            r"PRAGMA|CALL|EXECUTE)\b"
        )

        if re.search(forbidden, cleaned, re.I):
            raise ValueError("Unsafe SQL operation detected.")

        return cleaned

    # --------------------------------------------------
    # 16. EXECUTE SQL USING DUCKDB
    # --------------------------------------------------

    def execute_sql(sql, dataframe):

        connection = duckdb.connect(database=":memory:")

        try:
            connection.register("dataset", dataframe)

            result = connection.execute(sql).df()

            return result

        finally:
            connection.close()

    # --------------------------------------------------
    # 17. SELF-CORRECTION ENGINE
    # --------------------------------------------------

    def run_self_correction(user_question, dataframe):

        columns = ", ".join(
            f'"{column}" ({dataframe[column].dtype})'
            for column in dataframe.columns
        )

        previous_sql = None
        error_message = None

        for attempt in range(3):

            try:

                sql = generate_sql(
                    user_question,
                    columns,
                    previous_sql,
                    error_message
                )

                sql = validate_sql(sql)

                result = execute_sql(sql, dataframe)

                return sql, result, attempt

            except Exception as error:

                previous_sql = locals().get("sql", previous_sql)
                error_message = str(error)

                if attempt == 2:
                    raise RuntimeError(
                        f"Could not generate a working query "
                        f"after 3 attempts. Last error: {error_message}"
                    )

        raise RuntimeError("SQL execution failed.")

    # --------------------------------------------------
    # 18. AUTOMATIC CHART GENERATION
    # --------------------------------------------------

    def generate_chart(result):

        if result.empty:
            st.warning("No data available for visualization.")
            return

        numeric_columns = result.select_dtypes(
            include="number"
        ).columns.tolist()

        date_columns = result.select_dtypes(
            include=["datetime", "datetimetz"]
        ).columns.tolist()

        if not date_columns:
            for column in result.columns:
                try:
                    converted = pd.to_datetime(
                        result[column],
                        errors="coerce"
                    )

                    if converted.notna().sum() > 0:
                        date_columns.append(column)
                        result[column] = converted
                        break

                except Exception:
                    continue

        category_columns = [
            column for column in result.columns
            if column not in numeric_columns + date_columns
        ]

        if date_columns and numeric_columns:

            fig = px.line(
                result,
                x=date_columns[0],
                y=numeric_columns[0],
                markers=True,
                title="Trend Analysis"
            )

        elif category_columns and numeric_columns:

            fig = px.bar(
                result,
                x=category_columns[0],
                y=numeric_columns[0],
                title="Category Comparison",
                text_auto=True
            )

        elif len(numeric_columns) >= 2:

            fig = px.scatter(
                result,
                x=numeric_columns[0],
                y=numeric_columns[1],
                title="Data Relationship"
            )

        elif len(numeric_columns) == 1:

            fig = px.histogram(
                result,
                x=numeric_columns[0],
                title="Distribution Analysis"
            )

        else:
            st.info(
                "No suitable numeric columns were found "
                "for automatic chart generation."
            )
            return

        fig.update_layout(
            template="plotly_white",
            height=480
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------
    # 19. ASK AI BUTTON
    # --------------------------------------------------

    if st.button("✨ Analyze with VizPilot AI", type="primary"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            try:

                with st.spinner(
                    "Understanding your question and generating SQL..."
                ):

                    sql, result, attempts = run_self_correction(
                        question,
                        df
                    )

                st.session_state.last_sql = sql

                st.success("Analysis completed successfully!")

                if attempts > 0:
                    st.info(
                        f"Self-correction succeeded after "
                        f"{attempts} correction attempt(s)."
                    )
                else:
                    st.info("SQL executed successfully on the first attempt.")

                # Generated SQL
                st.subheader("Generated SQL Query")

                st.code(sql, language="sql")

                # Query result
                st.subheader("Query Results")

                st.dataframe(
                    result,
                    use_container_width=True
                )

                # Visualization
                st.subheader("Interactive Visualization")

                generate_chart(result)

                # Download results
                csv_data = result.to_csv(index=False).encode("utf-8")

                st.download_button(
                    "Download Results as CSV",
                    data=csv_data,
                    file_name="vizpilot_results.csv",
                    mime="text/csv"
                )

            except Exception as e:

                st.error(f"Analysis failed: {e}")

                st.warning(
                    "Check your API key, dataset columns, "
                    "and SQL query before trying again."
                )

st.divider()

st.caption(
    "VizPilot AI | AI-Powered Natural Language Data Visualization "
    "Agent with Self-Correction"
)
