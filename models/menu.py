from pydantic import BaseModel, Field
from typing import List

class MenuItem(BaseModel):
    """ A menu item in the restaurant """
    name: str = Field(description="Name of the menu item")
    description: str = Field(description="Description of the menu item")
    price: float = Field(description="Price of the menu item in INR")

class Menu(BaseModel):
    """ The restaurant menu """
    items: List[MenuItem] = Field(description="List of menu items available in the restaurant")
