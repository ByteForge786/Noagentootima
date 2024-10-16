import re

def modify_tag_value_condition(sql_query):
    # Pattern to match "tag_value = something" with flexible spacing
    pattern = r'(tag_value\s*=\s*)([\'"]?)(\w+)([\'"]?)'
    
    def replacement(match):
        prefix, quote_start, value, quote_end = match.groups()
        return f"{prefix}{quote_start}%{value}%{quote_end}"
    
    # Perform the replacement
    modified_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
    
    return modified_query

# Test the function
test_queries = [
    "SELECT * FROM table WHERE tag_value = 'something'",
    "SELECT * FROM table WHERE tag_value='something'",
    "SELECT * FROM table WHERE tag_value = something",
    "SELECT * FROM table WHERE tag_value =something",
    "SELECT * FROM table WHERE tag_value= 'something'",
    "SELECT * FROM table WHERE TAG_VALUE = 'SOMETHING'",
]

for query in test_queries:
    print("Original:", query)
    print("Modified:", modify_tag_value_condition(query))
    print()
import re

def modify_tag_value_condition(sql_query):
    # Pattern to match "tag_value = something" with flexible spacing and any characters in the value
    pattern = r'(tag_value\s*=\s*)([\'"]?)([^\'"\)]+)([\'"]?)'
    
    def replacement(match):
        prefix, quote_start, value, quote_end = match.groups()
        # Trim any leading/trailing whitespace from the value
        value = value.strip()
        return f"{prefix}{quote_start}%{value}%{quote_end}"
    
    # Perform the replacement
    modified_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)
    
    return modified_query

# Test the function
test_queries = [
    "SELECT * FROM table WHERE tag_value = 'something'",
    "SELECT * FROM table WHERE tag_value='something'",
    "SELECT * FROM table WHERE tag_value = something",
    "SELECT * FROM table WHERE tag_value =something",
    "SELECT * FROM table WHERE tag_value= 'something'",
    "SELECT * FROM table WHERE TAG_VALUE = 'SOMETHING'",
    "SELECT * FROM table WHERE tag_value = 'abc xyz'",
    "SELECT * FROM table WHERE tag_value = 'abc-xyz'",
    "SELECT * FROM table WHERE tag_value = 'abc 123 !@#'",
    "SELECT * FROM table WHERE tag_value = abc xyz",
]

for query in test_queries:
    print("Original:", query)
    print("Modified:", modify_tag_value_condition(query))
    print()
