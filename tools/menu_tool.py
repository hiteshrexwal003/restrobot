import json
import os
from autogen_core.tools import FunctionTool

MENU_FILE = os.path.join(os.path.dirname(__file__), "menu_data.json")

async def get_menu() -> str:
    """
    Get the restaurant menu with all available items, descriptions, and prices.
    
    Returns:
        str: A formatted string containing the restaurant menu items with their details.
    """
    try:
        with open(MENU_FILE, 'r') as file:
            menu_data = json.load(file)
        return json.dumps(menu_data, indent=2)
    except FileNotFoundError:
        return f"Error: Menu file not found at {MENU_FILE}"

# Wrap the function with FunctionTool and enable strict mode
get_menu_tool = FunctionTool(get_menu, description="Get the restaurant menu with all available items, descriptions, and prices", strict=True)