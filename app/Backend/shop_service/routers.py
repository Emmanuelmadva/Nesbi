# shop_service/routers.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from database import get_db
from models import Shop
from schemas import ShopCreate, ShopUpdate, ShopResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config import JWT_SECRET_KEY, JWT_ALGORITHM

router = APIRouter(prefix="/shops", tags=["shops"])
security = HTTPBearer()  # Pour récupérer le header Authorization

# -------------------------------
# Dépendance pour récupérer l'utilisateur via JWT
# -------------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return {"id": user_id, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

# -------------------------------
# Create shop avec logo
# -------------------------------
@router.post("/", response_model=ShopResponse, status_code=201)
def create_shop(
    name: str = Form(...),
    description: str = Form(...),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Vérifier si un shop avec le même nom existe déjà
    existing_shop = db.query(Shop).filter(Shop.name == name).first()
    if existing_shop:
        raise HTTPException(status_code=400, detail="Une boutique avec ce nom existe déjà")

    shop = Shop(
        owner_id=user["id"],
        name=name,
        description=description,
    )

    if logo:
        shop.logo = logo.file.read()
        shop.logo_filename = logo.filename
        shop.logo_content_type = logo.content_type

    db.add(shop)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erreur : doublon détecté")
    db.refresh(shop)
    return shop

# -------------------------------
# Get shop (seul le propriétaire peut accéder)
# -------------------------------
@router.get("/{shop_id}", response_model=ShopResponse)
def get_shop(shop_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(404, "Boutique introuvable")
    if shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")
    return shop

# -------------------------------
# Update shop
# -------------------------------
@router.patch("/{shop_id}",response_model=ShopResponse)
def update_shop(
    shop_id: int,
    name: str = Form(None),
    description: str = Form(None),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()

    if not shop:
        raise HTTPException(status_code=404, detail="Boutique introuvable")

    if shop.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Mise à jour des champs optionnels
    if name is not None:
        shop.name = name

    if description is not None:
        shop.description = description

    # Mise à jour du logo
    if logo:
        shop.logo = logo.file.read()
        shop.logo_filename = logo.filename
        shop.logo_content_type = logo.content_type

    db.commit()
    db.refresh(shop)

    return shop

# -------------------------------
# List shops (optionnel : afficher uniquement les boutiques de l'utilisateur)
# -------------------------------
@router.get("/", response_model=List[ShopResponse])
def list_shops(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Shop).filter(Shop.owner_id == user["id"]).offset(skip).limit(limit).all()

# -------------------------------
# Endpoint pour récupérer le logo
# -------------------------------
@router.get("/{shop_id}/logo")
def get_shop_logo(shop_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop or not shop.logo:
        raise HTTPException(404, "Logo introuvable")
    if shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")
    return Response(content=shop.logo, media_type=shop.logo_content_type)
# -------------------------------
# Delete shop (seul le propriétaire peut supprimer)
# -------------------------------
@router.delete("/{shop_id}", status_code=204)
def delete_shop(shop_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(404, "Boutique introuvable")
    if shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    db.delete(shop)
    db.commit()
    return None  # FastAPI renvoie 204 No Content
