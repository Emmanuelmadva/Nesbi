from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from app.Backend.product_service.database import get_db
from app.Backend.product_service.models import Product
from app.Backend.shop_service.models import Shop
from app.Backend.product_service.schemas import ProductResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import jwt

from app.Backend.product_service.config import JWT_SECRET_KEY, JWT_ALGORITHM

router = APIRouter(prefix="/products", tags=["products"])
security = HTTPBearer()

# -------------------------------
# Route publique pour récupérer l'image d'un produit
# -------------------------------
@router.get("/{product_id}/image/public")
def get_product_image_public(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or not product.image:
        raise HTTPException(404, detail="Image introuvable")
    return Response(content=product.image, media_type=product.image_content_type)
# -------------------------------
# AUTH
# -------------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {"id": payload.get("user_id"), "role": payload.get("role")}
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")


# -------------------------------
# PUBLIC : GET ALL PRODUCTS
# -------------------------------
@router.get("/all", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """
    Récupère tous les produits enregistrés (PUBLIC)
    """
    return db.query(Product).all()


# -------------------------------
# Create product (AUTH REQUIRED)
# -------------------------------
@router.post("/shops/{shop_id}/products", response_model=ProductResponse, status_code=201)
def create_product_for_shop(
    shop_id: int,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    category: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Vérifier que la boutique existe
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(404, "Boutique introuvable")

    # Vérifier que l'utilisateur est le propriétaire
    if shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    # Vérifier qu'aucun produit du même nom n'existe déjà dans cette boutique
    existing_product = db.query(Product).filter(
        Product.shop_id == shop_id,
        Product.name == name
    ).first()
    if existing_product:
        raise HTTPException(400, "Un produit avec ce nom existe déjà dans cette boutique")

    # Créer le produit
    product = Product(
        shop_id=shop_id,
        name=name,
        description=description,
        price=price,
        stock=stock,
        category=category
    )

    # Gestion de l'image
    if image:
        product.image = image.file.read()
        product.image_filename = image.filename
        product.image_content_type = image.content_type or "application/octet-stream"

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

# -------------------------------
# SEARCH
# -------------------------------
@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    q = q.strip()

    products = db.query(Product).join(Shop).filter(
        and_(
            Shop.owner_id == user["id"],
            or_(
                func.lower(func.coalesce(Product.name, '')).ilike(f"%{q.lower()}%"),
                func.lower(func.coalesce(Product.description, '')).ilike(f"%{q.lower()}%")
            )
        )
    ).all()

    return products


# -------------------------------
# GET ONE PRODUCT
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
# LIST PRODUCTS OF USER
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
# UPDATE PRODUCT
# -------------------------------
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: int = Form(None),
    stock: int = Form(None),
    category: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Produit introuvable")

    if product.shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    if name: product.name = name
    if description is not None: product.description = description
    if price is not None: product.price = price
    if stock is not None: product.stock = stock
    if category is not None: product.category = category

    if image:
        product.image = image.file.read()
        product.image_filename = image.filename
        product.image_content_type = image.content_type

    db.commit()
    db.refresh(product)
    return product


# -------------------------------
# IMAGE
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
# DELETE PRODUCT
# -------------------------------
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Produit introuvable")

    if product.shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    db.delete(product)
    db.commit()

    return {"message": f"Produit '{product.name}' supprimé"}


# -------------------------------
# LIST products of a shop
# -------------------------------
@router.get("/shops/{shop_id}/products", response_model=List[ProductResponse])
def list_products_of_shop(shop_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(404, "Boutique introuvable")

    if shop.owner_id != user["id"]:
        raise HTTPException(403, "Accès refusé")

    return db.query(Product).filter(Product.shop_id == shop_id).all()
