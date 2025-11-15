import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from agents.memory_aware import MemoryAwareAgent
from tools.cart_tool import add_to_cart_tool, remove_from_cart_tool, show_cart_tool, clear_cart_tool
from models.cart import CartResponse
from common.redis import redis_memory


model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("MODEL"),
    model=os.getenv("MODEL"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
)

cart_agent = MemoryAwareAgent(
    memory=redis_memory,
    name="cart_agent",
    model_client=model_client,
    tools=[add_to_cart_tool, remove_from_cart_tool, show_cart_tool, clear_cart_tool],
    system_message="""
        You are a restaurant cart assistant.

        Your responsibilities:
        1. Add menu items to the customer's cart using MenuItem objects
        2. Remove menu items from the cart using MenuItem objects
        3. Display all items currently in the cart with quantities and prices
        4. Clear the entire cart when requested

        Important notes:
        - You must receive valid MenuItem objects (with name, description, and price) to add or remove items
        - Cart data is persisted in Redis using the user's session_id
        - Each cart operation requires a session_id to identify the user
        - When adding items, you can specify quantity (default is 1)
        - Always provide clear confirmation messages to the user after each operation
    """,
    reflect_on_tool_use=True
)
