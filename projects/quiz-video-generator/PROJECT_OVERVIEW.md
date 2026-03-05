# Quiz Video Generator - Project Overview

## 🎯 Project Summary

A complete, production-ready web application for creating quiz/trivia videos with AI narration. Built for content creators targeting TikTok, YouTube Shorts, and standard YouTube formats.

**Status:** ✅ Complete and ready to deploy

---

## 📦 Deliverables Checklist

### Application Code
- ✅ Flask backend with RESTful API
- ✅ SQLite database with models
- ✅ Video generation engine (Pillow + ffmpeg)
- ✅ ElevenLabs TTS integration
- ✅ Modern dark-themed UI
- ✅ Image upload support
- ✅ Question/quiz management system

### Deployment Files
- ✅ `setup.sh` - Automated Ubuntu deployment script
- ✅ `requirements.txt` - Python dependencies
- ✅ `quiz-generator.service` - systemd service file
- ✅ `nginx.conf` - nginx reverse proxy configuration

### Documentation
- ✅ `README.md` - User guide and quick start
- ✅ `DEPLOYMENT.md` - Complete deployment guide
- ✅ `test_app.py` - Setup verification script
- ✅ `.gitignore` - Git ignore rules

### Sample Data
- ✅ `geography.json` - 10 geography questions
- ✅ `movies.json` - 10 movie trivia questions

---

## 🏗️ Architecture

### Backend (Flask + SQLite)
```
app/
├── __init__.py          # App factory
├── routes.py            # API endpoints
├── database.py          # Database layer
├── models.py            # Data models (Quiz, Question, Video, Settings)
└── video_generator.py   # Video composition engine
```

**Database Schema:**
- `settings` - App configuration (API keys, preferences)
- `quizzes` - Quiz metadata
- `questions` - Question bank with answers and images
- `videos` - Generated video records

### Frontend (Vanilla JS)
- **No framework dependencies** - Pure HTML/CSS/JavaScript
- **Dark theme** - Modern, visually appealing UI
- **Responsive design** - Works on desktop and tablet
- **Real-time feedback** - Progress indicators, alerts

### Video Generation Pipeline
1. **Question Frame** (3s) - Question text + optional image
2. **Countdown Timer** (5s) - Circular animated countdown
3. **Answer Frame** (4s) - Answer reveal with green background
4. **Repeat** for each question
5. **TTS Audio** - ElevenLabs narration (optional)
6. **Encode** - ffmpeg renders final MP4

**Output Formats:**
- **16:9** (1920x1080) - YouTube, desktop
- **9:16** (1080x1920) - TikTok, Instagram Reels, YouTube Shorts

---

## 🚀 Quick Start

### Development (Mac/Linux)
```bash
cd quiz-video-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 test_app.py    # Verify setup
python3 app.py         # Start server
```
→ Visit `http://localhost:5000`

### Production (Ubuntu)
```bash
sudo ./setup.sh        # One-command deployment
```
→ Configures everything automatically

---

## ✨ Key Features

### Quiz Management
- Create custom quizzes with categories
- Add unlimited questions
- Upload images for questions
- Edit/delete questions anytime
- Pre-built sample quizzes (geography, movies)

### Video Generation
- Both vertical (9:16) and horizontal (16:9) formats
- Animated countdown timers
- Gradient backgrounds
- Text with outlines for readability
- Optional AI narration via ElevenLabs
- ~12 seconds per question

### Settings
- Configurable ElevenLabs API key
- Voice ID selection
- Countdown duration (3-10 seconds)
- Default video format preference

### Video Library
- List all generated videos
- Download videos
- Delete videos
- Metadata (duration, format, creation date)

---

## 🎨 UI Design

**Color Palette:**
- Background: Dark blue gradient (#1a1a2e → #16213e)
- Primary: Cyan (#00d4ff)
- Success: Green (#4ade80)
- Danger: Red (#ff4444)
- Text: Light gray (#e4e4e4)

**Features:**
- Tab-based navigation
- Card-based layouts
- Hover effects and transitions
- Modal dialogs
- Progress indicators
- Toast notifications

---

## 🔧 Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | Flask 3.0 |
| Database | SQLite 3 |
| Video Processing | ffmpeg + Pillow |
| Text-to-Speech | ElevenLabs SDK |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Deployment | systemd + nginx |
| Python | 3.8+ |

**Why These Choices:**
- **Flask** - Lightweight, perfect for this use case
- **SQLite** - Zero-config, embedded database
- **Vanilla JS** - No build step, easy to modify
- **ffmpeg** - Industry standard for video processing
- **systemd** - Native Linux service management

---

## 📁 File Structure

```
quiz-video-generator/
├── app/                          # Application code
│   ├── __init__.py              # Flask app factory
│   ├── routes.py                # API endpoints (17 routes)
│   ├── database.py              # DB connection & schema
│   ├── models.py                # Data models
│   └── video_generator.py       # Video composition engine
├── static/                       # Frontend assets
│   ├── css/style.css            # Dark theme styling
│   ├── js/app.js                # Frontend logic
│   └── uploads/                 # User-uploaded images
├── templates/                    # HTML templates
│   └── index.html               # Main UI (single page)
├── sample_data/                  # Pre-built quizzes
│   ├── geography.json           # 10 geography questions
│   └── movies.json              # 10 movie questions
├── deployment/                   # Deployment configs
│   ├── quiz-generator.service  # systemd service
│   └── nginx.conf               # nginx reverse proxy
├── videos/                       # Generated videos
├── frames/                       # Temporary frames (auto-cleaned)
├── music/                        # Background music (future feature)
├── app.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── setup.sh                      # Ubuntu deployment script
├── test_app.py                  # Setup verification
├── README.md                     # User documentation
├── DEPLOYMENT.md                 # Deployment guide
├── PROJECT_OVERVIEW.md           # This file
└── .gitignore                    # Git ignore rules
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main UI |
| GET | `/api/quizzes` | List all quizzes |
| POST | `/api/quizzes` | Create new quiz |
| GET | `/api/quizzes/<id>` | Get quiz with questions |
| DELETE | `/api/quizzes/<id>` | Delete quiz |
| PUT | `/api/quizzes/<id>` | Update quiz |
| POST | `/api/quizzes/<id>/questions` | Add question |
| DELETE | `/api/questions/<id>` | Delete question |
| PUT | `/api/questions/<id>` | Update question |
| POST | `/api/upload` | Upload image |
| POST | `/api/generate/<id>` | Generate video |
| GET | `/api/videos` | List all videos |
| GET | `/api/videos/<id>/download` | Download video |
| DELETE | `/api/videos/<id>` | Delete video |
| GET | `/api/settings` | Get settings |
| POST | `/api/settings` | Update settings |
| POST | `/api/sample-data/load` | Load sample quiz |

---

## 📊 Video Specs

### Horizontal (16:9)
- Resolution: 1920x1080
- FPS: 30
- Codec: H.264
- Format: MP4
- Target: YouTube

### Vertical (9:16)
- Resolution: 1080x1920
- FPS: 30
- Codec: H.264
- Format: MP4
- Target: TikTok, Reels, Shorts

### Timing per Question
- Question display: 3 seconds
- Countdown: 5 seconds (configurable 3-10)
- Answer reveal: 4 seconds
- **Total: ~12 seconds per question**

### File Sizes (Approximate)
- 5 questions: ~10-15 MB
- 10 questions: ~20-30 MB
- 20 questions: ~40-60 MB

---

## 🔐 Security Considerations

### Implemented
- ✅ File type validation for uploads (images only)
- ✅ Secure filename handling
- ✅ SQL injection prevention (parameterized queries)
- ✅ File size limits (50 MB max)
- ✅ API key storage in database (not in code)
- ✅ No user authentication (single-user application)

### Recommended for Production
- Add rate limiting for video generation
- Set up HTTPS with SSL certificates
- Configure firewall rules
- Regular backups
- Monitor disk space (videos can accumulate)

---

## 🧪 Testing

Run the test suite:
```bash
python3 test_app.py
```

**Tests Performed:**
- ✅ Module imports
- ✅ Dependencies installed
- ✅ ffmpeg availability
- ✅ Directory structure
- ✅ Database initialization
- ✅ Sample data validity

---

## 📈 Performance

### Video Generation Time
- **Without TTS:** ~5-10 seconds for 10 questions
- **With TTS:** ~30-60 seconds for 10 questions
  - Depends on ElevenLabs API latency
  - Network speed affects TTS calls

### Optimizations
- Frames cleaned up after generation
- Audio files removed after encoding
- Database queries optimized with indexes
- Static files served with long cache headers

### Scaling Considerations
- For high traffic, use gunicorn with multiple workers
- Consider Redis for session/cache management
- Offload video generation to background workers (Celery)
- Use cloud storage for videos (S3, etc.)

---

## 🎓 Learning Resources

### For Customization

**Change video appearance:**
- Edit `app/video_generator.py`
- Modify gradient colors in `create_gradient_background()`
- Adjust fonts, sizes, and layout

**Add new quiz categories:**
- Create JSON file in `sample_data/`
- Update category dropdown in `templates/index.html`

**Modify UI theme:**
- Edit `static/css/style.css`
- Change color variables
- Adjust card layouts

**Add background music:**
- Implement in `video_generator.py`
- Use ffmpeg's audio mixing
- Add music files to `music/` directory

---

## 🐛 Known Limitations

1. **Single-user design** - No authentication, meant for personal/internal use
2. **No background jobs** - Video generation blocks the request
3. **Local storage only** - Videos stored on server disk
4. **No video preview** - Can't preview before generating
5. **Basic image handling** - No cropping or advanced editing
6. **No undo/redo** - Question edits are immediate

---

## 🔮 Future Enhancements

**Potential Features:**
- [ ] Background job queue for video generation
- [ ] Video preview before generation
- [ ] Multiple quiz templates/themes
- [ ] Batch video generation
- [ ] Export/import quiz data
- [ ] Video editing (trim, rearrange)
- [ ] Background music library
- [ ] Score tracking in videos
- [ ] Multi-language support
- [ ] User authentication
- [ ] Cloud storage integration
- [ ] Social media auto-posting
- [ ] Analytics dashboard

---

## 📝 License

MIT License - Free to use and modify for any purpose.

---

## 🙏 Credits

**Built with:**
- Flask - Web framework
- Pillow - Image processing
- ffmpeg - Video encoding
- ElevenLabs - Text-to-speech
- Modern CSS - Dark theme design

**Created:** February 2026
**Status:** Production-ready
**Version:** 1.0.0

---

## 📞 Support

**For Issues:**
1. Check logs: `sudo journalctl -u quiz-generator -f`
2. Run tests: `python3 test_app.py`
3. Review `DEPLOYMENT.md` for troubleshooting
4. Verify ffmpeg: `ffmpeg -version`
5. Check permissions: `ls -la videos/ frames/`

**Common Commands:**
```bash
# Check service
sudo systemctl status quiz-generator

# Restart service
sudo systemctl restart quiz-generator

# View logs
sudo journalctl -u quiz-generator -f

# Test nginx
sudo nginx -t
```

---

**Ready to create viral quiz content! 🎬✨**
