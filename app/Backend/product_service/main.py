from fastapi import FastAPI
from app.Backend.product_service.database import Base, engine
from routers import router as product_router
from app.Backend.shop_service.models import Shop
from app.Backend.product_service.models import Product

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Service")

app.include_router(product_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
