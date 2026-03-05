# 🎬 Quiz Video Generator

A complete web application for creating and generating quiz/trivia videos with AI-powered narration, supporting both vertical (TikTok/Shorts) and horizontal (YouTube) formats.

## Features

- **Web UI** - Modern, dark-themed interface for creating and managing quizzes
- **Multiple Quiz Types** - Geography, Movies, General Trivia, and Custom
- **AI Narration** - ElevenLabs text-to-speech integration
- **Flexible Video Formats** - 9:16 (vertical) for TikTok/Shorts or 16:9 (horizontal) for YouTube
- **Visual Elements** - Animated countdown timers, gradient backgrounds, text with outlines
- **Sample Data** - Pre-built geography and movie quizzes to get started quickly
- **Video Library** - Manage, download, and delete generated videos
- **Image Support** - Add custom images to questions

## Tech Stack

- **Backend:** Flask + SQLite
- **Frontend:** HTML/CSS/JavaScript (vanilla, no frameworks)
- **Video Generation:** ffmpeg + Pillow
- **Text-to-Speech:** ElevenLabs Python SDK
- **Deployment:** systemd + nginx

## Quick Start (Development)

### Prerequisites

- Python 3.8+
- ffmpeg
- ElevenLabs API key (optional, for narration)

### Installation

```bash
# Clone or navigate to the project directory
cd quiz-video-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from app.database import init_db; init_db()"

# Run the application
python3 app.py
```

The application will be available at `http://localhost:5000`

## Ubuntu Server Deployment

For production deployment on Ubuntu:

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (requires sudo)
sudo ./setup.sh
```

The setup script will:
- Install all system dependencies (Python, nginx, ffmpeg)
- Create virtual environment and install Python packages
- Initialize the database
- Configure systemd service
- Set up nginx reverse proxy
- Start the application

### Post-Installation

1. **Update nginx domain:**
   ```bash
   sudo nano /etc/nginx/sites-available/quiz-generator
   # Change server_name to your domain or IP
   sudo systemctl restart nginx
   ```

2. **Configure ElevenLabs API:**
   - Open the web interface
   - Go to Settings tab
   - Enter your API key and voice ID
   - Save settings

3. **Set up SSL (recommended):**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Usage Guide

### Creating a Quiz

1. **Quick Start:**
   - Click "Create New" tab
   - Use "Load Sample Data" buttons for pre-made quizzes
   - OR create from scratch:

2. **Manual Creation:**
   - Enter quiz name, category, difficulty
   - Select video format (16:9 or 9:16)
   - Click "Create Quiz"
   - Add questions one by one
   - Optionally upload images for questions

### Adding Questions

1. Click "Edit" on any quiz
2. Click "+ Add Question"
3. Enter question and answer text
4. Optionally upload an image
5. Click "Add Question"

### Generating Videos

1. Click "Generate Video" on any quiz
2. Wait for processing (can take 2-5 minutes depending on quiz length)
3. Video appears in "Video Library" tab
4. Download or share as needed

### Video Format

Each generated video includes:
- Question slide (3 seconds) with optional image
- Circular countdown timer (5 seconds, configurable)
- Answer reveal (4 seconds)
- AI narration for questions and answers (if API key configured)

**Total duration:** ~12 seconds per question

## Configuration

Settings are configurable via the web UI (Settings tab):

- **ElevenLabs API Key** - For text-to-speech narration
- **Voice ID** - ElevenLabs voice to use
- **Countdown Duration** - Seconds for countdown (3-10)
- **Default Video Format** - 16:9 or 9:16

## File Structure

```
quiz-video-generator/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # API routes
│   ├── database.py          # Database functions
│   ├── models.py            # Data models
│   └── video_generator.py   # Video generation engine
├── static/
│   ├── css/style.css        # Styling
│   ├── js/app.js            # Frontend logic
│   └── uploads/             # Uploaded images
├── templates/
│   └── index.html           # Main UI template
├── sample_data/
│   ├── geography.json       # Sample geography quiz
│   └── movies.json          # Sample movie quiz
├── deployment/
│   ├── quiz-generator.service  # systemd service file
│   └── nginx.conf           # nginx configuration
├── videos/                  # Generated videos
├── frames/                  # Temporary frames (auto-cleaned)
├── app.py                   # Main application entry
├── requirements.txt         # Python dependencies
├── setup.sh                 # Ubuntu deployment script
└── README.md               # This file
```

## Troubleshooting

### Video generation fails
- Check that ffmpeg is installed: `ffmpeg -version`
- Ensure write permissions on `videos/` and `frames/` directories
- Check logs: `sudo journalctl -u quiz-generator -f`

### No audio in videos
- Verify ElevenLabs API key is entered in Settings
- Check API quota at elevenlabs.io
- Videos generate without audio if no API key is configured

### Service won't start
```bash
# Check status
sudo systemctl status quiz-generator

# View logs
sudo journalctl -u quiz-generator -n 50

# Restart service
sudo systemctl restart quiz-generator
```

### nginx errors
```bash
# Test configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

## API Endpoints

The application provides a RESTful API:

- `GET /api/quizzes` - List all quizzes
- `POST /api/quizzes` - Create new quiz
- `GET /api/quizzes/<id>` - Get quiz details
- `DELETE /api/quizzes/<id>` - Delete quiz
- `POST /api/quizzes/<id>/questions` - Add question
- `POST /api/generate/<id>` - Generate video
- `GET /api/videos` - List all videos
- `GET /api/videos/<id>/download` - Download video
- `DELETE /api/videos/<id>` - Delete video
- `GET /api/settings` - Get settings
- `POST /api/settings` - Update settings

## Development

### Running in debug mode

```bash
python3 app.py
```

The app runs with `debug=True` by default, enabling hot reload.

### Adding new quiz categories

1. Create a JSON file in `sample_data/` with questions
2. Add category option to the UI in `templates/index.html`
3. Add sample data button in `static/js/app.js`

### Customizing video appearance

Edit `app/video_generator.py`:
- `create_gradient_background()` - Background colors
- `draw_text_with_outline()` - Text styling
- `draw_circular_countdown()` - Timer appearance
- Font sizes in `__init__()`

## License

MIT License - feel free to use and modify for your projects.

## Credits

- Built with Flask, Pillow, and ffmpeg
- Text-to-speech powered by ElevenLabs
- UI inspired by modern dark theme design

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs with `journalctl -u quiz-generator -f`
3. Ensure all dependencies are installed
4. Verify file permissions

---

**Enjoy creating quiz videos!** 🎬✨
