"""
Master Data Routes - Datos maestros
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.database.models import CustomerDB, CountryDB, ChannelDB, MerchantDB
from app.models.master_schemas import Customer, Country, Channel, Merchant
from app.security import verify_api_key

router = APIRouter()


@router.get(
    "/customers",
    response_model=List[Customer],
    summary="Obtener lista de clientes",
    dependencies=[Depends(verify_api_key)]
)
async def get_customers(db: Session = Depends(get_db)):
    """
    Obtiene la lista completa de clientes
    
    **REQUIERE X-API-Key**
    """
    customers = db.query(CustomerDB).all()
    return customers


@router.get(
    "/countries",
    response_model=List[Country],
    summary="Obtener lista de países",
    dependencies=[Depends(verify_api_key)]
)
async def get_countries(db: Session = Depends(get_db)):
    """
    Obtiene la lista completa de países
    
    **REQUIERE X-API-Key**
    """
    countries = db.query(CountryDB).all()
    return countries


@router.get(
    "/channels",
    response_model=List[Channel],
    summary="Obtener lista de canales",
    dependencies=[Depends(verify_api_key)]
)
async def get_channels(db: Session = Depends(get_db)):
    """
    Obtiene la lista completa de canales de transacción
    
    **REQUIERE X-API-Key**
    """
    channels = db.query(ChannelDB).all()
    return channels


@router.get(
    "/merchants",
    response_model=List[Merchant],
    summary="Obtener lista de comercios",
    dependencies=[Depends(verify_api_key)]
)
async def get_merchants(db: Session = Depends(get_db)):
    """
    Obtiene la lista completa de comercios
    
    **REQUIERE X-API-Key**
    """
    merchants = db.query(MerchantDB).all()
    return merchants