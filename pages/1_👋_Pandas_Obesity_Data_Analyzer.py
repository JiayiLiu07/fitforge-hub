import os
import re
import streamlit as st
import plotly.express as px
import pandas as pd
from openai import OpenAI
import logging
import sys
import sqlite3

# Ensure UTF-8 encoding to handle emojis
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Log session state and SQLite version for debugging
logging.info(f"Session state keys: {list(st.session_state.keys())}")
logging.info(f"SQLite version: {sqlite3.sqlite_version}")

st.markdown("""
<style>
    .main { background-color: #f9fafb; padding: 2rem; }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        border: none;
        font-weight: 600;
        transition: background-color 0.2s;
    }
</style> 
""", unsafe_allow_html=True)

# Initialize session state for history and summary
if "history" not in st.session_state:
    st.session_state.history = []
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Check for API Key from main page
if not st.session_state.get("api_key"):
    st.markdown(
        """
        <h1 style='text-align:center; font-size:2.8rem; margin-top:-1rem;'>
            👋 Pandas Obesity Data Analyzer
        </h1>
        <p style='text-align:center; font-size:1.1rem; color:#6c757d;'>
         Use LLM to convert natural language into SQL, and then use Pandas to calculate obesity data and plot it in seconds! <br>📈 Data: <i>obesity_level_attribute.csv</i> + <i>obesity_level_result.csv</i>
        </p>
        """,
        unsafe_allow_html=True
    )
    st.warning("⚠️ Please go to the sidebar and enter a valid API key in FitForge_Hub🚀 page")
    st.stop()

# Initialize OpenAI client for Aliyun
def initialize_client(api_key):
    return OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

try:
    client = initialize_client(st.session_state["api_key"])
except Exception as e:
    st.error(f"🚨 Failed to initialize OpenAI client: {e}")
    logging.error(f"OpenAI client initialization failed: {e}")
    st.stop()

# ---------- 1. Load data ----------
base_path = "data"
attribute_path = os.path.join(base_path, "obesity_level_attribute_clean.csv")
result_path = os.path.join(base_path, "obesity_level_result_clean.csv")

# Check if data files exist
if not os.path.exists(attribute_path) or not os.path.exists(result_path):
    st.error(f"🚨 Data files not found: {attribute_path} or {result_path}")
    logging.error(f"Data files not found: {attribute_path} or {result_path}")
    st.stop()

try:
    attr_df = pd.read_csv(attribute_path)
    result_df = pd.read_csv(result_path)
    logging.info(f"attr_df shape: {attr_df.shape}")
    logging.info(f"result_df shape: {result_df.shape}")
except Exception as e:
    st.error(f"🚨 Failed to load data files: {e}")
    logging.error(f"Data loading failed: {e}")
    st.stop()

# Process result
level_map = {
    'Overweight_Level_II': 3,
    'Overweight_Level_I': 2,
    'Obesity_Type_III': 6,
    'Obesity_Type_II': 5,
    'Obesity_Type_I': 4,
    'Normal_Weight': 1,
    'Insufficient_Weight': 0
}

result_df['level_num'] = result_df['obesity_level'].map(level_map)

# ---------- 2. Build Prompt ----------
PROMPT_TEMPLATE = """
You are a senior data analyst tasked with converting natural language questions into SQL queries for a Pandas DataFrame using pandasql.
The database contains a single DataFrame `merged_df` created by merging two DataFrames on `id`:

merged_df(
   id INT,
   Gender STRING,
   Age DOUBLE,
   Height DOUBLE,
   Weight DOUBLE,
   family_history_with_overweight INT,
   FAVC INT,
   FCVC DOUBLE,
   NCP DOUBLE,
   CAEC STRING,
   SMOKE INT,
   CH2O DOUBLE,
   SCC INT,
   FAF DOUBLE,
   TUE DOUBLE,
   CALC STRING,
   MTRANS STRING,
   obesity_level STRING,
   level_num INT
)

`level_num` is a numerical representation of the obesity level, higher values indicate more severe obesity levels.
Write a SQL query to be executed on `merged_df` using `pandasql`, and provide Plotly visualization code using the resulting DataFrame `df`.

Follow this format strictly:
```sql
SELECT ...
FROM merged_df
...
```

```python
# Plotly visualization code, df is the SQL result DataFrame
import plotly.express as px
fig = px.XXX(df, ...)
```

User's question: {question}

CRITICAL INSTRUCTIONS:
- Use `merged_df` as the table name in the SQL query.
- Do NOT use `attr_df` or `result_df`.
- Do NOT use `level_num` in ORDER BY or WHERE clauses.
- Use the following mapping for `obesity_level`: {level_map}
- For power operations (e.g., Height squared for BMI), you MUST use `Height * Height` in the SQL query. Under NO circumstances use POWER(Height, 2), POW(Height, 2), or Height ** 2, as these are NOT supported by SQLite in pandasql and will cause execution errors. `Height * Height` is the ONLY valid method for squaring Height.
- For BMI calculations (Weight / Height^2), ALWAYS use `Weight / (Height * Height)` in the SQL query. Example: SELECT Gender, (Weight / (Height * Height)) AS BMI FROM merged_df;
- Verify that your SQL query avoids any functions not supported by SQLite, such as POW or POWER.
"""

# ---------- 3. Convert natural language to SQL and Plotly code ----------
def nl_to_sql_and_plot(question: str):
    full_prompt = f"""
    Summary: {st.session_state.summary}
    """
    for q, a in st.session_state.history[-3:]:
        full_prompt += f"\nHistorical question: {q}\nHistorical answer: {a}"
    full_prompt += f"\nCurrent question: {PROMPT_TEMPLATE.format(question=question, level_map=level_map)}"

    logging.info("=========== Prompt ===========")
    logging.info(f"Sending prompt to LLM:\n{full_prompt}")

    messages = [{"role": "user", "content": full_prompt}]
    try:
        resp = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            temperature=0
        )
        text = resp.choices[0].message.content
    except Exception as e:
        logging.error(f"LLM API call failed: {e}")
        raise

    logging.info(f"LLM response:\n{text}")

    try:
        sql_block = re.findall(r"```sql\n(.*?)\n```", text, re.S)[0].strip()
        plot_block = re.findall(r"```python\n(.*?)\n```", text, re.S)[0].strip()
    except IndexError:
        logging.error("Failed to extract SQL or Plotly code from LLM response")
        raise ValueError("Invalid LLM response format")

    return sql_block, plot_block, text

# ---------- 4. Execute query and generate plot ----------
def run_and_plot(question: str):
    logging.info(f"Processing query: {question}")
    # Force Pandas for BMI queries to avoid SQLite issues
    if 'BMI' in question.upper():
        logging.info("Using Pandas for BMI calculation (skipping SQL)")
        merged_df = pd.merge(attr_df, result_df, on='id')
        df = merged_df[['Gender', 'Height', 'Weight']].copy()
        df['BMI'] = df['Weight'] / (df['Height'] * df['Height'])  # Use Pandas multiplication
        sql = "SELECT Gender, (Weight / (Height * Height)) AS BMI FROM merged_df"
        plot_code = """
import plotly.express as px
fig = px.histogram(df, x='BMI', color='Gender', nbins=50, title='BMI Distribution by Gender')
fig.update_layout(bargap=0.02)
"""
        answer = f"Pandas-based BMI calculation used to avoid SQLite issues.\n```sql\n{sql}\n```\n```python\n{plot_code}\n```"
    else:
        try:
            sql, plot_code, answer = nl_to_sql_and_plot(question)
        except Exception as e:
            st.error(f"🚨 API Key validation or LLM call failed: {e}")
            logging.error(f"LLM call failed: {e}")
            return None, None, None
        
        logging.info("=========== Code ===========")
        logging.info(f"Generated SQL query:\n{sql}")
        logging.info(f"Generated Plotly code:\n{plot_code}")

        # Post-process SQL to replace incorrect power operations
        original_sql = sql
        sql = re.sub(r'(?i)\bPOW\s*\(\s*Height\s*,\s*2\s*\)', '(Height * Height)', sql, flags=re.DOTALL | re.IGNORECASE)
        sql = re.sub(r'(?i)\bPOWER\s*\(\s*Height\s*,\s*2\s*\)', '(Height * Height)', sql, flags=re.DOTALL | re.IGNORECASE)
        sql = re.sub(r'Height\s*\*\*\s*2', '(Height * Height)', sql, flags=re.DOTALL | re.IGNORECASE)
        sql = re.sub(r'\(\s*Weight\s*/\s*POW\s*\(\s*Height\s*,\s*2\s*\)\s*\)', '(Weight / (Height * Height))', sql, flags=re.DOTALL | re.IGNORECASE)
        sql = re.sub(r'\(\s*Weight\s*/\s*POWER\s*\(\s*Height\s*,\s*2\s*\)\s*\)', '(Weight / (Height * Height))', sql, flags=re.DOTALL | re.IGNORECASE)
        if original_sql != sql:
            logging.info(f"SQL modified: Replaced power operations. Original:\n{original_sql}\nModified:\n{sql}")
        else:
            logging.info("No power operation replacements needed in SQL query")
        logging.info(f"Post-processed SQL query:\n{sql}")

        try:
            from pandasql import sqldf
            # Merge DataFrames for SQL query
            merged_df = pd.merge(attr_df, result_df, on='id')
            logging.info(f"merged_df shape: {merged_df.shape}")
            logging.info(f"merged_df sample:\n{merged_df.head().to_string()}")
            # Ensure SQL query uses merged_df
            sql = sql.replace("attr_df", "merged_df").replace("result_df", "merged_df")
            df = sqldf(sql, {"merged_df": merged_df})
        except Exception as e:
            logging.error(f"SQL execution failed: {e}")
            st.error(f"🚨 SQL execution failed: {e}")
            return None, None, None

    loc = {"df": df, "px": px, "fig": None}
    try:
        exec(plot_code, loc)
    except Exception as e:
        st.error(f"🚨 Plotly execution failed: {e}")
        logging.error(f"Plotly execution failed: {e}")
        loc["fig"] = px.bar(df)  # Fallback to default bar chart

    # Update summary
    summary_prompt = f"""
    Historical summary: {st.session_state.summary}
    New question: {question}
    New answer: {answer}
    Please summarize the above conversation into a concise summary, within 100 words.
    """
    try:
        summary_resp = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0
        )
        st.session_state.summary = summary_resp.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"🚨 Summary generation failed: {e}")
        logging.error(f"Summary generation failed: {e}")

    # Save to history
    st.session_state.history.append((question, answer))
    
    return sql, df, loc["fig"]

# ---------- 5. Streamlit UI ----------
st.set_page_config(page_title="Pandas Obesity Data Analyzer", layout="wide")
st.title("👋 Pandas Obesity Data Analyzer")
st.markdown("Use LLM to convert natural language into SQL, and then use Pandas to calculate obesity data and plot it in seconds! 📈 Data: *obesity_level_attribute.csv* + *obesity_level_result.csv*")

# Sidebar for history
with st.sidebar:
    st.header("🕒 Query History")
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.session_state.summary = ""
        st.success("History cleared! ✅")
    
    if st.session_state.history:
        for i, (q, a) in enumerate(st.session_state.history):
            with st.expander(f"Query {i+1}: {q[:50]}..."):
                st.markdown(f"**Question:** {q}")
                st.markdown(f"**Answer:** {a}")
    else:
        st.info("No queries yet. Start asking! 🥳")

# Main query input with examples
st.subheader("🔍 Ask Your Question")
question = st.text_input(
    "💬 Describe your custom query:",
    value="",
    placeholder="e.g., Show obesity levels by gender"
)
example_queries = [
    "Select an example query...",
    "Create a stacked bar chart showing obesity levels across different genders",
    "Show a scatter plot of age vs weight colored by obesity level",
    "Display a pie chart of obesity level distribution",
    "Create a histogram of BMI (Weight/Height^2) by gender",
    "Show a box plot of water consumption (CH2O) across obesity levels"
]
selected_query = st.selectbox("💡 Choose an example or type your own:", example_queries)

if st.button("Run Query 🚀"):
    query_to_run = selected_query if selected_query != "Select an example query..." and question == "" else question
    if not query_to_run.strip():
        st.error("Please enter a query or select an example! 😔")
    else:
        with st.spinner("Processing your query..."):
            sql, df, fig = run_and_plot(query_to_run)
            if sql and df is not None and fig is not None:
                st.subheader("Results")
                st.code(sql, language="sql")
                st.subheader("Data Preview")
                st.dataframe(df)
                st.subheader("Visualization")
                st.plotly_chart(fig, use_container_width=True)
                st.success("Query executed successfully! 🎉")
            else:
                st.error("Failed to process the query. Please try again. 😔")