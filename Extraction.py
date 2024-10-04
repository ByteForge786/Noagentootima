import re

def extract_code(code):
    # Search for words like 'optimise', 'optimized', 'optimisation', etc.
    trigger_words = re.search(r"\boptimise\b|\boptimized\b|\boptimisation\b|\boptimization\b", code, re.IGNORECASE)
    
    if trigger_words:
        # Extract the part of the text that comes after the trigger word
        code_after_trigger = code[trigger_words.end():]
        
        if "```python" in code_after_trigger:
            try:
                # Extract the first Python code block after the trigger word
                code = re.findall(r"```python(.*?)```", code_after_trigger, re.DOTALL)[0].strip()
            except:
                # Handle cases where the code block is not properly closed
                code = re.findall(r"```python(.*?)$", code_after_trigger, re.DOTALL)[0].strip()
        elif "```" in code_after_trigger:
            try:
                # Extract the first general code block after the trigger word
                code = re.findall(r"```(.*?)```", code_after_trigger, re.DOTALL)[0].strip()
            except:
                start = code_after_trigger.find("```")
                code = code_after_trigger[start+3:].strip()
        return code
    else:
        # If no trigger words are found, return None or an empty string
        return None
