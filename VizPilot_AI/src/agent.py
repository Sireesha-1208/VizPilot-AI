

import re
import duckdb
import pandas as pd
import streamlit as st
from google import genai


class VisualizationAgent:

    def generate_text(self, prompt):
        try:
            response = self.client.interactions.create(
                model=self.model_name,
                input=prompt,
                timeout=60,
                generation_config={
                    "thinking_level": "low",
                    "max_output_tokens": 800
                }
            )

            text = response.output_text

            if not text:
                raise RuntimeError("Gemini returned an empty response.")

            return text.strip()

        except Exception as error:
            raise RuntimeError(
                f"Gemini API request failed: {error}"
            ) from error

    except Exception as error:
        raise RuntimeError(
            f"Gemini API request failed: {error}"
        ) from error
    # Analyze dataset columns
    def get_schema(self, df):

        schema = []

        for col in df.columns:
            schema.append(f"{col}: {df[col].dtype}")

        return "\n".join(schema)

    # Remove markdown formatting from SQL
    def clean_sql(self, sql):

        sql = re.sub(
            r"```(?:sql)?|```",
            "",
            sql,
            flags=re.IGNORECASE
        )

        return sql.strip().rstrip(";").strip()

    # Validate generated SQL
    def validate_sql(self, sql):

        sql = self.clean_sql(sql)

        if not re.match(
            r"^(SELECT|WITH)\b",
            sql,
            re.IGNORECASE
        ):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        if ";" in sql:
            raise ValueError(
                "Multiple SQL statements are not allowed."
            )

        blocked = (
            r"\b(COPY|ATTACH|DETACH|INSTALL|LOAD|CREATE|INSERT|"
            r"UPDATE|DELETE|DROP|ALTER|EXPORT|IMPORT|PRAGMA|"
            r"CALL|SET|RESET|VACUUM)\b"
        )

        if re.search(blocked, sql, re.IGNORECASE):
            raise ValueError(
                "The SQL query contains a prohibited operation."
            )

        external_functions = (
            r"\b(read_csv|read_csv_auto|read_parquet|read_json|"
            r"read_json_auto|read_text|read_blob|glob)\s*\("
        )

        if re.search(
            external_functions,
            sql,
            re.IGNORECASE
        ):
            raise ValueError(
                "External file access is not allowed."
            )

        return sql

    # Generate SQL from user question
    def generate_sql(self, question, schema):

        prompt = f"""
You are an expert DuckDB SQL data analyst.

Dataset table name: uploaded_data

Dataset schema:
{schema}

User question:
{question}

Generate a valid DuckDB SELECT query.

Rules:
1. Use only existing column names.
2. Use uploaded_data as the table name.
3. Generate SELECT queries only.
4. Do not access external files or tables.
5. Return only SQL code.
6. Do not use markdown code blocks.
"""

        response = self.generate_text(prompt)

        return self.validate_sql(response)

    # Execute SQL using DuckDB
    def execute_sql(self, sql, df):

        sql = self.validate_sql(sql)

        con = duckdb.connect(database=":memory:")

        try:
            # Disable external file access
            con.execute(
                "SET enable_external_access = false"
            )

            con.register("uploaded_data", df)

            result = con.execute(sql).fetchdf()

            return result

        finally:
            con.close()

    # Correct failed SQL automatically
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

Previous SQL query:
{previous_sql}

Database execution error:
{error}

Generate a corrected DuckDB SELECT query.

Rules:
1. Use only columns present in the schema.
2. Use uploaded_data as the table name.
3. Generate SELECT queries only.
4. Do not access external files or tables.
5. Preserve the original user intention.
6. Return only corrected SQL.
7. Do not use markdown code blocks.
"""

        response = self.generate_text(prompt)

        return self.validate_sql(response)

    # Automatically select appropriate chart
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

        response = self.generate_text(prompt)

        details = response.splitlines()

        values = {}

        for line in details:

            if ":" in line:

                key, value = line.split(":", 1)

                values[key.strip().upper()] = value.strip()

        chart_type = values.get(
            "CHART",
            "bar"
        ).lower()

        allowed = [
            "bar",
            "line",
            "pie",
            "scatter",
            "histogram",
            "box",
            "table"
        ]

        if chart_type not in allowed:
            chart_type = "bar"

        columns = list(result.columns)

        x = columns[0] if len(columns) >= 1 else None

        y = columns[1] if len(columns) >= 2 else None

        return {
            "title": values.get(
                "TITLE",
                "Data Visualization"
            ),

            "explanation": values.get(
                "EXPLANATION",
                "Dataset analysis completed."
            ),

            "chart_type": chart_type,

            "x": x,

            "y": y
        }

    # Main agent execution
    def run(self, question, df):

        trace = []

        try:

            # Step 1: Analyze dataset
            schema = self.get_schema(df)

            trace.append(
                "Step 1: Dataset schema analyzed."
            )

            trace.append(
                "Step 2: Relevant columns identified."
            )

            # Step 2: Generate SQL
            sql = self.generate_sql(
                question,
                schema
            )

            trace.append(
                "Step 3: SQL query generated."
            )

            # Step 3: Execute SQL with self-correction
            result = None

            for attempt in range(self.max_attempts):

                try:

                    result = self.execute_sql(
                        sql,
                        df
                    )

                    trace.append(
                        f"Attempt {attempt + 1}: SQL executed successfully."
                    )

                    break

                except Exception as error:

                    trace.append(
                        f"Attempt {attempt + 1}: SQL execution failed."
                    )

                    if attempt == self.max_attempts - 1:

                        raise RuntimeError(
                            f"SQL failed after {self.max_attempts} attempts: {error}"
                        )

                    trace.append(
                        "Self-correction: Sending error to Gemini."
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

            if result is None:

                raise RuntimeError(
                    "No SQL result was generated."
                )

            # Step 4: Generate chart information
            chart_details = self.choose_chart(
                question,
                result
            )

            trace.append(
                "Step 4: Visualization generated."
            )

            # Return final result
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
