import sqlite3
import json
from contextlib import contextmanager
from flask import current_app, g

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@contextmanager
def get_db_cursor():
    """Context manager for database operations"""
    db = get_db()
    cursor = db.cursor()
    try:
        yield cursor
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database schema"""
    db = sqlite3.connect('quiz_generator.db')
    cursor = db.cursor()
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    # Quizzes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT,
            video_format TEXT DEFAULT '16:9',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            answer_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'open',
            choices TEXT,
            image_path TEXT,
            order_index INTEGER NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE
        )
    ''')
    
    # Migration: add columns if they don't exist
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN question_type TEXT DEFAULT 'open'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN choices TEXT")
    except:
        pass
    
    # Videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            format TEXT NOT NULL,
            duration REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE
        )
    ''')
    
    # Insert default settings
    cursor.execute('''
        INSERT OR IGNORE INTO settings (key, value) VALUES 
        ('elevenlabs_api_key', ''),
        ('elevenlabs_voice_id', 'EXAVITQu4vr4xnSDxMaL'),
        ('default_video_format', '16:9'),
        ('background_music_enabled', 'false'),
        ('countdown_duration', '5')
    ''')
    
    db.commit()
    db.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
