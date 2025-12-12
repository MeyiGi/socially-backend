import uuid
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserUpdate

def get_user_by_email_or_username(cursor, identifier: str):
    sql = "SELECT id, password_hash FROM users WHERE email = :1 OR username = :2"
    cursor.execute(sql, (identifier, identifier))
    return cursor.fetchone()

def create_user(cursor, user: UserCreate):
    user_id = str(uuid.uuid4())
    hashed_pw = get_password_hash(user.password)
    # Ensure image_url is not None to avoid DB errors
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

def update_user_profile(cursor, user_id: str, data: UserUpdate):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return
    
    set_clauses = [f"{key} = :{key}" for key in update_data]
    params = update_data
    params['user_id'] = user_id
    
    sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = :user_id"
    
    cursor.execute(sql, params)

def get_profile_by_username(cursor, username: str):
    # Subqueries to get follower/following/post counts
    sql = """
        SELECT u.id, u.name, u.username, u.email, u.image, u.bio, u.location, u.website, u.created_at,
               (SELECT COUNT(*) FROM follows WHERE following_id = u.id) as followers,
               (SELECT COUNT(*) FROM follows WHERE follower_id = u.id) as following,
               (SELECT COUNT(*) FROM posts WHERE author_id = u.id) as posts
        FROM users u
        WHERE u.username = :1
    """
    cursor.execute(sql, (username,))
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0], 
            "name": row[1], 
            "username": row[2], 
            "email": row[3],
            "image": row[4], 
            "bio": row[5], 
            "location": row[6], 
            "website": row[7],
            "createdAt": row[8],
            "_count": {
                "followers": row[9], 
                "following": row[10], 
                "posts": row[11]
            }
        }
    return None

def get_random_users(cursor, exclude_user_id: str = None):
    # Fetch 3 random users. 
    # Since Oracle SAMPLE can be tricky with complex WHERE clauses, we just fetch rows where ID != current
    sql = """
        SELECT id, name, username, image, 
               (SELECT COUNT(*) FROM follows WHERE following_id = users.id) as followers
        FROM users
        WHERE id != :1
        ORDER BY DBMS_RANDOM.VALUE
        FETCH FIRST 3 ROWS ONLY
    """
    # If no user logged in, pass a dummy ID that won't match any UUID
    uid = exclude_user_id if exclude_user_id else "0"
    cursor.execute(sql, (uid,))
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            "id": r[0], 
            "name": r[1], 
            "username": r[2], 
            "image": r[3], 
            "_count": {"followers": r[4]}
        })
    return results

def toggle_follow(cursor, follower_id: str, following_id: str):
    check_sql = "SELECT 1 FROM follows WHERE follower_id = :1 AND following_id = :2"
    cursor.execute(check_sql, (follower_id, following_id))
    
    if cursor.fetchone():
        # Unfollow
        cursor.execute("DELETE FROM follows WHERE follower_id = :1 AND following_id = :2", (follower_id, following_id))
        return False
    else:
        # Follow
        cursor.execute("INSERT INTO follows (follower_id, following_id) VALUES (:1, :2)", (follower_id, following_id))
        return True

def is_following(cursor, follower_id: str, following_id: str):
    sql = "SELECT 1 FROM follows WHERE follower_id = :1 AND following_id = :2"
    cursor.execute(sql, (follower_id, following_id))
    return cursor.fetchone() is not None