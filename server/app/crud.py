from typing import Any, Iterable, Optional, Type, TypeVar

from fastapi import HTTPException, status
from sqlmodel import SQLModel, Session, select

ModelType = TypeVar("ModelType", bound=SQLModel)


def list_for_user(model: Type[ModelType], session: Session, user_id: int, *, limit: int = 200) -> Iterable[ModelType]:
    statement = select(model).where(getattr(model, "user_id") == user_id).limit(limit)
    return session.exec(statement).all()


def create_for_user(model: Type[ModelType], session: Session, user_id: int, data: dict[str, Any]) -> ModelType:
    obj = model(**data, user_id=user_id)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def get_for_user(model: Type[ModelType], session: Session, user_id: int, object_id: Any) -> ModelType:
    obj = session.get(model, object_id)
    if not obj or getattr(obj, "user_id", user_id) != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return obj


def update_for_user(model: Type[ModelType], session: Session, user_id: int, object_id: Any, data: dict[str, Any]) -> ModelType:
    obj = get_for_user(model, session, user_id, object_id)
    for key, value in data.items():
        if value is not None:
            setattr(obj, key, value)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def delete_for_user(model: Type[ModelType], session: Session, user_id: int, object_id: Any) -> None:
    obj = get_for_user(model, session, user_id, object_id)
    session.delete(obj)
    session.commit()
