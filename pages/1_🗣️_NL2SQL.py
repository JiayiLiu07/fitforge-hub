import os
import re
import streamlit as st
import plotly.express as px
from openai import OpenAI
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import IntegerType
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# ---------- 0. Initialize client for Aliyun ----------
API_KEY = "your-api-key"
client = OpenAI(api_key=API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# ---------- 1. Initialize Spark ----------
master = "local[*]"
app_name = "llm_demo"
@st.cache_resource
def get_spark():
    spark_conf = SparkConf().setMaster(master).setAppName(app_name)
    return SparkSession.builder.config(conf=spark_conf).getOrCreate()
spark = get_spark()

# ---------- 2. Load data ----------
base_path = "data"
attribute_path = os.path.join(base_path, "obesity_level_attribute_clean.csv")
result_path = os.path.join(base_path, "obesity_level_result_clean.csv")
attr_df = spark.read.csv(attribute_path, header=True, inferSchema=True)
result_df = spark.read.csv(result_path, header=True, inferSchema=True)

attr_df.createOrReplaceTempView("attribute")
result_df.createOrReplaceTempView("result")

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

@udf(returnType=IntegerType())
def level_to_num(level):
    return level_map.get(level, None)
spark.udf.register("level_to_num", level_to_num)
result_df = result_df.withColumn("level_num", level_to_num(col("obesity_level")))
result_df.createOrReplaceTempView("result")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "summary" not in st.session_state:
    st.session_state.summary = ""

# ---------- 3. Build Prompt ----------
PROMPT_TEMPLATE = """
You are a senior data analyst tasked with converting natural language questions into SQL queries for a Spark SQL database.
The database contains two tables:

1) attribute(
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
   MTRANS STRING
)

2) result(
   id INT,
   obesity_level STRING,
   level_num INT
)

These tables are related by the `id` field. level_num is a numerical representation of the obesity level, higher values indicate more severe obesity levels.
Write a Spark SQL query to answer the user's question, and provide Plotly visualization code using the resulting DataFrame `df`.

Follow this format strictly:
```sql
SELECT ...
```

```python
# Plotly visualization code, df is the SQL result DataFrame
import plotly.express as px
fig = px.XXX(df, ...)
```

User's question: {question}

IMPORTANT:
- Do **NOT** use `r.level_num` in ORDER BY or WHERE clauses.
- Use `level_to_num(r.obesity_level)` instead.
"""

# ---------- 4. Convert natural language to SQL and Plotly code ----------
def nl_to_sql_and_plot(question: str):
    full_prompt = f"""
    Summary: {st.session_state.summary}
    """
    for q, a in st.session_state.history[-3:]:
        full_prompt += f"\nHistorical question: {q}\nHistorical answer: {a}"
    full_prompt += f"\nCurrent question: {PROMPT_TEMPLATE.format(question=question)}"

    logging.info("=========== Prompt ===========")
    logging.info(f"Sending prompt to LLM:\n{full_prompt}")

    messages = [{"role": "user", "content": full_prompt}]
    resp = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        temperature=0
    )
    text = resp.choices[0].message.content

    logging.info(f"LLM response:\n{text}")

    sql_block = re.findall(r"```sql\n(.*?)\n```", text, re.S)[0].strip()
    plot_block = re.findall(r"```python\n(.*?)\n```", text, re.S)[0].strip()

    return sql_block, plot_block, text

# ---------- 5. Execute query and generate plot ----------
def run_and_plot(question: str):
    sql, plot_code, answer = nl_to_sql_and_plot(question)
    
    logging.info("=========== Code ===========")
    logging.info(f"Generated SQL query:\n{sql}")
    logging.info(f"Generated Plotly code:\n{plot_code}")

    try:
        df = spark.sql(sql).toPandas()
    except Exception as e:
        st.error(f"🚨 SQL execution failed: {e}")
        return None, None, None

    loc = {"df": df, "px": px, "fig": None}
    try:
        exec(plot_code, loc)
    except Exception as e:
        st.error(f"🚨 Plotly execution failed: {e}")
        loc["fig"] = px.bar(df)  # Fallback to default bar chart

    # Update summary
    summary_prompt = f"""
    Historical summary: {st.session_state.summary}
    New question: {question}
    New answer: {answer}
    Please summarize the above conversation into a concise summary, within 100 words.
    """
    summary_resp = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0
    )
    st.session_state.summary = summary_resp.choices[0].message.content.strip()

    # Save to history
    st.session_state.history.append((question, answer))
    
    return sql, df, loc["fig"]

# ---------- 6. Streamlit UI ----------
st.set_page_config(page_title="NL2SQL Demo", layout="wide")
st.title("🗣️ LLM + PySpark NL2SQL Demo ")
st.markdown("Explore obesity data with natural language queries! 📈 Data: *obesity_level_attribute.csv* + *obesity_level_result.csv*")

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
        st.info("No queries yet. Start asking!🥳")

# Main query input with examples
st.subheader("🔍Ask Your Question")
question = st.text_input(
    "💬Describe your custom query:",
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
selected_query = st.selectbox("💡Choose an example or type your own:", example_queries)

if st.button("Run Query 🚀"):
    query_to_run = selected_query if selected_query != "Select an example query..." and question == "" else question
    if not query_to_run.strip():
        st.error("Please enter a query or select an example! 😔")
    else:
        with st.spinner("Processing your query..."):
            sql, pdf, fig = run_and_plot(query_to_run)
            if sql and pdf is not None and fig is not None:
                st.subheader("Results")
                st.code(sql, language="sql")
                st.subheader("Data Preview")
                st.dataframe(pdf)
                st.subheader("Visualization")
                st.plotly_chart(fig, use_container_width=True)
                st.success("Query executed successfully! 🎉")
            else:
                st.error("Failed to process the query. Please try again. 😔")