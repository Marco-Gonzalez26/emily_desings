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
)

from fastapi.middleware.cors import CORSMiddleware
from app.db.config import check_db_connection

app = FastAPI(
    title="Emily Designs API",
    description="API de e-commerce con análisis morfológico",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Cambiar a la URL del front y del produccion
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
# app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
# app.include_router(carritos.router, prefix="/api/carritos", tags=["carritos"])


@app.on_event("startup")
async def startup():
    check_db_connection()
