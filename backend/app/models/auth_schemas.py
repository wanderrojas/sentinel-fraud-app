"""
Authentication Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Request para login"""
    username: str = Field(..., description="Usuario")
    password: str = Field(..., description="Contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }

class UserData(BaseModel):
    """Datos del usuario"""
    usuario: str
    nombreUsuario: str
    rolId: int
    rol: str
    horaConeccion: str


class AuthDTO(BaseModel):
    """Response de autenticación"""
    token: str
    userData: UserData
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "userData": {
                    "usuario": "admin",
                    "nombreUsuario": "Administrador del Sistema",
                    "rolId": 1,
                    "rol": "Administrador",
                    "horaConeccion": "2025-12-23T15:30:00"
                }
            }
        }


class TokenData(BaseModel):
    """Datos decodificados del token"""
    username: Optional[str] = None
    rol_id: Optional[int] = None