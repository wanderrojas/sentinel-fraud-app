"""
Master Data Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Customer(BaseModel):
    """Esquema de cliente"""
    customer_id: str
    nombre: str
    apellido: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "customer_id": "CU-001",
                "nombre": "Juan Carlos",
                "apellido": "Pérez García",
                "email": "juan.perez@email.com",
                "telefono": "+51 987654321"
            }
        }


class Country(BaseModel):
    """Esquema de país"""
    code: str
    name: str
    currency: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "PE",
                "name": "Perú",
                "currency": "PEN"
            }
        }


class Channel(BaseModel):
    """Esquema de canal"""
    code: str
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "web",
                "name": "Web",
                "description": "Banca por Internet"
            }
        }


class Merchant(BaseModel):
    """Esquema de comercio"""
    merchant_id: str
    nombre: str
    categoria: Optional[str] = None
    pais: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "merchant_id": "M-001",
                "nombre": "Supermercados Wong",
                "categoria": "Supermercado",
                "pais": "PE"
            }
        }