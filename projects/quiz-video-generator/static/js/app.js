// Global state
let currentQuizId = null;

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Load data for specific tabs
        if (tabName === 'quizzes') loadQuizzes();
        if (tabName === 'videos') loadVideos();
        if (tabName === 'settings') loadSettings();
    });
});

// Create quiz form
document.getElementById('create-quiz-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        name: document.getElementById('quiz-name').value,
        category: document.getElementById('quiz-category').value,
        difficulty: document.getElementById('quiz-difficulty').value,
        video_format: document.getElementById('quiz-format').value
    };
    
    try {
        const response = await fetch('/api/quizzes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Quiz created successfully!', 'success');
            document.getElementById('create-quiz-form').reset();
            
            // Switch to quizzes tab
            document.querySelector('[data-tab="quizzes"]').click();
        } else {
            showAlert(result.error || 'Failed to create quiz', 'error');
        }
    } catch (error) {
        showAlert('Error creating quiz', 'error');
        console.error(error);
    }
});

// Settings form
document.getElementById('settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const settings = {
        elevenlabs_api_key: document.getElementById('elevenlabs-key').value,
        elevenlabs_voice_id: document.getElementById('voice-id').value,
        countdown_duration: document.getElementById('countdown-duration').value,
        default_video_format: document.getElementById('default-format').value
    };
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            showAlert('Settings saved successfully!', 'success');
        } else {
            showAlert('Failed to save settings', 'error');
        }
    } catch (error) {
        showAlert('Error saving settings', 'error');
        console.error(error);
    }
});

// Load quizzes
async function loadQuizzes() {
    const container = document.getElementById('quiz-list');
    container.innerHTML = '<div class="loading">Loading quizzes</div>';
    
    try {
        const response = await fetch('/api/quizzes');
        const quizzes = await response.json();
        
        if (quizzes.length === 0) {
            container.innerHTML = '<p style="color: #888; text-align: center;">No quizzes yet. Create one to get started!</p>';
            return;
        }
        
        container.innerHTML = quizzes.map(quiz => `
            <div class="quiz-item">
                <h3>${quiz.name}</h3>
                <div class="meta">
                    ${quiz.category} • ${quiz.difficulty} • ${quiz.video_format}
                </div>
                <div class="actions">
                    <button onclick="editQuiz(${quiz.id})">Edit</button>
                    <button onclick="generateVideo(${quiz.id})">Generate Video</button>
                    <button class="danger" onclick="deleteQuiz(${quiz.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: #ff4444;">Error loading quizzes</p>';
        console.error(error);
    }
}

// Load videos
async function loadVideos() {
    const container = document.getElementById('video-list');
    container.innerHTML = '<div class="loading">Loading videos</div>';
    
    try {
        const response = await fetch('/api/videos');
        const videos = await response.json();
        
        if (videos.length === 0) {
            container.innerHTML = '<p style="color: #888; text-align: center;">No videos yet. Generate one from your quizzes!</p>';
            return;
        }
        
        container.innerHTML = videos.map(video => `
            <div class="video-item">
                <h3>${video.quiz_name}</h3>
                <div class="video-player">
                    <video controls preload="metadata" style="width:100%; max-height:400px; border-radius:8px; margin-bottom:10px;">
                        <source src="/api/videos/${video.id}/stream" type="video/mp4">
                        Your browser does not support video playback.
                    </video>
                </div>
                <div class="info">
                    ${video.category} • ${video.format}<br>
                    Duration: ~${Math.floor(video.duration / 60)}m ${video.duration % 60}s<br>
                    <small>${new Date(video.created_at).toLocaleString()}</small>
                </div>
                <div class="actions">
                    <button onclick="downloadVideo(${video.id})">⬇ Download</button>
                    <button class="danger" onclick="deleteVideo(${video.id})">🗑 Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: #ff4444;">Error loading videos</p>';
        console.error(error);
    }
}

// Load settings
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        
        document.getElementById('elevenlabs-key').value = settings.elevenlabs_api_key || '';
        document.getElementById('voice-id').value = settings.elevenlabs_voice_id || 'EXAVITQu4vr4xnSDxMaL';
        document.getElementById('countdown-duration').value = settings.countdown_duration || '5';
        document.getElementById('default-format').value = settings.default_video_format || '16:9';
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Edit quiz
async function editQuiz(quizId) {
    currentQuizId = quizId;
    
    try {
        const response = await fetch(`/api/quizzes/${quizId}`);
        const data = await response.json();
        
        const content = document.getElementById('edit-quiz-content');
        content.innerHTML = `
            <h3>${data.quiz.name}</h3>
            <p style="color: #888; margin-bottom: 20px;">
                ${data.quiz.category} • ${data.quiz.difficulty} • ${data.quiz.video_format}
            </p>
            
            <h4 style="color: #00d4ff; margin-bottom: 15px;">Questions (${data.questions.length})</h4>
            
            <div class="question-list" id="question-list">
                ${data.questions.map((q, idx) => {
                    let choicesHtml = '';
                    if (q.question_type === 'multiple_choice' && q.choices) {
                        let parsedChoices = typeof q.choices === 'string' ? JSON.parse(q.choices) : q.choices;
                        const labels = ['A', 'B', 'C', 'D', 'E', 'F'];
                        choicesHtml = '<div style="margin: 8px 0; padding-left: 15px;">' + 
                            parsedChoices.map((c, i) => 
                                `<div style="color: ${c === q.answer_text ? '#50c850' : '#aaa'}; margin: 2px 0;">${labels[i]}. ${c} ${c === q.answer_text ? '✓' : ''}</div>`
                            ).join('') + '</div>';
                    }
                    return `
                    <div class="question-item">
                        <div class="question-text">${idx + 1}. ${q.question_text} ${q.question_type === 'multiple_choice' ? '<span style="color:#00d4ff;font-size:12px;">[MC]</span>' : ''}</div>
                        ${choicesHtml}
                        <div class="answer-text">✓ ${q.answer_text}</div>
                        ${q.image_path ? `<img src="/${q.image_path}" style="max-width: 200px; margin: 10px 0; border-radius: 5px;">` : ''}
                        <div class="actions">
                            <button class="danger" onclick="deleteQuestion(${q.id})">Delete</button>
                        </div>
                    </div>
                `}).join('')}
            </div>
            
            <button onclick="openQuestionModal()" style="margin-top: 20px;">+ Add Question</button>
        `;
        
        document.getElementById('edit-modal').classList.add('active');
    } catch (error) {
        showAlert('Error loading quiz', 'error');
        console.error(error);
    }
}

// Close edit modal
function closeEditModal() {
    document.getElementById('edit-modal').classList.remove('active');
    currentQuizId = null;
}

// Open question modal
function openQuestionModal() {
    document.getElementById('question-modal').classList.add('active');
}

// Close question modal
function closeQuestionModal() {
    document.getElementById('question-modal').classList.remove('active');
    document.getElementById('add-question-form').reset();
    document.getElementById('image-preview').style.display = 'none';
}

// Image preview
document.getElementById('question-image').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('image-preview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

// Toggle multiple choice inputs
function toggleChoices() {
    const type = document.getElementById('question-type').value;
    const section = document.getElementById('choices-section');
    const hint = document.getElementById('answer-hint');
    section.style.display = type === 'multiple_choice' ? 'block' : 'none';
    hint.style.display = type === 'multiple_choice' ? 'block' : 'none';
}

// Add question form
document.getElementById('add-question-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentQuizId) return;
    
    let imagePath = null;
    
    // Upload image if provided
    const imageFile = document.getElementById('question-image').files[0];
    if (imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        
        try {
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (uploadResponse.ok) {
                const uploadResult = await uploadResponse.json();
                imagePath = uploadResult.path;
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    }
    
    // Gather choices if multiple choice
    const questionType = document.getElementById('question-type').value;
    let choices = null;
    if (questionType === 'multiple_choice') {
        choices = Array.from(document.querySelectorAll('.choice-input'))
            .map(input => input.value.trim())
            .filter(v => v.length > 0);
        if (choices.length < 2) {
            showAlert('Please provide at least 2 choices', 'error');
            return;
        }
    }
    
    // Add question
    const questionData = {
        question_text: document.getElementById('question-text').value,
        answer_text: document.getElementById('answer-text').value,
        question_type: questionType,
        choices: choices,
        image_path: imagePath
    };
    
    try {
        const response = await fetch(`/api/quizzes/${currentQuizId}/questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(questionData)
        });
        
        if (response.ok) {
            showAlert('Question added!', 'success');
            closeQuestionModal();
            editQuiz(currentQuizId); // Refresh the quiz view
        } else {
            showAlert('Failed to add question', 'error');
        }
    } catch (error) {
        showAlert('Error adding question', 'error');
        console.error(error);
    }
});

// Delete quiz
async function deleteQuiz(quizId) {
    if (!confirm('Are you sure you want to delete this quiz?')) return;
    
    try {
        const response = await fetch(`/api/quizzes/${quizId}`, { method: 'DELETE' });
        
        if (response.ok) {
            showAlert('Quiz deleted', 'success');
            loadQuizzes();
        } else {
            showAlert('Failed to delete quiz', 'error');
        }
    } catch (error) {
        showAlert('Error deleting quiz', 'error');
        console.error(error);
    }
}

// Delete question
async function deleteQuestion(questionId) {
    if (!confirm('Delete this question?')) return;
    
    try {
        const response = await fetch(`/api/questions/${questionId}`, { method: 'DELETE' });
        
        if (response.ok) {
            showAlert('Question deleted', 'success');
            editQuiz(currentQuizId);
        } else {
            showAlert('Failed to delete question', 'error');
        }
    } catch (error) {
        showAlert('Error deleting question', 'error');
        console.error(error);
    }
}

// Generate video
async function generateVideo(quizId) {
    if (!confirm('Generate video for this quiz? This may take a few minutes.')) return;
    
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Generating...';
    button.disabled = true;
    
    try {
        const response = await fetch(`/api/generate/${quizId}`, { method: 'POST' });
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Video generated successfully!', 'success');
            document.querySelector('[data-tab="videos"]').click();
        } else {
            showAlert(result.error || 'Failed to generate video', 'error');
        }
    } catch (error) {
        showAlert('Error generating video', 'error');
        console.error(error);
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
}

// Download video
function downloadVideo(videoId) {
    window.location.href = `/api/videos/${videoId}/download`;
}

// Delete video
async function deleteVideo(videoId) {
    if (!confirm('Delete this video?')) return;
    
    try {
        const response = await fetch(`/api/videos/${videoId}`, { method: 'DELETE' });
        
        if (response.ok) {
            showAlert('Video deleted', 'success');
            loadVideos();
        } else {
            showAlert('Failed to delete video', 'error');
        }
    } catch (error) {
        showAlert('Error deleting video', 'error');
        console.error(error);
    }
}

// Load sample data
async function loadSampleData(category) {
    const format = document.getElementById('quiz-format').value;
    
    try {
        const response = await fetch('/api/sample-data/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, video_format: format })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`Loaded ${category} quiz with ${result.message}!`, 'success');
            document.querySelector('[data-tab="quizzes"]').click();
        } else {
            showAlert(result.error || 'Failed to load sample data', 'error');
        }
    } catch (error) {
        showAlert('Error loading sample data', 'error');
        console.error(error);
    }
}

// Show alert
function showAlert(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.textContent = message;
    alert.style.position = 'fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.style.minWidth = '300px';
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// Initialize
loadQuizzes();
