from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional
from app.Backend.auth_service.database import SessionLocal
from app.Backend.auth_service.models import User, UserRole
from app.Backend.auth_service.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.Backend.auth_service.utils import get_password_hash, verify_password, create_access_token, decode_access_token
from app.Backend.auth_service.schemas import ChangePasswordRequest

auth_router = APIRouter(prefix="/auth", tags=["authentification"])

# Dependency pour DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency pour vérifier JWT
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token manquant")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    return user

# -------------------
# ROUTES PRINCIPALES
# -------------------

# Inscription
@auth_router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Connexion
@auth_router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    token = create_access_token({
        "user_id": db_user.id,
        "username": db_user.username,
        "role": db_user.role.value
    })
    return {"access_token": token, "token_type": "bearer"}

# Récupérer le profil
@auth_router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Changer le mot de passe (authentifié)
@auth_router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Mot de passe changé avec succès"}

# Réinitialisation du mot de passe (simulé)
# Ici on génère un token de réinitialisation (dans une vraie app, tu enverrais un mail)
@auth_router.post("/reset-password-request")
def reset_password_request(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = create_access_token({"user_id": user.id}, expires_delta=None)  # durée limitée à config si souhaité
    # En vrai, envoyer le token par email
    return {"message": "Token de réinitialisation généré", "reset_token": token}

@auth_router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Mot de passe réinitialisé avec succès"}

# Vérification des rôles (exemple)
@auth_router.get("/admin-only")
def admin_only_route(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return {"message": f"Bienvenue Admin {current_user.username}"}


# Supprimer un utilisateur (admin only)
@auth_router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Vérifier que l'utilisateur courant est admin
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Accès refusé : seule les administrateurs peuvent supprimer")

    # Chercher l'utilisateur à supprimer
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Empêcher l'admin de se supprimer lui-même
    if user_to_delete.id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous supprimer vous-même")

    db.delete(user_to_delete)
    db.commit()
    return {"message": f"Utilisateur {user_to_delete.username} supprimé avec succès"}