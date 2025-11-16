from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Product
from app.Backend.shop_service.models import Shop
from schemas import ProductResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import jwt

from config import JWT_SECRET_KEY, JWT_ALGORITHM

router = APIRouter(prefix="/products", tags=["products"])
security = HTTPBearer()


# -------------------------------
# Auth via JWT
# -------------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {"id": payload.get("user_id"), "role": payload.get("role")}
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")


# -------------------------------
# Create product in a shop
# -------------------------------
@router.post("/shops/{shop_id}/products", response_model=ProductResponse, status_code=201)
def create_product_for_shop(
    shop_id: int,
    name: str = Form(...),
    description: str = Form(None),
    price: int = Form(..., description="Prix en FCFA"),
    stock: int = Form(..., description="Quantité en stock"),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Vérifier que la boutique existe
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Boutique introuvable")

    # Vérifier que l'utilisateur est le propriétaire
    if shop.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Accès refusé : vous n'êtes pas le propriétaire de cette boutique")

    # Création du produit (plus de vérification du nom)
    product = Product(
        shop_id=shop_id,
        name=name,
        description=description,
        price=price,  # en FCFA
        stock=stock
    )

    # Gestion de l'image (optionnelle)
    if image:
        product.image = image.file.read()
        product.image_filename = image.filename
        product.image_content_type = image.content_type

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# -------------------------------
# Get product by ID (owner only)
# -------------------------------
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Produit introuvable")

    if product.shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    return product


# -------------------------------
# List all products of the user
# -------------------------------
@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(Product)
        .join(Shop)
        .filter(Shop.owner_id == user["id"])
        .all()
    )


# -------------------------------
# Update product
# -------------------------------
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    stock: int = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Produit introuvable")

    if product.shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    if name:
        exists = db.query(Product).filter(Product.shop_id == product.shop_id, Product.name == name).first()
        if exists and exists.id != product_id:
            raise HTTPException(400, "Un produit avec ce nom existe déjà")
        product.name = name

    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock

    if image:
        product.image = image.file.read()
        product.image_filename = image.filename
        product.image_content_type = image.content_type

    db.commit()
    db.refresh(product)
    return product


# -------------------------------
# Get product image
# -------------------------------
@router.get("/{product_id}/image")
def get_product_image(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or not product.image:
        raise HTTPException(404, "Image introuvable")

    if product.shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    return Response(content=product.image, media_type=product.image_content_type)


# -------------------------------
# Delete product
# -------------------------------
@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Produit introuvable")

    if product.shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    db.delete(product)
    db.commit()
    return None


# -------------------------------
# List products of a shop
# -------------------------------
@router.get("/shops/{shop_id}/products", response_model=List[ProductResponse])
def list_products_of_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(404, "Boutique introuvable")

    if shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    return db.query(Product).filter(Product.shop_id == shop_id).all()


# -------------------------------
# Get a product from a shop
# -------------------------------
@router.get("/shops/{shop_id}/products/{product_id}", response_model=ProductResponse)
def get_product_from_shop(
    shop_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id, Product.shop_id == shop_id).first()
    if not product:
        raise HTTPException(404, "Produit introuvable")

    if product.shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    return product


# -------------------------------
# Search products by keyword
# -------------------------------
@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., description="Mot clé à rechercher"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    products = (
        db.query(Product)
        .join(Shop)
        .filter(Shop.owner_id == user["id"])
        .filter(
            or_(
                Product.name.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%")
            )
        )
        .all()
    )
    return products
