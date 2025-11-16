from fastapi import FastAPI
from database import Base, engine
from routers import router as product_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Service")

app.include_router(product_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
