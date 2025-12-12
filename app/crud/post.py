import uuid
from collections import defaultdict

def create_post(cursor, author_id: str, content: str, image: str | None):
    pid = str(uuid.uuid4())
    sql = "INSERT INTO posts (id, author_id, content, image) VALUES (:1, :2, :3, :4)"
    cursor.execute(sql, (pid, author_id, content, image))
    return pid

def get_post_by_id(cursor, post_id: str):
    sql = "SELECT id, author_id FROM posts WHERE id = :1"
    cursor.execute(sql, (post_id,))
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "author_id": row[1]}
    return None

def create_comment(cursor, author_id: str, post_id: str, content: str):
    cid = str(uuid.uuid4())
    sql = "INSERT INTO comments (id, author_id, post_id, content) VALUES (:1, :2, :3, :4)"
    cursor.execute(sql, (cid, author_id, post_id, content))
    return cid

def delete_post(cursor, post_id: str, author_id: str):
    cursor.execute("SELECT author_id FROM posts WHERE id = :1", (post_id,))
    row = cursor.fetchone()
    if not row or row[0] != author_id:
        return False
    
    cursor.execute("DELETE FROM posts WHERE id = :1", (post_id,))
    return True

def _format_posts(rows, comments_by_post_id):
    """Helper to convert database tuples into clean dictionaries."""
    results = []
    for row in rows:
        post_id = row[0]
        # Handle Oracle CLOB objects if they exist
        post_content = row[1]
        if post_content and hasattr(post_content, "read"):
            post_content = post_content.read()

        results.append({
            "id": post_id,
            "content": post_content,
            "image": row[2],
            "createdAt": row[3],
            "author": {
                "id": row[4], "name": row[5], "username": row[6], "image": row[7]
            },
            "_count": {"likes": row[8], "comments": row[9]},
            "likes": [], # We can implement fetching these if needed
            "comments": comments_by_post_id.get(post_id, []) 
        })
    return results

def _fetch_and_group_comments(cursor, post_ids):
    """Fetches all comments for a list of post IDs and groups them."""
    if not post_ids:
        return defaultdict(list)

    # Create bind placeholders like :1, :2, :3
    bind_names = [f":{i+1}" for i in range(len(post_ids))]
    
    comments_sql = f"""
        SELECT c.id, c.content, c.created_at, c.post_id, 
               u.id as author_id, u.name, u.username, u.image
        FROM comments c
        JOIN users u ON c.author_id = u.id
        WHERE c.post_id IN ({','.join(bind_names)})
        ORDER BY c.created_at ASC
    """
    cursor.execute(comments_sql, post_ids)
    
    comments_by_post_id = defaultdict(list)
    for comment_row in cursor.fetchall():
        # Handle CLOB for comment content
        comment_content = comment_row[1]
        if comment_content and hasattr(comment_content, "read"):
            comment_content = comment_content.read()

        comments_by_post_id[comment_row[3]].append({
            "id": comment_row[0],
            "content": comment_content,
            "createdAt": comment_row[2],
            "author": {
                "id": comment_row[4],
                "name": comment_row[5],
                "username": comment_row[6],
                "image": comment_row[7]
            }
        })
    return comments_by_post_id

def _fetch_posts_and_comments(cursor, sql, params=()):
    """A generic function to fetch posts, their comments, and format them."""
    cursor.execute(sql, params)
    post_rows = cursor.fetchall()

    if not post_rows:
        return []

    post_ids = [row[0] for row in post_rows]
    comments_by_post_id = _fetch_and_group_comments(cursor, post_ids)
    
    return _format_posts(post_rows, comments_by_post_id)

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
    return _fetch_posts_and_comments(cursor, sql)

def get_posts_by_author(cursor, author_id: str):
    sql = """
        SELECT p.id, p.content, p.image, p.created_at,
               u.id as auth_id, u.name, u.username, u.image as auth_img,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as likes,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comments
        FROM posts p
        JOIN users u ON p.author_id = u.id
        WHERE p.author_id = :1
        ORDER BY p.created_at DESC
    """
    return _fetch_posts_and_comments(cursor, sql, (author_id,))

def get_posts_liked_by_user(cursor, user_id: str):
    sql = """
        SELECT p.id, p.content, p.image, p.created_at,
               u.id as auth_id, u.name, u.username, u.image as auth_img,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as likes,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comments
        FROM posts p
        JOIN users u ON p.author_id = u.id
        JOIN likes l ON l.post_id = p.id
        WHERE l.user_id = :1
        ORDER BY l.created_at DESC
    """
    return _fetch_posts_and_comments(cursor, sql, (user_id,))

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