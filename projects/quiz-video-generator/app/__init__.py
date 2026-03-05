from flask import Flask
import os

def create_app():
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['DATABASE'] = 'quiz_generator.db'
    app.config['VIDEOS_FOLDER'] = 'videos'
    app.config['FRAMES_FOLDER'] = 'frames'
    app.config['MUSIC_FOLDER'] = 'music'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    
    # Ensure directories exist
    for folder in [app.config['VIDEOS_FOLDER'], 
                   app.config['FRAMES_FOLDER'], 
                   app.config['MUSIC_FOLDER']]:
        os.makedirs(folder, exist_ok=True)
    
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
