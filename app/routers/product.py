from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from app.database import get_db
from app.models import Product, Inventory, UserRole
from app.auth import RoleChecker

router = APIRouter(prefix="/products", tags=["Products & Inventory"])

# ==========================================
# pydantic schemas (Input/Output Validation)
# ==========================================
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    initial_stock: int = 0

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# routes
# ==========================================

# 1. get all products(Public/Customer Access)
# Eager load the 1-to-1 inventory relationship
@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """Fetch all products and their current inventory stock."""
    products = db.query(Product).options(joinedload(Product.inventory)).all()
    result = []
    
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.inventory.stock if p.inventory else 0
        })
    return result


# 2. create product (ADMIN ONLY - Role-Based Access Control)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate, 
    db: Session = Depends(get_db),
    # THIS is your RBAC in action! Only tokens with 'admin' role can pass this check.
    current_admin = Depends(RoleChecker([UserRole.ADMIN])) 
):
    """Creates a new product and automatically initializes its inventory."""
    
    # 1.create the Product
    new_product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price
    )
    db.add(new_product)
    db.flush() # flushes to DB to get the new_product.id without fully committing

    # 2. create the linked Inventory record (1-to-1 relationship)
    new_inventory = Inventory(
        product_id=new_product.id,
        stock=product_in.initial_stock
    )
    db.add(new_inventory)
    
    # 3.commit the transaction
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product and Inventory created successfully", 
        "product_id": new_product.id
    }


# 3. update inventory stock (admin only)
@router.put("/{product_id}/inventory")
def update_inventory(
    product_id: int,
    added_stock: int, # Pass a positive number to add stock, negative to reduce
    db: Session = Depends(get_db),
    current_admin = Depends(RoleChecker([UserRole.ADMIN]))
):
    """Admin endpoint to add or remove stock from the warehouse."""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Inventory record not found for this product"
        )
    
    if inventory.stock + added_stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )
    inventory.stock += added_stock
    db.commit()
    
    return {
        "message": "Inventory successfully updated", 
        "new_total_stock": inventory.stock
    }