import re
import json
import logging
import ast

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _infer_type(value: str):
    """Infers the data type of a string value."""
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    if value.lower() in ('null', 'none'):
        return None
    
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    try:
        return ast.literal_eval(value)
    except SyntaxError:
        pass
    except ValueError:
        pass

    return value

def xml_preprocessor(content: str) -> dict[str, any]:
    '''Extracts the tool data from the ai message using XML parsing via Regex'''
    
    # 1. Extract thought
    thought_match = re.search(r'<thought>(.*?)</thought>', content, re.DOTALL)
    thought = thought_match.group(1).strip() if thought_match else None

    # 2. Extract tool_name
    name_match = re.search(r'<tool_name>\s*(.*?)\s*</tool_name>', content, re.DOTALL)
    if not name_match:
        logger.debug(content)
        raise ValueError("No <tool_name> found")
    tool_name = name_match.group(1).strip()

    # 3. Extract tool_args block
    args_block_match = re.search(r'<tool_args>\s*(.*?)\s*</tool_args>', content, re.DOTALL)
    tool_args = {}
    
    if args_block_match:
        args_content = args_block_match.group(1)
        # 1. Extract individual arguments using regex
        # Pattern looks for <key>value</key>
        # strict mode: won't handle nested tags well, but good for flat arguments
        # Using finditer to get all arguments
        for match in re.finditer(r'<(\w+)>\s*(.*?)\s*</\1>', args_content, re.DOTALL):
            key = match.group(1)
            value = match.group(2).strip()
            # Try to infer type
            tool_args[key] = _infer_type(value)

    return {
        "thought": thought,
        "tool_name": tool_name,
        "tool_args": tool_args
    }