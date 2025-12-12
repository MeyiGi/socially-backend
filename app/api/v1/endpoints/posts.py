from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_cursor, get_current_user_id
from app.schemas.post import PostCreate, CommentCreate
from app.crud import post as post_crud
from app.crud import notification as notif_crud

router = APIRouter()

@router.get("/")
def get_posts(cursor=Depends(get_cursor)):
    # Returns the list of dicts directly from CRUD
    return post_crud.get_feed(cursor)

@router.post("/")
def create_post(post: PostCreate, user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    pid = post_crud.create_post(cursor, user_id, post.content, post.image)
    return {"success": True, "id": pid}

@router.post("/{post_id}/like")
def like_post(post_id: str, user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    # 1. Get the post to find its author
    post = post_crud.get_post_by_id(cursor, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 2. Toggle the like status in the database
    liked = post_crud.toggle_like(cursor, user_id, post_id)

    # 3. If a new like was added (not an unlike), create a notification
    if liked:
        notif_crud.create_notification(
            cursor,
            type_n="LIKE",
            user_id=post["author_id"],  # The user to notify is the post's author
            creator_id=user_id,         # The user who performed the action
            post_id=post_id
        )

    return {"success": True, "liked": liked}

@router.post("/{post_id}/comments")
def create_comment_on_post(
    post_id: str,
    comment: CommentCreate,
    user_id: str = Depends(get_current_user_id),
    cursor=Depends(get_cursor),
):
    post = post_crud.get_post_by_id(cursor, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_id = post_crud.create_comment(cursor, user_id, post_id, comment.content)

    notif_crud.create_notification(
        cursor,
        type_n="COMMENT",
        user_id=post["author_id"],
        creator_id=user_id,
        post_id=post_id,
        comment_id=comment_id,
    )

    return {"success": True, "comment_id": comment_id}

@router.delete("/{post_id}", status_code=200)
def delete_post_by_id(
    post_id: str,
    user_id: str = Depends(get_current_user_id),
    cursor=Depends(get_cursor)
):
    success = post_crud.delete_post(cursor, post_id, user_id)
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized or post not found")
    return {"success": True, "message": "Post deleted"}