from fastapi import FastAPI
from routers import auth_router
from database import init_db

app = FastAPI(title="Auth Service - Nesbi Market")

app.include_router(auth_router, prefix="/auth")

# Créer les tables au démarrage
init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
