from src.agent.views import LLMResponse
from typing import Any
import json
import ast
import re

def extract_llm_response(text)->LLMResponse:
    # Dictionary to store extracted values
    result=LLMResponse(thought='',action_name='',action_input={})
    # Extract Thought
    thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
    if thought_match:
        result['thought'] = thought_match.group(1).strip()
    # Extract Action-Name
    action_name_match = re.search(r"<Action-Name>(.*?)<\/Action-Name>", text, re.DOTALL)
    if action_name_match:
        result['action_name'] = action_name_match.group(1).strip()  
    # Extract and convert Action-Input to a dictionary
    action_input_match = re.search(r"<Action-Input>(.*?)<\/Action-Input>", text, re.DOTALL)
    if action_input_match:
        action_input_str = action_input_match.group(1).strip()
        try:
            # Convert string to dictionary safely using ast.literal_eval
            result['action_input'] = ast.literal_eval(action_input_str)
        except (ValueError, SyntaxError):
            # If there's an issue with conversion, store it as raw string
            result['action_input'] = json.loads(action_input_str)
    return result
