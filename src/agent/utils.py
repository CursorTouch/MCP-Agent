import re
import json

def json_preprocessor(content: str) -> dict[str, dict[str, str]]:
    '''Extracts the json data from the ai message'''
    # Try to find JSON within markdown code fences first
    json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
    
    if json_match:
        raw_json = json_match.group(1).strip()
    else:
        # Fallback: try to find JSON object directly
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            raw_json = json_match.group(0).strip()
        else:
            # Last resort: assume the entire content is JSON
            raw_json = content.strip()
    
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        # If there's extra data, try to decode just the valid part
        try:
            obj, _ = json.JSONDecoder().raw_decode(raw_json)
            return obj
        except Exception:
            raise