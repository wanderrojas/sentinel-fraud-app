"""
Security - Autenticación con API Key + JWT
"""
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings
from app.services.auth_service import get_auth_service
from app.models.auth_schemas import TokenData

settings = get_settings()
auth_service = get_auth_service()

# ============================================
# NIVEL 1: API KEY (TODAS LAS RUTAS)
# ============================================

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    NIVEL 1: Verificar API Key (obligatorio para todas las rutas excepto /health)
    
    Args:
        api_key: API Key enviada en el header X-API-Key
    
    Raises:
        HTTPException: Si el API Key es inválida o no existe
    
    Returns:
        str: API Key válida
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "API Key no proporcionada",
                "message": "Debes incluir el header X-API-Key con tu API Key válida",
                "example": "X-API-Key: tu-api-key-aqui"
            }
        )
    
    if api_key != settings.API_KEY_VALUE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "API Key inválida",
                "message": "La API Key proporcionada no es válida",
                "provided": api_key[:10] + "..." if len(api_key) > 10 else api_key
            }
        )
    
    return api_key


# ============================================
# NIVEL 2: JWT TOKEN (RUTAS PROTEGIDAS)
# ============================================

security_bearer = HTTPBearer(auto_error=False)


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer)
) -> TokenData:
    """
    NIVEL 2: Verificar JWT token (para rutas que requieren autenticación de usuario)
    
    Args:
        credentials: Credenciales Bearer con JWT token
    
    Raises:
        HTTPException: Si el token es inválido o expirado
    
    Returns:
        TokenData: Datos del usuario decodificados del token
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Token no proporcionado",
                "message": "Debes incluir el header Authorization: Bearer <token>"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    token_data = auth_service.decode_token(token)
    
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Token inválido o expirado",
                "message": "El token JWT proporcionado no es válido o ha expirado"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


async def get_current_user(
    token_data: TokenData = Depends(verify_jwt_token)
) -> dict:
    """
    Obtener usuario actual desde el token JWT
    
    Returns:
        Dict con información del usuario
    """
    from app.services.auth_service import USERS_DB
    
    user = USERS_DB.get(token_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return {
        "username": user["username"],
        "nombre_usuario": user["nombre_usuario"],
        "rol_id": user["rol_id"],
        "rol": user["rol"]
    }


# ============================================
# COMBINACIÓN: API KEY + JWT TOKEN
# ============================================

async def verify_api_key_and_jwt(
    api_key: str = Depends(verify_api_key),
    token_data: TokenData = Depends(verify_jwt_token)
) -> TokenData:
    """
    Verificar AMBOS: API Key + JWT Token
    
    Uso:
        dependencies=[Depends(verify_api_key_and_jwt)]
    
    Returns:
        TokenData: Datos del usuario autenticado
    """
    return token_data