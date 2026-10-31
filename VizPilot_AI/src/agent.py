

import re
import duckdb
import pandas as pd
import google.generativeai as genai
import streamlit as st


class VisualizationAgent:

    def __init__(self):
        api_key = st.secrets["GOOGLE_API_KEY"]

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            "gemini-2.0-flash"
        )

        self.max_attempts = 3

    def get_schema(self, df):
        schema = []

        for col in df.columns:
            schema.append(
                f"{col}: {df[col].dtype}"
            )

        return "\n".join(schema)

    def generate_sql(self, question, schema):
        prompt = f"""
You are an expert SQL data analyst.

Dataset table name: uploaded_data

Dataset schema:
{schema}

User question:
{question}

Generate a valid DuckDB SQL query.

Rules:
1. Use only existing column names.
2. Use uploaded_data as the table name.
3. Generate SELECT queries only.
4. Return only SQL code.
5. Do not use markdown code blocks.
"""

        response = self.model.generate_content(prompt)

        return self.clean_sql(response.text)

    def clean_sql(self, sql):
        sql = re.sub(r"```sql|```", "", sql)
        return sql.strip().rstrip(";")

    def execute_sql(self, sql, df):
        con = duckdb.connect(database=":memory:")

        try:
            con.register("uploaded_data", df)

            result = con.execute(sql).fetchdf()

            return result

        finally:
            con.close()

    def correct_sql(
        self,
        question,
        schema,
        previous_sql,
        error
    ):
        prompt = f"""
You are an expert DuckDB SQL debugging assistant.

Original user question:
{question}

Dataset schema:
{schema}

Previous incorrect SQL:
{previous_sql}

Database execution error:
{error}

Correct the SQL query.

Rules:
1. Use only columns present in the schema.
2. Use uploaded_data as the table name.
3. Generate SELECT queries only.
4. Preserve the user's original intention.
5. Return only corrected SQL.
"""

        response = self.model.generate_content(prompt)

        return self.clean_sql(response.text)

    def choose_chart(self, question, result):
        prompt = f"""
You are a data visualization expert.

User question:
{question}

Result columns:
{list(result.columns)}

Result preview:
{result.head(5).to_string()}

Choose the most appropriate chart.

Available chart types:
bar, line, pie, scatter, histogram, box, table

Return exactly three lines:
TITLE: chart title
EXPLANATION: short explanation
CHART: chart type
"""

        response = self.model.generate_content(prompt)

        details = response.text.strip().splitlines()

        values = {}

        for line in details:
            if ":" in line:
                key, value = line.split(":", 1)
                values[key.strip().upper()] = value.strip()

        chart_type = values.get("CHART", "bar").lower()

        allowed = [
            "bar", "line", "pie",
            "scatter", "histogram", "box", "table"
        ]

        if chart_type not in allowed:
            chart_type = "bar"

        columns = list(result.columns)

        x = columns[0] if len(columns) >= 1 else None
        y = columns[1] if len(columns) >= 2 else None

        return {
            "title": values.get("TITLE", "Data Visualization"),
            "explanation": values.get(
                "EXPLANATION",
                "Dataset analysis completed."
            ),
            "chart_type": chart_type,
            "x": x,
            "y": y
        }

    def run(self, question, df):

        trace = []

        try:
            # Step 1: Analyze dataset schema
            schema = self.get_schema(df)

            trace.append(
                "Step 1: Dataset schema analyzed."
            )

            trace.append(
                "Step 2: Relevant columns identified."
            )

            # Step 2: Generate SQL
            sql = self.generate_sql(question, schema)

            trace.append(
                "Step 3: SQL query generated."
            )

            # Step 3: Execute and self-correct
            result = None

            for attempt in range(self.max_attempts):

                try:
                    result = self.execute_sql(sql, df)

                    trace.append(
                        f"Attempt {attempt + 1}: SQL executed successfully."
                    )

                    break

                except Exception as error:

                    trace.append(
                        f"Attempt {attempt + 1}: SQL execution failed."
                    )

                    trace.append(
                        f"Error detected: {str(error)}"
                    )

                    if attempt == self.max_attempts - 1:
                        raise RuntimeError(
                            "SQL execution failed after "
                            f"{self.max_attempts} attempts: {error}"
                        )

                    trace.append(
                        "Self-correction: Sending error to AI."
                    )

                    sql = self.correct_sql(
                        question,
                        schema,
                        sql,
                        str(error)
                    )

                    trace.append(
                        f"Attempt {attempt + 2}: Corrected SQL generated."
                    )

            # Step 4: Generate visualization
            chart_details = self.choose_chart(
                question,
                result
            )

            trace.append(
                "Step 4: Visualization generated."
            )

            return {
                "status": "success",
                "title": chart_details["title"],
                "explanation": chart_details["explanation"],
                "data": result,
                "sql": sql,
                "chart_type": chart_details["chart_type"],
                "x": chart_details["x"],
                "y": chart_details["y"],
                "trace": trace
            }

        except Exception as error:

            trace.append(
                f"Agent failed: {str(error)}"
            )

            return {
                "status": "error",
                "error": str(error),
                "trace": trace
            }
