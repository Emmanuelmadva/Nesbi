from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from app.Backend.product_service.routers import router as product_router
from app.Backend.auth_service.routers import auth_router
from app.Database.database import Base, engine
import app.Backend.product_service.models
import app.Backend.shop_service.models
Base.metadata.create_all(bind=engine)
app = FastAPI()
# Monter le dossier Frontend comme static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/Frontend/templates")

#routes
app.include_router(product_router)
app.include_router(auth_router)
@app.get("/")
async def page_acceuil(request: Request):
    return templates.TemplateResponse("pageAcceuil.html", {"request": request})
@app.get("/produits", response_class=HTMLResponse)
async def read_produits(request: Request):
    return templates.TemplateResponse("produits.html", {"request": request})
