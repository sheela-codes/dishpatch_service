# imports you'll need
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.app.database import get_db
from src.app.models import Account, Contact, Cuisine, MenuItem, Profile, Restaurant, User
from src.app.schemas import RestaurantCreate, RestaurantOut, RestaurantUpdate


DEFAULT_PASSWORD = "changeme"
router = APIRouter(prefix="/restaurants", tags=["restaurants"])
logger = logging.getLogger(__name__)


@router.get("", response_model=List[RestaurantOut])
def list_restaurants(db: Session = Depends(get_db)):
    query = select(Restaurant).options(
        selectinload(Restaurant.menu_items).and_(MenuItem.active == False),
        selectinload(Restaurant.cuisine),
    ).where(Restaurant.operational == True)
    restaurants = db.scalars(query).all()
    return restaurants



@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    query = select(Restaurant).options(
        selectinload(Restaurant.menu_items.and_(MenuItem.active == True)), # Avoid lazy load, N+1 query problem
        selectinload(Restaurant.cuisine),
    ).where(Restaurant.id == restaurant_id)
    restaurant = db.scalars(query).first()
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found") 
    return restaurant   
    


@router.post("", response_model=RestaurantOut, status_code=201)
def create_restaurant(data: RestaurantCreate, db: Session = Depends(get_db)):
    #ToDO: Add cuisine_cache in main.py - later, cuisines table is small and does not change often, so OK for now
    query_cuisine_id = select(Cuisine).where(Cuisine.name == data.cuisine)
    cuisine = db.scalars(query_cuisine_id).first()
    if None is cuisine:
        raise  HTTPException(status_code=400, detail=f"Unknown Cuisine {data.cuisine}")
    
    query_email_exists = select(Account).where(Account.username ==  data.owner.email)
    email_id = db.scalars(query_email_exists).first()
    if not email_id is None:
        raise  HTTPException(status_code=409, detail="Email already registered")

    query_r_name= select(Restaurant).where(Restaurant.name ==  data.name)
    r_name = db.scalars(query_r_name).first()
    if not r_name is None:
        raise  HTTPException(status_code=409, detail="Name already registered")

    contact = Contact(
        email = data.owner.email,
        phone_number = data.owner.phone,
        city = data.city
    )
    profile = Profile(preferred_name=data.owner.name, contact=contact)
    #ToDO: Handle Authn/Authz
    account = Account(username=data.owner.email, password=DEFAULT_PASSWORD, type="Restaurant", profile=profile)

    #add account to generate account.id, changes are not written to DB yet
    user = User(account = account)
    db.add(user)
    db.flush()

    menu_items = []
    for m in data.menu_items:
        mi = MenuItem(name = m.name, price = m.price)
        menu_items.append(mi)

    
    restaurant = Restaurant(name = data.name, user_id=user.id, 
                            menu_items = menu_items, cuisine_id= cuisine.id,city = data.city)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant) 
    logger.info("Restaurant %s onboarded: %s", restaurant.id, restaurant.name)
    return restaurant    

@router.delete("/{restaurant_id}", response_model=RestaurantOut)
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found") 
    restaurant.operational = False
    db.commit()
    db.refresh(restaurant)
    logger.info("Restaurant %s :: %s deactivated", restaurant.id, restaurant.name)
    return restaurant

@router.patch("/{restaurant_id}/reactivate", response_model=RestaurantOut)
def reactivate_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found") 
    restaurant.operational = True
    db.commit()
    db.refresh(restaurant)
    logger.info("Restaurant %s :: %s reactivated", restaurant.id, restaurant.name)
    return restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(restaurant_id: int, data: RestaurantUpdate, db: Session = Depends(get_db)):
    """Change only the fields that were sent. Add and remove dishes too."""
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail=f"Restaurant {restaurant_id} not found")

    if data.cuisine is not None:
        cuisine = db.scalars(select(Cuisine).where(Cuisine.name == data.cuisine)).first()
        if cuisine is None:
            raise HTTPException(status_code=400, detail=f"Unknown Cuisine {data.cuisine}")
        restaurant.cuisine_id = cuisine.id

    # only check the name if it actually changes, otherwise it would clash with itself
    if data.name is not None and data.name != restaurant.name:
        taken = db.scalars(select(Restaurant).where(Restaurant.name == data.name)).first()
        if taken is not None:
            raise HTTPException(status_code=409, detail="Name already registered")
        restaurant.name = data.name

    if data.city is not None:
        restaurant.city = data.city

    if data.opened_at is not None:
        restaurant.opened_at = data.opened_at

    # appending to the relationship fills in menu_item.restaurant_id for us
    for m in data.add_menu_items:
        restaurant.menu_items.append(MenuItem(name=m.name, price=m.price))

    # soft delete: old orders still point to these dishes
    for item_id in data.remove_menu_item_ids:
        item = db.get(MenuItem, item_id)
        if item is None or item.restaurant_id != restaurant.id:
            raise HTTPException(status_code=400,
                                detail=f"Menu item {item_id} is not on this restaurant's menu")
        item.active = False

    # nothing above is saved until here: an error on any step means no change at all
    db.commit()
    db.refresh(restaurant)
    logger.info("Restaurant %s :: %s updated", restaurant.id, restaurant.name)
    return restaurant
