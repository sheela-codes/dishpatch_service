import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException

from src.app.models import MenuItem, Order, OrderItem, Restaurant, User
from src.app.schemas import OrderCreate, OrderItemOut, OrderOut
from src.app.database import get_db


router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger(__name__)

@router.post("", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    user = db.get(User, data.customer_id)
    if user is None or  not user.account.type == 'Customer':
        raise  HTTPException(status_code=404, detail=f"Unknown Customer id {data.customer_id}")
    res = db.get(Restaurant, data.restaurant_id)
    if None is res or not res.operational:
        raise  HTTPException(status_code=404, detail=f"Unknown or inactive Restaurant id {data.restaurant_id}")
    order_items = []
    for oi in data.items:
        dish = db.get(MenuItem, oi.menu_item_id)
        if dish is None or dish.restaurant_id != data.restaurant_id or not dish.active:
            raise  HTTPException(status_code=400, detail=f"Unknown Menu Item {oi.menu_item_id}")
        order_item_db = OrderItem(menu_item = dish, quantity = oi.quantity, unit_price = dish.price)
        order_items.append(order_item_db)
        
    order = Order(customer_id=data.customer_id, restaurant_id=data.restaurant_id, items=order_items)
    db.add(order)
    db.commit()
    db.refresh(order) 
    logger.info("Order created %s", order)
    return order_out_helper(order)

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order,order_id)
    if order is None :
        raise HTTPException(status_code=404, detail=f"Unknown Order {order_id}")
    return order_out_helper(order)  

def order_out_helper(created: Order):
    order_items = []
    for oi in created.items:
        order_item_out = OrderItemOut(menu_item_id=oi.menu_item_id, name=oi.menu_item.name, quantity=oi.quantity, unit_price = oi.unit_price)
        order_items.append(order_item_out)
    total = 0    
    for item in order_items:
        total+= item.quantity*item.unit_price
    return OrderOut(id=created.id, customer_id=created.customer_id,
                    restaurant_id=created.restaurant_id, status = created.status, 
                    placed_at = created.placed_at,items = order_items, total = total)    





