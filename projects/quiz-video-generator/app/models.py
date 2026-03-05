import json
from app.database import get_db_cursor

class Settings:
    @staticmethod
    def get(key, default=None):
        """Get a setting value"""
        with get_db_cursor() as cursor:
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else default
    
    @staticmethod
    def set(key, value):
        """Set a setting value"""
        with get_db_cursor() as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value) 
                VALUES (?, ?)
            ''', (key, value))
    
    @staticmethod
    def get_all():
        """Get all settings as a dictionary"""
        with get_db_cursor() as cursor:
            cursor.execute('SELECT key, value FROM settings')
            return dict(cursor.fetchall())

class Quiz:
    @staticmethod
    def create(name, category, difficulty='medium', video_format='16:9'):
        """Create a new quiz"""
        with get_db_cursor() as cursor:
            cursor.execute('''
                INSERT INTO quizzes (name, category, difficulty, video_format)
                VALUES (?, ?, ?, ?)
            ''', (name, category, difficulty, video_format))
            return cursor.lastrowid
    
    @staticmethod
    def get(quiz_id):
        """Get a quiz by ID"""
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM quizzes WHERE id = ?', (quiz_id,))
            return cursor.fetchone()
    
    @staticmethod
    def get_all():
        """Get all quizzes"""
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM quizzes ORDER BY created_at DESC')
            return cursor.fetchall()
    
    @staticmethod
    def delete(quiz_id):
        """Delete a quiz"""
        with get_db_cursor() as cursor:
            cursor.execute('DELETE FROM quizzes WHERE id = ?', (quiz_id,))
    
    @staticmethod
    def update(quiz_id, **kwargs):
        """Update quiz fields"""
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if fields:
            values.append(quiz_id)
            query = f"UPDATE quizzes SET {', '.join(fields)} WHERE id = ?"
            with get_db_cursor() as cursor:
                cursor.execute(query, values)

class Question:
    @staticmethod
    def create(quiz_id, question_text, answer_text, order_index, image_path=None, question_type='open', choices=None):
        """Create a new question"""
        import json as _json
        choices_str = _json.dumps(choices) if choices else None
        with get_db_cursor() as cursor:
            cursor.execute('''
                INSERT INTO questions (quiz_id, question_text, answer_text, image_path, order_index, question_type, choices)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (quiz_id, question_text, answer_text, image_path, order_index, question_type, choices_str))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_quiz(quiz_id):
        """Get all questions for a quiz"""
        with get_db_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM questions 
                WHERE quiz_id = ? 
                ORDER BY order_index
            ''', (quiz_id,))
            return cursor.fetchall()
    
    @staticmethod
    def delete(question_id):
        """Delete a question"""
        with get_db_cursor() as cursor:
            cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    
    @staticmethod
    def update(question_id, **kwargs):
        """Update question fields"""
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if fields:
            values.append(question_id)
            query = f"UPDATE questions SET {', '.join(fields)} WHERE id = ?"
            with get_db_cursor() as cursor:
                cursor.execute(query, values)

class Video:
    @staticmethod
    def create(quiz_id, filename, format_type, duration=None):
        """Create a new video record"""
        with get_db_cursor() as cursor:
            cursor.execute('''
                INSERT INTO videos (quiz_id, filename, format, duration, status)
                VALUES (?, ?, ?, ?, 'completed')
            ''', (quiz_id, filename, format_type, duration))
            return cursor.lastrowid
    
    @staticmethod
    def get_all():
        """Get all videos"""
        with get_db_cursor() as cursor:
            cursor.execute('''
                SELECT v.*, q.name as quiz_name, q.category 
                FROM videos v
                JOIN quizzes q ON v.quiz_id = q.id
                ORDER BY v.created_at DESC
            ''')
            return cursor.fetchall()
    
    @staticmethod
    def delete(video_id):
        """Delete a video record"""
        with get_db_cursor() as cursor:
            cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
    
    @staticmethod
    def get(video_id):
        """Get a video by ID"""
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
            return cursor.fetchone()
