"""
Lightweight Sensor Ingestion API Server for Digital DNA Mobile biometrics.
Listens for motion (accelerometer, gyroscope) and touch telemetry over HTTP.
"""

import sys
import json
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from collectors.mobile.main_mobile_collector import MobileCollector

class SensorRequestHandler(BaseHTTPRequestHandler):
    collector: Optional[MobileCollector] = None

    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in {"/health", "/api/v1/status"}:
            status = {
                "status": "online",
                "collector_running": self.collector._running if self.collector else False,
                "motion_events": len(self.collector.motion._events) if self.collector else 0,
                "touch_events": len(self.collector.touch._events) if self.collector else 0
            }
            self._send_json(200, status)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            payload = json.loads(post_body.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"error": f"Invalid JSON payload: {str(e)}"})
            return

        if self.path == "/api/v1/sensors/motion":
            if not self.collector:
                self._send_json(500, {"error": "Collector not initialized"})
                return
            ax = float(payload.get("ax", 0.0))
            ay = float(payload.get("ay", 0.0))
            az = float(payload.get("az", 0.0))
            gx = float(payload.get("gx", 0.0))
            gy = float(payload.get("gy", 0.0))
            gz = float(payload.get("gz", 0.0))
            t = payload.get("timestamp", None)
            self.collector.motion.ingest_sensor_reading(ax, ay, az, gx, gy, gz, timestamp=t)
            self._send_json(200, {"status": "ingested", "sensor": "motion"})

        elif self.path == "/api/v1/sensors/touch":
            if not self.collector:
                self._send_json(500, {"error": "Collector not initialized"})
                return
            action = str(payload.get("action", "down"))
            x = float(payload.get("x", 0.0))
            y = float(payload.get("y", 0.0))
            pressure = float(payload.get("pressure", 1.0))
            area = float(payload.get("area", 1.0))
            t = payload.get("timestamp", None)
            self.collector.touch.ingest_touch_event(action, x, y, pressure=pressure, area=area, timestamp=t)
            self._send_json(200, {"status": "ingested", "sensor": "touch"})
        else:
            self._send_json(404, {"error": "Endpoint not found"})

class SensorApiServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8088, collector: Optional[MobileCollector] = None):
        self.host = host
        self.port = port
        self.collector = collector or MobileCollector()
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        SensorRequestHandler.collector = self.collector
        self.collector.start()
        self.server = HTTPServer((self.host, self.port), SensorRequestHandler)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        print(f"SensorApiServer listening on http://{self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        if self.collector:
            self.collector.stop()

if __name__ == "__main__":
    server = SensorApiServer()
    server.start()
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
