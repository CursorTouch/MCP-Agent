import pytest
from src.agent.utils import xml_preprocessor

def test_xml_preprocessor_valid_output():
    xml_content = """
    <thought>Thinking about it</thought>
    <tool_name>TestTool</tool_name>
    <tool_args>
        <arg1>value1</arg1>
        <arg2>123</arg2>
        <arg3>true</arg3>
    </tool_args>
    """
    result = xml_preprocessor(xml_content)
    
    assert result["thought"] == "Thinking about it"
    assert result["tool_name"] == "TestTool"
    assert result["tool_args"] == {
        "arg1": "value1",
        "arg2": 123,
        "arg3": True
    }

def test_xml_preprocessor_missing_thought():
    xml_content = """
    <tool_name>TestTool</tool_name>
    <tool_args>
        <arg1>value1</arg1>
    </tool_args>
    """
    result = xml_preprocessor(xml_content)
    
    # Thought is optional/None if not found?
    # Checking implementation: thought_match = ... if thought_match else None
    assert result["thought"] is None
    assert result["tool_name"] == "TestTool"

def test_xml_preprocessor_no_tool_args():
    xml_content = """
    <thought>Just thinking</thought>
    <tool_name>ThinkTool</tool_name>
    """
    result = xml_preprocessor(xml_content)
    
    assert result["thought"] == "Just thinking"
    assert result["tool_name"] == "ThinkTool"
    assert result["tool_args"] == {}

def test_xml_preprocessor_invalid_xml():
    xml_content = "Just some text"
    
    # It raises ValueError if no tool_name found
    with pytest.raises(ValueError, match="No <tool_name> found"):
        xml_preprocessor(xml_content)
