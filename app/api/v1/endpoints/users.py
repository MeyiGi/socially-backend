from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.core.deps import get_cursor, get_optional_user_id, get_current_user_id
from app.crud import user as user_crud
from app.crud import post as post_crud
from app.crud import notification as notif_crud

router = APIRouter()

@router.get("/suggestions")
def get_suggestions(cursor=Depends(get_cursor), user_id: Optional[str] = Depends(get_optional_user_id)):
    return user_crud.get_random_users(cursor, user_id)

@router.get("/{username}")
def get_profile(username: str, cursor=Depends(get_cursor)):
    user = user_crud.get_profile_by_username(cursor, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# THESE ARE THE MISSING ROUTES FOR PROFILE TABS
@router.get("/{user_id}/posts")
def get_user_posts(user_id: str, cursor=Depends(get_cursor)):
    return post_crud.get_posts_by_author(cursor, user_id)

@router.get("/{user_id}/likes")
def get_user_liked_posts(user_id: str, cursor=Depends(get_cursor)):
    return post_crud.get_posts_liked_by_user(cursor, user_id)

@router.get("/{target_id}/is_following")
def check_follow(target_id: str, user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    return {"is_following": user_crud.is_following(cursor, user_id, target_id)}

@router.post("/{target_id}/follow")
def follow_user(target_id: str, user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    is_following = user_crud.toggle_follow(cursor, user_id, target_id)
    if is_following:
        notif_crud.create_notification(cursor, "FOLLOW", target_id, user_id)
    return {"success": True, "following": is_following}