import uuid
from app.core.security import get_password_hash
from app.schemas.user import UserCreate

def get_user_by_email_or_username(cursor, identifier: str):
    # Fixed: Use :1 and :2 and pass the value twice to satisfy the driver
    sql = "SELECT id, password_hash FROM users WHERE email = :1 OR username = :2"
    cursor.execute(sql, (identifier, identifier))
    return cursor.fetchone()

def create_user(cursor, user: UserCreate):
    user_id = str(uuid.uuid4())
    hashed_pw = get_password_hash(user.password)
    image_url = f"https://api.dicebear.com/9.x/initials/svg?seed={user.username}"
    
    sql = """
        INSERT INTO users (id, email, username, password_hash, name, image)
        VALUES (:1, :2, :3, :4, :5, :6)
    """
    cursor.execute(sql, (user_id, user.email, user.username, hashed_pw, user.name, image_url))
    return user_id

def get_user_profile(cursor, user_id: str):
    sql = """
        SELECT id, name, username, email, image, bio, location, website 
        FROM users WHERE id = :1
    """
    cursor.execute(sql, (user_id,))
    row = cursor.fetchone()
    if row:
        return dict(zip(["id", "name", "username", "email", "image", "bio", "location", "website"], row))
    return None