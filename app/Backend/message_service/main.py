from fastapi import FastAPI
from routers import router as message_router
from database import Base, engine

# Crée les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Message Service")

app.include_router(message_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
