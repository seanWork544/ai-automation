from collections.abc import Callable
from typing import Any, Generic, List, Optional, Type, TypeVar

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..crud import create_for_user, delete_for_user, get_for_user, list_for_user, update_for_user
from ..database import get_session
from ..models import User
from ..security import get_current_user

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
ReadSchemaType = TypeVar("ReadSchemaType")


def build_crud_router(
    *,
    model: Type[Any],
    create_schema: Type[Any],
    update_schema: Type[Any],
    read_schema: Type[Any],
    prefix: str,
    tags: list[str],
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("/", response_model=List[read_schema])  # type: ignore[arg-type]
    def list_items(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ) -> list[Any]:
        return list_for_user(model, session, current_user.id)

    @router.post("/", response_model=read_schema, status_code=201)
    def create_item(
        payload: create_schema,  # type: ignore[arg-type]
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ) -> Any:
        return create_for_user(model, session, current_user.id, payload.dict())

    @router.get("/{item_id}", response_model=read_schema)
    def get_item(
        item_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ) -> Any:
        return get_for_user(model, session, current_user.id, item_id)

    @router.patch("/{item_id}", response_model=read_schema)
    def update_item(
        item_id: int,
        payload: update_schema,  # type: ignore[arg-type]
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ) -> Any:
        return update_for_user(model, session, current_user.id, item_id, payload.dict(exclude_unset=True))

    @router.delete("/{item_id}", status_code=204)
    def delete_item(
        item_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ) -> None:
        delete_for_user(model, session, current_user.id, item_id)

    return router
