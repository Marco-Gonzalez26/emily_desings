from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.config import get_db
from app.schemas.schemas import (
    UsuarioCreate,
    UsuarioResponse,
    UserLogin,
    Token,
    CambiarPasswordRequest,
)
from app.services import auth_service
from app.utils.auth_security import decode_access_token


router = APIRouter(tags=["Autenticación"], prefix="/api/auth")


# HTTPBearer scheme para extraer el token del header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Dependency para obtener el usuario actual desde el token JWT

    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos

    Returns:
        Usuario actual autenticado

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Decodificar token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Buscar usuario en la base de datos
    from uuid import UUID

    user = auth_service.get_user_by_id(db, UUID(user_id))

    if user is None:
        raise credentials_exception

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )

    return user


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
)
def register(user_data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario

    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 8 caracteres)
    - **nombre_completo**: Nombre completo (opcional)
    - **telefono**: Teléfono de contacto (opcional)
    - **direccion**: Dirección (opcional)
    - **rol**: Rol del usuario (cliente/administrador, default: cliente)

    Returns:
        Token JWT y datos del usuario
    """
    # Crear usuario
    new_user = auth_service.create_user(db, user_data)

    # Generar token
    token_data = auth_service.create_user_token(new_user)

    # Convertir usuario a schema de respuesta
    user_response = UsuarioResponse.model_validate(new_user)

    return {**token_data, "user": user_response}


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Iniciar sesión

    - **email**: Email del usuario
    - **password**: Contraseña

    Returns:
        Token JWT y datos del usuario
    """
    # Autenticar usuario
    user = auth_service.authenticate_user(db, credentials)

    # Generar token
    token_data = auth_service.create_user_token(user)

    # Convertir usuario a schema de respuesta
    user_response = UsuarioResponse.model_validate(user)

    return {**token_data, "user": user_response}


@router.get("/me", response_model=UsuarioResponse)
def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Obtener información del usuario actual (requiere autenticación)

    Endpoint protegido que requiere token JWT en el header:
    Authorization: Bearer <token>

    Returns:
        Datos del usuario autenticado
    """
    return current_user


@router.post("/logout")
def logout():
    """
    Cerrar sesión

    Nota: Con JWT, el logout se maneja en el cliente eliminando el token.
    Este endpoint está aquí por completitud de la API.
    """
    return {"message": "Sesión cerrada exitosamente. Elimine el token del cliente."}


print("AUTH ROUTER LOADED:", router.routes)


@router.post("/reestablecer-contraseña")
def cambiar_password(data: CambiarPasswordRequest, db: Session = Depends(get_db)):
    """Cambiar contraseña (requiere contraseña actual)"""

    auth_service.cambiar_password(
        db=db,
        email=data.email,
        password_actual=data.password_actual,
        password_nueva=data.password_nueva,
    )

    return {"message": "Contraseña actualizada exitosamente"}
