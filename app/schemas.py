from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.models import UserRole, OrderStatus

# user_auth Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(
        min_length=6,
        max_length=72,
        description="Minimum 6 character secure password")
    role: Optional[UserRole] = UserRole.CUSTOMER

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole

# product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0, description="Product price must be greater than zero")

class ProductCreate(ProductBase):
    initial_stock: int = Field(0, ge=0, description="Initial inventory amount")

class ReviewResponse(BaseModel):
    rating:int
    comment: str | None=None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    stock: int
    reviews: List[ReviewResponse] = []

    class Config:
        from_attributes = True

# cart schemas
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1, description="Must add at least 1 item")

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

# inventory updates
class InventoryUpdate(BaseModel):
    stock: int = Field(..., ge=0, description="Set absolute stock value")

#create reviews
class CreateReview(BaseModel):
    product_id: int
    #validation
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5 stars")
    comment: Optional[str]=None