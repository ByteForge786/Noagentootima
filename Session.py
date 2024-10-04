import streamlit as st
import pandas as pd
import snowflake.connector
import time
import logging

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Placeholder functions
def cortex_inference(prompt: str) -> str:
    query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', '{prompt}');"
    con = snowflake.connector.connect()  # Assuming connection utility
    result = pd.read_sql(query, con)
    con.close()
    return result.iloc[0, 0]

def query_sql_checker_tool(query: str) -> str:
    prompt = f"""
    {query}
    Double check the query above for common mistakes, including:
    - Using NOT IN with NULL values
    - Using UNION when UNION ALL should have been used
    - Using BETWEEN for exclusive ranges
    - Data type mismatch in predicates
    - Properly quoting identifiers
    - Using the correct number of arguments for functions
    - Casting to the correct data type
    - Using the proper columns for joins
    If there are any mistakes, rewrite the query. Output the final SQL query only.
    """
    return cortex_inference(prompt)

# Function to remove single inverted commas
def remove_single_quotes(query: str) -> str:
    return query.replace("'", "")

def run_query(query: str) -> float:
    con = snowflake.connector.connect()  # Assuming connection utility
    start_time = time.time()
    pd.read_sql(query, con)
    con.close()
    execution_time = time.time() - start_time
    return execution_time

# Initialize session state variables
if "input_sql" not in st.session_state:
    st.session_state.input_sql = None
if "execution_time" not in st.session_state:
    st.session_state.execution_time = None
if "optimized_sql" not in st.session_state:
    st.session_state.optimized_sql = None
if "query_checked" not in st.session_state:
    st.session_state.query_checked = False

# Streamlit UI
st.title("Snowflake SQL Optimizer")

# Step 1: Get input SQL and execution time
input_sql = st.text_area("Enter your SQL query")
execution_time = st.text_input("Enter execution time (optional)", value="")

if st.button("Submit SQL"):
    st.session_state.input_sql = input_sql
    if execution_time:
        st.session_state.execution_time = float(execution_time)
    else:
        # Run the query to get the execution time
        st.session_state.execution_time = run_query(input_sql)
    st.success("SQL submitted and execution time recorded.")

# Step 2: Optimize SQL
if st.session_state.input_sql:
    st.write(f"Original SQL:\n{st.session_state.input_sql}")
    
    # Generating optimized SQL (placeholder logic)
    optimized_sql = remove_single_quotes(st.session_state.input_sql)  # Remove single quotes as part of optimization
    st.session_state.optimized_sql = optimized_sql
    
    st.write("Optimized SQL generated:")
    st.code(st.session_state.optimized_sql)

    if st.button("Run Optimized Query"):
        # Show backend processing before running the query
        with st.spinner("Running Optimized Query..."):
            time.sleep(2)  # Simulate delay for query checking
        
        # Step 3: Use query checker tool
        query_checked = query_sql_checker_tool(optimized_sql)
        st.session_state.query_checked = True
        
        st.write("Query Checker Tool Feedback:")
        st.code(query_checked)
        
        if st.button("Proceed with Optimized Query"):
            with st.spinner("Running optimized query on Snowflake..."):
                exec_time = run_query(query_checked)
                st.write(f"Optimized Query Execution Time: {exec_time} seconds")
            st.success("Optimized query executed successfully.")

# Prevent full refresh by ensuring buttons control state directly, avoiding resets
