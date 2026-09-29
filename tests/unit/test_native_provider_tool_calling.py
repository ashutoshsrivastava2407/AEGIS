"""Unit test verifying real native provider function calling adapters.

Path verified:
AEGIS ToolDefinition -> Native Provider Tool Schema -> Provider Tool Call -> AEGIS Normalized ToolCall -> GovernedToolExecutor -> Real Tool -> Validated Result.
"""

import pytest
from services.agents.tools.tool_registry import tool_registry
from services.llm.providers.native_provider import NativeLLMFunctionCallingProvider
from services.agents.tools.executor import tool_executor


def test_native_provider_schema_export():
    """Verify tool definitions export cleanly to OpenAI, Anthropic, and Gemini schemas."""
    openai_schemas = tool_registry.export_tools_schema(provider_format="openai")
    anthropic_schemas = tool_registry.export_tools_schema(provider_format="anthropic")
    gemini_schemas = tool_registry.export_tools_schema(provider_format="gemini")

    assert len(openai_schemas) >= 18
    assert len(anthropic_schemas) >= 18
    assert len(gemini_schemas) >= 18

    # OpenAI format
    assert openai_schemas[0]["type"] == "function"
    assert "name" in openai_schemas[0]["function"]

    # Anthropic format
    assert "input_schema" in anthropic_schemas[0]

    # Gemini format
    assert "parameters" in gemini_schemas[0]


def test_native_provider_function_call_execution_pipeline():
    """Verify end-to-end native provider function call normalization and execution."""
    provider = NativeLLMFunctionCallingProvider("native-llm-primary", provider_format="gemini")
    tools = tool_registry.export_tools_schema(provider_format="gemini")

    llm_response = provider.generate_chat(
        model="aegis-llm-pro",
        prompt="Investigate unexpected revenue anomaly in West region",
        tools=tools
    )

    assert llm_response["status"] == "SUCCESS"
    assert "tool_calls" in llm_response
    assert len(llm_response["tool_calls"]) > 0

    tc = llm_response["tool_calls"][0]
    tool_name = tc["tool_name"]
    arguments = tc["arguments"]

    # Execute normalized tool call through GovernedToolExecutor
    exec_res = tool_executor.execute_tool(
        tool_name=tool_name,
        params=arguments,
        agent_type="SUPERVISOR",
        tenant_id="tenant-alpha"
    )

    assert exec_res["success"] is True
    assert exec_res["status"] == "SUCCEEDED"
    assert exec_res["result_schema_valid"] is True
    assert "data" in exec_res
