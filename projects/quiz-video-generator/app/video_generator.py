import os
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from elevenlabs.client import ElevenLabs
import math

class VideoGenerator:
    def __init__(self, video_format='16:9', elevenlabs_api_key=None, voice_id=None):
        """
        Initialize video generator
        
        Args:
            video_format: '16:9' for horizontal or '9:16' for vertical
            elevenlabs_api_key: API key for ElevenLabs
            voice_id: Voice ID for TTS
        """
        self.video_format = video_format
        self.elevenlabs_api_key = elevenlabs_api_key
        self.voice_id = voice_id
        
        # Set dimensions based on format
        if video_format == '9:16':
            self.width, self.height = 1080, 1920  # Vertical (TikTok/Shorts)
        else:
            self.width, self.height = 1920, 1080  # Horizontal (YouTube)
        
        self.fps = 30
        self.frames_dir = 'frames'
        self.videos_dir = 'videos'
        
        os.makedirs(self.frames_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
        
        # Try to load fonts
        self.font_large = self._get_font(80)
        self.font_medium = self._get_font(50)
        self.font_small = self._get_font(35)
    
    def _get_font(self, size):
        """Get font, fallback to default if not found"""
        font_paths = [
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    pass
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def generate_tts(self, text, output_path):
        """Generate speech using ElevenLabs"""
        if not self.elevenlabs_api_key:
            print(f"No API key, skipping TTS for: {text}")
            return None
        
        try:
            client = ElevenLabs(api_key=self.elevenlabs_api_key)
            audio_generator = client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id or "EXAVITQu4vr4xnSDxMaL",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            # Write the audio bytes to file
            with open(output_path, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            print(f"TTS generated: {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path
        except Exception as e:
            print(f"TTS error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_gradient_background(self, color1=(20, 20, 40), color2=(60, 20, 80)):
        """Create a gradient background"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
    
    def draw_text_with_outline(self, draw, text, position, font, fill=(255, 255, 255), outline=(0, 0, 0), outline_width=3):
        """Draw text with outline for better visibility"""
        x, y = position
        
        # Draw outline
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline)
        
        # Draw main text
        draw.text(position, text, font=font, fill=fill)
    
    def draw_circular_countdown(self, img, seconds_remaining, total_seconds=5):
        """Draw a circular countdown timer"""
        draw = ImageDraw.Draw(img)
        
        # Center position
        center_x = self.width // 2
        center_y = self.height // 2
        radius = 150
        
        # Calculate angle (full circle = 360 degrees)
        progress = seconds_remaining / total_seconds
        angle = 360 * progress
        
        # Draw background circle
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=(100, 100, 100),
            width=15
        )
        
        # Draw progress arc
        if angle > 0:
            draw.arc(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                start=-90,
                end=-90 + angle,
                fill=(0, 255, 150),
                width=15
            )
        
        # Draw number in center
        number_text = str(int(seconds_remaining))
        bbox = draw.textbbox((0, 0), number_text, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        self.draw_text_with_outline(
            draw,
            number_text,
            (center_x - text_width // 2, center_y - text_height // 2),
            self.font_large,
            fill=(255, 255, 255)
        )
        
        return img
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Use textbbox instead of deprecated textsize
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_question_frame(self, question_text, question_number, total_questions, image_path=None, choices=None):
        """Create a frame showing the question with optional multiple choice"""
        img = self.create_gradient_background((30, 30, 60), (60, 30, 90))
        draw = ImageDraw.Draw(img)
        
        # Draw question number
        header_text = f"Question {question_number}/{total_questions}"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_medium)
        header_width = bbox[2] - bbox[0]
        
        self.draw_text_with_outline(
            draw,
            header_text,
            (self.width // 2 - header_width // 2, 60),
            self.font_medium,
            fill=(255, 200, 100)
        )
        
        # Draw question text (wrapped)
        max_text_width = self.width - 200
        lines = self.wrap_text(question_text, self.font_large, max_text_width)
        
        y_offset = 180 if choices else (300 if not image_path else 200)
        line_spacing = 90
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_large)
            line_width = bbox[2] - bbox[0]
            self.draw_text_with_outline(
                draw,
                line,
                (self.width // 2 - line_width // 2, y_offset),
                self.font_large
            )
            y_offset += line_spacing
        
        # Draw multiple choice options
        if choices:
            y_offset += 30
            labels = ['A', 'B', 'C', 'D', 'E', 'F']
            option_colors = [
                (230, 80, 80),    # Red
                (80, 150, 230),   # Blue
                (80, 200, 80),    # Green
                (230, 180, 50),   # Yellow
                (180, 100, 230),  # Purple
                (230, 130, 50),   # Orange
            ]
            
            # Layout: 2 columns for 4 options, single column for others
            if len(choices) == 4:
                # 2x2 grid layout
                box_width = (self.width - 240) // 2
                box_height = 100
                padding = 20
                
                for i, choice in enumerate(choices[:4]):
                    col = i % 2
                    row = i // 2
                    
                    x = 100 + col * (box_width + 40)
                    y = y_offset + row * (box_height + padding)
                    
                    # Draw option box
                    color = option_colors[i % len(option_colors)]
                    draw.rounded_rectangle(
                        [x, y, x + box_width, y + box_height],
                        radius=15,
                        fill=(*color, 180),
                        outline=(255, 255, 255, 100),
                        width=2
                    )
                    
                    # Draw label + text
                    option_text = f"{labels[i]}.  {choice}"
                    opt_lines = self.wrap_text(option_text, self.font_small, box_width - 40)
                    text_y = y + (box_height - len(opt_lines) * 40) // 2
                    for line in opt_lines:
                        self.draw_text_with_outline(
                            draw, line, (x + 20, text_y),
                            self.font_small, fill=(255, 255, 255), outline_width=2
                        )
                        text_y += 40
            else:
                # Single column
                for i, choice in enumerate(choices[:6]):
                    box_x = 100
                    box_y = y_offset + i * 80
                    box_width = self.width - 200
                    
                    color = option_colors[i % len(option_colors)]
                    draw.rounded_rectangle(
                        [box_x, box_y, box_x + box_width, box_y + 65],
                        radius=12,
                        fill=(*color, 180),
                        outline=(255, 255, 255, 100),
                        width=2
                    )
                    
                    option_text = f"{labels[i]}.  {choice}"
                    self.draw_text_with_outline(
                        draw, option_text, (box_x + 20, box_y + 14),
                        self.font_small, fill=(255, 255, 255), outline_width=2
                    )
        
        # Add image if provided (only for non-MC or if space allows)
        if image_path and os.path.exists(image_path) and not choices:
            try:
                question_img = Image.open(image_path)
                max_img_size = (self.width - 400, 500)
                question_img.thumbnail(max_img_size, Image.Resampling.LANCZOS)
                img_x = (self.width - question_img.width) // 2
                img_y = y_offset + 50
                img.paste(question_img, (img_x, img_y))
            except Exception as e:
                print(f"Error loading image: {e}")
        
        return img
    
    def _overlay_countdown(self, img, seconds_remaining, total_seconds=5):
        """Overlay a countdown timer on an existing frame (bottom-right corner)"""
        draw = ImageDraw.Draw(img)
        
        # Position in bottom-right
        radius = 70
        margin = 40
        center_x = self.width - radius - margin
        center_y = self.height - radius - margin
        
        # Semi-transparent background circle
        draw.ellipse(
            [center_x - radius - 10, center_y - radius - 10, center_x + radius + 10, center_y + radius + 10],
            fill=(0, 0, 0, 200)
        )
        
        # Progress arc
        progress = seconds_remaining / total_seconds
        angle = 360 * progress
        
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=(80, 80, 80),
            width=8
        )
        
        if angle > 0:
            draw.arc(
                [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                start=-90,
                end=-90 + angle,
                fill=(0, 255, 150),
                width=8
            )
        
        # Number
        number_text = str(int(seconds_remaining))
        bbox = draw.textbbox((0, 0), number_text, font=self.font_medium)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        self.draw_text_with_outline(
            draw, number_text,
            (center_x - text_width // 2, center_y - text_height // 2),
            self.font_medium, fill=(255, 255, 255)
        )

    def create_countdown_frame(self, seconds_remaining):
        """Create a countdown frame"""
        img = self.create_gradient_background((40, 20, 60), (70, 30, 100))
        
        # Draw circular countdown
        img = self.draw_circular_countdown(img, seconds_remaining)
        
        return img
    
    def create_answer_frame(self, answer_text, question_number, total_questions, choices=None, correct_index=None):
        """Create a frame showing the answer"""
        img = self.create_gradient_background((20, 60, 20), (30, 100, 30))
        draw = ImageDraw.Draw(img)
        
        # Draw "Answer!" text
        header_text = "Answer!"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_large)
        header_width = bbox[2] - bbox[0]
        
        self.draw_text_with_outline(
            draw,
            header_text,
            (self.width // 2 - header_width // 2, 150),
            self.font_large,
            fill=(100, 255, 100)
        )
        
        # Draw answer text (wrapped)
        max_text_width = self.width - 200
        lines = self.wrap_text(answer_text, self.font_large, max_text_width)
        
        y_offset = 400
        line_spacing = 100
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.font_large)
            line_width = bbox[2] - bbox[0]
            self.draw_text_with_outline(
                draw,
                line,
                (self.width // 2 - line_width // 2, y_offset),
                self.font_large,
                fill=(255, 255, 255)
            )
            y_offset += line_spacing
        
        return img
    
    def generate_video(self, questions, output_filename, countdown_seconds=5, use_tts=True):
        """
        Generate quiz video from questions
        
        Args:
            questions: List of dicts with 'question', 'answer', and optional 'image' keys
            output_filename: Output video filename
            countdown_seconds: Seconds for countdown timer
            use_tts: Whether to use text-to-speech
        
        Returns:
            Path to generated video
        """
        frame_count = 0
        audio_files = []
        
        total_questions = len(questions)
        
        for idx, q in enumerate(questions, 1):
            question_text = q['question']
            answer_text = q['answer']
            image_path = q.get('image')
            choices = q.get('choices')
            question_type = q.get('question_type', 'open')
            
            # Parse choices if it's a JSON string
            if isinstance(choices, str):
                try:
                    import json as _json
                    choices = _json.loads(choices)
                except:
                    choices = None
            
            # Generate TTS for question only (not choices)
            question_audio = None
            if use_tts and self.elevenlabs_api_key:
                audio_path = os.path.join(self.frames_dir, f'question_{idx}.mp3')
                question_audio = self.generate_tts(question_text, audio_path)
                if question_audio:
                    audio_files.append(question_audio)
            
            # Create question frame
            question_frame = self.create_question_frame(question_text, idx, total_questions, image_path, choices=choices)
            
            # Show question briefly without countdown (2 seconds to read)
            for i in range(self.fps * 2):
                question_frame.save(os.path.join(self.frames_dir, f'frame_{frame_count:05d}.png'))
                frame_count += 1
            
            # Countdown frames WITH question still visible
            for second in range(countdown_seconds, 0, -1):
                countdown_frame = question_frame.copy()
                self._overlay_countdown(countdown_frame, second, countdown_seconds)
                for i in range(self.fps):
                    countdown_frame.save(os.path.join(self.frames_dir, f'frame_{frame_count:05d}.png'))
                    frame_count += 1
            
            # Generate TTS for answer reveal
            answer_audio = None
            if use_tts and self.elevenlabs_api_key:
                audio_path = os.path.join(self.frames_dir, f'answer_{idx}.mp3')
                answer_audio = self.generate_tts(f"The answer is {answer_text}!", audio_path)
                if answer_audio:
                    audio_files.append(answer_audio)
            
            # Answer frame (4 seconds)
            answer_frame = self.create_answer_frame(answer_text, idx, total_questions)
            for i in range(self.fps * 4):
                answer_frame.save(os.path.join(self.frames_dir, f'frame_{frame_count:05d}.png'))
                frame_count += 1
        
        # Encode video with ffmpeg
        output_path = os.path.join(self.videos_dir, output_filename)
        video_only_path = os.path.join(self.videos_dir, f'_video_{output_filename}')
        
        # Step 1: Create video from frames
        ffmpeg_video = [
            'ffmpeg', '-y',
            '-framerate', str(self.fps),
            '-i', os.path.join(self.frames_dir, 'frame_%05d.png'),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            video_only_path
        ]
        
        try:
            subprocess.run(ffmpeg_video, check=True, capture_output=True)
            print(f"Video frames encoded: {video_only_path}")
            
            # Step 2: Concatenate TTS audio segments with silence gaps
            combined_audio_path = None
            if audio_files:
                combined_audio_path = os.path.join(self.frames_dir, 'combined_tts.mp3')
                self._combine_audio_segments(audio_files, combined_audio_path, questions, countdown_seconds)
            
            # Step 3: Mix audio with video
            bg_music_path = os.path.join('music', 'theme.mp3')
            has_bg_music = os.path.exists(bg_music_path)
            
            if combined_audio_path and os.path.exists(combined_audio_path) and has_bg_music:
                # Mix TTS + background music + video
                ffmpeg_mix = [
                    'ffmpeg', '-y',
                    '-i', video_only_path,
                    '-i', combined_audio_path,
                    '-i', bg_music_path,
                    '-filter_complex',
                    '[1:a]apad[tts];[2:a]aloop=loop=-1:size=2e+09,volume=0.15[bg];[tts][bg]amix=inputs=2:duration=shortest[aout]',
                    '-map', '0:v', '-map', '[aout]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest',
                    output_path
                ]
                subprocess.run(ffmpeg_mix, check=True, capture_output=True)
            elif combined_audio_path and os.path.exists(combined_audio_path):
                # TTS only, no background music
                ffmpeg_mix = [
                    'ffmpeg', '-y',
                    '-i', video_only_path,
                    '-i', combined_audio_path,
                    '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest',
                    output_path
                ]
                subprocess.run(ffmpeg_mix, check=True, capture_output=True)
            elif has_bg_music:
                # Background music only, no TTS
                ffmpeg_mix = [
                    'ffmpeg', '-y',
                    '-i', video_only_path,
                    '-i', bg_music_path,
                    '-filter_complex',
                    '[1:a]aloop=loop=-1:size=2e+09,volume=0.2[bg]',
                    '-map', '0:v', '-map', '[bg]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest',
                    output_path
                ]
                subprocess.run(ffmpeg_mix, check=True, capture_output=True)
            else:
                # No audio at all - just rename
                os.rename(video_only_path, output_path)
            
            print(f"Video generated: {output_path}")
            
            # Clean up
            for f in os.listdir(self.frames_dir):
                if f.endswith(('.png', '.mp3', '.wav')):
                    os.remove(os.path.join(self.frames_dir, f))
            if os.path.exists(video_only_path):
                os.remove(video_only_path)
            
            return output_path
        
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise
    
    def _combine_audio_segments(self, audio_files, output_path, questions, countdown_seconds):
        """Combine TTS audio segments with proper timing gaps using ffmpeg"""
        # Calculate timing for each segment
        # Each question: 2s read + countdown_seconds + 4s answer
        # TTS plays during question display and answer display
        
        # Build ffmpeg concat filter with silence padding
        filter_parts = []
        inputs = []
        
        for i, audio_file in enumerate(audio_files):
            if os.path.exists(audio_file):
                inputs.extend(['-i', audio_file])
        
        if not inputs:
            return
        
        # Simple concatenation with silence between segments
        n = len(inputs) // 2  # number of input files
        
        if n == 1:
            # Single file, just copy
            subprocess.run(['ffmpeg', '-y', '-i', inputs[1], '-c:a', 'libmp3lame', output_path],
                         check=True, capture_output=True)
            return
        
        # Generate silence gaps (countdown duration between question and answer TTS)
        silence_path = os.path.join(self.frames_dir, 'silence.mp3')
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i',
            f'anullsrc=r=44100:cl=stereo',
            '-t', str(countdown_seconds),
            '-c:a', 'libmp3lame', silence_path
        ], check=True, capture_output=True)
        
        # Build concat list file
        list_path = os.path.join(self.frames_dir, 'audio_list.txt')
        with open(list_path, 'w') as f:
            for i, audio_file in enumerate(audio_files):
                if os.path.exists(audio_file):
                    f.write(f"file '{os.path.abspath(audio_file)}'\n")
                    # Add silence after each segment except last
                    if i < len(audio_files) - 1:
                        f.write(f"file '{os.path.abspath(silence_path)}'\n")
        
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', list_path,
            '-c:a', 'libmp3lame', '-b:a', '192k',
            output_path
        ], check=True, capture_output=True)
