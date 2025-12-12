import uuid

def create_post(cursor, author_id: str, content: str, image: str | None):
    pid = str(uuid.uuid4())
    sql = "INSERT INTO posts (id, author_id, content, image) VALUES (:1, :2, :3, :4)"
    cursor.execute(sql, (pid, author_id, content, image))
    return pid

def get_feed(cursor):
    sql = """
        SELECT p.id, p.content, p.image, p.created_at,
               u.id as auth_id, u.name, u.username, u.image as auth_img,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as likes,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comments
        FROM posts p
        JOIN users u ON p.author_id = u.id
        ORDER BY p.created_at DESC
        FETCH FIRST 20 ROWS ONLY
    """
    cursor.execute(sql)
    # Returns a list of tuples
    return cursor.fetchall()

def toggle_like(cursor, user_id: str, post_id: str):
    check_sql = "SELECT id FROM likes WHERE user_id = :1 AND post_id = :2"
    cursor.execute(check_sql, (user_id, post_id))
    
    if cursor.fetchone():
        cursor.execute("DELETE FROM likes WHERE user_id = :1 AND post_id = :2", (user_id, post_id))
        return False # Unliked
    else:
        lid = str(uuid.uuid4())
        cursor.execute("INSERT INTO likes (id, user_id, post_id) VALUES (:1, :2, :3)", (lid, user_id, post_id))
        return True # Liked