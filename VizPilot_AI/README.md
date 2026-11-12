# VizPilot AI – Natural Language to Data Visualization Agent with Self-Correction

## 1. Project Overview

VizPilot AI is an AI-powered Natural Language to Data Visualization Agent that converts user questions written in simple English into meaningful data visualizations.

The system allows users to analyze datasets without requiring programming or SQL knowledge. Users can upload a CSV dataset, ask questions in natural language, and receive automatically generated visualizations based on the data.

The system also incorporates a **Self-Correction Mechanism** that identifies errors during query generation or execution, analyzes the errors, and attempts to correct them automatically.

## 2. Project Objective

The main objective of VizPilot AI is to simplify data analysis and visualization by allowing users to interact with datasets using natural language.

The project aims to:

- Convert natural language questions into SQL queries.
- Analyze uploaded datasets and understand their structure.
- Automatically execute generated queries.
- Select suitable chart types based on the query and dataset.
- Generate interactive visualizations.
- Detect and correct query-generation and execution errors using self-correction.

## 3. Key Features

### 3.1 Dataset Upload
- Upload CSV datasets.
- Automatically analyze dataset structure.
- Identify column names and data types.
- Display dataset information, including records and columns.

### 3.2 Natural Language Processing
- Accept questions in simple English.
- Understand user intent.
- Identify relevant columns and operations.
- Convert natural language questions into SQL queries.

### 3.3 AI-Based Query Generation
- Generate SQL queries based on user questions.
- Use dataset schema to identify relevant columns.
- Execute queries using DuckDB.

### 3.4 Automatic Chart Selection
- Analyze query results.
- Identify suitable visualization types.
- Generate charts based on the retrieved data.
- Display interactive visualizations using Plotly.

### 3.5 Self-Correction Mechanism
- Detect errors during query execution.
- Analyze error messages.
- Generate corrected queries.
- Retry execution within a limited number of attempts.
- Display the final result when execution succeeds.

### 3.6 Interactive Dashboard
- Display dataset statistics.
- Provide sample questions.
- Show generated SQL queries.
- Display visualizations and analysis results.
- Provide execution steps and processing information.

## 4. System Architecture

The system follows a modular architecture consisting of the following components:

1. **User Interface:** Streamlit provides the interactive application interface.
2. **Dataset Processing:** Pandas processes uploaded datasets and extracts schema information.
3. **Natural Language Understanding:** Understands user questions and identifies the required analysis.
4. **SQL Generation:** Generates SQL queries using the dataset schema and AI-based processing.
5. **Query Execution:** DuckDB executes the generated SQL queries.
6. **Self-Correction Engine:** Identifies errors and attempts to generate corrected queries.
7. **Visualization Engine:** Plotly generates interactive charts.
8. **Result Display:** Streamlit displays the final query results and visualizations.

## 5. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Pandas | Data processing and analysis |
| DuckDB | SQL query execution |
| Plotly | Interactive data visualization |
| Google Gemini API | AI-based natural language and query generation |
| SQLGlot | SQL parsing and validation |
| Groq | Alternative LLM integration, if configured |
| Git & GitHub | Version control and project hosting |

## 6. Algorithms and Methodologies

- Natural Language Processing (NLP)
- Schema-Based Query Generation
- Natural Language to SQL (NL2SQL)
- Data Profiling and Analysis
- Automatic Visualization Selection
- Execution-Based Error Detection
- AI-Based Self-Correction
- Iterative Query Execution

## 7. Project Workflow

1. User uploads a CSV dataset.
2. System reads and analyzes the dataset.
3. Dataset schema is extracted.
4. User enters a question in natural language.
5. AI understands the question.
6. SQL query is generated.
7. DuckDB executes the generated query.
8. If an error occurs, the self-correction mechanism analyzes and attempts to fix it.
9. The corrected query is executed again.
10. The system selects an appropriate chart.
11. Plotly generates the visualization.
12. Streamlit displays the final output.

## 8. Project Structure

```text
VizPilot_AI/
│
├── .venv/                  # Virtual environment
├── data/                   # Sample datasets
│   └── sample_sales.csv
│
├── src/
│   └── agent.py            # AI agent and query processing
│
├── app.py                  # Streamlit application
├── requirements.txt        # Project dependencies
├── .streamlit/
│   └── secrets.toml        # API key configuration (local only)
│
└── README.md               # Project documentation
```

## 9. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sireesha-1208/VizPilot-AI.git
```

### Step 2: Navigate to the Project Folder

```bash
cd VizPilot-AI/VizPilot_AI
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

For Windows:

```bash
.venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure API Key

Configure your Google Gemini API key using Streamlit secrets.

Create `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your_api_key_here"
```

For deployment, configure the same secret in the Streamlit Cloud application settings.

**Important:** Never upload API keys or `secrets.toml` containing private credentials to GitHub.

### Step 7: Run the Application

```bash
python -m streamlit run app.py
```

### Step 8: Open the Application

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## 10. Sample User Queries

Users can ask questions such as:

- Which category has the highest sales?
- Show total profit by region.
- What is the average sales value?
- Count the records in each category.
- Display sales distribution using a chart.

## 11. Evaluation Metrics

The performance of VizPilot AI can be evaluated using:

| Metric | Description |
|---|---|
| Query Execution Accuracy | Measures successful SQL execution |
| Chart Selection Accuracy | Evaluates appropriate chart selection |
| Visualization Correctness | Checks whether charts represent the query results correctly |
| Self-Correction Success Rate | Measures successful error correction |
| Response Time | Measures the time required to process a query |

## 12. Applications

- Business intelligence and reporting.
- Sales and financial data analysis.
- Educational data analysis.
- Exploratory data analysis.
- Data-driven decision-making.
- Automated reporting and visualization.

## 13. Future Enhancements

- Support for Excel and additional database formats.
- Advanced AI-powered data insights.
- Multiple LLM provider support.
- Improved query optimization.
- More visualization types.
- Conversation history and query tracking.
- Advanced visualization validation.
- Enhanced self-correction capabilities.

## 14. Conclusion

VizPilot AI simplifies data analysis by combining Natural Language Processing, AI-based SQL generation, automatic visualization, and self-correction.

It enables users without technical knowledge to explore datasets and generate meaningful visualizations using simple English questions.

The project aims to make data analysis more accessible, efficient, and user-friendly.

## 15. Author

**Developed by:** C. Sireesha

**Project Title:** VizPilot AI – Natural Language to Data Visualization Agent with Self-Correction

**GitHub Repository:**  
https://github.com/Sireesha-1208/VizPilot-AI
