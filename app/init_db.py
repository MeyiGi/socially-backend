import oracledb
import sys
import os

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def init_db():
    print(f"Connecting to database: {settings.DB_DSN}")
    try:
        conn = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dsn=settings.DB_DSN
        )
        cursor = conn.cursor()
        print("Connected successfully.")

        # List of tables to drop (to start fresh)
        tables = ["notifications", "follows", "likes", "comments", "posts", "users"]
        
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
                print(f"Dropped table {table}")
            except oracledb.DatabaseError as e:
                # Ignore error if table doesn't exist (ORA-00942)
                error, = e.args
                if error.code != 942:
                    raise

        # Create Tables
        print("Creating tables...")
        
        cursor.execute("""
        CREATE TABLE users (
            id VARCHAR2(36) PRIMARY KEY NOT NULL,
            email VARCHAR2(255) UNIQUE NOT NULL,
            username VARCHAR2(255) UNIQUE NOT NULL,
            password_hash VARCHAR2(255) NOT NULL,
            name VARCHAR2(255),
            bio VARCHAR2(1000),
            image VARCHAR2(1000),
            location VARCHAR2(255),
            website VARCHAR2(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        cursor.execute("""
        CREATE TABLE posts (
            id VARCHAR2(36) PRIMARY KEY NOT NULL,
            author_id VARCHAR2(36) NOT NULL,
            content CLOB,
            image VARCHAR2(1000),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_post_author FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
        )""")

        cursor.execute("""
        CREATE TABLE comments (
            id VARCHAR2(36) PRIMARY KEY NOT NULL,
            content CLOB NOT NULL,
            author_id VARCHAR2(36) NOT NULL,
            post_id VARCHAR2(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_comment_author FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_comment_post FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )""")

        cursor.execute("""
        CREATE TABLE likes (
            id VARCHAR2(36) PRIMARY KEY NOT NULL,
            post_id VARCHAR2(36) NOT NULL,
            user_id VARCHAR2(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_like_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_like_post FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            CONSTRAINT uq_like_user_post UNIQUE (user_id, post_id)
        )""")

        cursor.execute("""
        CREATE TABLE follows (
            follower_id VARCHAR2(36) NOT NULL,
            following_id VARCHAR2(36) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (follower_id, following_id),
            CONSTRAINT fk_follow_follower FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_follow_following FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE
        )""")

        cursor.execute("""
        CREATE TABLE notifications (
            id VARCHAR2(36) PRIMARY KEY NOT NULL,
            user_id VARCHAR2(36) NOT NULL,
            creator_id VARCHAR2(36) NOT NULL,
            type VARCHAR2(20) NOT NULL,
            read_status NUMBER(1) DEFAULT 0,
            post_id VARCHAR2(36),
            comment_id VARCHAR2(36),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_notif_creator FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_notif_post FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            CONSTRAINT fk_notif_comment FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE
        )""")

        conn.commit()
        print("All tables created successfully.")
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init_db()