import uuid

def create_notification(cursor, type_n: str, user_id: str, creator_id: str, post_id: str = None, comment_id: str = None):
    # Don't notify if user interacts with themselves
    if user_id == creator_id:
        return
        
    nid = str(uuid.uuid4())
    # 0 = Unread, 1 = Read
    sql = """
        INSERT INTO notifications (id, type, user_id, creator_id, post_id, comment_id, read_status)
        VALUES (:1, :2, :3, :4, :5, :6, 0)
    """
    cursor.execute(sql, (nid, type_n, user_id, creator_id, post_id, comment_id))

def get_notifications(cursor, user_id: str):
    sql = """
        SELECT n.id, n.type, n.read_status, n.created_at,
               c.id as creator_id, c.name, c.username, c.image,
               p.id as post_id, p.content, p.image as post_image,
               cm.id as comment_id, cm.content as comment_content
        FROM notifications n
        JOIN users c ON n.creator_id = c.id
        LEFT JOIN posts p ON n.post_id = p.id
        LEFT JOIN comments cm ON n.comment_id = cm.id
        WHERE n.user_id = :1
        ORDER BY n.created_at DESC
    """
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        # Handle Oracle CLOBs if present
        post_content = row[9].read() if row[9] and hasattr(row[9], 'read') else row[9]
        comment_content = row[12].read() if row[12] and hasattr(row[12], 'read') else row[12]

        results.append({
            "id": row[0],
            "type": row[1],
            "read": bool(row[2]),
            "createdAt": row[3],
            "creator": {
                "id": row[4], "name": row[5], "username": row[6], "image": row[7]
            },
            "post": {"id": row[8], "content": post_content, "image": row[10]} if row[8] else None,
            "comment": {"id": row[11], "content": comment_content} if row[11] else None
        })
    return results

def mark_read(cursor, user_id: str, notification_ids: list[str]):
    if not notification_ids:
        return
    
    # Create binding string dynamically like :2, :3, :4
    # :1 is reserved for user_id
    bind_names = [f":{i+2}" for i in range(len(notification_ids))]
    sql = f"UPDATE notifications SET read_status = 1 WHERE user_id = :1 AND id IN ({','.join(bind_names)})"
    
    # Combine user_id with the list of IDs for arguments
    args = [user_id] + notification_ids
    cursor.execute(sql, args)