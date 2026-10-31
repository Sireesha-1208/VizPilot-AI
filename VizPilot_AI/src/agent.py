
import re
import duckdb
import sqlglot


class VisualizationAgent:

    def __init__(self):
        self.trace = []

    def run(self, question, df):

        self.trace = []
        columns = list(df.columns)

        numeric = df.select_dtypes(
            include="number"
        ).columns.tolist()

        categorical = [
            c for c in columns if c not in numeric
        ]

        q = question.lower()

        metric = next(
            (
                c for c in numeric
                if any(k in c.lower() for k in
                       ["sales", "profit", "revenue", "amount"])
            ),
            numeric[0] if numeric else None
        )

        dimension = next(
            (
                c for c in categorical
                if any(k in c.lower() for k in
                       ["category", "region", "product"])
            ),
            categorical[0] if categorical else None
        )

        if not metric or not dimension:
            return {
                "status": "error",
                "error": "A categorical and numeric column are needed.",
                "trace": ["Dataset schema analyzed."]
            }

        if any(k in q for k in ["count", "number of"]):
            sql = (
                f'SELECT "{dimension}", COUNT(*) AS total_count '
                f'FROM uploaded_data GROUP BY 1 ORDER BY 2 DESC'
            )
            y = "total_count"
            title = f"Record count by {dimension}"

        else:
            safe_metric = re.sub(
                r"[^a-zA-Z0-9_]", "_", metric
            )

            sql = (
                f'SELECT "{dimension}", SUM("{metric}") '
                f'AS total_{safe_metric} '
                f'FROM uploaded_data GROUP BY 1 ORDER BY 2 DESC'
            )

            y = f"total_{safe_metric}"
            title = f"{metric} by {dimension}"

        chart = "line" if any(
            k in q for k in ["trend", "over time", "monthly"]
        ) else "bar"

        self.trace.append("Step 1: Dataset schema analyzed.")
        self.trace.append("Step 2: Relevant columns identified.")
        self.trace.append("Step 3: SQL query generated.")

        for attempt in range(1, 4):

            try:
                parsed = sqlglot.parse_one(
                    sql, read="duckdb"
                )

                if parsed.key.lower() != "select":
                    raise ValueError(
                        "Only SELECT queries are allowed."
                    )

                if ";" in sql.rstrip(";"):
                    raise ValueError(
                        "Multiple SQL statements are not allowed."
                    )

                con = duckdb.connect(":memory:")
                con.register("uploaded_data", df)

                result = con.execute(sql).df()
                con.close()

                self.trace.append(
                    f"Attempt {attempt}: SQL executed successfully."
                )

                return {
                    "status": "success",
                    "sql": sql,
                    "data": result,
                    "chart_type": chart,
                    "x": dimension,
                    "y": y,
                    "title": title,
                    "explanation":
                        "Dataset analyzed and grouped successfully.",
                    "trace": self.trace
                }

            except Exception as e:

                self.trace.append(
                    f"Attempt {attempt}: {str(e)}"
                )

                if attempt == 3:
                    return {
                        "status": "error",
                        "error": str(e),
                        "trace": self.trace
                    }

                self.trace.append("Retrying query.")
