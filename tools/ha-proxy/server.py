#!/usr/bin/env python3
"""
OpenAI-compatible proxy for Home Assistant → OpenClaw.
Handles /v1/models (which OpenClaw doesn't serve) and forwards
/v1/chat/completions to the OpenClaw gateway.

v2: Added streaming support, request logging, error resilience.
"""

import json
import time
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8199
OPENCLAW_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "70fef837b8e641402c3e5e2d7f6a1f8d1a4293cbb4ad1272"
TIMEOUT = 120  # seconds — long enough for complex queries


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/v1/models", "/models"):
            response = {
                "object": "list",
                "data": [{
                    "id": "openclaw:main",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "openclaw"
                }]
            }
            self._json_response(200, response)
        elif self.path == "/":
            self._json_response(200, {
                "status": "ok",
                "service": "saturday-ha-proxy",
                "version": "2.0",
                "upstream": OPENCLAW_URL,
                "uptime_check": self._check_upstream()
            })
        elif self.path == "/health":
            upstream_ok = self._check_upstream()
            code = 200 if upstream_ok == "ok" else 503
            self._json_response(code, {
                "status": "healthy" if upstream_ok == "ok" else "degraded",
                "upstream": upstream_ok
            })
        else:
            self._json_response(404, {"error": "not found"})

    def do_POST(self):
        if self.path in ("/v1/chat/completions", "/chat/completions"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                self._json_response(400, {"error": "invalid JSON"})
                return

            is_streaming = parsed.get("stream", False)

            # Force model to openclaw:main if not set
            parsed.setdefault("model", "openclaw:main")
            body = json.dumps(parsed).encode()

            req = urllib.request.Request(
                f"{OPENCLAW_URL}/v1/chat/completions",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENCLAW_TOKEN}",
                    "x-openclaw-agent-id": "main"
                },
                method="POST"
            )

            try:
                resp = urllib.request.urlopen(req, timeout=TIMEOUT)

                if is_streaming:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Connection", "keep-alive")
                    self.end_headers()

                    # Stream chunks as they arrive
                    while True:
                        chunk = resp.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                else:
                    result = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(result)

                resp.close()

            except urllib.error.HTTPError as e:
                error_body = e.read().decode() if e.fp else str(e)
                self._json_response(e.code, {"error": error_body})
            except urllib.error.URLError as e:
                self._json_response(502, {"error": f"upstream unreachable: {e.reason}"})
            except Exception as e:
                self._json_response(500, {"error": str(e)})
        else:
            self._json_response(404, {"error": "not found"})

    def _json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _check_upstream(self):
        try:
            req = urllib.request.Request(f"{OPENCLAW_URL}/")
            urllib.request.urlopen(req, timeout=3)
            return "ok"
        except Exception:
            return "unreachable"

    def log_message(self, format, *args):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")


if __name__ == "__main__":
    print(f"Saturday HA Proxy v2 on port {PORT} → OpenClaw {OPENCLAW_URL}")
    server = HTTPServer(("0.0.0.0", PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down.")
        server.server_close()
