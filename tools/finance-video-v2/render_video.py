#!/usr/bin/env python3
"""
Finance Video V2 — Visual Renderer (Enhanced)
Dark neon aesthetic with glassmorphism, kinetic typography, animated data cards,
scrolling ticker, crypto logos, and cinematic transitions.
"""

import json
import os
import sys
import shutil
import subprocess
import math
import random
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ── Config ──
FPS = 30
FRAME_DIR = os.path.expanduser("~/finance-video-generator/output-v2/frames")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_DIR = os.path.join(ASSETS_DIR, "logos")

PROFILES = {
    "shorts": {"w": 1080, "h": 1920},
    "landscape": {"w": 1920, "h": 1080},
}

# ── Color Palette (Dark Neon Finance — Refined) ──
BG_DARK = (6, 8, 16)
BG_GRADIENT_TOP = (8, 12, 28)
BG_GRADIENT_BOT = (4, 6, 12)
BG_CARD = (14, 18, 30, 200)  # RGBA for glassmorphism
BG_CARD_OPAQUE = (14, 18, 30)
CARD_BORDER = (40, 55, 90)
CARD_HIGHLIGHT = (50, 65, 100)
NEON_CYAN = (0, 210, 255)
NEON_BLUE = (56, 132, 244)
GOLD = (255, 193, 7)
GOLD_BRIGHT = (255, 215, 50)
GREEN = (16, 230, 110)
RED = (255, 55, 70)
WHITE = (235, 240, 252)
GRAY = (120, 130, 150)
DARK_GRAY = (50, 58, 78)
ACCENT_PURPLE = (140, 80, 255)
TICKER_BG = (10, 14, 24)

# ── Font helpers ──
FONT_CACHE = {}
LOGO_CACHE = {}

def get_font(size, bold=False, condensed=False):
    key = (size, bold, condensed)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    font_search = []
    if condensed:
        font_search.extend([
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ])
    if bold:
        font_search.extend([
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ])
    else:
        font_search.extend([
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ])
    for fp in font_search:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, size)
                FONT_CACHE[key] = font
                return font
            except:
                continue
    font = ImageFont.load_default()
    FONT_CACHE[key] = font
    return font


def get_logo(symbol, size=48):
    """Load and cache a crypto/stock logo, resized to size x size."""
    key = (symbol, size)
    if key in LOGO_CACHE:
        return LOGO_CACHE[key]
    path = os.path.join(LOGO_DIR, f"{symbol}.png")
    if os.path.exists(path):
        try:
            img = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
            LOGO_CACHE[key] = img
            return img
        except:
            pass
    LOGO_CACHE[key] = None
    return None


# ── Easing ──
def ease_out_cubic(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3

def ease_out_back(t):
    t = min(max(t, 0), 1)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

def ease_out_elastic(t):
    t = min(max(t, 0), 1)
    if t == 0 or t == 1:
        return t
    p = 0.3
    return pow(2, -10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1

def ease_in_out_quad(t):
    t = min(max(t, 0), 1)
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

def lerp_color(c1, c2, t):
    t = min(max(t, 0), 1)
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


class FinanceVideoV2:
    def __init__(self, profile="landscape"):
        self.profile = profile
        cfg = PROFILES[profile]
        self.w = cfg["w"]
        self.h = cfg["h"]
        self._bg_cache = None
        self._particle_seeds = None

    def _init_particles(self, count=80):
        """Pre-generate particle positions for consistency."""
        random.seed(42)
        self._particle_seeds = []
        for _ in range(count):
            self._particle_seeds.append({
                "x": random.random(),
                "y": random.random(),
                "speed_x": (random.random() - 0.5) * 0.3,
                "speed_y": random.random() * 0.2 + 0.1,
                "size": random.uniform(1.0, 3.5),
                "brightness": random.uniform(0.15, 0.6),
                "pulse_phase": random.random() * math.pi * 2,
                "color_type": random.choice(["cyan", "blue", "white", "gold"]),
            })

    def _make_bg(self):
        """Create a vertical gradient background with radial glow and vignette."""
        img = Image.new("RGB", (self.w, self.h))
        draw = ImageDraw.Draw(img)
        for y in range(self.h):
            t = y / self.h
            r = int(BG_GRADIENT_TOP[0] + (BG_GRADIENT_BOT[0] - BG_GRADIENT_TOP[0]) * t)
            g = int(BG_GRADIENT_TOP[1] + (BG_GRADIENT_BOT[1] - BG_GRADIENT_TOP[1]) * t)
            b = int(BG_GRADIENT_TOP[2] + (BG_GRADIENT_BOT[2] - BG_GRADIENT_TOP[2]) * t)
            center_boost = int(8 * math.sin(t * math.pi))
            draw.line((0, y, self.w, y), fill=(r, g, min(255, b + center_boost)))

        # Radial glow — soft blue/cyan bloom in upper-center for depth
        glow = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        cx, cy = self.w // 2, int(self.h * 0.3)
        max_r = int(self.w * 0.45)
        for radius in range(max_r, 0, -4):
            t = radius / max_r
            a = int(18 * (1 - t) ** 2)  # quadratic falloff
            glow_draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                              fill=(0, 80, 160, a))
        img_rgba = img.convert("RGBA")
        img_rgba = Image.alpha_composite(img_rgba, glow)

        # Vignette — darken edges
        vignette = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        vig_draw = ImageDraw.Draw(vignette)
        for border in range(0, min(self.w, self.h) // 3, 2):
            edge_t = 1 - (border / (min(self.w, self.h) / 3))
            a = int(50 * edge_t ** 2)
            vig_draw.rectangle(
                (border, border, self.w - 1 - border, self.h - 1 - border),
                outline=(0, 0, 0, a)
            )
        img_rgba = Image.alpha_composite(img_rgba, vignette)

        return img_rgba.convert("RGB")

    def _new_frame(self):
        """Create a new frame with gradient background."""
        if self._bg_cache is None:
            self._bg_cache = self._make_bg()
            self._init_particles()
        img = self._bg_cache.copy()
        draw = ImageDraw.Draw(img)
        return img, draw

    def _draw_particles(self, draw, frame_num, density_mult=1.0):
        """Draw animated floating particles with glow."""
        if not self._particle_seeds:
            self._init_particles()

        color_map = {
            "cyan": (0, 150, 200),
            "blue": (40, 90, 180),
            "white": (100, 110, 130),
            "gold": (160, 130, 20),
        }

        count = int(len(self._particle_seeds) * density_mult)
        for p in self._particle_seeds[:count]:
            t = frame_num / FPS
            x = (p["x"] * self.w + p["speed_x"] * t * 60) % self.w
            y = (p["y"] * self.h + p["speed_y"] * t * 30) % self.h

            # Pulsing brightness
            pulse = 0.6 + 0.4 * math.sin(t * 1.5 + p["pulse_phase"])
            brightness = p["brightness"] * pulse

            base = color_map[p["color_type"]]
            color = tuple(int(c * brightness) for c in base)
            size = p["size"]

            # Outer glow
            if size > 2:
                glow_size = size * 2.5
                glow_color = tuple(max(0, c // 4) for c in color)
                draw.ellipse(
                    (x - glow_size, y - glow_size, x + glow_size, y + glow_size),
                    fill=glow_color
                )
            draw.ellipse((x - size, y - size, x + size, y + size), fill=color)

    def _draw_grid(self, draw, frame_num, alpha=0.3):
        """Subtle animated grid."""
        grid_spacing = self.h // 14
        scroll = (frame_num * 0.15) % grid_spacing

        # Horizontal lines
        for y in range(0, self.h + grid_spacing, grid_spacing):
            yy = int(y + scroll)
            if 0 <= yy < self.h:
                # Fade grid lines near edges
                edge_fade = min(yy / 100, (self.h - yy) / 100, 1.0)
                a = int(12 * alpha * edge_fade)
                draw.line((0, yy, self.w, yy), fill=(a + 8, a + 12, a + 22), width=1)

        # Vertical lines (static)
        for x in range(0, self.w, grid_spacing):
            edge_fade = min(x / 100, (self.w - x) / 100, 1.0)
            a = int(10 * alpha * edge_fade)
            draw.line((x, 0, x, self.h), fill=(a + 6, a + 10, a + 18), width=1)

    def _draw_border_frame(self, draw, frame_num):
        """Animated neon border with glowing corners."""
        pulse = 0.6 + 0.4 * math.sin(frame_num * 0.04)
        base_a = int(35 * pulse)

        # Thin outer border
        border_color = (0, base_a + 25, base_a + 50)
        m = 6  # margin
        draw.line((m + 30, m, self.w - m - 30, m), fill=border_color, width=1)
        draw.line((m + 30, self.h - m, self.w - m - 30, self.h - m), fill=border_color, width=1)
        draw.line((m, m + 30, m, self.h - m - 30), fill=border_color, width=1)
        draw.line((self.w - m, m + 30, self.w - m, self.h - m - 30), fill=border_color, width=1)

        # Glowing corner brackets
        corner_len = 35
        bright = (0, min(255, base_a + 100), min(255, base_a + 160))
        corners = [
            (m + 30, m, 1, 1), (self.w - m - 30, m, -1, 1),
            (m + 30, self.h - m, 1, -1), (self.w - m - 30, self.h - m, -1, -1),
        ]
        for cx, cy, dx, dy in corners:
            draw.line((cx, cy, cx + corner_len * dx, cy), fill=bright, width=2)
            draw.line((cx, cy, cx, cy + corner_len * dy), fill=bright, width=2)
            # Corner glow dot
            draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=bright)

    def _draw_watermark(self, draw, frame_num=0):
        """Gold branding watermark with subtle animation."""
        font = get_font(int(self.w * 0.016), bold=True)
        text = "DAILY FINANCE PULSE"
        pulse = 0.85 + 0.15 * math.sin(frame_num * 0.03)
        color = tuple(int(c * pulse) for c in GOLD)

        x, y = 22, 16
        draw.text((x, y), text, fill=color, font=font)
        bbox = draw.textbbox((x, y), text, font=font)
        line_y = bbox[3] + 3
        draw.line((x, line_y, bbox[2], line_y), fill=color, width=2)

        # Small "LIVE" or date indicator
        now_str = datetime.now(timezone.utc).strftime("%b %d")
        font_small = get_font(int(self.w * 0.012))
        draw.text((x, line_y + 5), now_str, fill=GRAY, font=font_small)

    def _draw_full_bg(self, draw, frame_num, show_grid=True, show_particles=True,
                       show_border=True, show_watermark=True):
        """Draw all background layers."""
        if show_grid:
            self._draw_grid(draw, frame_num)
        if show_particles:
            self._draw_particles(draw, frame_num)
        if show_border:
            self._draw_border_frame(draw, frame_num)
        if show_watermark:
            self._draw_watermark(draw, frame_num)

    def _draw_glassmorphism_card(self, img, draw, x, y, w, h, radius=16, opacity=0.75,
                                  border_color=CARD_BORDER, highlight=True):
        """Draw a glassmorphism card with frosted glass effect."""
        # Create card overlay
        card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)

        # Semi-transparent fill
        fill_a = int(255 * opacity)
        cd.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius,
                             fill=(14, 18, 30, fill_a))
        # Border
        cd.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius,
                             outline=(*border_color, 180), width=1)

        # Top highlight (glass reflection)
        if highlight:
            for i in range(min(8, h // 4)):
                a = int(25 * (1 - i / 8))
                cd.rounded_rectangle((2, 2 + i, w - 3, 2 + i + 1), radius=max(0, radius - 2),
                                     fill=(255, 255, 255, a))

        # Composite onto main image
        # Convert main image to RGBA for compositing
        if img.mode != "RGBA":
            rgba = img.convert("RGBA")
        else:
            rgba = img
        rgba.paste(card, (x, y), card)
        # Copy back to RGB
        if img.mode == "RGB":
            img.paste(rgba.convert("RGB"))

    def _draw_glow_text(self, draw, pos, text, font, color, glow_radius=4, glow_strength=0.25):
        """Draw text with neon glow effect."""
        x, y = pos
        glow_color = tuple(min(255, int(c * glow_strength)) for c in color)
        for offset in range(glow_radius, 0, -1):
            fade = 1.0 - (offset / glow_radius)
            gc = tuple(int(c * fade) for c in glow_color)
            for dx in range(-offset, offset + 1, max(1, offset // 2)):
                for dy in range(-offset, offset + 1, max(1, offset // 2)):
                    if dx * dx + dy * dy <= offset * offset:
                        draw.text((x + dx, y + dy), text, fill=gc, font=font)
        draw.text((x, y), text, fill=color, font=font)

    def _draw_scrolling_ticker(self, draw, frame_num, ticker_items, y=None):
        """Draw an animated scrolling ticker strip at the bottom."""
        if not ticker_items:
            return

        if y is None:
            y = self.h - 38

        ticker_h = 32
        # Dark background strip
        draw.rectangle((0, y, self.w, y + ticker_h), fill=TICKER_BG)
        # Top border line
        draw.line((0, y, self.w, y), fill=(30, 40, 65), width=1)
        # Bottom border
        draw.line((0, y + ticker_h, self.w, y + ticker_h), fill=(20, 28, 48), width=1)

        font = get_font(int(self.w * 0.013), bold=True)
        sep_font = get_font(int(self.w * 0.011))

        # Build ticker text pieces
        pieces = []
        for item in ticker_items:
            name = item["name"]
            price = item["price"]
            change = item.get("change", 0)
            if change > 0:
                change_str = f"+{change:.1f}%"
                ccolor = GREEN
            elif change < 0:
                change_str = f"{change:.1f}%"
                ccolor = RED
            else:
                change_str = "0.0%"
                ccolor = GRAY
            pieces.append((name, price, change_str, ccolor))

        # Calculate total width of one cycle
        cycle_width = 0
        sep = "  •  "
        sep_w = draw.textlength(sep, font=sep_font)

        item_widths = []
        for name, price, cs, _ in pieces:
            txt = f"{name}  {price}  {cs}"
            w = draw.textlength(txt, font=font)
            item_widths.append(w)
            cycle_width += w + sep_w

        if cycle_width == 0:
            return

        # Scroll position
        speed = 1.2  # pixels per frame
        offset = -(frame_num * speed) % cycle_width

        # Draw ticker items (repeat to fill screen)
        tx = offset
        text_y = y + (ticker_h - 16) // 2
        reps = int(self.w / cycle_width) + 3

        for _ in range(reps):
            for i, (name, price, cs, ccolor) in enumerate(pieces):
                if tx > self.w + 100:
                    tx += item_widths[i] + sep_w
                    continue
                if tx + item_widths[i] < -100:
                    tx += item_widths[i] + sep_w
                    continue

                # Name
                draw.text((tx, text_y), name, fill=WHITE, font=font)
                name_w = draw.textlength(name, font=font)
                # Price
                draw.text((tx + name_w + 8, text_y), price, fill=GRAY, font=font)
                price_w = draw.textlength(price, font=font)
                # Change
                draw.text((tx + name_w + price_w + 16, text_y), cs, fill=ccolor, font=font)

                tx += item_widths[i] + sep_w
                # Separator dot
                if i < len(pieces) - 1:
                    draw.text((tx - sep_w, text_y), sep, fill=DARK_GRAY, font=sep_font)

    def _draw_data_card_v2(self, img, draw, y, name, price, change_str, change_color,
                            accent, frame_t, delay=0, width=None, logo_symbol=None,
                            sparkline_data=None):
        """Draw a glassmorphism data card with logo, accent, and animated entrance."""
        t = max(0, frame_t - delay)
        if t <= 0:
            return 0

        if width is None:
            width = int(self.w * 0.82)
        card_h = int(self.h * 0.105)
        x = (self.w - width) // 2
        pad = 20

        # Slide in from right with elastic overshoot
        progress = ease_out_cubic(min(t * 2.2, 1.0))
        x_off = int((1 - progress) * self.w * 0.6)
        alpha = min(1.0, t * 3.5)

        cx = x + x_off

        # Glassmorphism card background
        self._draw_glassmorphism_card(img, draw, cx, y, width, card_h, radius=14,
                                       opacity=0.7, border_color=CARD_BORDER)
        # Re-get draw after composite
        draw = ImageDraw.Draw(img)

        # Accent bar with glow
        bar_x = cx + 4
        bar_top = y + 12
        bar_bot = y + card_h - 12
        draw.rectangle((bar_x, bar_top, bar_x + 4, bar_bot), fill=accent)
        # Accent glow
        glow_a = tuple(min(255, c + 50) for c in accent)
        draw.rectangle((bar_x + 4, bar_top + 2, bar_x + 6, bar_bot - 2),
                       fill=tuple(c // 4 for c in glow_a))

        # Logo
        logo_size = int(card_h * 0.52)
        logo_x = cx + pad + 10
        logo_y = y + (card_h - logo_size) // 2
        logo = get_logo(logo_symbol or name, logo_size) if logo_symbol or name else None
        name_offset = 0

        if logo and img.mode == "RGB":
            # Paste logo with alpha
            temp = img.convert("RGBA")
            temp.paste(logo, (logo_x, logo_y), logo)
            img.paste(temp.convert("RGB"))
            draw = ImageDraw.Draw(img)
            name_offset = logo_size + 10

        # Layout zones (adjusted for sparkline between price and change)
        name_x = cx + pad + 12 + name_offset
        name_w = int(width * 0.25)
        price_zone_x = cx + int(width * 0.38)
        price_zone_w = int(width * 0.20)
        # Sparkline occupies ~12% at width*0.60
        change_zone_x = cx + int(width * 0.75)
        change_zone_w = int(width * 0.21)

        vy = y + card_h // 2

        # Name
        font_name = get_font(int(self.w * 0.024), bold=True)
        ncolor = tuple(int(c * alpha) for c in WHITE)
        display_name = name
        nbbox = draw.textbbox((0, 0), display_name, font=font_name)
        while nbbox[2] - nbbox[0] > name_w and len(display_name) > 5:
            display_name = display_name[:-2] + "."
            nbbox = draw.textbbox((0, 0), display_name, font=font_name)
        nh = nbbox[3] - nbbox[1]
        draw.text((name_x, vy - nh // 2 - 2), display_name, fill=ncolor, font=font_name)

        # Price (right-aligned, with subtle mono feel)
        font_price = get_font(int(self.w * 0.023))
        pbbox = draw.textbbox((0, 0), price, font=font_price)
        pw = pbbox[2] - pbbox[0]
        ph = pbbox[3] - pbbox[1]
        pcolor = tuple(int(c * alpha) for c in (195, 205, 222))
        draw.text((price_zone_x + price_zone_w - pw, vy - ph // 2 - 2),
                  price, fill=pcolor, font=font_price)

        # Change pill with gradient feel
        font_change = get_font(int(self.w * 0.019), bold=True)
        cbbox = draw.textbbox((0, 0), change_str, font=font_change)
        cw_text = cbbox[2] - cbbox[0]
        ch_text = cbbox[3] - cbbox[1]
        pill_w = cw_text + 24
        pill_h = ch_text + 12
        pill_x = change_zone_x + (change_zone_w - pill_w) // 2
        pill_y = vy - pill_h // 2

        # Pill background (dark version of change color)
        pill_bg = tuple(max(0, min(255, c // 6 + 8)) for c in change_color)
        draw.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
                               radius=8, fill=pill_bg)
        # Pill border
        pill_border = tuple(max(0, min(255, c // 3)) for c in change_color)
        draw.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
                               radius=8, outline=pill_border, width=1)

        # Arrow indicator
        arrow_font = get_font(int(self.w * 0.014))
        arrow = "▲" if change_color == GREEN else "▼" if change_color == RED else "–"
        arrow_color = tuple(int(c * alpha * 0.7) for c in change_color)

        ccolor = tuple(int(c * alpha) for c in change_color)
        # Center text in pill
        draw.text((pill_x + 8, pill_y + 3), arrow, fill=arrow_color, font=arrow_font)
        draw.text((pill_x + 18, pill_y + 4), change_str, fill=ccolor, font=font_change)

        # Sparkline (mini 7-day chart between price and change pill)
        if sparkline_data and len(sparkline_data) >= 2 and alpha > 0.3:
            spark_w = int(width * 0.12)
            spark_h = int(card_h * 0.45)
            spark_x = price_zone_x + price_zone_w + 8
            spark_y = y + (card_h - spark_h) // 2
            # Use the daily change color so sparkline matches the % pill
            spark_color = change_color
            self._draw_sparkline(draw, spark_x, spark_y, spark_w, spark_h,
                                 sparkline_data, color=spark_color, alpha=alpha)

        return card_h + 12, draw

    def _draw_kinetic_text(self, draw, text, y, frame_t, color=WHITE, size_mult=1.0,
                            effect="slam", delay=0, center=True, x=None):
        """Draw text with kinetic animation effect. Returns (height, text_width)."""
        t = max(0, frame_t - delay)
        if t <= 0:
            return 0

        font_size = int(self.w * 0.06 * size_mult)
        font = get_font(font_size, bold=True, condensed=True)

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        if x is None:
            x = (self.w - tw) // 2

        if effect == "slam":
            scale = ease_out_back(min(t * 3, 1.0))
            if scale < 0.01:
                return th
            anim_size = int(font_size * (0.4 + scale * 0.6))
            anim_font = get_font(anim_size, bold=True, condensed=True)
            abbox = draw.textbbox((0, 0), text, font=anim_font)
            atw = abbox[2] - abbox[0]
            ax = (self.w - atw) // 2 if center else x
            alpha = min(1.0, t * 4)
            acolor = tuple(int(c * alpha) for c in color)
            # Glow behind
            if alpha > 0.3:
                self._draw_glow_text(draw, (ax, y), text, anim_font, acolor,
                                     glow_radius=3, glow_strength=0.2)
            else:
                draw.text((ax, y), text, fill=acolor, font=anim_font)

        elif effect == "slide_left":
            progress = ease_out_cubic(min(t * 2.5, 1.0))
            offset = int((1 - progress) * self.w * 0.4)
            alpha = min(1.0, t * 3)
            acolor = tuple(int(c * alpha) for c in color)
            draw.text((x - offset, y), text, fill=acolor, font=font)

        elif effect == "slide_right":
            progress = ease_out_cubic(min(t * 2.5, 1.0))
            offset = int((1 - progress) * self.w * 0.4)
            alpha = min(1.0, t * 3)
            acolor = tuple(int(c * alpha) for c in color)
            draw.text((x + offset, y), text, fill=acolor, font=font)

        elif effect == "fade":
            alpha = ease_out_cubic(min(t * 2, 1.0))
            acolor = tuple(int(c * alpha) for c in color)
            if alpha > 0.5:
                self._draw_glow_text(draw, (x, y), text, font, acolor,
                                     glow_radius=2, glow_strength=0.15)
            else:
                draw.text((x, y), text, fill=acolor, font=font)

        elif effect == "typewriter":
            chars = int(len(text) * min(t * 3, 1.0))
            partial = text[:chars]
            draw.text((x, y), partial, fill=color, font=font)
            # Blinking cursor
            if int(t * 6) % 2 == 0 and chars < len(text):
                curs_x = x + draw.textlength(partial, font=font)
                draw.rectangle((curs_x + 2, y + 2, curs_x + 5, y + th - 2), fill=NEON_CYAN)

        return th + 10

    # ── Scene Renderers ──

    def _draw_pulse_line(self, draw, x, y, w, h, frame_num, color=NEON_CYAN, speed=2.0):
        """Draw an animated EKG/pulse line across a region."""
        points = []
        num_points = 60
        sweep_x = (frame_num * speed) % (num_points + 20)
        for i in range(num_points):
            px = x + int(i / num_points * w)
            # Create a heartbeat-like pattern
            phase = (i / num_points) * math.pi * 6
            # Main wave
            amplitude = h * 0.3
            base_y = y + h // 2
            # Heartbeat spikes at regular intervals
            spike = 0
            rel = i % 15
            if rel == 5:
                spike = -amplitude * 1.8
            elif rel == 6:
                spike = amplitude * 0.9
            elif rel == 7:
                spike = -amplitude * 0.4
            else:
                spike = math.sin(phase * 0.3) * amplitude * 0.08
            
            py = int(base_y + spike)
            # Fade based on sweep position
            dist = abs(i - sweep_x)
            if dist < 12:
                points.append((px, py, min(1.0, (12 - dist) / 12)))
            else:
                points.append((px, py, 0.15))
        
        # Draw the line segments
        for i in range(1, len(points)):
            x1, y1, a1 = points[i - 1]
            x2, y2, a2 = points[i]
            a = (a1 + a2) / 2
            seg_color = tuple(int(c * a) for c in color)
            draw.line((x1, y1, x2, y2), fill=seg_color, width=2)
            # Glow on bright segments
            if a > 0.5:
                glow_c = tuple(int(c * a * 0.3) for c in color)
                draw.line((x1, y1 - 1, x2, y2 - 1), fill=glow_c, width=1)
                draw.line((x1, y1 + 1, x2, y2 + 1), fill=glow_c, width=1)

    def _count_up_value(self, final_str, progress):
        """Animate a value string counting up from 0. Handles $XX,XXX.XX formats."""
        if progress >= 1.0:
            return final_str
        # Extract numeric part
        prefix = ""
        suffix = ""
        num_str = final_str
        for ch in final_str:
            if ch in '0123456789.,':
                break
            prefix += ch
            num_str = num_str[1:]
        # Find suffix
        clean = ""
        for ch in num_str:
            if ch in '0123456789.,':
                clean += ch
            else:
                suffix = num_str[len(clean):]
                break
        try:
            num_val = float(clean.replace(",", ""))
            current = num_val * progress
            # Format like original
            if "," in clean:
                formatted = f"{current:,.{clean.split('.')[-1].__len__() if '.' in clean else 0}f}"
                if '.' not in clean:
                    formatted = f"{int(current):,}"
            elif "." in clean:
                decimals = len(clean.split(".")[-1])
                formatted = f"{current:.{decimals}f}"
            else:
                formatted = str(int(current))
            return prefix + formatted + suffix
        except (ValueError, IndexError):
            return final_str if progress > 0.5 else ""

    def render_scene_title(self, date_str, num_frames=90, ticker_items=None):
        """Scene 1: Cinematic title card with stat cards and pulse line."""
        frames = []
        for f in range(num_frames):
            img, draw = self._new_frame()
            t = f / max(num_frames, 1)
            self._draw_full_bg(draw, f, show_watermark=False)

            cy = self.h * 0.18

            # "DAILY FINANCE PULSE" — big slam
            self._draw_kinetic_text(draw, "DAILY FINANCE PULSE", int(cy),
                                     t, color=GOLD, size_mult=1.0, effect="slam")

            # Decorative double line with diamond center
            if t > 0.15:
                line_t = ease_out_cubic(min((t - 0.15) * 3, 1.0))
                line_w = int(self.w * 0.32 * line_t)
                line_y = int(cy + self.h * 0.085)
                center = self.w // 2
                alpha_f = line_t
                gold_line = tuple(int(c * alpha_f) for c in GOLD)
                draw.line((center - line_w, line_y, center - 8, line_y), fill=gold_line, width=2)
                draw.line((center + 8, line_y, center + line_w, line_y), fill=gold_line, width=2)
                # Diamond accent
                d = 5
                diamond = [(center, line_y - d), (center + d, line_y),
                           (center, line_y + d), (center - d, line_y)]
                draw.polygon(diamond, fill=gold_line)
                # Thin second line
                draw.line((center - line_w * 0.6, line_y + 6, center + line_w * 0.6, line_y + 6),
                          fill=tuple(c // 2 for c in gold_line), width=1)

            # Date with day-of-week
            if t > 0.3:
                font_date = get_font(int(self.w * 0.020))
                alpha = ease_out_cubic(min((t - 0.3) * 3, 1.0))
                dcolor = tuple(int(c * alpha) for c in GRAY)
                dbbox = draw.textbbox((0, 0), date_str, font=font_date)
                dw = dbbox[2] - dbbox[0]
                draw.text(((self.w - dw) // 2, int(cy + self.h * 0.12)), date_str, fill=dcolor, font=font_date)

            # "MARKET RECAP"
            if t > 0.4:
                self._draw_kinetic_text(draw, "MARKET RECAP", int(cy + self.h * 0.18),
                                         t - 0.4, color=NEON_CYAN, size_mult=0.45, effect="slide_left")

            # Animated pulse line
            if t > 0.35:
                pulse_alpha = ease_out_cubic(min((t - 0.35) * 3, 1.0))
                pulse_y = int(cy + self.h * 0.27)
                pulse_color = tuple(int(c * pulse_alpha * 0.6) for c in NEON_CYAN)
                self._draw_pulse_line(draw, int(self.w * 0.1), pulse_y,
                                      int(self.w * 0.8), int(self.h * 0.06),
                                      f, color=pulse_color, speed=1.5)

            # Stat cards in glassmorphism boxes
            if t > 0.5:
                stats = getattr(self, '_title_stats', [
                    ("BITCOIN", "$64,109", RED),
                    ("S&P 500", "5,088.80", GREEN),
                    ("GOLD", "$2,035", GREEN),
                ])
                num_stats = len(stats)
                card_w = int(self.w * 0.22)
                card_h = int(self.h * 0.20)
                total_w = num_stats * card_w + (num_stats - 1) * 20
                start_x = (self.w - total_w) // 2
                stat_y = int(cy + self.h * 0.32)

                for i, stat_tuple in enumerate(stats):
                    label, val, color = stat_tuple[0], stat_tuple[1], stat_tuple[2]
                    change_pct_str = stat_tuple[3] if len(stat_tuple) > 3 else None
                    card_delay = 0.5 + i * 0.08
                    if t <= card_delay:
                        continue
                    card_t = (t - card_delay)
                    progress = ease_out_cubic(min(card_t * 2.5, 1.0))
                    
                    # Slide up + fade
                    y_off = int((1 - progress) * 30)
                    sa = progress

                    cx = start_x + i * (card_w + 20)
                    card_cy = stat_y + y_off

                    # Glassmorphism card
                    self._draw_glassmorphism_card(img, draw, cx, card_cy, card_w, card_h,
                                                  radius=12, opacity=0.6,
                                                  border_color=tuple(int(c * 0.4) for c in color))
                    draw = ImageDraw.Draw(img)

                    # Accent top bar
                    bar_color = tuple(int(c * sa) for c in color)
                    draw.rectangle((cx + 8, card_cy + 4, cx + card_w - 8, card_cy + 7),
                                   fill=bar_color)

                    # Logo (if crypto)
                    logo_map = {"BITCOIN": "BTC", "ETHEREUM": "ETH", "SOLANA": "SOL"}
                    logo_sym = logo_map.get(label.upper())
                    if logo_sym:
                        logo = get_logo(logo_sym, int(card_h * 0.3))
                        if logo:
                            lx = cx + card_w - int(card_h * 0.35) - 6
                            ly = card_cy + 14
                            if img.mode == "RGB":
                                temp = img.convert("RGBA")
                                # Apply alpha fade
                                faded = logo.copy()
                                r, g, b, a = faded.split()
                                a = a.point(lambda p: int(p * sa * 0.4))
                                faded = Image.merge("RGBA", (r, g, b, a))
                                temp.paste(faded, (lx, ly), faded)
                                img.paste(temp.convert("RGB"))
                                draw = ImageDraw.Draw(img)

                    # Label
                    font_label = get_font(int(self.w * 0.014))
                    lcolor = tuple(int(c * sa) for c in GRAY)
                    draw.text((cx + 14, card_cy + 16), label, fill=lcolor, font=font_label)

                    # Value — counting up animation
                    font_val = get_font(int(self.w * 0.026), bold=True)
                    count_progress = ease_out_cubic(min(card_t * 2.5, 1.0))
                    display_val = self._count_up_value(val, count_progress)
                    vcolor = tuple(int(c * sa) for c in color)
                    # Glow on the value
                    val_y = card_cy + int(card_h * 0.42)
                    if sa > 0.5:
                        self._draw_glow_text(draw, (cx + 14, val_y), display_val,
                                             font_val, vcolor, glow_radius=2, glow_strength=0.15)
                    else:
                        draw.text((cx + 14, val_y), display_val, fill=vcolor, font=font_val)

                    # Change percentage
                    font_arrow = get_font(int(self.w * 0.015))
                    arrow_y = card_cy + card_h - 30
                    if change_pct_str:
                        arrow_text = f"▲ {change_pct_str}" if color == GREEN else f"▼ {change_pct_str}"
                        draw.text((cx + 14, arrow_y), arrow_text,
                                  fill=tuple(int(c * sa * 0.7) for c in color), font=font_arrow)
                    elif color == GREEN:
                        draw.text((cx + 14, arrow_y), "▲ UP", 
                                  fill=tuple(int(c * sa * 0.7) for c in GREEN), font=font_arrow)
                    elif color == RED:
                        draw.text((cx + 14, arrow_y), "▼ DOWN",
                                  fill=tuple(int(c * sa * 0.7) for c in RED), font=font_arrow)

            # Scrolling ticker at bottom
            if ticker_items and t > 0.3:
                self._draw_scrolling_ticker(draw, f, ticker_items)

            frames.append(img)
        return frames

    def render_scene_overlay(self, overlay_text, subtitle, num_frames, frame_offset=0,
                              ticker_items=None, color=NEON_CYAN):
        """Section header overlay with dramatic entrance."""
        frames = []
        for f in range(num_frames):
            img, draw = self._new_frame()
            t = f / max(num_frames, 1)
            self._draw_full_bg(draw, f + frame_offset)

            cy = self.h * 0.32

            # Section title with glow
            font_size = int(self.w * 0.06)
            font = get_font(font_size, bold=True, condensed=True)
            bbox = draw.textbbox((0, 0), overlay_text, font=font)
            tw = bbox[2] - bbox[0]
            tx = (self.w - tw) // 2

            alpha = ease_out_cubic(min(t * 3.5, 1.0))
            if alpha > 0.01:
                main_color = tuple(int(c * alpha) for c in color)
                self._draw_glow_text(draw, (tx, int(cy)), overlay_text, font, main_color,
                                     glow_radius=5, glow_strength=0.3)

            # Expanding lines from center
            if t > 0.1:
                line_t = ease_out_cubic(min((t - 0.1) * 2.5, 1.0))
                line_w = int(self.w * 0.32 * line_t)
                line_y = int(cy + self.h * 0.075)
                center_x = self.w // 2
                la = int(alpha * 180)
                lc = tuple(min(255, int(c * alpha * 0.7)) for c in color)
                draw.line((center_x - line_w, line_y, center_x + line_w, line_y), fill=lc, width=2)
                draw.line((center_x - line_w // 2, line_y + 5, center_x + line_w // 2, line_y + 5),
                          fill=tuple(c // 3 for c in lc), width=1)

            # Subtitle
            if t > 0.2:
                font_sub = get_font(int(self.w * 0.022))
                sub_alpha = ease_out_cubic(min((t - 0.2) * 3, 1.0))
                scolor = tuple(int(c * sub_alpha) for c in (170, 180, 200))
                sbbox = draw.textbbox((0, 0), subtitle, font=font_sub)
                sw = sbbox[2] - sbbox[0]
                draw.text(((self.w - sw) // 2, int(cy + self.h * 0.10)), subtitle, fill=scolor, font=font_sub)

            if ticker_items:
                self._draw_scrolling_ticker(draw, f + frame_offset, ticker_items)

            frames.append(img)
        return frames

    def render_scene_data(self, section_title, items, num_frames, frame_offset=0,
                           ticker_items=None):
        """Render animated data cards with glassmorphism."""
        frames = []
        for f in range(num_frames):
            img, draw = self._new_frame()
            t = f / num_frames
            self._draw_full_bg(draw, f + frame_offset)

            # Section header
            font_header = get_font(int(self.w * 0.026), bold=True)
            hbbox = draw.textbbox((0, 0), section_title, font=font_header)
            hw = hbbox[2] - hbbox[0]
            alpha = min(1.0, t * 4)
            hcolor = tuple(int(c * alpha) for c in NEON_CYAN)
            draw.text(((self.w - hw) // 2, int(self.h * 0.07)), section_title, fill=hcolor, font=font_header)

            # Animated underline
            line_y = int(self.h * 0.07) + hbbox[3] - hbbox[1] + 6
            line_w = int(hw * ease_out_cubic(min(t * 3, 1.0)))
            cx = self.w // 2
            draw.line((cx - line_w // 2, line_y, cx + line_w // 2, line_y), fill=NEON_CYAN, width=2)

            # Data cards
            y = int(self.h * 0.15)
            max_items = min(len(items), 7 if self.profile == "shorts" else 6)
            accents = [NEON_CYAN, NEON_BLUE, GOLD, GREEN, ACCENT_PURPLE, RED]

            for i, item in enumerate(items[:max_items]):
                delay = 0.08 + i * 0.07
                accent = accents[i % len(accents)]

                change_val = item.get("change", 0)
                if change_val > 0:
                    change_str = f"+{change_val:.2f}%"
                    change_color = GREEN
                elif change_val < 0:
                    change_str = f"{change_val:.2f}%"
                    change_color = RED
                else:
                    change_str = "0.00%"
                    change_color = GRAY

                result = self._draw_data_card_v2(
                    img, draw, y, item["name"], item["price"],
                    change_str, change_color, accent, t, delay=delay,
                    logo_symbol=item.get("symbol"),
                    sparkline_data=item.get("sparkline")
                )
                if isinstance(result, tuple):
                    card_h, draw = result
                else:
                    card_h = result
                y += card_h

            if ticker_items:
                self._draw_scrolling_ticker(draw, f + frame_offset, ticker_items)

            frames.append(img)
        return frames

    def _draw_sparkline(self, draw, x, y, w, h, values, color=NEON_CYAN, alpha=1.0):
        """Draw a mini sparkline chart. values = list of floats (price history)."""
        if not values or len(values) < 2:
            return
        min_v = min(values)
        max_v = max(values)
        v_range = max_v - min_v if max_v != min_v else 1.0

        points = []
        for i, v in enumerate(values):
            px = x + int(i / (len(values) - 1) * w)
            py = y + h - int((v - min_v) / v_range * h)
            points.append((px, py))

        # Draw area fill (gradient-like) under the line
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            # Fill down to bottom
            for xi in range(x1, x2 + 1):
                if x2 == x1:
                    yi = y1
                else:
                    yi = y1 + (y2 - y1) * (xi - x1) / (x2 - x1)
                fill_alpha = int(20 * alpha)
                fill_color = tuple(max(0, min(255, c // 8)) for c in color)
                draw.line((xi, int(yi), xi, y + h), fill=fill_color, width=1)

        # Draw the line itself (2px wide for smoothness)
        line_color = tuple(int(c * alpha) for c in color)
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=line_color, width=2)

        # Endpoint dot with glow
        if points:
            ex, ey = points[-1]
            glow_c = tuple(max(0, c // 3) for c in line_color)
            draw.ellipse((ex - 4, ey - 4, ex + 4, ey + 4), fill=glow_c)
            draw.ellipse((ex - 2, ey - 2, ex + 2, ey + 2), fill=line_color)

    def _draw_fear_greed_gauge(self, img, draw, cx, cy, radius, value, label, alpha=1.0):
        """Draw a semicircular Fear & Greed gauge with anti-aliased arcs."""
        arc_width = max(8, radius // 6)

        # Use Pillow's arc drawing for smooth anti-aliased arcs
        # Background arc
        bbox_outer = (cx - radius, cy - radius, cx + radius, cy + radius)
        bbox_inner = (cx - radius + arc_width, cy - radius + arc_width,
                      cx + radius - arc_width, cy + radius - arc_width)

        # Draw background arc using multiple concentric arcs for thickness
        for r_off in range(arc_width):
            r = radius - r_off
            draw.arc((cx - r, cy - r, cx + r, cy + r), 180, 360,
                     fill=(25, 30, 45), width=1)

        # Colored arc segments: red → orange → yellow → green
        segments = [
            (180, 225, RED),            # Extreme Fear
            (225, 270, (255, 140, 0)),  # Fear
            (270, 315, GOLD),           # Neutral
            (315, 360, GREEN),          # Greed
        ]
        fill_angle = 180 + (value / 100) * 180

        for start, end, color in segments:
            actual_end = min(end, fill_angle)
            if start >= actual_end:
                continue
            seg_color = tuple(int(v * alpha) for v in color)
            for r_off in range(arc_width):
                r = radius - r_off
                draw.arc((cx - r, cy - r, cx + r, cy + r),
                         start, actual_end, fill=seg_color, width=1)

        # Tick marks at segment boundaries
        for angle_deg in [180, 225, 270, 315, 360]:
            angle = math.radians(angle_deg)
            tick_outer = radius + 3
            tick_inner = radius - arc_width - 3
            x1 = int(cx + tick_outer * math.cos(angle))
            y1 = int(cy + tick_outer * math.sin(angle))
            x2 = int(cx + tick_inner * math.cos(angle))
            y2 = int(cy + tick_inner * math.sin(angle))
            draw.line((x1, y1, x2, y2), fill=(50, 58, 78), width=1)

        # Needle with shadow
        needle_angle = math.radians(180 + (value / 100) * 180)
        needle_len = radius - arc_width - 10
        nx = int(cx + needle_len * math.cos(needle_angle))
        ny = int(cy + needle_len * math.sin(needle_angle))
        # Shadow
        draw.line((cx + 1, cy + 1, nx + 1, ny + 1),
                  fill=(0, 0, 0), width=3)
        # Main needle
        draw.line((cx, cy, nx, ny),
                  fill=tuple(int(c * alpha) for c in WHITE), width=2)
        # Center hub
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5),
                     fill=tuple(int(c * alpha) for c in WHITE))
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3),
                     fill=tuple(int(c * alpha * 0.7) for c in NEON_CYAN))

        # Value text
        font_val = get_font(int(radius * 0.55), bold=True)
        val_str = str(value)
        vbbox = draw.textbbox((0, 0), val_str, font=font_val)
        vw = vbbox[2] - vbbox[0]
        vh = vbbox[3] - vbbox[1]
        if value < 25:
            val_color = RED
        elif value < 45:
            val_color = (255, 140, 0)
        elif value < 55:
            val_color = GOLD
        else:
            val_color = GREEN
        self._draw_glow_text(draw, (cx - vw // 2, cy - vh - 8), val_str, font_val,
                             tuple(int(c * alpha) for c in val_color),
                             glow_radius=3, glow_strength=0.2)

        # Label
        font_label = get_font(int(radius * 0.25))
        lbbox = draw.textbbox((0, 0), label, font=font_label)
        lw = lbbox[2] - lbbox[0]
        draw.text((cx - lw // 2, cy + 8), label,
                  fill=tuple(int(c * alpha) for c in GRAY), font=font_label)

        # Sub-labels at extremes
        font_sub = get_font(int(radius * 0.18))
        sub_alpha = int(alpha * 140)
        draw.text((cx - radius - 5, cy + 4), "FEAR",
                  fill=(RED[0], RED[1], RED[2]), font=font_sub)
        greed_bbox = draw.textbbox((0, 0), "GREED", font=font_sub)
        draw.text((cx + radius - (greed_bbox[2] - greed_bbox[0]) + 5, cy + 4), "GREED",
                  fill=(GREEN[0], GREEN[1], GREEN[2]), font=font_sub)

    def render_scene_analysis(self, text_lines, num_frames, frame_offset=0,
                               ticker_items=None, fear_greed=None):
        """Render analysis with glassmorphism panels, highlighted numbers, and F&G gauge."""
        frames = []
        for f in range(num_frames):
            img, draw = self._new_frame()
            t = f / max(num_frames, 1)
            self._draw_full_bg(draw, f + frame_offset)

            # "MARKET ANALYSIS" header with gold glow
            header_y = int(self.h * 0.06)
            font_header = get_font(int(self.w * 0.042), bold=True, condensed=True)
            header_text = "MARKET ANALYSIS"
            hbbox = draw.textbbox((0, 0), header_text, font=font_header)
            hw = hbbox[2] - hbbox[0]
            hx = (self.w - hw) // 2
            h_alpha = ease_out_cubic(min(t * 3, 1.0))
            gold_color = tuple(int(c * h_alpha) for c in GOLD)
            self._draw_glow_text(draw, (hx, header_y), header_text, font_header, gold_color,
                                 glow_radius=4, glow_strength=0.25)

            uy = header_y + hbbox[3] - hbbox[1] + 6
            line_w = int(hw * 0.5 * ease_out_cubic(min(t * 2, 1.0)))
            draw.line((self.w // 2 - line_w // 2, uy, self.w // 2 + line_w // 2, uy),
                      fill=gold_color, width=2)

            # Two-column layout: bullets on left, gauge on right
            has_gauge = fear_greed and fear_greed.get("value") is not None
            left_w = int(self.w * 0.58) if has_gauge else int(self.w * 0.88)
            panel_x = int(self.w * 0.04)
            panel_y = int(self.h * 0.19)
            panel_h = int(self.h * 0.62)

            # Left panel — bullet points
            if t > 0.1:
                panel_alpha = ease_out_cubic(min((t - 0.1) * 3, 1.0))
                self._draw_glassmorphism_card(img, draw, panel_x, panel_y, left_w, panel_h,
                                               radius=16, opacity=0.5 * panel_alpha)
                draw = ImageDraw.Draw(img)

            bullet_y = panel_y + 25
            font_bullet = get_font(int(self.w * 0.024))
            font_highlight = get_font(int(self.w * 0.024), bold=True)
            bullet_colors = [NEON_CYAN, GREEN, NEON_BLUE, GOLD, ACCENT_PURPLE, WHITE]

            for i, line in enumerate(text_lines[:6]):
                delay = 0.18 + i * 0.09
                line_t = max(0, t - delay)
                if line_t > 0:
                    alpha = ease_out_cubic(min(line_t * 3, 1.0))
                    x_slide = int((1 - ease_out_cubic(min(line_t * 2, 1.0))) * 40)
                    x_base = panel_x + 25

                    # Accent bar (small rectangle, not dot)
                    bc = bullet_colors[i % len(bullet_colors)]
                    bar_color = tuple(int(c * alpha) for c in bc)
                    draw.rectangle(
                        (x_base + x_slide, bullet_y + 4, x_base + x_slide + 4, bullet_y + 16),
                        fill=bar_color
                    )

                    # Render text with number highlighting
                    tx = x_base + x_slide + 16
                    self._draw_highlighted_text(draw, tx, bullet_y - 1, line, font_bullet,
                                                 font_highlight, alpha, bc)

                    # Separator
                    sep_y = bullet_y + int(self.h * 0.068)
                    sep_w = int(left_w * 0.80 * alpha)
                    draw.line((x_base + x_slide, sep_y, x_base + x_slide + sep_w, sep_y),
                              fill=(20, 26, 40), width=1)

                bullet_y += int(self.h * 0.082)

            # Right panel — Fear & Greed gauge
            if has_gauge and t > 0.25:
                gauge_alpha = ease_out_cubic(min((t - 0.25) * 2.5, 1.0))
                right_x = panel_x + left_w + int(self.w * 0.02)
                right_w = int(self.w * 0.32)
                right_h = int(self.h * 0.42)

                self._draw_glassmorphism_card(img, draw, right_x, panel_y, right_w, right_h,
                                               radius=16, opacity=0.5 * gauge_alpha)
                draw = ImageDraw.Draw(img)

                # Gauge title
                font_gt = get_font(int(self.w * 0.016), bold=True)
                gt_text = "FEAR & GREED INDEX"
                gtbbox = draw.textbbox((0, 0), gt_text, font=font_gt)
                gtw = gtbbox[2] - gtbbox[0]
                draw.text((right_x + (right_w - gtw) // 2, panel_y + 15),
                          gt_text, fill=tuple(int(c * gauge_alpha) for c in GRAY), font=font_gt)

                # Draw gauge
                gauge_cx = right_x + right_w // 2
                gauge_cy = panel_y + right_h // 2 + 25
                gauge_r = min(right_w, right_h) // 3
                fg_val = fear_greed.get("value", 50)
                fg_label = fear_greed.get("label", "Neutral")
                self._draw_fear_greed_gauge(img, draw, gauge_cx, gauge_cy, gauge_r,
                                             fg_val, fg_label, gauge_alpha)

            if ticker_items:
                self._draw_scrolling_ticker(draw, f + frame_offset, ticker_items)

            frames.append(img)
        return frames

    def _draw_highlighted_text(self, draw, x, y, text, font_normal, font_bold, alpha, accent_color):
        """Draw text with numbers and percentages highlighted in accent colors."""
        import re
        # Split text into segments: numbers/percentages get highlighted
        parts = re.split(r'(\$[\d,]+\.?\d*|[+-]?\d+\.?\d*%|[\d,]+\.?\d*)', text)
        tx = x
        for part in parts:
            if not part:
                continue
            # Check if this is a number/percentage
            is_number = bool(re.match(r'^[\$\+\-]?[\d,]+\.?\d*%?$', part))
            if is_number:
                # Color based on content
                if '+' in part or (not '-' in part and '%' in part):
                    color = GREEN
                elif '-' in part:
                    color = RED
                else:
                    color = accent_color
                fcolor = tuple(int(c * alpha) for c in color)
                draw.text((tx, y), part, fill=fcolor, font=font_bold)
                tx += draw.textlength(part, font=font_bold)
            else:
                fcolor = tuple(int(c * alpha) for c in WHITE)
                draw.text((tx, y), part, fill=fcolor, font=font_normal)
                tx += draw.textlength(part, font=font_normal)

    def render_scene_end(self, num_frames=75, ticker_items=None):
        """End card with CTA."""
        frames = []
        for f in range(num_frames):
            img, draw = self._new_frame()
            t = f / num_frames
            self._draw_full_bg(draw, f + 9999, show_watermark=False)

            cy = self.h * 0.28

            # Brand name with glow
            self._draw_kinetic_text(draw, "DAILY FINANCE PULSE", int(cy),
                                     t, color=GOLD, size_mult=1.0, effect="fade")

            if t > 0.3:
                font_cta = get_font(int(self.w * 0.022))
                alpha = ease_out_cubic(min((t - 0.3) * 2, 1.0))
                ccolor = tuple(int(c * alpha) for c in WHITE)
                cta = "Subscribe for daily market analysis"
                cbbox = draw.textbbox((0, 0), cta, font=font_cta)
                cw = cbbox[2] - cbbox[0]
                draw.text(((self.w - cw) // 2, int(cy + self.h * 0.13)), cta, fill=ccolor, font=font_cta)

            if t > 0.5:
                font_url = get_font(int(self.w * 0.019))
                alpha = ease_out_cubic(min((t - 0.5) * 2, 1.0))
                ucolor = tuple(int(c * alpha) for c in NEON_CYAN)
                url = "dailyfinancepulse.com"
                ubbox = draw.textbbox((0, 0), url, font=font_url)
                uw = ubbox[2] - ubbox[0]
                ux = (self.w - uw) // 2
                self._draw_glow_text(draw, (ux, int(cy + self.h * 0.20)), url, font_url, ucolor,
                                     glow_radius=3, glow_strength=0.2)

            if ticker_items:
                self._draw_scrolling_ticker(draw, f + 9999, ticker_items)

            frames.append(img)
        return frames

    def render_scene_transition(self, num_frames=15, frame_offset=0):
        """Quick transition scene (dark pulse)."""
        frames = []
        for f in range(num_frames):
            img, draw = self._new_frame()
            t = f / num_frames
            # Pulse to darker then back
            darkness = math.sin(t * math.pi)
            overlay = Image.new("RGB", (self.w, self.h), (0, 0, 0))
            img = Image.blend(img, overlay, darkness * 0.5)
            draw = ImageDraw.Draw(img)
            self._draw_particles(draw, f + frame_offset, density_mult=0.3)
            frames.append(img)
        return frames

    def render_full_video(self, market_data, audio_manifest=None, output_path=None):
        """Render the complete video from market data."""
        if os.path.exists(FRAME_DIR):
            shutil.rmtree(FRAME_DIR)
        os.makedirs(FRAME_DIR, exist_ok=True)

        now = datetime.now(timezone.utc)
        date_str = now.strftime("%B %d, %Y").upper()

        # Extract data
        crypto = market_data.get("crypto", {})
        indices = market_data.get("indices", {})
        commodities = market_data.get("commodities", {})
        forex = market_data.get("forex", {})

        # Build item lists
        crypto_items = []
        for sym, data in list(crypto.items())[:5]:
            price = data.get("price", 0)
            if price >= 10000:
                ps = f"${price:,.0f}"
            elif price >= 1:
                ps = f"${price:,.2f}"
            else:
                ps = f"${price:,.4f}"
            crypto_items.append({
                "name": sym, "symbol": sym,
                "price": ps,
                "change": data.get("change_24h", 0),
                "sparkline": data.get("sparkline_7d", []),
            })

        index_items = []
        for name, data in list(indices.items())[:5]:
            price = data.get("price", 0)
            index_items.append({
                "name": name,
                "price": f"{price:,.2f}" if price else "—",
                "change": data.get("change_pct", 0),
                "sparkline": data.get("sparkline_7d", []),
            })

        commodity_items = []
        for name, data in list(commodities.items())[:3]:
            price = data.get("price", 0)
            commodity_items.append({
                "name": name,
                "price": f"${price:,.2f}",
                "change": data.get("change_pct", 0),
            })
        for name, data in list(forex.items())[:2]:
            price = data.get("price", 0)
            commodity_items.append({
                "name": name,
                "price": f"{price:.4f}",
                "change": data.get("change_pct", 0),
            })

        # Build ticker items (all assets for scrolling ticker)
        ticker_items = []
        for item in crypto_items[:4]:
            ticker_items.append(item)
        for item in index_items[:3]:
            ticker_items.append(item)
        for item in commodity_items[:3]:
            ticker_items.append(item)

        # Calculate frame counts based on audio durations
        if audio_manifest:
            segments = audio_manifest.get("segments", [])
            seg_durations = {s["id"]: s.get("audio_duration", s.get("duration_hint", 8)) for s in segments}
        else:
            seg_durations = {
                "hook": 8, "crypto": 25, "indices": 20,
                "commodities_forex": 18, "analysis": 20, "outlook": 8,
            }

        frame_idx = 0
        frame_offset = 0
        transition_frames = 12  # Quick transitions between sections

        def save_frames(frames):
            nonlocal frame_idx
            for fr in frames:
                fr.save(f"{FRAME_DIR}/frame_{frame_idx:05d}.jpg", quality=92)
                frame_idx += 1
            frames.clear()

        # Set title card stats from actual data
        title_stats = []
        if crypto_items:
            ci = crypto_items[0]
            c = GREEN if ci["change"] >= 0 else RED
            chg = f"+{ci['change']:.1f}%" if ci['change'] >= 0 else f"{ci['change']:.1f}%"
            title_stats.append((ci["name"], ci["price"], c, chg))
        if index_items:
            ii = index_items[0]
            c = GREEN if ii["change"] >= 0 else RED
            chg = f"+{ii['change']:.1f}%" if ii['change'] >= 0 else f"{ii['change']:.1f}%"
            title_stats.append((ii["name"], ii["price"], c, chg))
        if commodity_items:
            cm = commodity_items[0]
            c = GREEN if cm["change"] >= 0 else RED
            chg = f"+{cm['change']:.1f}%" if cm['change'] >= 0 else f"{cm['change']:.1f}%"
            title_stats.append((cm["name"], cm["price"], c, chg))
        if title_stats:
            self._title_stats = title_stats

        # Title
        title_frames = int(seg_durations.get("hook", 8) * FPS)
        print(f"Rendering title ({title_frames} frames)...")
        save_frames(self.render_scene_title(date_str, title_frames, ticker_items))
        frame_offset += title_frames

        # Transition
        save_frames(self.render_scene_transition(transition_frames, frame_offset))
        frame_offset += transition_frames

        # Crypto section
        crypto_total = int(seg_durations.get("crypto", 25) * FPS)
        header_f = min(60, crypto_total // 4)
        data_f = crypto_total - header_f
        print(f"Rendering crypto ({crypto_total} frames)...")
        save_frames(self.render_scene_overlay("CRYPTO MARKETS", "24H PERFORMANCE", header_f,
                                               frame_offset, ticker_items, color=NEON_CYAN))
        frame_offset += header_f
        save_frames(self.render_scene_data("CRYPTOCURRENCY", crypto_items, data_f,
                                            frame_offset, ticker_items))
        frame_offset += data_f

        # Transition
        save_frames(self.render_scene_transition(transition_frames, frame_offset))
        frame_offset += transition_frames

        # Indices
        index_total = int(seg_durations.get("indices", 20) * FPS)
        header_f = min(60, index_total // 4)
        data_f = index_total - header_f
        print(f"Rendering indices ({index_total} frames)...")
        save_frames(self.render_scene_overlay("STOCK INDICES", "GLOBAL MARKETS", header_f,
                                               frame_offset, ticker_items, color=NEON_BLUE))
        frame_offset += header_f
        save_frames(self.render_scene_data("INDICES", index_items, data_f,
                                            frame_offset, ticker_items))
        frame_offset += data_f

        # Transition
        save_frames(self.render_scene_transition(transition_frames, frame_offset))
        frame_offset += transition_frames

        # Commodities & Forex
        comm_frames = int(seg_durations.get("commodities_forex", 18) * FPS)
        print(f"Rendering commodities ({comm_frames} frames)...")
        save_frames(self.render_scene_data("COMMODITIES & FOREX", commodity_items, comm_frames,
                                            frame_offset, ticker_items))
        frame_offset += comm_frames

        # Transition
        save_frames(self.render_scene_transition(transition_frames, frame_offset))
        frame_offset += transition_frames

        # Analysis
        analysis_frames = int(seg_durations.get("analysis", 20) * FPS)
        print(f"Rendering analysis ({analysis_frames} frames)...")
        analysis_lines = _generate_analysis_lines(market_data)
        fear_greed = market_data.get("fear_greed")
        save_frames(self.render_scene_analysis(analysis_lines, analysis_frames,
                                                frame_offset, ticker_items, fear_greed))
        frame_offset += analysis_frames

        # End card
        end_frames = int(seg_durations.get("outlook", 8) * FPS)
        print(f"Rendering end card ({end_frames} frames)...")
        save_frames(self.render_scene_end(end_frames, ticker_items))

        print(f"Total frames saved: {frame_idx}")

        # Encode video
        if output_path is None:
            output_path = f"/tmp/finance-v2-{self.profile}.mp4"

        print("Encoding video...")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", f"{FRAME_DIR}/frame_%05d.jpg",
        ]

        audio_path = audio_manifest.get("full_audio") if audio_manifest else None
        if audio_path and os.path.exists(audio_path):
            cmd.extend(["-i", audio_path, "-c:a", "aac", "-b:a", "192k", "-shortest"])

        cmd.extend([
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "19",
            "-movflags", "+faststart",
            output_path,
        ])

        subprocess.run(cmd, check=True, capture_output=True)
        shutil.rmtree(FRAME_DIR, ignore_errors=True)

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        duration = frame_idx / FPS
        print(f"Encoded: {output_path} ({duration:.1f}s, {size_mb:.1f}MB)")

        # Auto-compress if over 15MB (WhatsApp limit is 16MB)
        MAX_SIZE_MB = 15.0
        if size_mb > MAX_SIZE_MB:
            print(f"File exceeds {MAX_SIZE_MB}MB, re-encoding with lower bitrate...")
            target_bitrate_kbps = int((MAX_SIZE_MB * 8 * 1024) / duration * 0.9)  # 90% of theoretical max
            compressed_path = output_path.replace(".mp4", "-compressed.mp4")
            compress_cmd = [
                "ffmpeg", "-y", "-i", output_path,
                "-c:v", "libx264", "-b:v", f"{target_bitrate_kbps}k",
                "-pass", "1", "-an", "-f", "null", "/dev/null",
            ]
            subprocess.run(compress_cmd, check=True, capture_output=True)
            compress_cmd2 = [
                "ffmpeg", "-y", "-i", output_path,
                "-c:v", "libx264", "-b:v", f"{target_bitrate_kbps}k",
                "-pass", "2", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            ]
            if audio_path and os.path.exists(audio_path):
                compress_cmd2.extend(["-c:a", "aac", "-b:a", "128k"])
            compress_cmd2.append(compressed_path)
            subprocess.run(compress_cmd2, check=True, capture_output=True)
            # Clean up 2-pass log files
            for f in ["ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]:
                if os.path.exists(f):
                    os.remove(f)
            comp_size = os.path.getsize(compressed_path) / (1024 * 1024)
            print(f"Compressed: {compressed_path} ({comp_size:.1f}MB)")
            # Replace original with compressed version
            os.replace(compressed_path, output_path)
            size_mb = comp_size

        print(f"Done: {output_path} ({duration:.1f}s, {size_mb:.1f}MB)")
        return output_path


def _generate_analysis_lines(market_data):
    """Generate analysis bullet points from market data."""
    lines = []
    crypto = market_data.get("crypto", {})
    indices = market_data.get("indices", {})

    btc = crypto.get("BTC", {})
    if btc:
        change = btc.get("change_24h", 0)
        price = btc.get("price", 0)
        direction = "surging" if change > 3 else "climbing" if change > 0 else "declining" if change > -3 else "dropping"
        lines.append(f"Bitcoin {direction} at ${price:,.0f} ({change:+.1f}%)")

    eth = crypto.get("ETH", {})
    if eth:
        change = eth.get("change_24h", 0)
        lines.append(f"Ethereum {'outperforming' if change > btc.get('change_24h', 0) else 'tracking'} at ${eth.get('price', 0):,.0f}")

    for name, data in list(indices.items())[:2]:
        change = data.get("change_pct", 0)
        lines.append(f"{name} {'up' if change > 0 else 'down'} {abs(change):.1f}% on the session")

    fg = market_data.get("fear_greed", {})
    if fg:
        lines.append(f"Fear & Greed Index at {fg.get('value', 50)} — {fg.get('label', 'Neutral')}")

    lines.append("Watch for Fed commentary on rates this week")
    return lines


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Market data JSON")
    parser.add_argument("--audio-manifest", help="Audio manifest JSON")
    parser.add_argument("--profile", choices=["shorts", "landscape"], default="landscape")
    parser.add_argument("--output", help="Output path")
    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)
    if "market" in data:
        data = data["market"]

    audio_manifest = None
    if args.audio_manifest:
        with open(args.audio_manifest) as f:
            audio_manifest = json.load(f)

    renderer = FinanceVideoV2(profile=args.profile)
    renderer.render_full_video(data, audio_manifest, args.output)
