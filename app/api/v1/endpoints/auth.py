from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.deps import get_cursor, get_current_user_id
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.schemas.token import Token
from app.crud import user as user_crud

router = APIRouter()

@router.post("/register", status_code=201)
def register(user: UserCreate, cursor=Depends(get_cursor)):
    # Check if email is taken
    if user_crud.get_user_by_email_or_username(cursor, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
        
    # Check if username is taken
    if user_crud.get_user_by_email_or_username(cursor, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_crud.create_user(cursor, user)
    return {"message": "User registered successfully"}

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), cursor=Depends(get_cursor)):
    user = user_crud.get_user_by_email_or_username(cursor, form_data.username)
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user[0]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(user_id: str = Depends(get_current_user_id), cursor=Depends(get_cursor)):
    user = user_crud.get_user_profile(cursor, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserOut)
def update_me(
    user_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    cursor=Depends(get_cursor)
):
    user_crud.update_user_profile(cursor, user_id, user_data)
    updated_user = user_crud.get_user_profile(cursor, user_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found after update")
    return updated_user