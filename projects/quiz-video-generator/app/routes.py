from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
import json
from app.models import Settings, Quiz, Question, Video
from app.video_generator import VideoGenerator
from werkzeug.utils import secure_filename
import traceback

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@bp.route('/api/quizzes', methods=['GET', 'POST'])
def quizzes():
    """Get all quizzes or create new quiz"""
    if request.method == 'GET':
        quizzes = Quiz.get_all()
        return jsonify([dict(q) for q in quizzes])
    
    elif request.method == 'POST':
        data = request.json
        quiz_id = Quiz.create(
            name=data['name'],
            category=data['category'],
            difficulty=data.get('difficulty', 'medium'),
            video_format=data.get('video_format', '16:9')
        )
        return jsonify({'id': quiz_id, 'message': 'Quiz created successfully'})

@bp.route('/api/quizzes/<int:quiz_id>', methods=['GET', 'DELETE', 'PUT'])
def quiz_detail(quiz_id):
    """Get, update, or delete a specific quiz"""
    if request.method == 'GET':
        quiz = Quiz.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        questions = Question.get_by_quiz(quiz_id)
        return jsonify({
            'quiz': dict(quiz),
            'questions': [dict(q) for q in questions]
        })
    
    elif request.method == 'DELETE':
        Quiz.delete(quiz_id)
        return jsonify({'message': 'Quiz deleted successfully'})
    
    elif request.method == 'PUT':
        data = request.json
        Quiz.update(quiz_id, **data)
        return jsonify({'message': 'Quiz updated successfully'})

@bp.route('/api/quizzes/<int:quiz_id>/questions', methods=['POST'])
def add_question(quiz_id):
    """Add a question to a quiz"""
    data = request.json
    
    # Get current question count for order
    questions = Question.get_by_quiz(quiz_id)
    order_index = len(questions)
    
    question_id = Question.create(
        quiz_id=quiz_id,
        question_text=data['question_text'],
        answer_text=data['answer_text'],
        order_index=order_index,
        image_path=data.get('image_path'),
        question_type=data.get('question_type', 'open'),
        choices=data.get('choices')
    )
    
    return jsonify({'id': question_id, 'message': 'Question added successfully'})

@bp.route('/api/questions/<int:question_id>', methods=['DELETE', 'PUT'])
def question_detail(question_id):
    """Update or delete a question"""
    if request.method == 'DELETE':
        Question.delete(question_id)
        return jsonify({'message': 'Question deleted successfully'})
    
    elif request.method == 'PUT':
        data = request.json
        Question.update(question_id, **data)
        return jsonify({'message': 'Question updated successfully'})

@bp.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload an image for a question"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        return jsonify({'path': filepath, 'message': 'File uploaded successfully'})
    
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/api/generate/<int:quiz_id>', methods=['POST'])
def generate_video(quiz_id):
    """Generate video for a quiz"""
    try:
        # Get quiz and questions
        quiz = Quiz.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        questions = Question.get_by_quiz(quiz_id)
        if not questions:
            return jsonify({'error': 'No questions found'}), 400
        
        # Get settings
        api_key = Settings.get('elevenlabs_api_key')
        voice_id = Settings.get('elevenlabs_voice_id')
        countdown = int(Settings.get('countdown_duration', 5))
        
        # Prepare questions for video generator
        video_questions = []
        for q in questions:
            video_questions.append({
                'question': q['question_text'],
                'answer': q['answer_text'],
                'image': q['image_path'],
                'question_type': q['question_type'] if 'question_type' in q.keys() else 'open',
                'choices': q['choices'] if 'choices' in q.keys() else None
            })
        
        # Generate video
        video_format = quiz['video_format']
        generator = VideoGenerator(
            video_format=video_format,
            elevenlabs_api_key=api_key if api_key else None,
            voice_id=voice_id
        )
        
        output_filename = f"quiz_{quiz_id}_{video_format.replace(':', 'x')}.mp4"
        
        use_tts = bool(api_key)
        video_path = generator.generate_video(
            video_questions,
            output_filename,
            countdown_seconds=countdown,
            use_tts=use_tts
        )
        
        # Save video record to database
        Video.create(
            quiz_id=quiz_id,
            filename=output_filename,
            format_type=video_format,
            duration=len(questions) * (3 + countdown + 4)  # Approximate duration
        )
        
        return jsonify({
            'message': 'Video generated successfully',
            'filename': output_filename,
            'path': video_path
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/videos', methods=['GET'])
def videos():
    """Get all videos"""
    videos = Video.get_all()
    return jsonify([dict(v) for v in videos])

@bp.route('/api/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete a video"""
    video = Video.get(video_id)
    if video:
        # Delete file
        video_path = os.path.join('videos', video['filename'])
        if os.path.exists(video_path):
            os.remove(video_path)
        
        # Delete database record
        Video.delete(video_id)
        
        return jsonify({'message': 'Video deleted successfully'})
    
    return jsonify({'error': 'Video not found'}), 404

@bp.route('/api/videos/<int:video_id>/download')
def download_video(video_id):
    """Download a video"""
    video = Video.get(video_id)
    if video:
        video_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'videos', video['filename'])
        if os.path.exists(video_path):
            return send_file(video_path, as_attachment=True)
    
    return jsonify({'error': 'Video not found'}), 404

@bp.route('/api/videos/<int:video_id>/stream')
def stream_video(video_id):
    """Stream a video for inline playback"""
    video = Video.get(video_id)
    if video:
        video_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'videos', video['filename'])
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/mp4')
    
    return jsonify({'error': 'Video not found'}), 404

@bp.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    if request.method == 'GET':
        return jsonify(Settings.get_all())
    
    elif request.method == 'POST':
        data = request.json
        for key, value in data.items():
            Settings.set(key, str(value))
        
        return jsonify({'message': 'Settings updated successfully'})

@bp.route('/api/sample-data/load', methods=['POST'])
def load_sample_data():
    """Load sample quiz data"""
    data = request.json
    category = data.get('category')
    
    sample_file = f'sample_data/{category}.json'
    
    if not os.path.exists(sample_file):
        return jsonify({'error': 'Sample data not found'}), 404
    
    with open(sample_file, 'r') as f:
        sample_data = json.load(f)
    
    # Create quiz
    quiz_id = Quiz.create(
        name=sample_data['name'],
        category=sample_data['category'],
        difficulty=sample_data.get('difficulty', 'medium'),
        video_format=data.get('video_format', '16:9')
    )
    
    # Add questions
    for idx, q in enumerate(sample_data['questions']):
        Question.create(
            quiz_id=quiz_id,
            question_text=q['question'],
            answer_text=q['answer'],
            order_index=idx,
            image_path=q.get('image'),
            question_type=q.get('question_type', 'open'),
            choices=q.get('choices')
        )
    
    return jsonify({
        'quiz_id': quiz_id,
        'message': f'Loaded {len(sample_data["questions"])} questions'
    })
