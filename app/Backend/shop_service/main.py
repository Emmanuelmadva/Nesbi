# shop_service/main.py
from fastapi import FastAPI
from routers import router as shop_router
from database import Base, engine

app = FastAPI(title="Shop Service - Nesbi Market")

# Inclure le router pour les boutiques
app.include_router(shop_router)

# Créer les tables au démarrage
def init_db():
    Base.metadata.create_all(bind=engine)

init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
