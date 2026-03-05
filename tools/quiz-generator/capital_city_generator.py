import os
import random
from PIL import ImageDraw
from PIL import Image
from app.geography_map_generator import GeographyMapGenerator


# Capital cities database — curated list of countries and their capitals
CAPITALS_DB = {
    # Europe
    "France": "Paris", "Germany": "Berlin", "Spain": "Madrid", "Portugal": "Lisbon",
    "Italy": "Rome", "United Kingdom": "London", "Greece": "Athens", "Norway": "Oslo",
    "Sweden": "Stockholm", "Finland": "Helsinki", "Denmark": "Copenhagen",
    "Poland": "Warsaw", "Czech Republic": "Prague", "Austria": "Vienna",
    "Switzerland": "Bern", "Netherlands": "Amsterdam", "Belgium": "Brussels",
    "Ireland": "Dublin", "Romania": "Bucharest", "Hungary": "Budapest",
    "Bulgaria": "Sofia", "Croatia": "Zagreb", "Serbia": "Belgrade",
    "Slovakia": "Bratislava", "Slovenia": "Ljubljana", "Estonia": "Tallinn",
    "Latvia": "Riga", "Lithuania": "Vilnius", "Albania": "Tirana",
    "North Macedonia": "Skopje", "Montenegro": "Podgorica", "Bosnia and Herzegovina": "Sarajevo",
    "Moldova": "Chișinău", "Belarus": "Minsk", "Ukraine": "Kyiv",
    "Iceland": "Reykjavik", "Luxembourg": "Luxembourg City", "Malta": "Valletta",
    "Cyprus": "Nicosia", "Turkey": "Ankara",
    # Asia
    "Japan": "Tokyo", "China": "Beijing", "India": "New Delhi", "South Korea": "Seoul",
    "Thailand": "Bangkok", "Vietnam": "Hanoi", "Indonesia": "Jakarta",
    "Philippines": "Manila", "Malaysia": "Kuala Lumpur", "Myanmar": "Naypyidaw",
    "Pakistan": "Islamabad", "Bangladesh": "Dhaka", "Nepal": "Kathmandu",
    "Mongolia": "Ulaanbaatar", "Laos": "Vientiane", "Cambodia": "Phnom Penh",
    "Sri Lanka": "Sri Jayawardenepura Kotte", "Kazakhstan": "Astana",
    "Uzbekistan": "Tashkent", "Turkmenistan": "Ashgabat", "Tajikistan": "Dushanbe",
    "Kyrgyzstan": "Bishkek", "Afghanistan": "Kabul", "Iraq": "Baghdad",
    "Iran": "Tehran", "Saudi Arabia": "Riyadh", "Israel": "Jerusalem",
    "Jordan": "Amman", "Lebanon": "Beirut", "Syria": "Damascus",
    "Yemen": "Sana'a", "Oman": "Muscat", "United Arab Emirates": "Abu Dhabi",
    "Qatar": "Doha", "Kuwait": "Kuwait City", "Bahrain": "Manama",
    # Africa
    "Egypt": "Cairo", "South Africa": "Pretoria", "Nigeria": "Abuja",
    "Kenya": "Nairobi", "Morocco": "Rabat", "Ethiopia": "Addis Ababa",
    "Tanzania": "Dodoma", "Ghana": "Accra", "Algeria": "Algiers",
    "Madagascar": "Antananarivo", "Mozambique": "Maputo", "Angola": "Luanda",
    "Cameroon": "Yaoundé", "Senegal": "Dakar", "Tunisia": "Tunis",
    "Libya": "Tripoli", "Sudan": "Khartoum", "Uganda": "Kampala",
    "Zimbabwe": "Harare", "Zambia": "Lusaka", "Namibia": "Windhoek",
    "Botswana": "Gaborone", "Malawi": "Lilongwe", "Rwanda": "Kigali",
    "Burkina Faso": "Ouagadougou", "Mali": "Bamako", "Niger": "Niamey",
    "Chad": "N'Djamena", "Ivory Coast": "Yamoussoukro",
    "Democratic Republic of the Congo": "Kinshasa", "Republic of the Congo": "Brazzaville",
    "Gabon": "Libreville", "Togo": "Lomé", "Benin": "Porto-Novo",
    "Sierra Leone": "Freetown", "Liberia": "Monrovia", "Guinea": "Conakry",
    "Eritrea": "Asmara", "Djibouti": "Djibouti", "Somalia": "Mogadishu",
    # Americas
    "United States of America": "Washington, D.C.", "Canada": "Ottawa",
    "Mexico": "Mexico City", "Brazil": "Brasília", "Argentina": "Buenos Aires",
    "Chile": "Santiago", "Colombia": "Bogotá", "Peru": "Lima",
    "Venezuela": "Caracas", "Ecuador": "Quito", "Bolivia": "Sucre",
    "Paraguay": "Asunción", "Uruguay": "Montevideo", "Guyana": "Georgetown",
    "Suriname": "Paramaribo", "Cuba": "Havana", "Jamaica": "Kingston",
    "Haiti": "Port-au-Prince", "Dominican Republic": "Santo Domingo",
    "Guatemala": "Guatemala City", "Honduras": "Tegucigalpa",
    "El Salvador": "San Salvador", "Nicaragua": "Managua",
    "Costa Rica": "San José", "Panama": "Panama City",
    "Trinidad and Tobago": "Port of Spain",
    # Oceania
    "Australia": "Canberra", "New Zealand": "Wellington",
    "Papua New Guinea": "Port Moresby", "Fiji": "Suva",
    # Other
    "Russia": "Moscow",
}

# All capitals for generating wrong options
ALL_CAPITALS = list(set(CAPITALS_DB.values()))


class CapitalCityGenerator(GeographyMapGenerator):
    """Generate 'Guess the Capital' quiz videos.

    Shows a country highlighted on the map, displays the country name,
    and asks the viewer to guess the capital city from 4 options.
    """

    # Use amber/gold accent to distinguish from green geography quizzes
    ACCENT_COLOR = (255, 193, 7)  # Amber
    CORRECT_COLOR = (255, 193, 7)

    def _generate_capital_options(self, correct_capital, country_name, num_options=4):
        """Generate plausible wrong capital options from the same region."""
        # Get region of the country
        correct_row = self.world[self.world['NAME'] == country_name]
        region = subregion = None
        if not correct_row.empty:
            region = correct_row.iloc[0].get('REGION_UN', None)
            subregion = correct_row.iloc[0].get('SUBREGION', None)

        # Gather regional capitals as distractors
        distractors = []

        if subregion:
            sub_countries = self.world[
                (self.world['SUBREGION'] == subregion) & (self.world['NAME'] != country_name)
            ]['NAME'].tolist()
            sub_capitals = [CAPITALS_DB[c] for c in sub_countries if c in CAPITALS_DB and CAPITALS_DB[c] != correct_capital]
            if sub_capitals:
                distractors.extend(random.sample(sub_capitals, min(2, len(sub_capitals))))

        if region and len(distractors) < num_options - 1:
            reg_countries = self.world[
                (self.world['REGION_UN'] == region) & (self.world['NAME'] != country_name)
            ]['NAME'].tolist()
            reg_capitals = [CAPITALS_DB[c] for c in reg_countries
                           if c in CAPITALS_DB and CAPITALS_DB[c] != correct_capital and CAPITALS_DB[c] not in distractors]
            needed = num_options - 1 - len(distractors)
            if reg_capitals:
                distractors.extend(random.sample(reg_capitals, min(needed, len(reg_capitals))))

        if len(distractors) < num_options - 1:
            remaining = [c for c in ALL_CAPITALS if c != correct_capital and c not in distractors]
            needed = num_options - 1 - len(distractors)
            distractors.extend(random.sample(remaining, min(needed, len(remaining))))

        options = distractors[:num_options - 1] + [correct_capital]
        random.shuffle(options)
        correct_idx = options.index(correct_capital)
        labels = ['A', 'B', 'C', 'D']
        return options, correct_idx, labels

    def _draw_header(self, img, question_num, total_questions, country_name=None):
        """Draw header with 'GUESS THE CAPITAL' and country name."""
        draw = ImageDraw.Draw(img)
        s = self.scale

        # Header bar background
        header_h = int(90 * s)
        from PIL import Image as PILImage
        header_bg = PILImage.new('RGBA', (self.width, header_h), (0, 0, 0, 80))
        img_rgba = img.convert('RGBA')
        img_rgba.paste(header_bg, (0, 0), header_bg)
        img_result = img_rgba.convert('RGB')
        draw = ImageDraw.Draw(img_result)

        # Title
        title = "GUESS THE CAPITAL"
        bbox = draw.textbbox((0, 0), title, font=self.font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((self.width - tw) // 2, int(20 * s)), title, font=self.font_title, fill=(255, 255, 255))

        # Country name subtitle
        if country_name:
            sub_bbox = draw.textbbox((0, 0), country_name, font=self.font_counter)
            sw = sub_bbox[2] - sub_bbox[0]
            # Amber pill with country name on left side
            pill_w = sw + int(32 * s)
            pill_h = int(36 * s)
            pill_x = int(30 * s)
            pill_y = int(28 * s)
            self._draw_rounded_rect(draw, [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                                    radius=pill_h // 2, fill=(255, 193, 7))
            draw.text((pill_x + int(16 * s), pill_y + int(4 * s)), country_name,
                      font=self.font_counter, fill=(14, 22, 48))

        # Question counter pill on right
        counter_text = f"{question_num} / {total_questions}"
        cbbox = draw.textbbox((0, 0), counter_text, font=self.font_counter)
        cw = cbbox[2] - cbbox[0]
        ch = cbbox[3] - cbbox[1]
        pill_w = cw + int(32 * s)
        pill_h = ch + int(16 * s)
        pill_x = self.width - pill_w - int(30 * s)
        pill_y = int(25 * s)
        self._draw_rounded_rect(draw, [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                                radius=pill_h // 2, fill=(0, 229, 160))
        draw.text((pill_x + int(16 * s), pill_y + int(6 * s)), counter_text,
                  font=self.font_counter, fill=(14, 22, 48))

        return img_result

    def _compose_frame(self, map_img, question_num, total_questions,
                       timer_progress=None, seconds_left=None,
                       options=None, labels=None, correct_idx=None, show_answer=False,
                       country_name=None):
        bg = self._create_gradient_bg()
        s = self.scale

        # Map area
        map_top = int(90 * s)
        map_bottom = int(200 * s) if self.video_format != '9:16' else int(350 * s)
        map_h = self.height - map_top - map_bottom
        resized_map = map_img.resize((self.width, map_h), Image.LANCZOS)
        bg.paste(resized_map, (0, map_top))

        # Header with country name
        bg = self._draw_header(bg, question_num, total_questions, country_name=country_name)

        # Timer
        if timer_progress is not None:
            bg = self._draw_timer_bar(bg, timer_progress, seconds_left)

        # Options (capitals instead of country names)
        if options:
            bg = self._draw_options(bg, options, labels, correct_idx, show_answer)

        return bg

    def generate_video(self, questions, quiz_name, output_filename,
                       countdown_seconds=8, theme_music_path=None,
                       show_intro=True, show_outro=True,
                       question_display_seconds=1.0, answer_display_seconds=3.0,
                       question_start_label=1,
                       intro_video_path=None, outro_video_path=None):
        self._cleanup_frames()
        frame_counter = 0
        total_q = len(questions)

        print(f"[CapitalCity] Rendering {total_q} questions...")

        for idx, q in enumerate(questions):
            q_num = question_start_label + idx
            country_code = q.get('country_code', q.get('question_text', '')).upper()
            country_name = q.get('country_name', q.get('answer_text', ''))
            capital = q.get('capital', CAPITALS_DB.get(country_name, '???'))
            print(f"  [{q_num}/{total_q}] {country_name} → {capital}")

            # Generate capital options
            options, correct_idx, labels = self._generate_capital_options(capital, country_name)

            # Phase 1: Zoomed map with capital options, countdown timer
            zoom_bounds = self._get_country_bounds(country_code)
            zoomed_map = self._render_map(highlight_code=country_code, zoom_bounds=zoom_bounds)

            total_countdown_frames = int(countdown_seconds * self.fps)
            for f_idx in range(total_countdown_frames):
                progress = 1.0 - (f_idx / total_countdown_frames)
                secs = int(countdown_seconds * progress) + 1
                frame = self._compose_frame(
                    zoomed_map, q_num, total_q,
                    timer_progress=progress, seconds_left=secs,
                    options=options, labels=labels,
                    country_name=country_name
                )
                fp = os.path.join(self.frames_dir, f'frame_{frame_counter:06d}.png')
                frame.save(fp, quality=95)
                frame_counter += 1

            # Phase 2: Answer reveal
            answer_frame = self._compose_frame(
                zoomed_map, q_num, total_q,
                timer_progress=0.0, seconds_left=0,
                options=options, labels=labels, correct_idx=correct_idx, show_answer=True,
                country_name=country_name
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
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k', '-shortest',
            output_path,
        ])

        print(f"[CapitalCity] Compiling video ({frame_counter} frames, {total_duration:.1f}s)...")
        import subprocess
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr[-500:]}")

        self._cleanup_frames()
        print(f"[CapitalCity] Done! {output_path} ({total_duration:.1f}s)")
        return output_path, total_duration
