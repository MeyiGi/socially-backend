from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from app.core.deps import get_cursor, get_current_user_id
from app.crud import notification as notif_crud

router = APIRouter()

class MarkReadSchema(BaseModel):
    ids: List[str]

@router.get("/")
def get_user_notifications(user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    return notif_crud.get_notifications(cursor, user_id)

@router.post("/mark-read")
def mark_read(payload: MarkReadSchema, user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    notif_crud.mark_read(cursor, user_id, payload.ids)
    return {"success": True}