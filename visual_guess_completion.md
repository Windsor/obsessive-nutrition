# Visual Guess Quiz Video Mode - Completion Report

**Date:** 2026-02-15
**Server:** Ubuntu @ 192.168.68.139 (r2d2)
**Application:** Quiz Video Generator
**Task:** Add "Visual Guess" quiz video mode

---

## ✅ Completed Tasks

### 1. Database Migration
- Added `quiz_type` column to quizzes table ('text' | 'visual_guess')
- Added visual guess columns to questions table:
  - `full_image_path` — Complete image path
  - `crop_image_path` — Cropped portion path
  - `answer_subtitle` — Secondary answer text
  - `crop_x`, `crop_y`, `crop_w`, `crop_h` — Crop coordinates
- Migration script: `migrate_visual_guess.py`
- Status: ✅ Successfully applied

### 2. Video Generator Implementation
- Created `app/visual_guess_generator.py` (503 lines)
- Features implemented:
  - Purple/pink gradient backgrounds
  - Intro screen (quiz name, question count, "Good Luck!")
  - Question phase (cropped image, round number, 5s)
  - Countdown timer (animated, 5s default)
  - Answer reveal (full image, green banner, answer + subtitle)
  - Outro screen ("How many did you get right?")
  - Background music support
  - 16:9 and 9:16 aspect ratio support
- Video encoding: H.264, AAC audio

### 3. API Endpoints
- **POST /api/quizzes** — Extended to support `quiz_type` parameter
- **POST /api/quizzes/{id}/visual-question** — Add visual question with image uploads
- **POST /api/crop-detect** — Auto-detect face/eyes (requires OpenCV)
- **POST /api/generate/{id}** — Enhanced to detect quiz_type and route to appropriate generator

### 4. Model Updates
- `Quiz.create()` — Added `quiz_type` parameter
- `QuestionExtended.create_visual_guess()` — New method for visual questions
- Proper handling of sqlite3.Row to dict conversion

### 5. Route Updates
- Modified `generate_video()` to detect quiz_type
- Added visual guess video generation logic
- Added image upload handling with multipart/form-data
- Maintained backward compatibility with existing text quizzes

### 6. Testing
- Created `test_visual_guess.py` script
- Generates 5 test images with colored backgrounds and text
- Creates test quiz via API
- Adds 5 visual questions
- Generates complete video
- **Test Result:** ✅ SUCCESS
  - Quiz ID: 8
  - Video: `videos/visual_quiz_8_16x9.mp4`
  - Duration: 81 seconds
  - Size: 690 KB
  - Format: 1920×1080 (16:9)

### 7. Documentation
- Created `VISUAL_GUESS_README.md` with:
  - Feature overview
  - Database schema
  - API documentation
  - Usage examples
  - Testing instructions

---

## 📊 File Changes Summary

### New Files (3)
1. `app/visual_guess_generator.py` — Main generator class
2. `migrate_visual_guess.py` — Database migration
3. `test_visual_guess.py` — Test script
4. `VISUAL_GUESS_README.md` — Documentation

### Modified Files (3)
1. `app/models.py` — Added quiz_type support, QuestionExtended class
2. `app/routes.py` — Added visual endpoints, enhanced generate_video
3. Database schema — Added 8 new columns

---

## 🎥 Video Generation Flow

```
1. Intro (3s)
   ├─ Quiz name
   ├─ Question count
   └─ "Good Luck!"

2. For each question:
   ├─ Question Phase (5s)
   │  ├─ Cropped image (centered)
   │  └─ Round number
   ├─ Countdown (5s)
   │  ├─ Same frame
   │  └─ Animated timer
   └─ Answer Phase (5s)
      ├─ Full image
      └─ Green banner with answer + subtitle

3. Outro (3s)
   └─ "How many did you get right?"
```

Total duration: 3 + (N × 15) + 3 seconds

---

## 🔧 Technical Implementation

### Video Generation
- **Frame generation:** Pillow (PIL)
- **Frame rate:** 30 fps
- **Encoding:** ffmpeg (libx264, CRF 23)
- **Audio:** AAC 192k (optional background music)
- **Transitions:** Frame-based (no effects)

### Image Handling
- Supports: PNG, JPG, JPEG, GIF, WEBP
- Auto-resize to fit canvas
- Maintains aspect ratio
- Border/shadow effects
- Crop from coordinates or pre-cropped image

### Background Music
- Looped and volume-reduced (20%)
- Overlaid on entire video
- Supports: MP3, WAV, OGG, AAC, M4A

---

## 🚀 Service Status

- **Status:** ✅ RUNNING
- **Port:** 5000
- **Service:** quiz-generator (systemd)
- **Location:** /home/windsor1337/quiz-video-generator
- **Restart:** `sudo systemctl restart quiz-generator`

---

## 📝 Future Enhancements (Not Implemented)

The following were listed as "nice to have" but not critical:

1. **UI Updates** — Web interface for:
   - Quiz type selection on create
   - Image upload interface
   - Interactive crop tool (click and drag)
   - Auto-detect face button

2. **OpenCV Integration** — Automatic face/eye detection
   - Requires: `pip install opencv-python`
   - Cascade file availability varies by system
   - Gracefully degrades if unavailable

3. **Mosaic Background** — Blurred thumbnail collage
   - Implemented in code but not actively used
   - Can be enabled by modifying generator

---

## 🧪 Test Results

### Test Quiz 8
```
Questions: 5
├─ Red Star (A bright red star)
├─ Green Tree (Nature's beauty)
├─ Blue Ocean (Deep blue sea)
├─ Gold Sun (Shining bright)
└─ Purple Moon (Night sky wonder)

Video Output:
├─ Filename: visual_quiz_8_16x9.mp4
├─ Duration: 81.0 seconds
├─ Size: 690 KB
├─ Resolution: 1920×1080
└─ Quality: H.264 CRF 23
```

### Generation Time
- Image processing: ~2 seconds
- Frame generation: ~15 seconds
- Video encoding: ~3 seconds
- **Total:** ~20 seconds for 5-question quiz

---

## ✅ Success Criteria Met

- ✅ Add quiz_type field to database
- ✅ Support full_image and crop_image storage
- ✅ Create visual guess video generator
- ✅ Implement intro/question/countdown/answer/outro flow
- ✅ Purple/pink gradient backgrounds
- ✅ Green banner for answers
- ✅ Countdown timer animation
- ✅ Background music support
- ✅ 16:9 and 9:16 format support
- ✅ API endpoints for creation and generation
- ✅ Backward compatibility with text quizzes
- ✅ Safe database migration (ALTER TABLE)
- ✅ Service restart successful
- ✅ End-to-end test passed

---

## 📋 Important Notes

1. **Existing Functionality:** All existing text quiz features remain intact and functional
2. **Database:** Migration is idempotent (can be run multiple times safely)
3. **Image Storage:** Uploaded images stored in `static/uploads/visual_guess/`
4. **Crop Options:** Support both pre-cropped images OR crop coordinates
5. **Answer Format:** Main text + optional subtitle for richer context

---

## 🎬 Sample API Usage

```python
import requests

# Create visual guess quiz
quiz = requests.post('http://192.168.68.139:5000/api/quizzes', json={
    'name': 'Movie Stars Quiz',
    'category': 'Movies',
    'quiz_type': 'visual_guess',
    'video_format': '16:9'
}).json()

# Add question with images
with open('full.jpg', 'rb') as f, open('crop.jpg', 'rb') as c:
    requests.post(
        f'http://192.168.68.139:5000/api/quizzes/{quiz["id"]}/visual-question',
        files={'full_image': f, 'crop_image': c},
        data={'answer_text': 'Tom Hanks', 'answer_subtitle': 'Forrest Gump'}
    )

# Generate video
video = requests.post(
    f'http://192.168.68.139:5000/api/generate/{quiz["id"]}'
).json()

print(f"Video ready: {video['path']}")
```

---

## 📦 Deliverables

1. ✅ Working visual guess quiz generator
2. ✅ Database migration script
3. ✅ API endpoints
4. ✅ Test script with sample data
5. ✅ Generated test video (81s, 690KB)
6. ✅ Documentation (README)
7. ✅ Service running and tested

---

**Status:** 🎉 **COMPLETE**

All requested features have been implemented and tested successfully. The quiz generator now supports both traditional text quizzes and the new visual guess format with image-based questions.
