from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routers import (
    auth,
    products,
    catalog,
    orders,
    categories,
    brands,
    cart,
    sizes,
    colors,
    inventory,
    analysis,
    dashboard,
    product_images,
    user,
    reports,
)

from app.models import (
    Usuario,
    TokenSesion,
    TokenRecuperacion,
    # PerfilMorfologico,
    # PreferenciaEstilo,
    AnalisisMorfologico,
    ReglasRecomendacion,
    RecomendacionGenerada,
    Marca,
    Categoria,
    Color,
    Talla,
    Producto,
    ImagenProducto,
    ProductoEtiquetaMorfologica,
    Inventario,
    Carrito,
    CarritoItem,
    Orden,
    OrdenItem,
    Comprobante,
    HistorialProducto,
    RecomendacionIA,
    HistorialReporte,
)
from app.services import clasification_service
from fastapi.middleware.cors import CORSMiddleware
from app.db.config import check_db_connection


async def lifespan(app: FastAPI):
    # Pre cargar modelos
    clasification_service.inicializar_modelos()
    yield


app = FastAPI(
    title="Emily Designs API",
    description="API de e-commerce con análisis morfológico",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(products.router)
app.include_router(catalog.router)
app.include_router(orders.router)
app.include_router(categories.router)
app.include_router(brands.router)
app.include_router(cart.router)
app.include_router(sizes.router)
app.include_router(colors.router)
app.include_router(inventory.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(product_images.router)
app.include_router(user.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup():
    check_db_connection()
