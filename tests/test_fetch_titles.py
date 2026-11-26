import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import fetch_titles


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(2)
        if self.path == "/missing":
            self.send_error(404, "Not Found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><head><title> Hello &amp; welcome </title></head></html>")

    def log_message(self, *args):
        pass


@pytest.fixture
def base_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def test_title_404_and_timeout(base_url, monkeypatch):
    monkeypatch.setattr(fetch_titles, "TIMEOUT_SECONDS", 0.5)
    ok, missing, slow = fetch_titles.fetch_titles(
        [f"{base_url}/", f"{base_url}/missing", f"{base_url}/slow"]
    )
    assert ok["title"] == "Hello & welcome" and ok["error"] is None
    assert missing["title"] is None and missing["error"] == "HTTP 404: Not Found"
    assert slow["title"] is None and slow["error"] == "timeout"
