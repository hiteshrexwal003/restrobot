import json
import os
from autogen_core.tools import FunctionTool
from common.redis import RedisMemoryManager
from models.menu import MenuItem

# Initialize Redis memory manager
memory = RedisMemoryManager()

async def add_item_to_cart(session_id: str, menu_item: MenuItem, quantity: int = 1) -> str:
    """
    Add a menu item to the cart.
    
    Args:
        session_id: The user's session ID
        menu_item: MenuItem object to add to cart
        quantity: Quantity of the item (default: 1)
    
    Returns:
        str: A message confirming the addition or error message
    """
    # Get current cart from user_data
    user_data = await memory.get_user_data(session_id)
    cart = user_data.get("cart", {})
    
    # Add or update item
    if menu_item.name in cart:
        cart[menu_item.name]["quantity"] += quantity
    else:
        cart[menu_item.name] = {
            "quantity": quantity,
            "price": menu_item.price
        }
    
    # Save cart back to user_data
    user_data["cart"] = cart
    await memory.set_user_data(session_id, user_data)
    
    return f"Added {quantity} x {menu_item.name} (₹{menu_item.price} each) to cart."

async def remove_item_from_cart(session_id: str, menu_item: MenuItem, quantity: int = None) -> str:
    """
    Remove a menu item from the cart.
    
    Args:
        session_id: The user's session ID
        menu_item: MenuItem object to remove from cart
        quantity: Quantity to remove (default: None, which removes the entire item)
    
    Returns:
        str: A message confirming the removal or error message
    """
    # Get current cart from user_data
    user_data = await memory.get_user_data(session_id)
    cart = user_data.get("cart", {})
    
    if not cart:
        return "Your cart is empty."
    
    # Find the item (case-insensitive)
    item_key = next((key for key in cart.keys() if key.lower() == menu_item.name.lower()), None)
    
    if not item_key:
        return f"Error: '{menu_item.name}' is not in your cart."
    
    current_quantity = cart[item_key]["quantity"]
    
    # If no quantity specified, remove the entire item
    if quantity is None:
        del cart[item_key]
        message = f"Removed {item_key} from cart."
    # If quantity is greater than or equal to current quantity, remove the entire item
    elif quantity >= current_quantity:
        del cart[item_key]
        message = f"Removed all {current_quantity} x {item_key} from cart."
    # Otherwise, decrement the quantity
    else:
        cart[item_key]["quantity"] -= quantity
        remaining = cart[item_key]["quantity"]
        message = f"Removed {quantity} x {item_key} from cart. Remaining: {remaining}"
    
    # Save cart back to user_data
    user_data["cart"] = cart
    await memory.set_user_data(session_id, user_data)
    
    return message

async def show_cart(session_id: str) -> str:
    """
    Show all items in the cart with total price.
    
    Args:
        session_id: The user's session ID
    
    Returns:
        str: A formatted string showing cart contents and total
    """
    # Get current cart from user_data
    user_data = await memory.get_user_data(session_id)
    cart = user_data.get("cart", {})
    
    if not cart:
        return "Your cart is empty."
    
    cart_items = []
    total = 0.0
    
    for item_name, details in cart.items():
        quantity = details["quantity"]
        price = details["price"]
        item_total = quantity * price
        total += item_total
        cart_items.append(f"- {item_name}: {quantity} x ₹{price} = ₹{item_total}")
    
    cart_summary = "\n".join(cart_items)
    return f"Your Cart:\n{cart_summary}\n\n Total: ₹{total:.2f}"

async def clear_cart(session_id: str) -> str:
    """
    Clear all items from the cart.
    
    Args:
        session_id: The user's session ID
    
    Returns:
        str: A message confirming the cart has been cleared
    """
    # Get current user_data and clear cart
    user_data = await memory.get_user_data(session_id)
    user_data["cart"] = {}
    await memory.set_user_data(session_id, user_data)
    
    return "Cart has been cleared."

# Create FunctionTools without strict mode to allow default arguments
add_to_cart_tool = FunctionTool(
    add_item_to_cart,
    description="Add a menu item to the cart with specified quantity"
)

remove_from_cart_tool = FunctionTool(
    remove_item_from_cart,
    description="Remove a menu item from the cart"
)

show_cart_tool = FunctionTool(
    show_cart,
    description="Show all items in the cart with total price"
)

clear_cart_tool = FunctionTool(
    clear_cart,
    description="Clear all items from the cart"
)