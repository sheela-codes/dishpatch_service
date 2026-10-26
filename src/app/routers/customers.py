import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.app.database import get_db
from src.app.models import Account, Contact, Profile, User
from src.app.schemas import CustomerCreate, CustomerOut

DEFAULT_PASSWORD = "changeme"
router = APIRouter(prefix="/customers", tags=["customers"])
logger = logging.getLogger(__name__)

@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    query_email_exists = select(Account).where(Account.username ==  data.email)
    email_id = db.scalars(query_email_exists).first()
    if not email_id is None:
        raise  HTTPException(status_code=409, detail="Email already registered")
    
    contact = Contact(
            email = data.email,
            phone_number = data.phone,
            city = data.city,
            address = data.address
        )
    profile = Profile(preferred_name=data.name, contact=contact)
    #ToDO: Handle Authn/Authz
    account = Account(username=data.email, password=DEFAULT_PASSWORD, type="Customer", profile=profile)
    user = User(account = account)
    db.add(user)
    db.commit()
    db.refresh(user)

    customer = CustomerOut(
        id=user.id, name=data.name, account_type = user.account.type,
        email=data.email, phone=data.phone,
        address=data.address, city=data.city,
    )
    return customer

@router.get("/{customer_id}", response_model = CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    user = db.get(User, customer_id)
    if user is None:
        raise HTTPException(404, f"Customer account {customer_id} not found")
    existing = user.account.profile.contact
    customer = CustomerOut(
        id=user.id, name=user.account.profile.preferred_name,account_type = user.account.type,
        email=existing.email, phone=existing.phone_number,
        address=existing.address, city=existing.city,
    )
    return customer


    
