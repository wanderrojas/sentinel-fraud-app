"""
Authentication Routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.auth_schemas import LoginRequest, AuthDTO, TokenData
from app.services.auth_service import get_auth_service
from app.security import verify_api_key

router = APIRouter()
auth_service = get_auth_service()


@router.post(
    "/login",
    response_model=AuthDTO,
    summary="Login de usuario",
    description="Autenticar usuario y obtener JWT token. Requiere X-API-Key",
    dependencies=[Depends(verify_api_key)]  # ← PROTEGIDO CON API KEY
)
async def login(credentials: LoginRequest):
    """
    Login de usuario
    
    **REQUIERE X-API-Key en header**
    
    Usuarios disponibles:
    - admin / admin123 (Administrador)
    - analyst / analyst123 (Analista)
    - reviewer / reviewer123 (Revisor)
    
    Returns:
        AuthDTO con token JWT y datos del usuario
    """
    
    auth_dto = auth_service.login(
        credentials.username,
        credentials.password
    )
    
    if not auth_dto:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Credenciales inválidas",
                "message": "Usuario o contraseña incorrectos"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ Login exitoso: {credentials.username}")
    
    return auth_dto


@router.get(
    "/me",
    summary="Obtener usuario actual",
    description="Obtener datos del usuario autenticado. Requiere X-API-Key + JWT token",
    dependencies=[Depends(verify_api_key)]  # ← PROTEGIDO CON API KEY
)
async def get_current_user(token: str):
    """
    Obtener usuario actual desde el token
    
    **REQUIERE:**
    - X-API-Key en header
    - token en query parameter
    
    Returns:
        Datos del usuario
    """
    token_data = auth_service.decode_token(token)
    
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    return {
        "username": token_data.username,
        "rol_id": token_data.rol_id
    }


@router.post(
    "/verify-token",
    summary="Verificar token",
    description="Verificar si un token JWT es válido. Requiere X-API-Key",
    dependencies=[Depends(verify_api_key)]  # ← PROTEGIDO CON API KEY
)
async def verify_token(token: str):
    """
    Verificar validez del token
    
    **REQUIERE X-API-Key en header**
    
    Body:
    - token: JWT token a verificar
    
    Returns:
        {"valid": true/false}
    """
    token_data = auth_service.decode_token(token)
    
    return {
        "valid": token_data is not None,
        "username": token_data.username if token_data else None
    }