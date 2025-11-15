from pydantic import BaseModel, Field
from typing import List
from models.menu import MenuItem


class CartResponse(BaseModel):
    """ Cart response """
    status: str = Field(description="Status of the operation")
    message: str = Field(description="Message describing the result")
    items: List[MenuItem] = Field(default=[], description="List of items in cart")
    total: float = Field(default=0.0, description="Total price of items in cart")
