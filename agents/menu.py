import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from common.redis import redis_memory
from agents.memory_aware import MemoryAwareAgent
from tools.menu_tool import get_menu_tool
from models.menu import Menu


model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("MODEL"),
    model=os.getenv("MODEL"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
)


menu_agent = MemoryAwareAgent(
    memory=redis_memory,
    name="menu_agent",
    model_client=model_client,
    tools=[get_menu_tool],
    system_message="""
        You are a restaurant menu assistant.
        Use the get_menu tool to fetch the latest menu.
        Always respond with a structured Menu object.
    """,
    reflect_on_tool_use=True,
    output_content_type=Menu,
)
