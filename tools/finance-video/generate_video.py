#!/usr/bin/env python3
"""
Finance Video Generator — Creates short-form market recap videos.
Formats: 9:16 (Shorts/Reels/TikTok), 16:9 (YouTube), 1:1 (Instagram)

Uses Pillow to render frames, ffmpeg to encode video.
Each video: ~16 seconds, animated data cards, professional dark theme.
"""

import json
import os
import sys
import subprocess
import shutil
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import math

# ── Config ──
PROFILES = {
    "shorts": {"w": 1080, "h": 1920, "label": "9:16"},
    "landscape": {"w": 1920, "h": 1080, "label": "16:9"},
    "square": {"w": 1080, "h": 1080, "label": "1:1"},
}

FPS = 30
FRAME_DIR = "/tmp/finance-frames"

# ── Colors (Dark Professional Theme) ──
BG_COLOR = (13, 17, 23)
CARD_BG = (22, 27, 34)
CARD_BORDER = (48, 54, 61)
GREEN = (46, 160, 67)
RED = (248, 81, 73)
GOLD = (255, 193, 7)
WHITE = (230, 237, 243)
GRAY = (139, 148, 158)
BLUE = (56, 132, 244)
CYAN = (64, 224, 208)


def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def format_price(price):
    if price >= 10000:
        return "${:,.0f}".format(price)
    elif price >= 100:
        return "${:,.2f}".format(price)
    elif price >= 1:
        return "${:,.3f}".format(price)
    return "${:,.4f}".format(price)


def format_change(change):
    if change > 0:
        return "+{:.2f}%".format(change), GREEN
    elif change < 0:
        return "{:.2f}%".format(change), RED
    return "0.00%", GRAY


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


class FinanceVideoGenerator:
    def __init__(self, profile="shorts"):
        self.profile = PROFILES[profile]
        self.w = self.profile["w"]
        self.h = self.profile["h"]
        self.profile_name = profile

    def _new_frame(self):
        img = Image.new("RGB", (self.w, self.h), BG_COLOR)
        draw = ImageDraw.Draw(img)
        return img, draw

    def _draw_header(self, draw, text, y, alpha=1.0):
        font = get_font(int(self.w * 0.042), bold=True)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (self.w - tw) // 2
        color = tuple(int(c * alpha) for c in WHITE)
        draw.text((x, y), text, fill=color, font=font)
        return bbox[3] - bbox[1] + 20

    def _draw_asset_card(self, draw, y, name, price_str, change_str, change_color,
                         x_offset=0, width=None, accent=None):
        if width is None:
            width = self.w - 80
        x = 40 + x_offset
        card_h = int(self.h * 0.055)

        draw_rounded_rect(draw, (x, y, x + width, y + card_h), 12, CARD_BG, CARD_BORDER)

        if accent:
            draw.rectangle((x, y + 8, x + 4, y + card_h - 8), fill=accent)

        font_name = get_font(int(self.w * 0.028), bold=True)
        draw.text((x + 16, y + card_h // 2 - 12), name, fill=WHITE, font=font_name)

        font_price = get_font(int(self.w * 0.026))
        price_bbox = draw.textbbox((0, 0), price_str, font=font_price)
        pw = price_bbox[2] - price_bbox[0]
        draw.text((x + width - pw - 140, y + card_h // 2 - 12), price_str, fill=WHITE, font=font_price)

        font_change = get_font(int(self.w * 0.024), bold=True)
        change_bbox = draw.textbbox((0, 0), change_str, font=font_change)
        cw = change_bbox[2] - change_bbox[0]
        draw.text((x + width - cw - 16, y + card_h // 2 - 10), change_str, fill=change_color, font=font_change)

        return card_h + 8

    def _draw_fear_greed(self, draw, value, label, y):
        cx = self.w // 2
        radius = int(self.w * 0.12)

        draw.ellipse((cx - radius, y, cx + radius, y + radius * 2), outline=CARD_BORDER, width=3)

        font_val = get_font(int(self.w * 0.065), bold=True)

        if value <= 25:
            color = RED
        elif value <= 45:
            color = (255, 165, 0)
        elif value <= 55:
            color = GRAY
        elif value <= 75:
            color = GREEN
        else:
            color = (0, 200, 83)

        val_text = str(value)
        bbox = draw.textbbox((0, 0), val_text, font=font_val)
        vw = bbox[2] - bbox[0]
        vh = bbox[3] - bbox[1]
        draw.text((cx - vw // 2, y + radius - vh // 2 - 10), val_text, fill=color, font=font_val)

        font_label = get_font(int(self.w * 0.022))
        lbbox = draw.textbbox((0, 0), label, font=font_label)
        lw = lbbox[2] - lbbox[0]
        draw.text((cx - lw // 2, y + radius + vh // 2), label, fill=color, font=font_label)

        return radius * 2 + 30

    def generate_market_recap(self, data, output_path):
        if os.path.exists(FRAME_DIR):
            shutil.rmtree(FRAME_DIR)
        os.makedirs(FRAME_DIR, exist_ok=True)

        crypto = data.get("crypto", {})
        indices = data.get("indices", {})
        fg = data.get("fear_greed", {})
        forex = data.get("forex", {})
        commodities = data.get("commodities", {})

        now = datetime.now(timezone.utc)
        date_str = now.strftime("%B %d, %Y")

        frame_num = 0

        # Scene 1: Title (2s)
        for f in range(60):
            img, draw = self._new_frame()
            t = f / 60
            alpha = ease_out_cubic(min(t * 2, 1.0))

            y = int(self.h * 0.35)
            font_brand = get_font(int(self.w * 0.055), bold=True)
            brand = "DAILY FINANCE PULSE"
            bbox = draw.textbbox((0, 0), brand, font=font_brand)
            bw = bbox[2] - bbox[0]
            color = tuple(int(c * alpha) for c in GOLD)
            draw.text(((self.w - bw) // 2, y), brand, fill=color, font=font_brand)

            y += 80
            font_date = get_font(int(self.w * 0.03))
            dbbox = draw.textbbox((0, 0), date_str, font=font_date)
            dw = dbbox[2] - dbbox[0]
            dcolor = tuple(int(c * alpha) for c in GRAY)
            draw.text(((self.w - dw) // 2, y), date_str, fill=dcolor, font=font_date)

            y += 50
            sub = "MARKET RECAP"
            font_sub = get_font(int(self.w * 0.035))
            sbbox = draw.textbbox((0, 0), sub, font=font_sub)
            sw = sbbox[2] - sbbox[0]
            scolor = tuple(int(c * alpha) for c in WHITE)
            draw.text(((self.w - sw) // 2, y), sub, fill=scolor, font=font_sub)

            img.save("{}/frame_{:05d}.png".format(FRAME_DIR, frame_num))
            frame_num += 1

        # Scene 2: Crypto + Fear & Greed (4s)
        btc = crypto.get("BTC", {})
        eth = crypto.get("ETH", {})
        sol = crypto.get("SOL", {})
        for f in range(120):
            img, draw = self._new_frame()
            t = f / 120

            y = int(self.h * 0.08)
            y += self._draw_header(draw, "CRYPTO FEAR & GREED", y)
            y += 20

            animated_val = int(fg.get("value", 50) * ease_out_cubic(min(t * 2, 1.0)))
            y += self._draw_fear_greed(draw, animated_val, fg.get("label", "Neutral"), y)
            y += 20

            if t > 0.3 and btc:
                slide_t = ease_out_cubic(min((t - 0.3) / 0.3, 1.0))
                x_off = int((1 - slide_t) * self.w)
                price_str = format_price(btc.get("price", 0))
                ch_str, ch_color = format_change(btc.get("change_24h", 0))
                self._draw_asset_card(draw, y, "BTC  Bitcoin", price_str, ch_str, ch_color,
                                      x_offset=x_off, accent=CYAN)
                y += int(self.h * 0.07)

            if t > 0.45 and eth:
                slide_t = ease_out_cubic(min((t - 0.45) / 0.3, 1.0))
                x_off = int((1 - slide_t) * self.w)
                price_str = format_price(eth.get("price", 0))
                ch_str, ch_color = format_change(eth.get("change_24h", 0))
                self._draw_asset_card(draw, y, "ETH  Ethereum", price_str, ch_str, ch_color,
                                      x_offset=x_off, accent=BLUE)
                y += int(self.h * 0.07)

            if t > 0.6 and sol:
                slide_t = ease_out_cubic(min((t - 0.6) / 0.3, 1.0))
                x_off = int((1 - slide_t) * self.w)
                price_str = format_price(sol.get("price", 0))
                ch_str, ch_color = format_change(sol.get("change_24h", 0))
                self._draw_asset_card(draw, y, "SOL  Solana", price_str, ch_str, ch_color,
                                      x_offset=x_off, accent=GOLD)

            img.save("{}/frame_{:05d}.png".format(FRAME_DIR, frame_num))
            frame_num += 1

        # Scene 3: Stock Indices (4s)
        idx_items = list(indices.items())[:6]
        for f in range(120):
            img, draw = self._new_frame()
            t = f / 120

            y = int(self.h * 0.08)
            y += self._draw_header(draw, "STOCK INDICES", y)
            y += 20

            for i, (name, vals) in enumerate(idx_items):
                delay = i * 0.1
                if t > delay:
                    slide_t = ease_out_cubic(min((t - delay) / 0.3, 1.0))
                    x_off = int((1 - slide_t) * self.w)
                    price = vals.get("price", 0)
                    price_str = "{:,.2f}".format(price) if price else "—"
                    ch_str, ch_color = format_change(vals.get("change_pct", 0))
                    y += self._draw_asset_card(draw, y, name, price_str, ch_str, ch_color, x_offset=x_off)

            img.save("{}/frame_{:05d}.png".format(FRAME_DIR, frame_num))
            frame_num += 1

        # Scene 4: Commodities & Forex (4s)
        comm_items = list(commodities.items())[:4]
        fx_items = list(forex.items())[:3]
        for f in range(120):
            img, draw = self._new_frame()
            t = f / 120

            y = int(self.h * 0.08)
            y += self._draw_header(draw, "COMMODITIES", y)
            y += 10

            for i, (name, vals) in enumerate(comm_items):
                delay = i * 0.1
                if t > delay:
                    slide_t = ease_out_cubic(min((t - delay) / 0.3, 1.0))
                    x_off = int((1 - slide_t) * self.w)
                    price_str = format_price(vals.get("price", 0))
                    ch_str, ch_color = format_change(vals.get("change_pct", 0))
                    y += self._draw_asset_card(draw, y, name, price_str, ch_str, ch_color,
                                               x_offset=x_off, accent=GOLD)

            y += 20
            if t > 0.4:
                y += self._draw_header(draw, "FOREX", y)
                y += 10
                for i, (name, vals) in enumerate(fx_items):
                    delay = 0.5 + i * 0.1
                    if t > delay:
                        slide_t = ease_out_cubic(min((t - delay) / 0.3, 1.0))
                        x_off = int((1 - slide_t) * self.w)
                        price = vals.get("price", 0)
                        price_str = "{:.4f}".format(price) if "USD" in name else "{:.2f}".format(price)
                        ch_str, ch_color = format_change(vals.get("change_pct", 0))
                        y += self._draw_asset_card(draw, y, name, price_str, ch_str, ch_color, x_offset=x_off)

            img.save("{}/frame_{:05d}.png".format(FRAME_DIR, frame_num))
            frame_num += 1

        # Scene 5: End Card (2s)
        for f in range(60):
            img, draw = self._new_frame()
            t = f / 60
            alpha = ease_out_cubic(min(t * 2, 1.0))

            y = int(self.h * 0.3)
            font_big = get_font(int(self.w * 0.035), bold=True)
            text = "DAILY FINANCE PULSE"
            bbox = draw.textbbox((0, 0), text, font=font_big)
            tw = bbox[2] - bbox[0]
            color = tuple(int(c * alpha) for c in GOLD)
            draw.text(((self.w - tw) // 2, y), text, fill=color, font=font_big)

            y += 80
            font_cta = get_font(int(self.w * 0.028))
            cta = "Subscribe for daily market updates"
            cbbox = draw.textbbox((0, 0), cta, font=font_cta)
            cw = cbbox[2] - cbbox[0]
            ccolor = tuple(int(c * alpha) for c in GRAY)
            draw.text(((self.w - cw) // 2, y), cta, fill=ccolor, font=font_cta)

            img.save("{}/frame_{:05d}.png".format(FRAME_DIR, frame_num))
            frame_num += 1

        # Encode
        print("Encoding {} frames at {}fps...".format(frame_num, FPS))
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", "{}/frame_%05d.png".format(FRAME_DIR),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "23",
            "-movflags", "+faststart",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        shutil.rmtree(FRAME_DIR, ignore_errors=True)

        duration = frame_num / FPS
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print("Done: {} ({:.1f}s, {:.1f}MB, {})".format(output_path, duration, size_mb, self.profile["label"]))
        return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Finance Video Generator")
    parser.add_argument("--data", type=str, help="Path to market data JSON")
    parser.add_argument("--profile", choices=["shorts", "landscape", "square"], default="shorts")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--all-profiles", action="store_true", help="Generate all 3 formats")
    args = parser.parse_args()

    if args.data:
        with open(args.data) as f:
            data = json.load(f)
        if "market" in data:
            data = data["market"]
    else:
        sys.path.insert(0, os.path.expanduser("~/finance-publisher"))
        from data_pipeline import collect_all_data
        print("Fetching market data...")
        data = collect_all_data()

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = os.path.expanduser("~/finance-video-generator/output")
    os.makedirs(output_dir, exist_ok=True)

    if args.all_profiles:
        for profile in ["shorts", "landscape", "square"]:
            output = "{}/market-recap-{}-{}.mp4".format(output_dir, date_str, profile)
            gen = FinanceVideoGenerator(profile=profile)
            gen.generate_market_recap(data, output)
    else:
        output = args.output or "{}/market-recap-{}-{}.mp4".format(output_dir, date_str, args.profile)
        gen = FinanceVideoGenerator(profile=args.profile)
        gen.generate_market_recap(data, output)


if __name__ == "__main__":
    main()
