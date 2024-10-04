import streamlit as st
import pandas as pd
import snowflake.connector
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Prompts
system_message = """
    You are a helpful assistant for analyzing and optimizing queries running on Snowflake to reduce resource consumption and improve performance.
    If the user's question is not related to query analysis or optimization, then politely refuse to answer it.

    Scope: Only analyze and optimize SELECT queries. Do not run any queries that mutate the data warehouse (e.g., CREATE, UPDATE, DELETE, DROP).

    YOU SHOULD FOLLOW THIS PLAN and seek approval from the user at every step before proceeding further:
    1. Identify Expensive Queries
    2. Analyze Query Structure
    3. Suggest Optimizations
    4. Validate Improvements
    5. Prepare Summary
"""

# Define Snowflake connection (Already handled by the user)
def get_snowflake_connection():
    conn = None  # Placeholder
    return conn

# Function to use Snowflake Cortex for inference
def cortex_inference(prompt: str) -> str:
    logger.info(f"Sending prompt to Snowflake Cortex: {prompt}")
    query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', '{prompt}');"
    conn = get_snowflake_connection()
    result = pd.read_sql(query, conn)
    return result.iloc[0, 0]

# Query SQL Checker Tool
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
    logger.info("Running SQL checker for common mistakes.")
    return cortex_inference(prompt)

# Function to get query execution time from Snowflake
def get_execution_time(query: str) -> float:
    logger.info("Fetching execution time from Snowflake.")
    conn = get_snowflake_connection()
    query_history = f"""
        SELECT query_id, execution_time
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE query_text = '{query}' 
        AND query_start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
        ORDER BY query_start_time DESC
        LIMIT 1;
    """
    result = pd.read_sql(query_history, conn)
    if result.empty:
        logger.error("No matching query found in the history.")
        raise ValueError("No matching query found in the history.")
    execution_time = result['execution_time'].iloc[0]
    logger.info(f"Execution time retrieved: {execution_time} seconds")
    return execution_time

# Optimizing the SQL Query with Snowflake Cortex
def optimize_query(query: str) -> str:
    prompt = f"Optimize the following query: {query}"
    logger.info("Optimizing the SQL query using Cortex.")
    optimized_query = cortex_inference(prompt)
    return optimized_query

# Function to remove all single inverted commas (') from the query
def remove_single_quotes(query: str) -> str:
    logger.info("Removing single inverted commas from the query.")
    return query.replace("'", "")

# Streamlit application for SQL optimization
def main():
    st.title("Snowflake SQL Optimizer with Cortex")

    # Initialize session state variables if not present
    if 'sql_query' not in st.session_state:
        st.session_state.sql_query = ''
    if 'execution_time' not in st.session_state:
        st.session_state.execution_time = None
    if 'checked_query' not in st.session_state:
        st.session_state.checked_query = ''
    if 'optimized_query' not in st.session_state:
        st.session_state.optimized_query = ''
    if 'optimized_execution_time' not in st.session_state:
        st.session_state.optimized_execution_time = None

    # Inputs from the user
    sql_query = st.text_area("Enter your SQL query:", value=st.session_state.sql_query)
    execution_time_input = st.text_input("Execution Time (optional):", value=str(st.session_state.execution_time) if st.session_state.execution_time else '')

    if st.button("Optimize Query"):
        if not sql_query:
            st.error("Please enter a SQL query.")
            return

        # Save SQL query in session state
        st.session_state.sql_query = sql_query

        # Show progress in UI
        with st.spinner("Processing..."):
            try:
                # Step 1: Get Execution Time if not provided
                if not execution_time_input:
                    st.write("Fetching execution time from Snowflake...")
                    st.session_state.execution_time = get_execution_time(sql_query)
                else:
                    st.session_state.execution_time = float(execution_time_input)

                logger.info(f"User-provided SQL query: {sql_query}")
                logger.info(f"Execution Time: {st.session_state.execution_time} seconds")

                # Step 2: Check the SQL query for errors using Cortex
                st.write("Checking SQL query for common mistakes...")
                st.session_state.checked_query = query_sql_checker_tool(sql_query)
                st.write("Checked SQL Query for common mistakes:")
                st.code(st.session_state.checked_query)

                # Step 3: Optimize the SQL query
                st.write("Optimizing the SQL query...")
                st.session_state.optimized_query = optimize_query(st.session_state.checked_query)
                st.write("Optimized SQL Query:")
                st.code(st.session_state.optimized_query)

            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

    # Step 4: Run Optimized Query
    if st.session_state.optimized_query:
        if st.button("Run Optimized Query"):
            try:
                # Step 5: Remove single quotes from optimized query
                optimized_query_no_quotes = remove_single_quotes(st.session_state.optimized_query)
                st.write("Optimized SQL Query (without single quotes):")
                st.code(optimized_query_no_quotes)

                # Get execution time of the optimized query
                st.write("Running optimized query...")
                st.session_state.optimized_execution_time = get_execution_time(optimized_query_no_quotes)

                # Step 6: Display comparison of original and optimized queries
                st.write(f"Original Execution Time: {st.session_state.execution_time} seconds")
                st.write(f"Optimized Execution Time: {st.session_state.optimized_execution_time} seconds")

                if st.session_state.optimized_execution_time < st.session_state.execution_time:
                    st.success("The optimized query is faster!")
                else:
                    st.warning("The optimized query is slower or has no improvement.")

            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
