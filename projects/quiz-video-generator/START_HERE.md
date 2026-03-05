# 🚀 START HERE - Quiz Video Generator

Welcome! This is your complete quiz video generation application. Here's how to get started in 60 seconds.

---

## ⚡ Quick Start (3 Steps)

### 1️⃣ Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Test Everything Works
```bash
python3 test_app.py
```
You should see: `✓ All tests passed!`

### 3️⃣ Start the Application
```bash
python3 app.py
```
Then open: **http://localhost:5000**

**That's it!** 🎉

---

## 🎬 First Video (2 Minutes)

1. **Load Sample Quiz**
   - Click the **"Create New"** tab
   - Click **"🌍 Geography Quiz"** or **"🎬 Movie Quiz"**
   
2. **Generate Video**
   - Go to **"My Quizzes"** tab
   - Click **"Generate Video"** on the quiz
   - Wait 10-30 seconds
   
3. **Download**
   - Go to **"Video Library"** tab
   - Click **"Download"**
   - Watch your quiz video!

---

## 📱 What You Can Do

- ✅ Create unlimited quizzes
- ✅ Add custom questions with images
- ✅ Generate videos in 2 formats:
  - **16:9** (YouTube)
  - **9:16** (TikTok/Shorts)
- ✅ Add AI narration (optional - needs API key)
- ✅ Download and share videos

---

## 🔑 Add Voice Narration (Optional)

1. Get free API key from [elevenlabs.io](https://elevenlabs.io)
2. Click **"Settings"** tab in the app
3. Paste your API key
4. Click **"Save Settings"**

Now your videos will have AI narration! 🎙️

---

## 🖥️ Deploy to Server

**Ubuntu Server (One Command):**
```bash
sudo ./setup.sh
```

This automatically:
- Installs all dependencies
- Configures nginx
- Sets up systemd service
- Starts the application

See `DEPLOYMENT.md` for details.

---

## 📚 Documentation Guide

| File | What It's For |
|------|---------------|
| **START_HERE.md** | 👈 You are here! Quick start guide |
| **README.md** | Complete user manual |
| **DEPLOYMENT.md** | Production deployment guide |
| **PROJECT_OVERVIEW.md** | Technical architecture |
| **COMPLETION_REPORT.md** | Project summary |

**For most users:** Just read this file + README.md!

---

## 🎨 Example Video Timeline

For a 10-question quiz:
```
Question 1 (3s) → Countdown (5s) → Answer (4s) = 12s
Question 2 (3s) → Countdown (5s) → Answer (4s) = 12s
...
Question 10 (3s) → Countdown (5s) → Answer (4s) = 12s

Total: ~2 minutes video
```

---

## ❓ Troubleshooting

### "Port 5000 in use"
```bash
# Use different port
python3 app.py  # Then edit app.py to use port 5001
```

### "ffmpeg not found"
```bash
# Mac:
brew install ffmpeg

# Ubuntu:
sudo apt install ffmpeg

# Windows:
# Download from ffmpeg.org
```

### "Database error"
```bash
# Reinitialize database
python3 -c "from app.database import init_db; init_db()"
```

### "No videos generated"
- Check `videos/` directory exists
- Check file permissions
- View logs in terminal

---

## 🎯 Next Steps

1. **Try it locally** - Create a quiz, generate a video
2. **Customize appearance** - Edit colors in `app/video_generator.py`
3. **Add your content** - Create quizzes for your niche
4. **Deploy to server** - Run `setup.sh` on Ubuntu
5. **Share videos** - Upload to TikTok, YouTube, Instagram

---

## 🆘 Need Help?

**Check these in order:**
1. Run `python3 test_app.py` - Does everything pass?
2. Check terminal for error messages
3. Read `README.md` for detailed usage
4. Read `DEPLOYMENT.md` for server setup
5. Check logs: `journalctl -u quiz-generator -f` (on server)

---

## ✨ Features at a Glance

- 🎨 **Beautiful dark theme UI**
- 📱 **Two video formats** (vertical + horizontal)
- 🤖 **AI narration** (ElevenLabs)
- 🖼️ **Image support** for questions
- 📚 **Sample quizzes** included
- 🚀 **One-click deploy** to Ubuntu
- 📦 **No build step** - pure Python + vanilla JS
- 🔧 **Easy to customize**

---

## 🎓 Quick Tips

**Best Practices:**
- Keep questions short (under 100 characters)
- Use high-quality images (500x500+)
- Test without TTS first (faster)
- Generate 5-10 question quizzes (1-2 min videos)

**Video Format Guide:**
- **16:9** (horizontal) → YouTube, desktop viewing
- **9:16** (vertical) → TikTok, Instagram Reels, YouTube Shorts

**Quiz Ideas:**
- Geography: capitals, flags, landmarks
- Movies: quotes, scenes, trivia
- History: dates, events, people
- Science: facts, inventions, discoveries
- Pop culture: music, celebrities, trends

---

## 📊 File Structure Overview

```
quiz-video-generator/
├── app/                    # Backend code
├── static/                 # CSS, JavaScript, images
├── templates/              # HTML
├── sample_data/            # Example quizzes
├── videos/                 # Generated videos
├── deployment/             # Server configs
├── app.py                  # Start here
├── test_app.py            # Test setup
└── *.md                    # Documentation
```

---

## 🎉 You're All Set!

Just run:
```bash
python3 app.py
```

And visit: **http://localhost:5000**

**Create amazing quiz videos!** 🎬✨

---

*For detailed information, see README.md*  
*For deployment, see DEPLOYMENT.md*  
*For technical details, see PROJECT_OVERVIEW.md*
