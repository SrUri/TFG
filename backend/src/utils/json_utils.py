import logging
import re
import json
from typing import Dict

import json5

logger = logging.getLogger(__name__)

def safe_json_parse(text: str) -> Dict:
    # Attempt 1: Try standard JSON parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"Standard JSON failed: {str(e)}")
    
    # Attempt 2: Try JSON5 parsing (more lenient)
    try:
        return json5.loads(text)
    except Exception as e2:
        logger.warning(f"JSON5 parsing failed: {str(e2)}")
    
    # Attempt 3: Fix common issues and retry
    try:
        # Add missing closing braces if needed
        if text.count('{') > text.count('}'):
            text += '}' * (text.count('{') - text.count('}'))
        
        # Escape unquoted strings inside arrays
        text = re.sub(r',\s*([^"\]]+)\s*\]', r', "\1"]', text)
        text = re.sub(r'\[\s*([^"\]]+)\s*,', r'["\1",', text)
        
        # Fix unescaped quotes inside strings
        text = re.sub(r'([^\\])"([^\]})])', r'\1\\"\2', text)
        
        return json5.loads(text)
    except Exception as e3:
        logger.error(f"Repair attempt failed: {str(e3)}")
    
    # Final fallback: Manual extraction
    try:
        result = {}
        if '"similitudes_tecnicas":' in text:
            result["similitudes_tecnicas"] = re.findall(r'\[([^\]]+)\]', text.split('"similitudes_tecnicas":')[1])[0].split(',')
        # Similar extraction for other keys...
        return result
    except Exception as e4:
        logger.critical("All parsing methods failed")
        raise json.JSONDecodeError(f"Unrecoverable JSON: {text[:200]}", text, 0)