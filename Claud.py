import streamlit as st
import pandas as pd
import snowflake.connector
import logging
from datetime import datetime, timedelta

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
    conn = snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )
    return conn

# Function to use Snowflake Cortex for inference
def cortex_inference(prompt: str) -> str:
    logger.info(f"Sending prompt to Snowflake Cortex: {prompt}")
    query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', '{prompt}');"
    conn = get_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
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
    conn.close()
    if result.empty:
        logger.error("No matching query found in the history.")
        raise ValueError("No matching query found in the history.")
    execution_time = result['execution_time'].iloc[0] / 1000  # Convert to seconds
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

# Function to compare and execute queries
def compare_and_execute_queries(original_query: str, optimized_query: str) -> tuple:
    logger.info("Comparing and executing queries.")
    
    # Get execution time for original query
    original_execution_time = get_execution_time(original_query)
    
    # Execute optimized query
    conn = get_snowflake_connection()
    start_time = datetime.now()
    optimized_result = pd.read_sql(optimized_query, conn)
    end_time = datetime.now()
    conn.close()
    
    optimized_execution_time = (end_time - start_time).total_seconds()
    
    # Compare results
    original_result = pd.read_sql(original_query, get_snowflake_connection())
    results_match = original_result.equals(optimized_result)
    
    return original_query, original_execution_time, optimized_query, optimized_execution_time, results_match

# Streamlit application for SQL optimization
def main():
    st.title("Snowflake SQL Optimizer with Cortex")

    # Initialize session state variables if not present
    if 'sql_query' not in st.session_state:
        st.session_state.sql_query = ''
    if 'checked_query' not in st.session_state:
        st.session_state.checked_query = ''
    if 'optimized_query' not in st.session_state:
        st.session_state.optimized_query = ''
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None

    # Inputs from the user
    sql_query = st.text_area("Enter your SQL query:", value=st.session_state.sql_query)

    if st.button("Optimize Query"):
        if not sql_query:
            st.error("Please enter a SQL query.")
            return

        # Save SQL query in session state
        st.session_state.sql_query = sql_query

        # Show progress in UI
        with st.spinner("Processing..."):
            try:
                logger.info(f"User-provided SQL query: {sql_query}")

                # Step 1: Check the SQL query for errors using Cortex
                st.write("Checking SQL query for common mistakes...")
                st.session_state.checked_query = query_sql_checker_tool(sql_query)
                st.write("Checked SQL Query for common mistakes:")
                st.code(st.session_state.checked_query)

                # Step 2: Optimize the SQL query
                st.write("Optimizing the SQL query...")
                st.session_state.optimized_query = optimize_query(st.session_state.checked_query)
                st.write("Optimized SQL Query:")
                st.code(st.session_state.optimized_query)

            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

    # Step 3: Run Optimized Query
    if st.session_state.optimized_query:
        if st.button("Run Optimized Query"):
            try:
                # Step 4: Remove single quotes from optimized query
                optimized_query_no_quotes = remove_single_quotes(st.session_state.optimized_query)
                st.write("Optimized SQL Query (without single quotes):")
                st.code(optimized_query_no_quotes)

                # Step 5: Compare and execute queries
                st.write("Comparing and executing queries...")
                original_query, original_time, optimized_query, optimized_time, results_match = compare_and_execute_queries(
                    st.session_state.sql_query,
                    optimized_query_no_quotes
                )

                # Store results in session state
                st.session_state.comparison_results = {
                    'original_query': original_query,
                    'original_time': original_time,
                    'optimized_query': optimized_query,
                    'optimized_time': optimized_time,
                    'results_match': results_match
                }

            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

    # Display comparison results if available
    if st.session_state.comparison_results:
        st.write("Comparison Results:")
        st.write(f"Original Query Execution Time: {st.session_state.comparison_results['original_time']} seconds")
        st.write(f"Optimized Query Execution Time: {st.session_state.comparison_results['optimized_time']} seconds")
        
        if st.session_state.comparison_results['results_match']:
            st.success("The results of both queries match.")
        else:
            st.warning("The results of the queries do not match.")

        if st.session_state.comparison_results['optimized_time'] < st.session_state.comparison_results['original_time']:
            st.success("The optimized query is faster!")
        else:
            st.warning("The optimized query is slower or has no improvement.")

if __name__ == "__main__":
    main()
