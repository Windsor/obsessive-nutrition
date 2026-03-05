import os
import subprocess
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.profile_utils import get_resolution

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import geopandas as gpd


class GeographyMapGenerator:
    """Generate 'Guess the Country' quiz videos — improved v2."""

    # Colors
    BG_COLOR_TOP = (24, 36, 66)       # Deeper navy
    BG_COLOR_BOT = (14, 22, 48)
    OCEAN_COLOR = '#0F1A2E'
    LAND_FILL = '#2A3A5C'             # Subtle blue-grey instead of white
    LAND_BORDER = '#4A5A7A'
    HIGHLIGHT_COLOR = '#00E5A0'       # Vivid green
    HIGHLIGHT_BORDER = '#00B87A'
    CORRECT_COLOR = (0, 229, 160)     # Green for correct answer
    WRONG_COLOR = (120, 130, 160)     # Muted for wrong options
    ACCENT_COLOR = (255, 107, 74)     # Coral accent
    TIMER_GREEN = (0, 229, 160)
    TIMER_YELLOW = (255, 204, 0)
    TIMER_RED = (255, 59, 48)

    def __init__(self, video_format='16:9', profile=None):
        self.profile = profile
        if profile:
            self.width, self.height = get_resolution(profile.get('aspect_ratio', '16:9'))
            self.video_format = profile.get('aspect_ratio', '16:9')
        else:
            self.video_format = video_format
            if video_format == '9:16':
                self.width, self.height = 1080, 1920
            elif video_format == '1:1':
                self.width, self.height = 1080, 1080
            else:
                self.width, self.height = 1920, 1080
        self.fps = 30
        self.frames_dir = 'frames'
        self.videos_dir = 'videos'
        os.makedirs(self.frames_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)

        # Scale factor for responsive sizing
        self.scale = self.width / 1920

        # Load fonts
        self.font_title = self._get_font(int(52 * self.scale))
        self.font_subtitle = self._get_font(int(24 * self.scale))
        self.font_counter = self._get_font(int(32 * self.scale))
        self.font_option = self._get_font(int(36 * self.scale))
        self.font_option_small = self._get_font(int(28 * self.scale))
        self.font_answer = self._get_font(int(64 * self.scale))
        self.font_timer = self._get_font(int(28 * self.scale))

        # Load shapefile
        shapefile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ne_110m_admin_0_countries.shp')
        self.world = gpd.read_file(shapefile_path)

        # Build country name list for generating wrong options
        self.all_country_names = list(self.world['NAME'].dropna().unique())

    def _get_font(self, size):
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    pass
        return ImageFont.load_default()

    def _create_gradient_bg(self):
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        for y in range(self.height):
            ratio = y / self.height
            r = int(self.BG_COLOR_TOP[0] + (self.BG_COLOR_BOT[0] - self.BG_COLOR_TOP[0]) * ratio)
            g = int(self.BG_COLOR_TOP[1] + (self.BG_COLOR_BOT[1] - self.BG_COLOR_TOP[1]) * ratio)
            b = int(self.BG_COLOR_TOP[2] + (self.BG_COLOR_BOT[2] - self.BG_COLOR_TOP[2]) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        return img

    def _render_map(self, highlight_code=None, zoom_bounds=None):
        map_top = int(110 * self.scale)
        map_bottom = int(200 * self.scale) if self.video_format != '9:16' else int(350 * self.scale)
        map_h = self.height - map_top - map_bottom
        map_w = self.width

        dpi = 100
        fig, ax = plt.subplots(1, 1, figsize=(map_w / dpi, map_h / dpi), dpi=dpi)
        fig.patch.set_facecolor(self.OCEAN_COLOR)
        ax.set_facecolor(self.OCEAN_COLOR)

        # Draw countries with subtle fill and visible borders
        self.world.plot(ax=ax, color=self.LAND_FILL, edgecolor=self.LAND_BORDER, linewidth=0.8)

        # Highlight target
        if highlight_code:
            target = self.world[
                (self.world['ISO_A3_EH'] == highlight_code) |
                (self.world['ISO_A3'] == highlight_code) |
                (self.world['ADM0_A3'] == highlight_code)
            ]
            if not target.empty:
                target.plot(ax=ax, color=self.HIGHLIGHT_COLOR, edgecolor=self.HIGHLIGHT_BORDER, linewidth=2.0)

        if zoom_bounds:
            ax.set_xlim(zoom_bounds[0], zoom_bounds[2])
            ax.set_ylim(zoom_bounds[1], zoom_bounds[3])
        else:
            ax.set_xlim(-180, 180)
            ax.set_ylim(-60, 85)

        ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        map_img = Image.frombuffer('RGBA', fig.canvas.get_width_height(), buf, 'raw', 'RGBA', 0, 1)
        plt.close(fig)
        return map_img.convert('RGB')

    def _get_country_bounds(self, country_code, padding_factor=2.5):
        target = self.world[
            (self.world['ISO_A3_EH'] == country_code) |
            (self.world['ISO_A3'] == country_code) |
            (self.world['ADM0_A3'] == country_code)
        ]
        if target.empty:
            return None

        bounds = target.total_bounds
        w = bounds[2] - bounds[0]
        h = bounds[3] - bounds[1]
        cx = (bounds[0] + bounds[2]) / 2
        cy = (bounds[1] + bounds[3]) / 2
        w = max(w, 10)
        h = max(h, 8)
        pw = w * padding_factor / 2
        ph = h * padding_factor / 2

        map_bottom = int(200 * self.scale) if self.video_format != '9:16' else int(350 * self.scale)
        map_aspect = self.width / (self.height - int(110 * self.scale) - map_bottom)
        box_aspect = pw / ph
        if box_aspect > map_aspect:
            ph = pw / map_aspect
        else:
            pw = ph * map_aspect
        return (cx - pw, cy - ph, cx + pw, cy + ph)

    def _generate_options(self, correct_name, num_options=4):
        """Generate plausible multiple choice options — mostly from same region/subregion."""
        correct_row = self.world[self.world['NAME'] == correct_name]
        region = subregion = None
        if not correct_row.empty:
            region = correct_row.iloc[0].get('REGION_UN', None)
            subregion = correct_row.iloc[0].get('SUBREGION', None)

        distractors = []
        
        # Priority 1: Same subregion (most plausible)
        if subregion:
            sub_countries = self.world[
                (self.world['SUBREGION'] == subregion) & (self.world['NAME'] != correct_name)
            ]['NAME'].tolist()
            if sub_countries:
                distractors.extend(random.sample(sub_countries, min(2, len(sub_countries))))

        # Priority 2: Same region
        if region and len(distractors) < num_options - 1:
            regional = self.world[
                (self.world['REGION_UN'] == region) & 
                (self.world['NAME'] != correct_name) &
                (~self.world['NAME'].isin(distractors))
            ]['NAME'].tolist()
            needed = num_options - 1 - len(distractors)
            if regional:
                distractors.extend(random.sample(regional, min(needed, len(regional))))

        # Priority 3: Adjacent regions (still somewhat plausible)
        if len(distractors) < num_options - 1:
            all_others = [n for n in self.all_country_names if n != correct_name and n not in distractors]
            needed = num_options - 1 - len(distractors)
            if all_others:
                distractors.extend(random.sample(all_others, min(needed, len(all_others))))

        options = distractors[:num_options - 1] + [correct_name]
        random.shuffle(options)
        correct_idx = options.index(correct_name)
        labels = ['A', 'B', 'C', 'D']
        return options, correct_idx, labels

    def _draw_rounded_rect(self, draw, xy, radius, fill, outline=None, width=0):
        """Draw a rounded rectangle."""
        x1, y1, x2, y2 = xy
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    def _draw_header(self, img, question_num, total_questions):
        draw = ImageDraw.Draw(img)
        s = self.scale

        # Header bar background
        header_h = int(90 * s)
        header_bg = Image.new('RGBA', (self.width, header_h), (0, 0, 0, 80))
        img_rgba = img.convert('RGBA')
        img_rgba.paste(header_bg, (0, 0), header_bg)
        img_result = img_rgba.convert('RGB')
        draw = ImageDraw.Draw(img_result)

        # Title
        title = "GUESS THE COUNTRY"
        bbox = draw.textbbox((0, 0), title, font=self.font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((self.width - tw) // 2, int(20 * s)), title, font=self.font_title, fill=(255, 255, 255))

        # Question counter — clean pill badge on right
        counter_text = f"{question_num} / {total_questions}"
        cbbox = draw.textbbox((0, 0), counter_text, font=self.font_counter)
        cw = cbbox[2] - cbbox[0]
        ch = cbbox[3] - cbbox[1]
        pill_w = cw + int(32 * s)
        pill_h = ch + int(16 * s)
        pill_x = self.width - pill_w - int(30 * s)
        pill_y = int(25 * s)

        self._draw_rounded_rect(draw, [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                                radius=pill_h // 2, fill=(0, 229, 160), outline=None)
        draw.text((pill_x + int(16 * s), pill_y + int(6 * s)), counter_text,
                  font=self.font_counter, fill=(14, 22, 48))

        return img_result

    def _draw_options(self, img, options, labels, correct_idx=None, show_answer=False):
        """Draw multiple choice options at the bottom."""
        draw = ImageDraw.Draw(img)
        s = self.scale

        num = len(options)
        if self.video_format == '9:16':
            # Stack vertically for portrait
            option_h = int(72 * s)
            gap = int(14 * s)
            total_h = num * option_h + (num - 1) * gap
            start_y = self.height - total_h - int(100 * s)
            margin_x = int(40 * s)
            option_w = self.width - 2 * margin_x

            for i, (opt, lbl) in enumerate(zip(options, labels)):
                y = start_y + i * (option_h + gap)
                if show_answer and i == correct_idx:
                    bg_color = (0, 229, 160)
                    text_color = (14, 22, 48)
                    border_color = (0, 200, 140)
                elif show_answer:
                    bg_color = (35, 45, 75)
                    text_color = (130, 140, 170)
                    border_color = (50, 60, 90)
                else:
                    bg_color = (30, 42, 74)
                    text_color = (240, 245, 255)
                    border_color = (70, 85, 120)

                self._draw_rounded_rect(draw, [margin_x, y, margin_x + option_w, y + option_h],
                                        radius=int(12 * s), fill=bg_color, outline=border_color, width=2)

                # Label circle
                cx = margin_x + int(35 * s)
                cy = y + option_h // 2
                cr = int(18 * s)
                draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=border_color)
                lbl_bbox = draw.textbbox((0, 0), lbl, font=self.font_option_small)
                lbl_w = lbl_bbox[2] - lbl_bbox[0]
                draw.text((cx - lbl_w // 2, cy - int(14 * s)), lbl, font=self.font_option_small, fill=(255, 255, 255))

                # Option text
                font = self.font_option if len(opt) < 20 else self.font_option_small
                draw.text((margin_x + int(65 * s), y + int(12 * s)), opt, font=font, fill=text_color)
        else:
            # 2x2 grid for landscape
            option_h = int(55 * s)
            gap_x = int(20 * s)
            gap_y = int(12 * s)
            margin_x = int(40 * s)
            option_w = (self.width - 2 * margin_x - gap_x) // 2
            start_y = self.height - 2 * option_h - gap_y - int(50 * s)

            for i, (opt, lbl) in enumerate(zip(options, labels)):
                col = i % 2
                row = i // 2
                x = margin_x + col * (option_w + gap_x)
                y = start_y + row * (option_h + gap_y)

                if show_answer and i == correct_idx:
                    bg_color = (0, 229, 160)
                    text_color = (14, 22, 48)
                    border_color = (0, 200, 140)
                elif show_answer:
                    bg_color = (30, 38, 65)
                    text_color = (80, 90, 120)
                    border_color = (40, 50, 80)
                else:
                    bg_color = (30, 42, 74)
                    text_color = (220, 230, 255)
                    border_color = (60, 75, 110)

                self._draw_rounded_rect(draw, [x, y, x + option_w, y + option_h],
                                        radius=int(12 * s), fill=bg_color, outline=border_color, width=2)

                # Label
                lbl_x = x + int(20 * s)
                lbl_y = y + int(10 * s)
                cr = int(18 * s)
                draw.ellipse([lbl_x, lbl_y, lbl_x + 2 * cr, lbl_y + 2 * cr], fill=border_color)
                lbl_bbox = draw.textbbox((0, 0), lbl, font=self.font_option_small)
                lbl_w = lbl_bbox[2] - lbl_bbox[0]
                draw.text((lbl_x + cr - lbl_w // 2, lbl_y + int(4 * s)), lbl,
                          font=self.font_option_small, fill=(255, 255, 255))

                # Text
                font = self.font_option if len(opt) < 16 else self.font_option_small
                draw.text((lbl_x + 2 * cr + int(12 * s), y + int(12 * s)), opt, font=font, fill=text_color)

        return img

    def _draw_timer_bar(self, img, progress, seconds_left=None):
        draw = ImageDraw.Draw(img)
        s = self.scale
        bar_height = int(14 * s)
        options_area = int(180 * s) if self.video_format != '9:16' else int(320 * s)
        bar_y = self.height - options_area - int(30 * s)
        bar_width = int(self.width * 0.85)
        bar_x = (self.width - bar_width) // 2
        filled_width = int(bar_width * progress)

        # Background
        self._draw_rounded_rect(draw, [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                                radius=bar_height // 2, fill=(30, 40, 60))

        # Filled portion with color based on progress
        if filled_width > bar_height:
            if progress > 0.5:
                color = self.TIMER_GREEN
            elif progress > 0.25:
                color = self.TIMER_YELLOW
            else:
                color = self.TIMER_RED
            self._draw_rounded_rect(draw, [bar_x, bar_y, bar_x + filled_width, bar_y + bar_height],
                                    radius=bar_height // 2, fill=color)

        # Seconds text
        if seconds_left is not None:
            timer_text = f"{seconds_left}s"
            bbox = draw.textbbox((0, 0), timer_text, font=self.font_timer)
            tw = bbox[2] - bbox[0]
            draw.text((bar_x + bar_width + int(10 * s), bar_y - int(4 * s)),
                      timer_text, font=self.font_timer, fill=(180, 190, 210))

        return img

    def _compose_frame(self, map_img, question_num, total_questions,
                       timer_progress=None, seconds_left=None,
                       options=None, labels=None, correct_idx=None, show_answer=False):
        bg = self._create_gradient_bg()
        s = self.scale

        # Map area
        map_top = int(90 * s)
        map_bottom = int(200 * s) if self.video_format != '9:16' else int(350 * s)
        map_h = self.height - map_top - map_bottom
        resized_map = map_img.resize((self.width, map_h), Image.LANCZOS)
        bg.paste(resized_map, (0, map_top))

        # Header
        bg = self._draw_header(bg, question_num, total_questions)

        # Timer
        if timer_progress is not None:
            bg = self._draw_timer_bar(bg, timer_progress, seconds_left)

        # Options
        if options:
            bg = self._draw_options(bg, options, labels, correct_idx, show_answer)

        return bg

    def _write_static_frames(self, img, duration_secs, frame_counter):
        num_frames = int(round(duration_secs * self.fps))
        path = os.path.join(self.frames_dir, f'_geo_static_{frame_counter}.png')
        img.save(path, quality=95)
        for i in range(num_frames):
            fp = os.path.join(self.frames_dir, f'frame_{frame_counter + i:06d}.png')
            os.link(path, fp)
        os.remove(path)
        return frame_counter + num_frames

    def _cleanup_frames(self):
        for f in os.listdir(self.frames_dir):
            if f.startswith('frame_') or f.startswith('_geo_'):
                os.remove(os.path.join(self.frames_dir, f))

    def generate_video(self, questions, quiz_name, output_filename,
                       countdown_seconds=8, theme_music_path=None,
                       show_intro=True, show_outro=True,
                       question_display_seconds=1.0, answer_display_seconds=3.0,
                       question_start_label=1,
                       intro_video_path=None, outro_video_path=None):
        self._cleanup_frames()
        frame_counter = 0
        total_q = len(questions)

        print(f"[GeographyMap v2] Rendering {total_q} questions...")

        for idx, q in enumerate(questions):
            q_num = question_start_label + idx
            country_code = q.get('country_code', q.get('question_text', '')).upper()
            country_name = q.get('country_name', q.get('answer_text', ''))
            print(f"  [{q_num}/{total_q}] {country_name} ({country_code})")

            # Generate multiple choice options
            options, correct_idx, labels = self._generate_options(country_name)

            # Phase 1: Zoomed map with options, countdown timer
            zoom_bounds = self._get_country_bounds(country_code)
            zoomed_map = self._render_map(highlight_code=country_code, zoom_bounds=zoom_bounds)

            total_countdown_frames = int(countdown_seconds * self.fps)
            for f_idx in range(total_countdown_frames):
                progress = 1.0 - (f_idx / total_countdown_frames)
                secs = int(countdown_seconds * progress) + 1
                frame = self._compose_frame(
                    zoomed_map, q_num, total_q,
                    timer_progress=progress, seconds_left=secs,
                    options=options, labels=labels
                )
                fp = os.path.join(self.frames_dir, f'frame_{frame_counter:06d}.png')
                frame.save(fp, quality=95)
                frame_counter += 1

            # Phase 2: Answer reveal (highlight correct option)
            answer_frame = self._compose_frame(
                zoomed_map, q_num, total_q,
                timer_progress=0.0, seconds_left=0,
                options=options, labels=labels, correct_idx=correct_idx, show_answer=True
            )
            frame_counter = self._write_static_frames(answer_frame, answer_display_seconds, frame_counter)

        # Compile video
        output_path = os.path.join(self.videos_dir, output_filename)
        total_duration = frame_counter / self.fps

        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-framerate', str(self.fps),
            '-i', os.path.join(self.frames_dir, 'frame_%06d.png'),
        ]

        if theme_music_path and os.path.exists(theme_music_path):
            ffmpeg_cmd.extend(['-i', theme_music_path])
        else:
            ffmpeg_cmd.extend(['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo'])

        ffmpeg_cmd.extend([
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            output_path,
        ])

        print(f"[GeographyMap v2] Compiling video ({frame_counter} frames, {total_duration:.1f}s)...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr[-500:]}")

        self._cleanup_frames()
        print(f"[GeographyMap v2] Done! {output_path} ({total_duration:.1f}s)")
        return output_path, total_duration
