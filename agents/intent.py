import os
from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from common.redis import redis_memory
from agents.memory_aware import MemoryAwareAgent
from agents.menu import menu_agent
from agents.cart import cart_agent
from pydantic import BaseModel, Field
from typing import Literal

# Initialize model client
model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("MODEL"),
    model=os.getenv("MODEL"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
)


class IntentClassification(BaseModel):
    """Intent classification result"""
    intent: Literal["menu", "cart"] = Field(description="The classified intent: 'menu' for menu-related queries, 'cart' for cart-related queries")
    reasoning: str = Field(description="Brief explanation of why this intent was chosen")


# Intent classification agent - DON'T store messages
intent_agent = MemoryAwareAgent(
    memory=redis_memory,
    store_messages=False,  # Skip storing intent agent messages
    name="intent_classifier",
    model_client=model_client,
    system_message="""
        You are an intent classification assistant for a restaurant ordering system.
        
        Your job is to analyze user queries and classify them into one of two intents:
        
        1. "menu" - Use this when the user wants to:
           - View the restaurant menu
           - See available items
           - Get information about dishes
           - Browse what's available
           - Ask about specific menu items
        
        2. "cart" - Use this when the user wants to:
           - Add items to their cart
           - Remove items from cart
           - View their cart
           - Clear their cart
           - Manage their order
           - Check out or finalize order
        
        Analyze the user's query and respond with the appropriate intent classification.
    """,
    reflect_on_tool_use=False,
    output_content_type=IntentClassification,
)


async def process_user_query(user_query: str, session_id: str):
    """
    Main orchestrator function that:
    1. Stores user query in Redis memory
    2. Calls LLM to find intent
    3. Routes to appropriate agent (menu or cart)
    
    Args:
        user_query: The user's input query
        session_id: Session identifier for the user
    
    Returns:
        Response from the appropriate agent
    """
    # Step 0: Store user query in Redis memory FIRST
    await redis_memory.add_message(session_id, "user", user_query)
    
    # Step 1: Classify intent using LLM (won't be stored)
    intent_result = await intent_agent.run(task=user_query, session_id=session_id, cancellation_token=None)
    intent_classification = intent_result.messages[-1].content
    
    print(f"Detected intent: {intent_classification.intent}")
    print(f"Reasoning: {intent_classification.reasoning}\n")
    
    # Step 2: Route to appropriate agent based on intent (will be stored)
    if intent_classification.intent == "menu":
        print("Routing to menu agent...")
        response = await menu_agent.run(task=user_query, session_id=session_id, cancellation_token=None)
    elif intent_classification.intent == "cart":
        print("Routing to cart agent...")
        response = await cart_agent.run(task=user_query, session_id=session_id, cancellation_token=None)
    else:
        raise ValueError(f"Unknown intent: {intent_classification.intent}")
    
    print(await redis_memory.get_history(session_id))
    
    return response


# Synchronous wrapper for easier use
def handle_user_query(user_query: str, session_id: str = "default_session"):
    """
    Synchronous wrapper for process_user_query
    
    Args:
        user_query: The user's input query
        session_id: Session identifier for the user (default: "default_session")
    
    Returns:
        Response from the appropriate agent
    """
    import asyncio
    return asyncio.run(process_user_query(user_query, session_id))