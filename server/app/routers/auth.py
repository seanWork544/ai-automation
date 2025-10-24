from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from ..database import get_session
from ..models import User
from ..schemas import TokenResponse, UserCreate, UserRead
from ..security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=payload.email, password_hash=get_password_hash(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> TokenResponse:
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token = create_access_token(user_id=user.id, expires_delta=timedelta(minutes=60))
    return TokenResponse(access_token=access_token)
