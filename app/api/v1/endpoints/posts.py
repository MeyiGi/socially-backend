# backend/app/api/v1/endpoints/posts.py
from fastapi import APIRouter, Depends
from app.core.deps import get_cursor, get_current_user_id
from app.schemas.post import PostCreate
from app.crud import post as post_crud

router = APIRouter()

@router.get("/")
def get_posts(cursor=Depends(get_cursor)):
    raw_posts = post_crud.get_feed(cursor)
    results = []
    for row in raw_posts:
        # FIXED: Handle Oracle CLOB objects
        content = row[1]
        if content and hasattr(content, "read"):
            content = content.read()

        results.append({
            "id": row[0],
            "content": content, # Used the processed string
            "image": row[2],
            "createdAt": row[3],
            "author": {
                "id": row[4], "name": row[5], "username": row[6], "image": row[7]
            },
            "_count": {"likes": row[8], "comments": row[9]},
            "likes": [], 
            "comments": [] 
        })
    return results

@router.post("/")
def create_post(post: PostCreate, user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    pid = post_crud.create_post(cursor, user_id, post.content, post.image)
    return {"success": True, "id": pid}

@router.post("/{post_id}/like")
def like_post(post_id: str, user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    liked = post_crud.toggle_like(cursor, user_id, post_id)
    return {"success": True, "liked": liked}