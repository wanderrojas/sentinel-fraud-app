"""
Authentication Service - JWT (Versión simplificada sin bcrypt)
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
import hashlib
from app.config import get_settings
from app.models.auth_schemas import UserData, AuthDTO, TokenData

settings = get_settings()


def simple_hash(password: str) -> str:
    """Hash simple con SHA256 (seguro para desarrollo/demo)"""
    return hashlib.sha256(password.encode()).hexdigest()


# Base de datos de usuarios simulada (en producción usar PostgreSQL)
USERS_DB = {
    "admin@gmail.com": {
        "username": "admin@gmail.com",
        "hashed_password": simple_hash("admin123"),
        "nombre_usuario": "Administrador del Sistema",
        "rol_id": 1,
        'user_id':1,
        "rol": "Administrador"
    },
    "analyst@gmail.com": {
        "username": "analyst@gmail.com",
        "hashed_password": simple_hash("analyst123"),
        "nombre_usuario": "Analista de Fraude",
        "rol_id": 2,
        'user_id':2,
        "rol": "Analista"
    },
    "reviewer@gmail.com": {
        "username": "reviewer@gmail.com",
        "hashed_password": simple_hash("reviewer123"),
        "nombre_usuario": "Revisor HITL",
        "rol_id": 3,
        'user_id':3,
        "rol": "Revisor"
    }
}


class AuthService:
    """Servicio de autenticación JWT"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar password"""
        return simple_hash(plain_password) == hashed_password
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash de password"""
        return simple_hash(password)
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        """
        Autenticar usuario
        
        Args:
            username: Usuario
            password: Contraseña
        
        Returns:
            Datos del usuario si es válido, None si no
        """
        user = USERS_DB.get(username)
        if not user:
            return None
        
        if not AuthService.verify_password(password, user["hashed_password"]):
            return None
        
        return user
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crear JWT token
        
        Args:
            data: Datos a codificar en el token
            expires_delta: Tiempo de expiración
        
        Returns:
            JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """
        Decodificar JWT token
        
        Args:
            token: JWT token
        
        Returns:
            TokenData si es válido, None si no
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            username: str = payload.get("sub")
            rol_id: int = payload.get("rol_id")
            
            if username is None:
                return None
            
            return TokenData(username=username, rol_id=rol_id)
        
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def login(username: str, password: str) -> Optional[AuthDTO]:
        """
        Login completo
        
        Args:
            username: Usuario
            password: Contraseña
        
        Returns:
            AuthDTO con token y datos del usuario
        """
        # Autenticar
        user = AuthService.authenticate_user(username, password)
        if not user:
            return None
        
        # Crear token
        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        access_token = AuthService.create_access_token(
            data={
                "sub": user["username"],
                "rol_id": user["rol_id"]
            },
            expires_delta=access_token_expires
        )
        
        # Crear UserData
        user_data = UserData(
            usuario=user["username"],
            nombreUsuario=user["nombre_usuario"],
            rolId=user["rol_id"],
            rol=user["rol"],
            horaConeccion=datetime.now().isoformat()
        )
        
        # Crear AuthDTO
        auth_dto = AuthDTO(
            token=access_token,
            userData=user_data
        )
        
        return auth_dto


# ============================================
# INSTANCIA GLOBAL
# ============================================

def get_auth_service() -> AuthService:
    """Obtener instancia del servicio de autenticación"""
    return AuthService()