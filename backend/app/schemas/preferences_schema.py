from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime



ESTILOS_VALIDOS = {
    'casual', 'formal', 'elegante', 'deportivo', 
    'boho', 'minimalista', 'rockero', 'vintage',
    'urbano', 'clasico', 'romantico', 'moderno'
}


class PreferenciasBase(BaseModel):
    """Schema base con campos comunes"""
    estilos_preferidos: List[str] = Field(default_factory=list, max_length=5, description="Máximo 5 estilos")
    categorias_favoritas: List[UUID] = Field(default_factory=list, max_length=10, description="IDs de categorías favoritas")
    colores_preferidos: List[UUID] = Field(default_factory=list, max_length=10, description="IDs de colores favoritos")
    evitar_categorias: List[UUID] = Field(default_factory=list, max_length=5, description="Categorías a evitar")
    
    @validator('estilos_preferidos')
    def validar_estilos(cls, estilos):
        """Valida que los estilos sean válidos"""
        if not estilos:
            return estilos
        
        # Convertir a minúsculas
        estilos_lower = [e.lower().strip() for e in estilos]
        
        # Validar que estén en la lista
        invalidos = set(estilos_lower) - ESTILOS_VALIDOS
        if invalidos:
            raise ValueError(f"Estilos no válidos: {invalidos}. Estilos permitidos: {ESTILOS_VALIDOS}")
        
        return estilos_lower
    
    @validator('categorias_favoritas', 'evitar_categorias')
    def validar_sin_duplicados(cls, categorias):
        """Elimina duplicados"""
        return list(set(categorias)) if categorias else []


class PreferenciasCreate(PreferenciasBase):
    """Schema para crear preferencias"""
    pass


class PreferenciasUpdate(BaseModel):
    """Schema para actualizar preferencias (todos los campos opcionales)"""
    estilos_preferidos: Optional[List[str]] = None
    categorias_favoritas: Optional[List[UUID]] = None
    colores_preferidos: Optional[List[UUID]] = None
    evitar_categorias: Optional[List[UUID]] = None
    
    @validator('estilos_preferidos')
    def validar_estilos(cls, estilos):
        if estilos is None:
            return None
        estilos_lower = [e.lower().strip() for e in estilos]
        invalidos = set(estilos_lower) - ESTILOS_VALIDOS
        if invalidos:
            raise ValueError(f"Estilos no válidos: {invalidos}")
        return estilos_lower


class PreferenciasResponse(PreferenciasBase):
    """Schema para respuesta"""
    id: UUID
    usuario_id: UUID
    creado_en: datetime
    actualizado_en: datetime
    
    class Config:
        from_attributes = True


class EstilosDisponiblesResponse(BaseModel):
    """Lista de estilos disponibles"""
    estilos: List[str] = list(ESTILOS_VALIDOS)
    descripcion: str = "Estilos disponibles para preferencias de usuario"