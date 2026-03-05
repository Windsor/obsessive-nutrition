#!/usr/bin/env python3
"""
Quiz Video Generator - Main Application
"""
from app import create_app
from app.database import init_db, close_db
import os

# Initialize database if it doesn't exist
if not os.path.exists('quiz_generator.db'):
    print("Initializing database...")
    init_db()

app = create_app()

# Register teardown
app.teardown_appcontext(close_db)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
